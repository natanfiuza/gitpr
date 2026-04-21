from cryptography.fernet import Fernet
from pathlib import Path

# Caminho onde a chave mestra de criptografia será guardada
KEY_PATH = Path.home() / ".gitpr" / "secret.key"

def get_or_create_key():
    """
    Recupera a chave mestra do disco ou gera uma nova caso não exista.
    """
    if not KEY_PATH.exists():
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as key_file:
            key_file.write(key)
    return open(KEY_PATH, "rb").read()

def encrypt_data(data: str) -> str:
    """
    Transforma uma string em um hash criptografado.
    """
    if not data:
        return ""
    key = get_or_create_key()
    f = Fernet(key)
    # Encripta a string (convertida em bytes) e retorna como string legível
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """
    Transforma o hash criptografado de volta na string original.
    """
    if not encrypted_data:
        return ""
    try:
        key = get_or_create_key()
        f = Fernet(key)
        # Desencripta e converte de volta para string (utf-8)
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception:
        # Caso a chave seja inválida ou os dados estejam corrompidos
        return ""