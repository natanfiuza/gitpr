import subprocess
import os
import json
from google import genai
import click
from src.security import decrypt_data

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
    """Envia o diff e o contexto para o Gemini e retorna um JSON parseado de acordo com a ação."""
    if not diff_text or not diff_text.strip():
        click.secho("⚠️ Nenhum diff encontrado. Faça alguma alteração antes de rodar o comando.", fg="yellow")
        return None

    # Lê o valor encriptado do ambiente e desencripta na hora
    api_key_encrypted = os.getenv("GEMINI_API_KEY")
    if not api_key_encrypted:
      click.secho("❌ GEMINI_API_KEY inválida ou não encontrada...", fg="red")
      return None    
    api_key = decrypt_data(api_key_encrypted)
    api_model = os.getenv("GEMINI_API_MODEL", "gemini-2.5-flash")

    if not api_key:
        click.secho("❌ GEMINI_API_KEY inválida ou não encontrada. Apague a pasta ~/.gitpr e reconfigure.", fg="red")
        return None

    # Prepara o bloco de contexto caso o arquivo .gitpr.md exista
    contexto_adicional = f"\n\nRegras de Negócio e Contexto do Projeto:\n{skill_context}" if skill_context else ""

    # Construção dinâmica do Prompt baseada na ação solicitada
    if action_type == "commit":
        prompt = f"""
        Atue como um Desenvolvedor Sênior. Analise o seguinte `git diff` anexo.
        {contexto_adicional}
        
        Gere um JSON estrito contendo apenas uma chave:
        1. "commit_message": Uma única frase curta e precisa seguindo o padrão Conventional Commits (ex: feat:, fix:, refactor:).
    
        Retorne APENAS um JSON válido, sem blocos de código Markdown (` ```json `) em volta.
        Diff:\n{diff_text}
        """
    elif action_type == "review":
        prompt = f"""
        Atue como um Desenvolvedor Sênior e Revisor de Código exigente. Analise o seguinte `git diff` anexo.
        {contexto_adicional}
        
        Faça um Code Review focado estritamente nas "Regras de Negócio e Contexto do Projeto" fornecidas acima.
        Se não houver regras específicas, use boas práticas gerais de Clean Code e princípios SOLID.
        
        Aponte o que NÃO está de acordo com as diretrizes e sugira melhorias reais.
        Gere um JSON estrito contendo apenas uma chave:
        1. "review": Um texto em Markdown contendo a análise completa do code review.
        
        Retorne APENAS um JSON válido, sem blocos de código Markdown (` ```json `) em volta.
        Diff:\n{diff_text}
        """
    else: # Padrão: "pr"
        prompt = f"""
        Atue como um Desenvolvedor Sênior. Analise o seguinte `git diff` anexo.
        {contexto_adicional}
        
        Gere um JSON estrito contendo duas chaves:
        1. "commit_message": Uma frase curta seguindo o padrão Conventional Commits (ex: feat:, fix:, refactor:).
        2. "pr_description": Uma descrição de PR em Markdown contendo 'Resumo', 'Mudanças Técnicas' (bullet points) e 'Impacto'. Considere o contexto do projeto fornecido, se houver.
        
        Retorne APENAS um JSON válido, sem blocos de código Markdown (` ```json `) em volta.
        Diff:\n{diff_text}
        """

    try:
        click.secho("🤖 O GitPR está analisando o seu código...\n", fg="cyan")
        
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=api_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        return json.loads(response.text)
    except Exception as e:
        click.secho(f"❌ Erro ao contactar a API do Gemini: {str(e)}", fg="red")
        return None

def generate_skill_template():
    """Gera o arquivo de template .gitpr.md na raiz do projeto."""
    skill_file = os.path.join(os.getcwd(), ".gitpr.md")
    
    if os.path.exists(skill_file):
        click.secho("⚠️ O arquivo .gitpr.md já existe neste diretório. Edite-o diretamente.", fg="yellow")
        return False

    template = """# Contexto do Projeto (GitPR Skill)

## 🎯 Sobre o Projeto
Este é um sistema de [descreva o sistema]. Ele é focado em [objetivo principal].

## 🏗️ Arquitetura e Tecnologias
- Linguagem principal: [ex: Python 3.11]
- Framework: [ex: FastAPI]

## 📏 Regras de Negócio e Clean Code
1. **Nomenclatura**: Variáveis e métodos em `snake_case`, classes em `PascalCase`.
2. **Tipagem**: Uso de Type Hints é obrigatório.
3. **Idioma**: Código em inglês, mensagens em português.
"""
    try:
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(template)
        click.secho("✅ Arquivo .gitpr.md gerado com sucesso! Edite-o com as regras do seu projeto.", fg="green")
        return True
    except Exception as e:
        click.secho(f"❌ Erro ao gerar o arquivo de skill: {e}", fg="red")
        return False

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
        # Atualiza as referências remotas
        subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        click.secho("⚠️ Aviso: Falha ao fazer fetch (sem internet ou remote inexistente). Usando apenas diff local.", fg="yellow")
        return get_git_diff() # Fallback amigável

    base_branch = get_base_branch()
    try:
        # Executa o diff comparando a branch base remota com as alterações locais
        result = subprocess.run(
            ["git", "diff", f"origin/{base_branch}"], 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        click.secho(f"❌ Erro ao executar o Git Full Diff: {e.stderr}", fg="red")
        return None