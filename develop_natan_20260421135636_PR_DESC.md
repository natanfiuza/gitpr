# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
feat: Implementa a funcionalidade principal do GitPR CLI
```

---

### Resumo

Esta PR introduz a primeira versão da ferramenta GitPR CLI, desenvolvida para automatizar a geração de mensagens de commit e descrições de Pull Requests a partir do `git diff`. A ferramenta interage com a API do Gemini para analisar as alterações de código e produzir conteúdo formatado em Markdown, facilitando o processo de documentação e revisão de código.

### Mudanças Técnicas

- Adicionada a dependência `google-genai` para interação com a API do Gemini, substituindo `google-generativeai` no `Pipfile`.
- Criado o módulo `src/config.py` responsável pela configuração inicial do ambiente, incluindo a solicitação e armazenamento da `GEMINI_API_KEY` e do padrão de nome de ficheiro de saída num ficheiro `.env` localizado em `~/.gitpr/`.
- Desenvolvido o módulo `src/core.py` que contém a lógica para:
    - Obter o `git diff HEAD` do repositório atual.
    - Recuperar o nome da branch atual.
    - Enviar o `diff` para a API do Gemini e processar a resposta JSON.
- Implementado o módulo `src/main.py` como o ponto de entrada principal do CLI (`@click.command`), orchestrando o fluxo:
    - Exibição de um banner de boas-vindas.
    - Execução do setup do ambiente.
    - Obtenção e processamento do `git diff`.
    - Geração do conteúdo da PR pela IA.
    - Formatação dinâmica do nome do ficheiro de saída (com base na branch e data/hora).
    - Gravação do conteúdo final num ficheiro Markdown no diretório atual.

### Impacto

- **Para o utilizador:** Simplifica drasticamente o processo de criação de mensagens de commit e descrições de PRs, poupando tempo e garantindo uma documentação mais consistente e detalhada das alterações. A configuração inicial guiada torna a ferramenta fácil de começar a usar.
- **Para o projeto:** Estabelece a fundação de um CLI útil para desenvolvedores, com uma arquitetura modular que facilita futuras extensões e melhorias nas funcionalidades de automação.
