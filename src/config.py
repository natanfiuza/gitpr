import os
from pathlib import Path
import click
from dotenv import load_dotenv

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
        
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
            f.write(f"GEMINI_API_MODEL={api_model}\n")
            f.write(f"OUTPUT_FILE_NAME={output_filename}\n")
            
        click.secho(f"✅ Configuração salva em: {env_file}\n", fg="green")

    # Carrega as variáveis de ambiente do arquivo
    load_dotenv(env_file)