import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

def get_cache_base_dir():
    """Retorna o caminho ~/.gitpr/cache/prompts/"""
    path = Path.home() / ".gitpr" / "cache" / "prompts"
    return path

def generate_md5(text):
    """Gera o hash MD5 de uma string."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_cached_response(action_folder, prompt_text):
    """Verifica se existe um cache válido para o prompt e retorna o conteúdo."""
    md5_hash = generate_md5(prompt_text)
    cache_file = get_cache_base_dir() / action_folder / f"{md5_hash}.json"

    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("response")
        except (json.JSONDecodeError, IOError):
            return None
    return None

def save_cached_response(action_folder, action_type, prompt_text, response_dict):
    """Salva a resposta da IA no cache local."""
    md5_hash = generate_md5(prompt_text)
    folder_path = get_cache_base_dir() / action_folder
    folder_path.mkdir(parents=True, exist_ok=True)
    
    cache_file = folder_path / f"{md5_hash}.json"
    
    cache_data = {
        "md5": md5_hash,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_type": action_type,
        "prompt": prompt_text,
        "response": response_dict
    }

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except IOError:
        pass # Falha silenciosa no cache para não travar a ferramenta