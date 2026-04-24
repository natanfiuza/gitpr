# **GitPR CLI 🚀**

GitPR CLI é uma ferramenta de automação de linha de comando que utiliza a inteligência artificial do Google Gemini para analisar as suas alterações de código (git diff) e gerar automaticamente mensagens de commit no padrão *Conventional Commits*, além de uma descrição detalhada para o seu Pull Request.

## **🛠️ Tecnologias e Bibliotecas Utilizadas**

Este projeto foi desenvolvido em Python e utiliza as seguintes bibliotecas principais:

* [**Click**](https://click.palletsprojects.com/): Para criar uma interface de linha de comando (CLI) robusta e amigável.  
* [**Google GenAI**](https://pypi.org/project/google-genai/): Novo SDK oficial para integração direta com a API do Gemini (modelo gemini-2.5-flash).  
* [**Python-dotenv**](https://pypi.org/project/python-dotenv/): Para a gestão segura de variáveis de ambiente.  
* [**PyInstaller**](https://pyinstaller.org/): Para empacotar o projeto num único arquivo executável, facilitando a distribuição.
* [**Pytest**](https://docs.pytest.org/): Para execução de testes unitários de forma simples, colorida e legível no console.
* [**Cryptography**](https://cryptography.io/): Para garantir que sua `GEMINI_API_KEY` seja armazenada de forma encriptada e segura no disco.
* [**PyYAML**](https://pyyaml.org/): Utilizado para ler e processar as regras customizadas de análise estática do arquivo `.gitpr.linter.yml`.

----

## 📦 Como Compilar o Executável Localmente

Se você deseja gerar o seu próprio binário a partir do código-fonte, utilizamos o **PyInstaller**. Certifique-se de estar no diretório raiz do projeto e com o ambiente virtual configurado.

1. Instale as dependências de desenvolvimento (caso ainda não tenha feito):
   ```bash
   pipenv install --dev
   ```

2. Execute o comando de build apontando para o nosso ponto de entrada (`run.py`):
   ```bash
   pipenv run pyinstaller --noconfirm --onefile --icon=icon.ico --name gitpr run.py
   ```
> **Nota técnica:** A flag `--onefile` garante que todo o Python, bibliotecas e dependências ficam comprimidos num único binário, enquanto `--paths src` ajuda o compilador a encontrar os nossos arquivos `core.py` e `config.py`. 🛠️

Após a execução deste comando, o PyInstaller vai criar algumas pastas (`build` e `dist`). 
O seu arquivo final e pronto a usar estará dentro da pasta **`dist/`** com o nome `gitpr` (ou `gitpr.exe` no Windows). 


----

## 🧪 Executando Testes

Para garantir que a lógica de captura do Git e a integração com a IA estejam funcionando corretamente, utilizamos testes unitários.

1. Instale as dependências de teste (caso ainda não tenha feito):
   ```bash
   pipenv install --dev pytest
   ```

2. Execute os testes com o comando:
   ```bash
   pipenv run pytest -v
   ```
O Pytest irá detectar automaticamente os arquivos dentro da pasta `tests/` e apresentará um relatório detalhado da execução.

----
## **⚙️ Instalação e Configuração**

### **Usando o Executável (Recomendado)**

1. Faça o download do arquivo executável gitpr na aba "Releases" do GitHub.  
2. Mova o executável para uma pasta que esteja no seu PATH (ex: /usr/local/bin no Linux/Mac ou na pasta do seu utilizador no Windows).  
3. Na primeira execução, o assistente irá guiá-lo:  
   $ gitpr
```bash
🚀 Automação Inteligente de PRs com IA

🔧 Primeira execução detetada! Vamos configurar o GitPR CLI.

🔑 Insira sua GEMINI_API_KEY:

📄 Padrão do nome do arquivo de saída [{branch}_{datetime}_PR_DESC.md]:
```` 
*Nota: A sua configuração será guardada em segurança no arquivo `~/.gitpr/.env`.*

> **🔒 Nota sobre Segurança:** O GitPR CLI utiliza criptografia simétrica (Fernet). Sua chave de API é armazenada como um hash no arquivo `.env`, e a chave mestra para desencriptação é gerada automaticamente em `~/.gitpr/secret.key`. **Nunca compartilhe seu arquivo secret.key.**


### A partir do Código-Fonte

1. Clone o repositório: `git clone https://github.com/natanfiuza/gitpr.git`

2. Entre na pasta: `cd gitpr`

3. Atualize o ambiente:  
```bash  
pipenv install google-genai python-dotenv click cryptography
``` 
4. Execute: pipenv run python src/main.py

## **💻 Como Usar**

O GitPR possui um comportamento padrão poderoso e diversas opções avançadas para auxiliar no seu dia a dia como desenvolvedor.

### **Comportamento Padrão (Pull Request)**
Basta executar o comando puro no seu terminal:
```bash
gitpr
```
A ferramenta irá sincronizar com o remoto (`git fetch`), comparar as suas alterações com a branch principal remota (ex: `origin/main`), e gerar um arquivo Markdown (ex: `feature-login_20260421110134_PR_DESC.md`) na raiz do seu projeto com a sugestão completa para o seu Pull Request.

### **Opções e Comandos Avançados**
Você pode passar as seguintes *flags* para ações específicas:

* `-c` ou `--commit`: Executa um `git diff` local e exibe **apenas a mensagem de commit** sugerida diretamente no console, sem gerar arquivos. Ótimo para commits rápidos!
* `-r` ou `--review`: Realiza um **Code Review** detalhado das suas alterações locais que ainda não foram commitadas, gerando um arquivo `.txt` com análises de melhoria.
* `-f` ou `--fullreview`: Realiza um **Code Review completo**, analisando todas as alterações desde o ancestral comum com a branch remota, gerando também um arquivo `.txt`.
* `-s` ou `--skill`: Cria os arquivos de template **`.gitpr.md`** (contexto para IA) e **`.gitpr.linter.yml`** (regras de linter estático) na raiz do projeto. **Dica de Ouro:** Sempre que o GitPR for executado, ele lerá estes arquivos e moldará o Code Review e o Pull Request especificamente para o contexto da sua equipe! 🧠
* `-u` ou `--update`: Verifica no GitHub se existe uma nova versão do executável e realiza a atualização automaticamente (Hot-Swap).
* `-h` ou `--help`: Exibe o menu de ajuda com a lista rápida de todos os comandos diretamente no terminal.


## 🛡️ Linter Local (Análise Estática)

O GitPR CLI permite que você defina regras rígidas que serão validadas instantaneamente durante o `--review` ou `--fullreview`, sem depender da IA. Isso é ideal para evitar que erros comuns (como `console.log` ou IPs de teste) cheguem ao repositório.

### Como configurar o `.gitpr.linter.yml`:
Ao rodar `gitpr --skill`, um modelo será gerado. Você pode configurar regras usando Expressões Regulares (Regex):

```yaml
rules:
  - name: "check-localhost"
    extensions: ["js", "php"] # Extensões que serão validadas
    regex: 'http(s)?://(localhost|127\.0\.0\.1)' # O que procurar
    message: "🚨 Uso de localhost detectado no arquivo {file_name}"
    ignore_comments: true # Ignora se a linha estiver comentada
    ignore_paths: # Pastas ou arquivos ignorados (aceita *)
      - "vendor/*"
      - "node_modules/*"
```

O Linter analisa apenas as **linhas adicionadas** no seu `git diff`, garantindo uma execução focada e extremamente rápida. Se houver violações, elas aparecerão com destaque no topo do seu arquivo de revisão.

## ⚡ Sistema de Cache Local (Economia de Quota)

O GitPR possui um motor inteligente de cache baseado em **MD5**. Sempre que você rodar um comando (`--review`, `--commit`, etc.), a ferramenta gera um hash exato do seu código atual (diff) e das instruções. 
Se você rodar o mesmo comando novamente sem ter alterado o código, o GitPR intercepta a requisição e devolve o resultado instantaneamente (em milissegundos) a partir da pasta `~/.gitpr/cache/prompts/`, poupando seu tempo e suas cotas da API do Gemini!

## 🔄 Auto-Updater (Atualização Over-The-Air)

Nunca mais se preocupe em baixar novas versões manualmente. O GitPR possui um Guardião de Conexão e um atualizador embutido:
* Ele verifica a disponibilidade de rede antes de iniciar para não travar seu fluxo offline.
* Em cada execução, ele verifica silenciosamente se há um novo release oficial na API do GitHub.
* Você pode forçar a busca e instalação rodando `gitpr --update` ou `gitpr -u`.
* A ferramenta utiliza a técnica de *Hot-Swap*, baixando o novo `.exe` e substituindo a versão antiga de forma transparente.

## **🤝 Como Contribuir**

Contribuições são muito bem-vindas! Para contribuir:

1. Faça um Fork do projeto.  
2. Crie uma branch para a sua *feature* (git checkout \-b feature/NovaFuncionalidade).  
3. Faça o commit das suas alterações (git commit \-m 'feat: adiciona nova funcionalidade'). Sugestão: Use o próprio GitPR para gerar esta mensagem! 😄  
4. Faça o Push para a branch (git push origin feature/NovaFuncionalidade).  
5. Abra um Pull Request.

## **✨ Agradecimentos e Autoria**

Projeto idealizado e desenvolvido por:

**Natan Fiuza** \- [contato@natanfiuza.dev.br](mailto:contato@natanfiuza.dev.br)

## **📄 Licença**

Este projeto está licenciado sob a **GNU Lesser General Public License v2.1 (LGPL-2.1)**. Consulte o arquivo LICENSE para mais detalhes.