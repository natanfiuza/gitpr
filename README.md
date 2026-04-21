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

----

## 📦 Como Compilar o Executável Localmente

Se você deseja gerar o seu próprio binário a partir do código-fonte, utilizamos o **PyInstaller**. Certifique-se de estar no diretório raiz do projeto e com o ambiente virtual configurado.

1. Instale as dependências de desenvolvimento (caso ainda não tenha feito):
   ```bash
   pipenv install --dev
   ```

2. Execute o comando de build apontando para o nosso ponto de entrada (`run.py`):
   ```bash
   pipenv run pyinstaller --noconfirm --onefile --name gitpr run.py
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

Após realizar as suas alterações num repositório Git e ANTES de fazer o commit, basta executar:

gitpr

A ferramenta irá capturar o seu git diff HEAD, processar através da IA e gerar um arquivo Markdown (ex: feature-login_20260421110134_PR_DESC.md) na raiz do seu projeto com a sugestão completa.

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