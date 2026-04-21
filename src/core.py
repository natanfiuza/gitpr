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

def generate_pr_content(diff_text):
    """Envia o diff para o Gemini e retorna um JSON parseado."""
    if not diff_text or not diff_text.strip():
        click.secho("⚠️ Nenhum diff encontrado. Faça alguma alteração antes de rodar o comando.", fg="yellow")
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        click.secho("❌ GEMINI_API_KEY não encontrada. Apague a pasta ~/.gitpr e rode novamente.", fg="red")
        return None
    api_key = decrypt_data(api_key)    
    api_model = os.getenv("GEMINI_API_MODEL", "gemini-2.5-flash")

    prompt = f"""
    Atue como um Desenvolvedor Sénior. Analise o seguinte `git diff` anexo que contém as alterações de código.
    
    Gere um JSON estrito contendo duas chaves:
    1. "commit_message": Uma frase curta seguindo o padrão Conventional Commits (ex: feat:, fix:, refactor:).
    2. "pr_description": Uma descrição de PR em Markdown contendo 'Resumo', 'Mudanças Técnicas' (bullet points) e 'Impacto'.
    
    Retorne APENAS um JSON válido, sem blocos de código Markdown (` ```json `) em volta.
    
    Diff:
    {diff_text}
    """

    try:
        click.secho("🤖 O GitPR está analisando o seu código...", fg="cyan")
        
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