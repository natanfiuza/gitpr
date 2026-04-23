import os
import sys
import socket
from pathlib import Path
import click
from dotenv import load_dotenv
from src.security import encrypt_data

def setup_environment():
    """
    Verifica se o diretório e o arquivo .env existem no diretório home do usuário (~/.gitpr).
    Se não existirem, cria e solicita as configurações iniciais.
    Em seguida, carrega as variáveis de ambiente.
    """
    home_dir = Path.home() / ".gitpr"
    env_file = home_dir / ".env"

    if not env_file.exists():
        click.secho("🔧 Primeira execução detectada! Vamos configurar o GitPR CLI.", fg="cyan")
        home_dir.mkdir(parents=True, exist_ok=True)
        
        api_key = click.prompt("🔑 Insira sua GEMINI_API_KEY", hide_input=True)
        
        # Adicionamos a opção do modelo com o default sugerido
        api_model = click.prompt(
            "🤖 Modelo do Gemini", 
            default="gemini-2.5-flash"
        )
        
        default_filename = "{branch}_{datetime}_PR_DESC.md"
        output_filename = click.prompt(
            "📄 Padrão do nome do arquivo de saída", 
            default=default_filename
        )
        # Padrões para Review e Full Review
        default_review_pattern = "{branch}_{datetime}_PR_REVIEW.txt"
        output_review = click.prompt(
            "📄 Padrão do nome do arquivo de REVIEW", 
            default=default_review_pattern
        )

        default_full_pattern = "{branch}_{datetime}_PR_FULLREVIEW.txt"
        output_full = click.prompt(
            "📄 Padrão do nome do arquivo de FULL REVIEW", 
            default=default_full_pattern
        )
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={encrypt_data(api_key)}\n")
            f.write(f"GEMINI_API_MODEL={api_model}\n")
            f.write(f"OUTPUT_FILE_NAME={output_filename}\n")
            f.write(f"OUTPUT_FILE_NAME_REVIEW={output_review}\n") 
            f.write(f"OUTPUT_FILE_NAME_FULLREVIEW={output_full}\n")
            
        click.secho(f"✅ Configuração salva em: {env_file}\n", fg="green")

    # Carrega as variáveis de ambiente do arquivo
    load_dotenv(env_file)

def check_internet_connection(timeout=2):
    """Verifica se há conexão com a internet tentando conectar a um DNS global."""
    try:
        # Salva o timeout padrão do sistema
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        
        # Conecta e fecha o socket automaticamente usando 'with'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("8.8.8.8", 53))
            
        # CRÍTICO: Restaura o timeout para não quebrar a API do Gemini!
        socket.setdefaulttimeout(original_timeout)
        return True
    except socket.error:
        click.secho("\n❌ Erro: Sem conexão com a internet.", fg="red", bold=True)
        click.secho("O GitPR precisa de acesso à rede para consultar a IA e verificar atualizações.", fg="yellow")
        click.secho("Verifique sua conexão e tente novamente.\n", fg="white")
        sys.exit(1)