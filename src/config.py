import os
import sys
import socket
import click
import yaml
from pathlib import Path
from dotenv import load_dotenv, set_key
from src.security import encrypt_data, decrypt_data, get_or_create_key

# Caminho para o ficheiro .env global na pasta do utilizador (ex: ~/.gitpr/.env)
ENV_FILE = os.path.join(os.path.expanduser("~"), ".gitpr", ".env")

def get_ai_provider():
    """Retorna o provedor de IA padrão configurado, ou 'gemini' como fallback."""
    load_dotenv(ENV_FILE)
    return os.getenv("DEFAULT_AI_PROVIDER", "gemini").lower()

def get_api_key(provider):
    """Lê e desencripta a chave de API correspondente ao provedor escolhido."""
    load_dotenv(ENV_FILE)
    
    if provider == "gemini":
        encrypted_key = os.getenv("GEMINI_API_KEY_ENCRYPTED")
    elif provider == "deepseek":
        encrypted_key = os.getenv("DEEPSEEK_API_KEY_ENCRYPTED")
    else:
        return None

    if encrypted_key:
        return decrypt_data(encrypted_key)
    return None

def get_api_model(provider):
    """Retorna o modelo de IA configurado no .env ou um fallback padrão."""
    load_dotenv(ENV_FILE)
    
    if provider == "gemini":
        return os.getenv("GEMINI_API_MODEL", "gemini-pro-latest")
    elif provider == "deepseek":
        return os.getenv("DEEPSEEK_API_MODEL", "deepseek-v4-pro")
        
    return None

def setup_environment():
    """Garante que as chaves de encriptação, o provedor padrão e a chave da API estão configurados."""
    # Garante que a pasta global existe
    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
    
    # Chama a função existente em security.py para garantir que a chave mestra existe
    get_or_create_key()

    load_dotenv(ENV_FILE)
    
    # Pergunta o provedor padrão se não existir
    provider = os.getenv("DEFAULT_AI_PROVIDER")
    if not provider:
        click.secho("🤖 Bem-vindo ao GitPR! Vamos configurar o seu motor de IA.", fg="cyan", bold=True)
        provider = click.prompt(
            "Qual inteligência artificial deseja utilizar como padrão?", 
            type=click.Choice(['gemini', 'deepseek'], case_sensitive=False),
            default='gemini'
        ).lower()
        set_key(ENV_FILE, "DEFAULT_AI_PROVIDER", provider)
        click.echo("")

    # Verifica se a chave do provedor escolhido existe
    api_key = get_api_key(provider)
    if not api_key:
        click.secho(f"🔑 Chave de API do {provider.capitalize()} não encontrada.", fg="yellow")
        raw_key = click.prompt(f"Cole aqui a sua chave de API do {provider.capitalize()}", hide_input=True)
        
        # Encripta e guarda com o prefixo correto
        encrypted_key = encrypt_data(raw_key.strip())
        env_var_name = f"{provider.upper()}_API_KEY_ENCRYPTED"
        
        set_key(ENV_FILE, env_var_name, encrypted_key)
        click.secho("✅ Chave guardada com segurança em disco (Encriptada)!", fg="green")
        click.echo("")

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
        

def load_linter_rules():
    """
    Carrega as regras do linter estático a partir do arquivo .gitpr.linter.yml.
    Retorna uma lista de regras ou uma lista vazia se o arquivo não existir.
    """
    file_path = os.path.join(os.getcwd(), ".gitpr.linter.yml")

    # Se o arquivo não existir no projeto, não é um erro. Apenas não há regras a aplicar.
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Retorna a lista de regras ou vazio se o arquivo estiver em branco
        if not config or "rules" not in config:
            return []

        return config.get("rules", [])

    except yaml.YAMLError as e:
        # Se o usuário errar a indentação ou aspas, avisamos sem estourar o terminal
        click.secho(f"\n❌ Erro de sintaxe no arquivo .gitpr.linter.yml:\n{e}", fg="red")
        return []
    except Exception as e:
        click.secho(f"\n❌ Erro inesperado ao ler as regras do linter: {e}", fg="red")
        return []        