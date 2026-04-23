import re
import fnmatch
import yaml
import os
import click

def parse_diff_and_lint(diff_text, linter_file_path=".gitpr.linter.yml"):
    """Varre o git diff apenas nas linhas adicionadas e aplica as regras do Linter."""
    if not os.path.exists(linter_file_path):
        return [] # Se não houver arquivo de linter, segue o jogo silenciosamente
    click.secho("🔍 Rodando Linter Local de Análise Estática...", fg="cyan")
    with open(linter_file_path, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError:
            return ["🚨 Erro crítico: O arquivo .gitpr.linter.yml possui erros de formatação YAML."]

    rules = config.get('rules', [])
    if not rules:
        return []

    alerts = []
    current_file = ""
    current_line_num = 0

    # Iteramos o texto do Git Diff
    for line in diff_text.split('\n'):
        # Detecta qual arquivo estamos analisando no diff
        if line.startswith('+++ b/'):
            current_file = line[6:]
            continue
        
        # Detecta o número da linha atual no novo arquivo (@@ -start,count +start,count @@)
        elif line.startswith('@@ '):
            match = re.search(r'\+([0-9]+)(,[0-9]+)? @@', line)
            if match:
                current_line_num = int(match.group(1))
            continue

        # Processa APENAS as linhas adicionadas (+)
        if line.startswith('+') and not line.startswith('+++'):
            actual_code = line[1:] # Remove o '+' do diff
            stripped_code = actual_code.strip()
            
            for rule in rules:

                # Filtro de Extensão
                exts = rule.get('extensions', [])
                file_ext = current_file.split('.')[-1] if '.' in current_file else ''
                if exts and file_ext not in exts:
                    continue
                # Filtro de Caminhos Obrigatórios (Novo)
                require_paths = rule.get('require_paths', [])
                if require_paths:
                    is_in_required_path = False
                    for path_pattern in require_paths:
                        if fnmatch.fnmatch(current_file, path_pattern) or fnmatch.fnmatch(current_file, f"*/{path_pattern}"):
                            is_in_required_path = True
                            break
                    if not is_in_required_path:
                        continue

                # Filtro de Arquivos/Paths Ignorados (Substitui o -not -path do Linux)
                ignore_paths = rule.get('ignore_paths', [])
                ignored = False
                for path_pattern in ignore_paths:
                    # fnmatch permite usar curingas (*). Ex: */js/axios/*
                    if fnmatch.fnmatch(current_file, path_pattern) or fnmatch.fnmatch(current_file, f"*/{path_pattern}"):
                        ignored = True
                        break
                if ignored:
                    continue
                    
                # Filtro de Comentários
                if rule.get('ignore_comments', False):
                    # Ignora se começar com barras duplas, asterisco, /* ou #
                    if stripped_code.startswith('//') or stripped_code.startswith('/*') or stripped_code.startswith('*') or stripped_code.startswith('#'):
                        continue
                        
                # Avaliação da Expressão Regular
                pattern = rule.get('regex', '')
                if pattern and re.search(pattern, actual_code):
                    msg_template = rule.get('message', "🚨 Violação de regra na linha {line_number} do arquivo {file_name}")
                    msg = msg_template.format(
                        line_number=current_line_num,
                        file_name=current_file,
                        line_text=stripped_code
                    )
                    alerts.append(msg)
            
            current_line_num += 1
            
        # Linhas de contexto (espaço em branco no início) apenas incrementam o contador
        elif not line.startswith('-') and not line.startswith('\\'):
            current_line_num += 1

    return alerts