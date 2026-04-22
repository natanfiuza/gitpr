import os
from datetime import datetime
import click

# Importações dos nossos módulos internos
from src.config import setup_environment
from src.core import get_git_diff, get_current_branch, generate_pr_content

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
    click.secho("  🚀 Automação Inteligente de PRs com IA\n", fg="yellow", bold=True)

@click.command()
def cli():
    """GitPR CLI - Gera mensagens de commit e PRs automaticamente a partir do git diff."""
    # 0. Exibe o banner em toda execução
    print_banner()

    # 1. Garante que o ambiente e as chaves estão configurados
    setup_environment()

    # 2. Captura as alterações do repositório atual
    diff_text = get_git_diff()
    if not diff_text or not diff_text.strip():
        # A mensagem de aviso já é gerida dentro do get_git_diff / core
        click.secho(f"\n⚠️ Nenhuma alteração de código encontrada para geração de PR.\n", fg="yellow")
        return

    # 3. Chama a IA do Gemini para gerar o conteúdo
    pr_data = generate_pr_content(diff_text)
    if not pr_data:
        return

    # 4. Formata o nome dinâmico do arquivo de saída
    branch_name = get_current_branch()
    # Substitui barras por hífen para evitar a criação acidental de pastas (ex: feature/login -> feature-login)
    safe_branch_name = branch_name.replace("/", "-").replace("\\", "-")
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename_pattern = os.getenv("OUTPUT_FILE_NAME", "{branch}_{datetime}_PR_DESC.md")
    output_filename = filename_pattern.format(
        branch=safe_branch_name,
        datetime=current_time
    )

    # 5. Monta o conteúdo final em Markdown
    markdown_content = f"""# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
{pr_data.get('commit_message', 'Atualização de código')}
```

---

{pr_data.get('pr_description', 'Sem descrição detalhada.')}
"""

    # 6. Guarda o arquivo no diretório de trabalho atual
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        click.secho(f"\n✅ Sucesso! O arquivo '{output_filename}' foi gerado na pasta atual.", fg="green", bold=True)
    except Exception as e:
        click.secho(f"\n❌ Erro ao guardar o arquivo: {e}", fg="red")

if __name__ == "__main__":
    cli()