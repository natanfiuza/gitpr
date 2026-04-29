# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
feat: adiciona suporte a múltiplos provedores de IA (Gemini e DeepSeek)
```

---

## 🎯 Resumo
Esta alteração introduz suporte a múltiplos provedores de IA (Gemini e DeepSeek), permitindo que o utilizador escolha o motor de IA preferido. A configuração passa a ser dinâmica e encriptada por provedor, eliminando a dependência exclusiva do Gemini. Inclui também um novo ficheiro de habilidade para geração de commits e ajustes na ligação do linter.

## 🛠️ Mudanças Técnicas
- Adiciona dependência `openai` para uso futuro
- Refatora `src/config.py` para gerir múltiplos provedores (get_ai_provider, get_api_key, get_api_model)
- Atualiza `src/core.py` para delegar chamadas de IA a `call_ai_model` (abstração de provedor)
- Adiciona ficheiro de skill `.gitpr.commit.md` com regras de commit
- Adiciona opção `--provider` na CLI para forçar um provedor
- Corrige iteração dos alertas do linter em `src/main.py`
- Incrementa versão para 0.0.8

## ⚠️ Impacto/Avisos
- **Quebra de compatibilidade no `.env`**: agora utiliza variáveis como `GEMINI_API_KEY_ENCRYPTED` e `DEEPSEEK_API_KEY_ENCRYPTED`, exigindo reconfiguração
- A dependência `openai` foi adicionada mas não está funcional; não afeta o fluxo atual
- A função `generate_pr_content` teve a assinatura alterada, podendo impactar integrações internas
