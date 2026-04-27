import re
import fnmatch
from src.config import load_linter_rules


def _is_rule_applicable(rule, current_file, file_extension):
    """Verifica se a regra se aplica ao arquivo atual baseado na extensão e caminhos."""
    # Verifica extensão
    if file_extension not in rule.get('extensions', []):
        return False

    # Verifica require_paths (se existir, o arquivo TEM que dar match em algum)
    require_paths = rule.get('require_paths', [])
    if require_paths:
        match_required = any(re.search(p.replace('*', '.*'), current_file) for p in require_paths)
        if not match_required:
            return False

    # Verifica ignore_paths (se der match em algum, a regra não se aplica)
    ignore_paths = rule.get('ignore_paths', [])
    if ignore_paths:
        should_ignore = any(re.search(p.replace('*', '.*'), current_file) for p in ignore_paths)
        if should_ignore:
            return False

    return True

def _apply_rule(rule, code_line, line_number, current_file, alerts):
    """Aplica a regex da regra na linha de código e registra o alerta se necessário."""
    # Lógica de ignorar comentários no código
    if rule.get('ignore_comments', False):
        comment_patterns = [r'^//', r'^#', r'^/\*', r'^\*']
        if any(re.match(cp, code_line.strip()) for cp in comment_patterns):
            return

    # Validação da Regex da regra
    try:
        if re.search(rule['regex'], code_line):
            message = rule['message'].replace('{file_name}', current_file).replace('{line_number}', str(line_number))
            
            # Extrai a severidade (padrão é error)
            level = rule.get('level', 'error').lower()
            
            if level == 'warning':
                alerts["warnings"].append(message)
            else:
                alerts["errors"].append(message)
    except re.error as e:
        alerts["errors"].append(f"Regra '{rule.get('name')}' contém Regex inválida: {e}")

def parse_diff_and_lint(diff_text):
    """
    Analisa o git diff e aplica as regras definidas no .gitpr.linter.yml.
    Retorna um dicionário com duas listas: 'errors' (críticos) e 'warnings' (alertas).
    
    Args:
        diff_text (str): O texto do git diff a ser analisado.
        
    Returns:
        dict: Dicionário com as chaves 'errors' e 'warnings'.
    """
    rules = load_linter_rules()
    if not rules:
        return {"errors": [], "warnings": []}

    alerts = {
        "errors": [],
        "warnings": []
    }

    current_file = None
    file_extension = None
    line_number = 0

    lines = diff_text.split('\n')
    
    for line in lines:
        if line.startswith('+++ b/'):
            current_file = line[6:]
            file_extension = current_file.split('.')[-1] if '.' in current_file else ''
            line_number = 0 
            continue

        if line.startswith('@@'):
            match = re.search(r'\+(\d+)', line)
            if match:
                line_number = int(match.group(1)) - 1
            continue

        if line.startswith('+') and not line.startswith('+++'):
            line_number += 1
            code_line = line[1:].strip()

            if not current_file or not code_line:
                continue

            for rule in rules:
                if not _is_rule_applicable(rule, current_file, file_extension):
                    continue
                
                # Regra aplicável! Passa para a função de execução.
                _apply_rule(rule, code_line, line_number, current_file, alerts)

    return alerts