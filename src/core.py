import subprocess
import os
import json
from google import genai
import click
import stat
import urllib.request

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


def get_skill_context():
    """Lê o arquivo de contexto .gitpr.md se existir no diretório atual."""
    # Procura o arquivo na raiz de onde o comando gitpr foi executado
    skill_file = os.path.join(os.getcwd(), ".gitpr.md")
    
    if os.path.exists(skill_file):
        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                conteudo = f.read()
                click.secho("🧠 Arquivo .gitpr.md (Skill) encontrado e carregado!", fg="blue")
                return conteudo
        except Exception as e:
            click.secho(f"⚠️ Aviso: Falha ao ler o arquivo .gitpr.md ({e})", fg="yellow")
    
    # Retorna vazio se não existir, para a IA usar o conhecimento padrão
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

    # Construção dos Prompts curtos (forçando o formato de Objeto)
    if action_type == "commit":
        prompt = f"Gere APENAS um objeto JSON no formato {{\"commit_message\": \"...\"}} para este diff:\n{diff_text}"
    elif action_type == "review" or action_type == "fullreview":
        prompt = f"Gere APENAS um objeto JSON no formato {{\"review\": \"...\"}} apontando erros e melhorias para este diff:\n{diff_text}"
    else: # pr
        prompt = f"Gere APENAS um objeto JSON no formato {{\"commit_message\": \"...\", \"pr_description\": \"...\"}} para este diff:\n{diff_text}"

    # TENTA RECUPERAR DO CACHE
    cached_data = get_cached_response(action_folder, prompt)
    if cached_data:
        click.secho("⚡ Resposta recuperada do cache local.", fg="green", dim=True)
        return cached_data

    # CHAMADA À API COM CONFIGURAÇÃO DETERMINÍSTICA
    try:
        click.secho("🤖 O GitPR está analisando o seu código...\n", fg="cyan")
        client = genai.Client(api_key=api_key)
        
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

        # Se a IA retornar uma lista [ { ... } ], pega o primeiro objeto
        if isinstance(result_json, list):
            result_json = result_json[0] if result_json else {}

        # SALVA NO CACHE
        save_cached_response(action_folder, action_type, prompt, result_json)

        return result_json

    except Exception as e:
        click.secho(f"❌ Erro ao contactar a API do Gemini: {str(e)}", fg="red")
        return None

def generate_skill_template():
    """Gera os arquivos de template .gitpr.md e .gitpr.linter.yml na raiz do projeto."""
    skill_file = os.path.join(os.getcwd(), ".gitpr.md")
    linter_file = os.path.join(os.getcwd(), ".gitpr.linter.yml")
    
    # Gera o arquivo MD (Contexto para IA)
    if not os.path.exists(skill_file):
        template_md = """# Contexto do Projeto (GitPR Skill)

## Sobre o Projeto
Este é um sistema de [descreva o sistema]. Ele é focado em [objetivo principal].

## Arquitetura e Tecnologias
- Linguagem principal: [ex: Python 3.11]
- Framework: [ex: FastAPI]

## Regras de Negócio e Clean Code
* Nomenclatura: Variáveis e métodos em `snake_case`, classes em `PascalCase`.
* Tipagem: Uso de Type Hints é obrigatório.
* Idioma: Código em inglês, mensagens em português.
* --commit: A frase deve ser em português e refletir claramente a essência da mudança feita no código.
* --review: Em reviews ou fullreviews gere um texto mais completo e detalhado. Com a estrutura Descrição, Erros Críticos e Melhorias e Observações em formato markdown
"""
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(template_md)
        click.secho("✅ Arquivo .gitpr.md gerado com sucesso!", fg="green")

    # Gera o arquivo YAML (Linter Estático)
    if not os.path.exists(linter_file):
        template_yaml = """rules:
  - name: "check-console-log"
    extensions: ["js"]
    regex: 'console\.log'
    message: "🚨 'console.log' encontrado no arquivo {file_name} (Linha {line_number})"
    ignore_comments: true
    ignore_paths:
      - "app/js/plugin/multiselect/*"
      - "js/axios/*"
      - "*/Arquivos_HighCharts/*"
      - "*jquery*.js"
      - "*moment.js"

  - name: "check-localhost"
    extensions: ["js"]
    regex: 'http(s)?://(localhost|127\.0\.0\.1)'
    message: "🚨 Uso de 'localhost' detectado na linha {line_number} do arquivo {file_name}"
    ignore_comments: true
"""
        with open(linter_file, "w", encoding="utf-8") as f:
            f.write(template_yaml)
        click.secho("✅ Arquivo .gitpr.linter.yml gerado com sucesso!", fg="green")

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