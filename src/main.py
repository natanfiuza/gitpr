import os
from datetime import datetime
import click

# Importações dos nossos módulos internos atualizadas
from src.config import setup_environment
from src.core import (
    get_git_diff, 
    get_git_full_diff,
    get_current_branch, 
    generate_pr_content,
    get_skill_context,
    generate_skill_template
)
def print_banner():
    """Exibe a assinatura ASCII Art do projeto"""
    banner = """
   ▄██████▄   ▄█      ███        ▄███████▄    ▄████████ 
  ███    ███ ███  ▀█████████▄   ███    ███   ███    ███ 
  ███    █▀  ███▌    ▀███▀▀██   ███    ███   ███    ███ 
 ▄███        ███▌     ███   ▀   ███    ███  ▄███▄▄▄▄██▀ 
▀▀███ ████▄  ███▌     ███     ▀█████████▀  ▀▀███▀▀▀▀▀   
  ███    ███ ███      ███       ███        ▀███████████ 
  ███    ███ ███      ███       ███          ███    ███ 
  ████████▀  █▀      ▄████▀    ▄████▀        ███    ███ 
                                             ███    ███ 
    """
    click.secho(banner, fg="cyan", bold=True)
    click.secho("  🚀 Automação Inteligente de PRs com IA", fg="yellow", bold=True)
    click.secho("  Opções: --commit | --review | --fullreview | --skill | -h ou --help\n", fg="white", dim=True)

# Configuração nativa do Click para aceitar -h além de --help
@click.command()
@click.help_option('-h', '--help', help='Mostra esta mensagem e sai.')
@click.option('--commit', is_flag=True, help="Gera apenas a mensagem de commit e exibe no console.")
@click.option('--review', is_flag=True, help="Faz um code review das alterações locais (git diff).")
@click.option('--fullreview', is_flag=True, help="Faz um code review de todas as alterações desde a branch principal (origin/main).")
@click.option('--skill', is_flag=True, help="Gera o arquivo de template .gitpr.md na pasta atual.")
def cli(commit, review, fullreview, skill):
    """
    GitPR CLI - Automação de PRs e Code Review com IA.

    COMPORTAMENTO PADRÃO (Sem opções):
    Faz o fetch, compara com a branch principal remota e gera um arquivo Markdown (.md) com a descrição completa para o Pull Request.
    """
    # 0. Exibe o banner
    print_banner()

    # Opção --skill: Gera o template e encerra
    if skill:
        generate_skill_template()
        return

    # 1. Garante que o ambiente e as chaves estão configurados
    setup_environment()

    # 2. Determina o tipo de ação e qual diff capturar
    action_type = "pr"
    diff_text = ""
    
    if commit:
        action_type = "commit"
        diff_text = get_git_diff()
    elif review:
        action_type = "review"
        diff_text = get_git_diff()
    elif fullreview:
        action_type = "review" # Usamos o prompt de review
        diff_text = get_git_full_diff()
    else:
        # Padrão: Descrição de PR usando o Full Diff contra a main remota
        action_type = "pr"
        diff_text = get_git_full_diff()

    if not diff_text or not diff_text.strip():
        return

    # Busca o contexto do arquivo .gitpr.md (se existir)
    skill_context = get_skill_context()

    # Chama a IA do Gemini para gerar o conteúdo
    data = generate_pr_content(diff_text, action_type, skill_context)
    if not data:
        return

    # Processamento da Saída
    branch_name = get_current_branch()
    safe_branch_name = branch_name.replace("/", "-").replace("\\", "-")
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    # Apenas Commit no console
    if action_type == "commit":
        click.secho("\n💡 Dica: Use o comando sem --commit para gerar um arquivo de descrição de PR completo.\n", fg="yellow")
        click.secho("\n📝 Sugestão de Commit:\n", fg="green", bold=True)
        click.echo(data.get('commit_message', 'Sem sugestão disponível.'))
        click.echo("\n")
        return

    # Code Review (Arquivo .txt)
    if action_type == "review":
        
        if fullreview:
            pattern = os.getenv("OUTPUT_FILE_NAME_FULLREVIEW", "{branch}_{datetime}_PR_FULLREVIEW.txt")
        else:
            pattern = os.getenv("OUTPUT_FILE_NAME_REVIEW", "{branch}_{datetime}_PR_REVIEW.txt")
            
        output_filename = pattern.format(
            branch=safe_branch_name,
            datetime=current_time
        )
        content = data.get('review', 'Nenhuma análise gerada.')
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(content)
            click.secho(f"\n✅ Code Review gerado com sucesso: '{output_filename}'", fg="green", bold=True)
        except Exception as e:
            click.secho(f"\n❌ Erro ao salvar o review: {e}", fg="red")
        return

    # Pull Request Padrão (Arquivo .md)
    filename_pattern = os.getenv("OUTPUT_FILE_NAME", "{branch}_{datetime}_PR_DESC.md")
    output_filename = filename_pattern.format(branch=safe_branch_name, datetime=current_time)

    markdown_content = f"""# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
{data.get('commit_message', 'Atualização de código')}
```

---

{data.get('pr_description', 'Sem descrição detalhada.')}
"""

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        click.secho(f"\n✅ Sucesso! O ficheiro '{output_filename}' foi gerado na pasta atual.", fg="green", bold=True)
    except Exception as e:
        click.secho(f"\n❌ Erro ao guardar o ficheiro: {e}", fg="red")

if __name__ == "__main__":
    cli()