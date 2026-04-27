import os
from datetime import datetime
import click
import sys

# Importações dos nossos módulos internos atualizadas
from src.config import setup_environment, check_internet_connection
from src.updater import check_and_update, __version__
from src.core import (
    get_git_diff, 
    get_git_full_diff,
    get_current_branch, 
    generate_pr_content,
    get_skill_context,
    generate_skill_template,
    install_git_hooks
)
from src.linter_engine import parse_diff_and_lint


def print_banner():
    """Exibe a assinatura ASCII Art do projeto"""
    banner = """
 ,----.   ,--.  ,--.  ,------. ,------.  
'  .-./   `--',-'  '-.|  .--. '|  .--. ' 
|  | .---.,--.'-.  .-'|  '--' ||  '--'.' 
'  '--'  ||  |  |  |  |  | --' |  |\  \  
 `------' `--'  `--'  `--'     `--' '--' 
                                         
"""
    click.secho(banner, fg="cyan", bold=True)
    click.secho(f"  🚀 Automação Inteligente de PRs com IA (v{__version__})", fg="yellow", bold=True)
    click.secho("  Opções: -c,--commit | -r,--review | -f,--fullreview | -l,--linter | -s,--skill | -u,--update | -ih,--installhooks | -h ou --help\n", fg="white", dim=True)


# Configuração nativa do Click para aceitar -h além de --help
@click.command()
@click.help_option('-h', '--help', help='Mostra esta mensagem e sai.')
@click.option('-c', '--commit', is_flag=True, help="Gera apenas a mensagem de commit e exibe no console.")
@click.option('-r', '--review', is_flag=True, help="Faz um code review das alterações locais (git diff).")
@click.option('-f', '--fullreview', is_flag=True, help="Faz um code review de todas as alterações desde a branch principal (origin/main).")
@click.option('-l', '--linter', is_flag=True, help="Roda apenas o linter estático local (ideal para CI/CD).")
@click.option('-s', '--skill', is_flag=True, help="Gera o arquivo de template .gitpr.md na pasta atual.")
@click.option('-u', '--update', is_flag=True, help="Verifica e instala a versão mais recente do GitPR.")
@click.option('-ih', '--installhooks', is_flag=True, help="Instala automaticamente os Git Hooks de validação no projeto.")
@click.option('--hook', type=click.Path(), hidden=True, help="Caminho do arquivo de commit (uso interno dos hooks).")
@click.option('-q', '--quiet', is_flag=True, hidden=True, help="Oculta o banner e logs não essenciais (uso interno).")
def cli(commit, review, fullreview, linter, skill, update, installhooks, hook, quiet):
    """
    GitPR CLI - Automação de PRs e Code Review com IA.

    COMPORTAMENTO PADRÃO (Sem opções):
    Faz o fetch, compara com a branch principal remota e gera um arquivo Markdown (.md) com a descrição completa para o Pull Request.
    """
    # Silencia o banner se estiver no modo quiet ou via hook
    if not quiet and not hook:
        print_banner()



    # Limpeza do Hot-Swap (Deleta o .old se existir)
    if getattr(sys, 'frozen', False):
        old_exe = sys.executable + ".old"
        if os.path.exists(old_exe):
            try:
                os.remove(old_exe)
            except OSError:
                pass # Falha silenciosamente se o Windows ainda estiver segurando o arquivo

    if linter:
        diff_text = get_git_diff()
        
        if not diff_text or not diff_text.strip():
            if not quiet: click.secho("✅ Nada para validar (diff vazio).", fg="green")
            return

        linter_results = parse_diff_and_lint(diff_text)
        
        has_warnings = len(linter_results["warnings"]) > 0
        has_errors = len(linter_results["errors"]) > 0

        # Processamento de Warnings (Apenas Avisos)
        if has_warnings:
            # Os avisos DEVEM aparecer sempre, mesmo no modo quiet
            click.secho(f"\n⚠️ O Linter gerou {len(linter_results['warnings'])} aviso(s) de boas práticas:", fg="yellow", bold=True)
            for alert in linter_results["warnings"]:
                click.echo(f"  - {alert}")

        # Processamento de Erros (Críticos, Bloqueiam o Commit)
        if has_errors:
            # Os erros DEVEM aparecer sempre, mesmo no modo quiet
            click.secho(f"\n🚨 Falha na validação! Encontrados {len(linter_results['errors'])} erro(s) críticos:", fg="red", bold=True)
            for alert in linter_results["errors"]:
                click.echo(f"  - {alert}")
            # Trava o Git apenas se houver erros críticos
            sys.exit(1)
        
        # Sucesso silencioso (Nenhum erro crítico encontrado)
        if not quiet: 
            if has_warnings:
                click.secho("\n✅ Código aprovado com avisos. O commit prosseguirá.", fg="green")
            else:
                click.secho("\n✅ Código limpo! Nenhuma violação encontrada pelo Linter local.", fg="green", bold=True)
        return

    # Guardião de Conexão (Failing Fast)
    check_internet_connection()

    # Módulo de Atualização
    if update:    
        click.secho("🔍 Verificando atualizações no GitHub...", fg="cyan")
        check_and_update()
        return # Encerra após a verificação manual
    else:
        # Verificação automática em segundo plano a cada uso
        check_and_update()

    # Opção --skill: Gera o template e encerra
    if skill:
        generate_skill_template()
        return

 
    
    if installhooks:
        if install_git_hooks():
            click.secho("\n✅ Git Hooks instalados com sucesso!", fg="green", bold=True)
            click.echo("O Linter será agora executado automaticamente antes de cada commit.")
            
            click.echo("\n---")
            click.echo("📚 Guias de Utilização:")
            
            # Link da documentação geral de Hooks
            click.echo("• Como utilizar Git Hooks:")
            click.secho("  https://github.com/natanfiuza/gitpr/blob/main/docs/git-hooks-locais.md", fg="blue")
            
            # Novo link: Documentação de Regras Customizadas
            click.echo("• Como criar novas regras de Linter (.gitpr.linter.yml):")
            click.secho("  https://github.com/natanfiuza/gitpr/blob/main/docs/linter-regras-customizadas.md", fg="blue")
            click.echo("---\n")
        return
    
    
    # Garante que o ambiente e as chaves estão configurados
    setup_environment()

    # Determina o tipo de ação e qual diff capturar
    action_type = "pr"
    diff_text = ""
    
    if commit:
        action_type = "commit"
        diff_text = get_git_diff()
    elif review:
        action_type = "review"
        diff_text = get_git_diff()
    elif fullreview:
        action_type = "fullreview" 
        diff_text = get_git_full_diff()
    else:
        # Padrão: Descrição de PR usando o Full Diff contra a main remota
        action_type = "pr"
        diff_text = get_git_full_diff()
   
    # CRÍTICO: Avisa o usuário antes de sair se não houver alterações
    if not diff_text or not diff_text.strip():
        click.secho("\n⚠️ Nenhum código novo encontrado. Faça alguma alteração ou verifique sua branch antes de rodar o comando.\n", fg="yellow")
        return

    # Busca o contexto do arquivo correspondente à ação (PR ou Review)
    skill_context = get_skill_context(action_type)

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
        msg = data.get('commit_message', 'Atualização de código')

        if hook:
            # MODO HOOK: Injeta a mensagem direto no arquivo do Git
            try:
                with open(hook, "r", encoding="utf-8") as f:
                    original_content = f.read()
                
                # Coloca a sugestão no topo, mantendo os comentários originais do Git abaixo
                with open(hook, "w", encoding="utf-8") as f:
                    f.write(f"{msg}\n\n{original_content}")
                
                click.secho(f"✅ Mensagem injetada com sucesso no editor!", fg="green")
            except Exception as e:
                click.secho(f"❌ Erro ao injetar no hook: {e}", fg="red")
        else:
            # MODO CONSOLE: O comportamento original que já existia
            click.secho("\n💡 Dica: Use sem --commit para gerar o PR completo.\n", fg="yellow")
            click.secho("\n📝 Sugestão de Commit:\n", fg="green", bold=True)
            click.echo(msg)
            click.echo("\n")
        return

    # Code Review (Arquivo)  
    if action_type in ["review", "fullreview"]:
        
        if fullreview:
            pattern = os.getenv("OUTPUT_FILE_NAME_FULLREVIEW", "{branch}_{datetime}_PR_FULLREVIEW.txt")
        else:
            pattern = os.getenv("OUTPUT_FILE_NAME_REVIEW", "{branch}_{datetime}_PR_REVIEW.txt")
            
        output_filename = pattern.format(
            branch=safe_branch_name,
            datetime=current_time
        )
        content = data.get('review', 'Nenhuma análise gerada.')
        
        linter_alerts = parse_diff_and_lint(diff_text)
        
        if linter_alerts:
            
            click.secho(f"⚠️ Atenção! Encontrados {len(linter_alerts)} alertas nas regras do Linter.", fg="yellow")
            
            # Monta o cabeçalho com os erros do linter
            linter_header = "## 🚨 Alertas de Análise Estática Local (Regras YAML)\n\n"
            for alert in linter_alerts:
                linter_header += f"- {alert}\n"
            linter_header += "\n---\n\n## 🤖 Code Review da IA\n\n"
            
            # Injeta o cabeçalho no topo do conteúdo gerado pela IA
            content = linter_header + content
        else:
            click.secho("✅ Linter Local passou sem violações de regras!", fg="green")

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