# **🚀 GitPR - Automação Inteligente de Code Review e Pull Requests**

O **GitPR** é uma ferramenta de Interface de Linha de Comando (CLI) desenvolvida em Python que atua como um assistente de engenharia de software diretamente no terminal. Ele combina a velocidade de validações estáticas locais com o poder analítico de Inteligências Artificiais (Gemini e DeepSeek) para automatizar e elevar a qualidade de Commits, Code Reviews e Pull Requests.

## **🎯 Para que serve?**

O objetivo principal do GitPR é eliminar o trabalho repetitivo e garantir um alto padrão de qualidade (*Quality Gate*) no ciclo de vida do desenvolvimento de software. Ele resolve três problemas principais:

1. **Histórico de Git Poluído:** Força o uso de *Conventional Commits* e gera mensagens semânticas automaticamente.  
2. **Pull Requests Vazios ou Pobres:** Escreve descrições detalhadas baseadas no diff, separando mudanças técnicas de impacto no negócio.  
3. **Dívida Técnica e Bugs:** Realiza Code Reviews semânticos e validações de regras (Regex) antes mesmo de o código sair da máquina do desenvolvedor (abordagem *Shift-Left*).

---

## **✨ Funcionalidades Principais**

* **📝 Auto-Commit (-c ou --commit):** Lê as alterações em *staged* (git diff) e gera uma mensagem de commit concisa no formato imperativo.  
* **📖 Geração de Pull Request (Padrão):** Analisa o diff entre a branch atual e a principal, gerando um arquivo .md pronto para ser colado no GitHub/GitLab, contendo resumo, impacto e detalhes técnicos.  
* **🕵️ Code Review Inteligente (-r ou --review):** Inspeciona o código alterado em busca de más práticas de arquitetura, violações de SOLID e vulnerabilidades de segurança.  
* **🔬 Auditoria de Ficheiro Completo (-i / --input):** Permite apontar o GitPR para um ficheiro específico (ex: um código legado) para que a IA faça uma análise arquitetural de cima a baixo, sugerindo refatorações para o ficheiro inteiro.  
* **⚡ Linter Estático Local (-l ou --linter):** Um motor de Expressões Regulares (Regex) ultrarrápido que roda localmente para detetar erros óbvios (ex: console.log, chaves hardcoded) sem gastar tokens de IA.  
* **🪝 Integração com Git Hooks (-ih ou --installhooks):** Injeta o GitPR no ciclo natural do Git, rodando o Linter automaticamente num pre-commit ou sugerindo mensagens num prepare-commit-msg.  
* **🔄 Multi-Model (Agnóstico de IA):** Permite ao desenvolvedor escolher entre o **Google Gemini** ou o **DeepSeek** como motor de raciocínio, podendo alternar dinamicamente via .env ou pela flag --provider.

---

## **🛠️ Detalhes do Desenvolvimento e Arquitetura**

O GitPR foi arquitetado focando em **Performance**, **Segurança** e **Extensibilidade**.

### **1. Sistema de "Skills" (Prompt Engineering Desacoplado)**

Em vez de ter os *prompts* da IA fixos no código Python, o GitPR utiliza um sistema de arquivos .md locais (Skills) que atuam como *System Instructions*.

* .gitpr.commit.md  
* .gitpr.pr.md  
* .gitpr.review.md  
* .gitpr.filereview.md

Isso permite que cada equipa adapte a "personalidade" e as regras de negócio da IA sem precisar alterar uma única linha de código fonte da ferramenta.

### **2. Strategy Pattern para Provedores de IA**

O módulo ai_providers.py isola a comunicação com as APIs externas. O motor (Core) apenas pede um JSON, e este módulo decide como formatar a requisição usando o SDK da Google (google-genai) ou o SDK da OpenAI (configurado para a base URL do DeepSeek). Conta também com um sistema resiliente de **Retry Automático** para lidar com instabilidades de rede.

### **3. Segurança de Chaves (Cryptography)**

As chaves de API (API_KEYS) nunca são salvas em texto limpo. O módulo security.py utiliza a biblioteca cryptography (Fernet) para gerar uma chave mestra local e guardar as credenciais de forma cifrada no arquivo \~/.gitpr/.env.

### **4. Sistema de Cache MD5**

Para economizar consumo de Tokens de IA (dinheiro) e tempo (latência), o GitPR cria um hash MD5 do *prompt* gerado a partir do *diff*. Se o desenvolvedor pedir um Code Review do mesmo código duas vezes, o sistema recupera a resposta do diretório .gitpr/cache/ instantaneamente.

### **5. Duplo "Quality Gate" (Performance)**

A ferramenta foi desenhada para equilibrar o consumo de recursos:

* **Camada 1 (Linter Local):** Rápida (<100ms), offline, focada em sintaxe (via linter_engine.py e .gitpr.linter.yml).  
* **Camada 2 (IA Cloud):** Profunda (2s-8s), online, focada em semântica e intenção.

### **6. Sistema de Auto-Update**

Construído com empacotamento PyInstaller, o módulo updater.py consulta os *Releases* do repositório no GitHub. Se houver uma nova versão, o executável faz o download do novo binário, substitui-se a si mesmo (*hot-swap*) e relança o comando perfeitamente.

---

## **💻 Stack Tecnológica**

* **Linguagem:** Python 3.10+  
* **CLI Framework:** click (Para construção robusta de comandos e menus).  
* **Integrações de IA:** google-genai (Gemini), openai (DeepSeek).  
* **Segurança:** cryptography, python-dotenv.  
* **Análise Estrutural:** PyYAML (Leitura das regras do Linter), re (Expressões Regulares nativas).  
* **Build:** PyInstaller (Geração de executável *standalone*).

---

