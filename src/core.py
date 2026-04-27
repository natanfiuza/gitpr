import os
import json
import stat
import time
import click
import subprocess
import urllib.request
import urllib.error
from google import genai
from src.security import decrypt_data
from src.cache import get_cached_response, save_cached_response

def get_git_diff():
    """Executa 'git diff HEAD' e retorna a saída."""
    try:
        # Adicionamos encoding="utf-8" para o Windows não chorar com caracteres especiais
        result = subprocess.run(
            ["git", "diff", "HEAD"], 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        click.secho(f"❌ Erro ao executar o Git: {e.stderr}", fg="red")
        return None
    except FileNotFoundError:
        click.secho("❌ Git não encontrado. Certifique-se de que está instalado e no PATH.", fg="red")
        return None


def get_current_branch():
    """Retorna o nome da branch atual."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "main" # Fallback


def get_skill_context(action_type="pr"):
    """Lê o arquivo de contexto correto baseado na ação (PR/Commit ou Review)."""
    
    # Define qual arquivo procurar
    if action_type == "commit":
        target_file = ".gitpr.commit.md"
    elif action_type == "pr":
        target_file = ".gitpr.pr.md"
    else: # review ou fullreview
        target_file = ".gitpr.review.md"

    skill_file = os.path.join(os.getcwd(), target_file)
    
    # Fallback para o arquivo antigo (para retrocompatibilidade com usuários da versão anterior)
    legacy_file = os.path.join(os.getcwd(), ".gitpr.md")

    # Verifica o novo primeiro; se não achar, tenta o antigo
    file_to_load = skill_file if os.path.exists(skill_file) else (legacy_file if os.path.exists(legacy_file) else None)
    
    if file_to_load:
        try:
            with open(file_to_load, "r", encoding="utf-8") as f:
                conteudo = f.read()
                nome_arquivo = os.path.basename(file_to_load)
                click.secho(f"🧠 Arquivo {nome_arquivo} (Skill) encontrado e carregado!", fg="blue")
                return conteudo
        except Exception as e:
            click.secho(f"⚠️ Aviso: Falha ao ler o arquivo {nome_arquivo} ({e})", fg="yellow")
    
    # Retorna vazio se não existir
    return ""


def generate_pr_content(diff_text, action_type="pr", skill_context=""):
    """Envia o diff para o Gemini usando System Instruction e retorna um JSON parseado."""
    if not diff_text or not diff_text.strip():
        click.secho("⚠️ Nenhum diff encontrado. Faça alguma alteração antes de rodar o comando.", fg="yellow")
        return None

    # Configuração de pastas para o Cache
    action_folder_map = {
        "pr": "pr_desc",
        "commit": "commit",
        "review": "review",
        "fullreview": "review"
    }
    action_folder = action_folder_map.get(action_type, "misc")

    # Preparação das Chaves e Modelo
    api_key_encrypted = os.getenv("GEMINI_API_KEY")
    if not api_key_encrypted:
        click.secho("❌ GEMINI_API_KEY não encontrada.", fg="red")
        return None    
    
    api_key = decrypt_data(api_key_encrypted)
    if not api_key:
        click.secho("❌ Falha ao descriptografar a GEMINI_API_KEY. Apague a pasta ~/.gitpr e reconfigure.", fg="red")
        return None
    api_model = os.getenv("GEMINI_API_MODEL", "gemini-2.5-flash")

    # Definição da Instrução de Sistema (Persona e Regras)
    # Se houver skill_context, ele vira a regra mestre do sistema.
    instrucao_sistema = skill_context if skill_context else "Atue como um Desenvolvedor Sênior e Revisor de Código exigente."

    
    # O arquivo de skill baixado assume o comando. 
    # Se ele não existir (por algum motivo), usamos um fallback seguro.
    if action_type == "commit":
        instrucao_sistema = skill_context if skill_context else "Você é um especialista em Git. Gere mensagens de commit concisas."
        prompt = f"Gere APENAS um objeto JSON no formato {{\"commit_message\": \"...\"}} para este diff:\n{diff_text}"
        
    elif action_type in ["review", "fullreview"]:
        instrucao_sistema = skill_context if skill_context else "Você é um Arquiteto de Software Sênior. Foque em apontar melhorias de arquitetura."
        prompt = f"Gere APENAS um objeto JSON no formato {{\"review\": \"...\"}} apontando erros e melhorias para este diff:\n{diff_text}"
        
    else: # pr
        instrucao_sistema = skill_context if skill_context else "Você é um Tech Lead redigindo descrições de PR limpas e técnicas."
        prompt = f"Gere APENAS um objeto JSON no formato {{\"commit_message\": \"...\", \"pr_description\": \"...\"}} para este diff:\n{diff_text}"
    # TENTA RECUPERAR DO CACHE
    cached_data = get_cached_response(action_folder, prompt)
    if cached_data:
        click.secho("⚡ Resposta recuperada do cache local.", fg="green", dim=True)
        return cached_data

    # CHAMADA À API COM MECANISMO DE RETRY
    max_retries = 3
    retry_delay = 2 # segundos de espera entre tentativas

    click.secho("🤖 O GitPR está analisando o seu código...\n", fg="cyan")
    client = genai.Client(api_key=api_key)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=api_model,
                contents=prompt,
                config={
                    "system_instruction": instrucao_sistema,
                    "response_mime_type": "application/json",
                    "temperature": 0.0,
                    "top_p": 0.1,
                    "top_k": 1
                }
            )
            
            result_json = json.loads(response.text)

            # 🛡️ ESCUDO: Se a IA retornar uma lista [ { ... } ]
            if isinstance(result_json, list):
                result_json = result_json[0] if result_json else {}

            # SALVA NO CACHE E RETORNA
            save_cached_response(action_folder, action_type, prompt, result_json)
            return result_json

        except Exception as e:
            if attempt < max_retries:
                # O dim=True deixa o texto mais apagado no terminal para não poluir visualmente
                click.secho(f"⚠️ Instabilidade de rede detetada. A tentar novamente ({attempt}/{max_retries})...", fg="yellow", dim=True)
                time.sleep(retry_delay)
            else:
                # Falhou em todas as tentativas
                click.secho(f"❌ Erro crítico ao contactar a API do Gemini após {max_retries} tentativas: {str(e)}", fg="red", bold=True)
                return None

def generate_skill_template():
    """
    Faz o download dos templates .gitpr.pr.md, .gitpr.review.md 
    e .gitpr.linter.yml diretamente do repositório oficial.
    """
    click.secho("\n📥 Iniciando a configuração dos templates do GitPR...", fg="cyan", bold=True)
    
    base_url = "https://raw.githubusercontent.com/natanfiuza/gitpr/main/templates/"
    
    # Atualizado para contemplar os 3 arquivos
    files_to_download = {
        ".gitpr.commit.md": "gitpr.commit.md",
        ".gitpr.pr.md": "gitpr.pr.md",
        ".gitpr.review.md": "gitpr.review.md",
        ".gitpr.linter.yml": "gitpr.linter.yml"
    }
    
    success_count = 0
    
    for local_name, remote_name in files_to_download.items():
        file_path = os.path.join(os.getcwd(), local_name)
        url = base_url + remote_name
        
        if os.path.exists(file_path):
            click.secho(f"⚠️ O arquivo {local_name} já existe neste diretório. Ele não será sobrescrito.", fg="yellow")
            continue
            
        try:
            click.echo(f"A descarregar {local_name}...")
            with urllib.request.urlopen(url, timeout=5) as response:
                content = response.read().decode('utf-8')
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            success_count += 1
            
        except urllib.error.URLError as e:
            click.secho(f"❌ Erro de rede ao baixar {local_name}: {e.reason}", fg="red")
        except Exception as e:
            click.secho(f"❌ Falha ao processar {local_name}: {e}", fg="red")

    if success_count > 0:
        click.secho("\n✅ Templates base configurados com sucesso!", fg="green", bold=True)
        click.echo("Você pode agora abrir os arquivos gerados e personalizar o comportamento da ferramenta para o seu projeto:\n")       
        click.echo("  1. As regras de arquitetura para a IA no arquivo '.gitpr.pr.md' e '.gitpr.review.md'\n")
        click.echo("  2. As regras de regex locais no arquivo '.gitpr.linter.yml'\n")
    else:
        click.echo("\nNenhum arquivo novo foi baixado.")

def get_base_branch():
    """Descobre a branch principal remota (ex: main ou master)."""
    try:
        # Busca a referência da branch default do remote
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True, text=True, check=True
        )
        # O retorno é algo como 'refs/remotes/origin/main', então pegamos a última parte
        return result.stdout.strip().split('/')[-1]
    except subprocess.CalledProcessError:
        click.secho("⚠️ Aviso: Branch principal remota não detectada. Assumindo 'main' como fallback padrão.", fg="yellow")
        return "main" # Fallback padrão caso não encontre

def get_git_full_diff():
    """Faz o fetch e captura o diff entre a branch principal remota e o estado atual."""
    click.secho("🔄 Sincronizando com o repositório remoto (git fetch)...", fg="cyan")
    try:
        # 1. Faz o fetch para garantir que sabemos onde a origin/main está
        subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
        
        base_branch = get_base_branch()
        
        # 2. Encontra o HASH do commit onde a sua branch nasceu (o ancestral comum)
        merge_base_res = subprocess.run(
            ["git", "merge-base", f"origin/{base_branch}", "HEAD"],
            capture_output=True, text=True, check=True
        )
        ancestor_hash = merge_base_res.stdout.strip()

        # 3. Faz o diff entre esse HASH e o seu WORKSPACE ATUAL (sem usar HEAD)
        # Ao passar apenas o hash, o Git compara esse commit com os arquivos no seu disco.
        result = subprocess.run(
            ["git", "diff", ancestor_hash], 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            check=True
        )
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        click.secho(f"❌ Erro ao calcular o diff: {e.stderr}", fg="red")
        return None
    
def install_git_hooks():
    """Faz o download e instala os scripts de pre-commit e prepare-commit-msg."""
    hooks_dir = os.path.join(os.getcwd(), ".git", "hooks")
    
    if not os.path.exists(hooks_dir):
        click.secho("❌ Erro: Pasta .git não encontrada. Execute na raiz do projeto.", fg="red")
        return False

    # Mapeamento: Nome do Hook no Git -> Nome do Template no seu GitHub
    hooks_to_install = {
        "pre-commit": "pre-commit-template.sh",
        "prepare-commit-msg": "prepare-commit-msg-template.sh"
    }

    base_url = "https://raw.githubusercontent.com/natanfiuza/gitpr/main/scripts/"
    success_count = 0

    for hook_name, template_name in hooks_to_install.items():
        hook_path = os.path.join(hooks_dir, hook_name)
        url = base_url + template_name

        try:
            click.secho(f"📥 A descarregar {hook_name}...", fg="cyan")
            
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
                
            with open(hook_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Atribui permissão de execução (chmod +x)
            st = os.stat(hook_path)
            os.chmod(hook_path, st.st_mode | stat.S_IEXEC)
            
            success_count += 1
        except Exception as e:
            click.secho(f"⚠️ Falha ao instalar {hook_name}: {e}", fg="yellow")

    return success_count == len(hooks_to_install)