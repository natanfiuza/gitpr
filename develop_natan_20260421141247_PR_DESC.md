# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
feat: implementa CLI do GitPR com integração ao Google Gemini
```

---

### Resumo
Esta PR introduz a estrutura base do GitPR CLI, uma ferramenta que utiliza inteligência artificial para automatizar a geração de mensagens de commit e descrições de Pull Requests com base no `git diff`.

### Mudanças Técnicas
* **Dependências:** Atualização no `Pipfile` migrando a dependência de `google-generativeai` para o novo SDK `google-genai`.
* **Configuração (`src/config.py`):** Implementação do setup inicial do usuário, criando o diretório e arquivo `~/.gitpr/.env` e solicitando interativamente configurações como API Key, modelo do Gemini e formato do nome do arquivo.
* **Core (`src/core.py`):** Criação das funções de interação com o sistema Git (`get_git_diff`, `get_current_branch`) e a integração principal com a API do Gemini configurada para responder estruturadamente em JSON.
* **CLI (`src/main.py`):** Desenvolvimento do ponto de entrada principal utilizando `click`, responsável por exibir o banner visual, orquestrar as etapas de leitura do código, chamada à IA e salvar o resultado dinamicamente em um arquivo Markdown.

### Impacto
Fornece uma base funcional da ferramenta de linha de comando para desenvolvedores, reduzindo o tempo necessário para redigir documentações de pull requests de forma padronizada e otimizada por IA.
