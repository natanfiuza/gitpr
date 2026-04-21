# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
feat: implementa armazenamento seguro para a GEMINI_API_KEY e remove arquivo de licença obsoleto
```

---

### Resumo
Este PR introduz uma camada de segurança vital ao armazenar a `GEMINI_API_KEY` de forma encriptada localmente utilizando a biblioteca `cryptography`. Esta mudança protege as credenciais do utilizador contra acessos indevidos. Adicionalmente, foi realizada uma limpeza no repositório removendo o arquivo de licença `LGPL-2.1` não utilizado e melhorando a formatação do `README.md`.

### Mudanças Técnicas
* Adicionada a dependência `cryptography` no arquivo `Pipfile`.
* Atualizado o `src/config.py` para encriptar a chave (`encrypt_data`) antes de gravá-la no arquivo `.env`.
* Atualizado o `src/core.py` para desencriptar a chave (`decrypt_data`) em tempo de execução ao fazer chamadas para a API.
* Remoção completa do arquivo `LGPL-2.1`.
* Limpeza de caracteres de escape incorretos no `README.md` e adição de nota técnica alertando sobre o novo modelo de segurança simétrica (Fernet) adotado.

### Impacto
O projeto agora é mais robusto em termos de segurança. Desenvolvedores e utilizadores existentes precisarão atualizar suas dependências rodando o comando de instalação atualizado. Como as chaves antigas estarão em texto puro, será necessário acionar a reconfiguração na inicialização do CLI para gerar o novo arquivo de cofre local (`secret.key`) e sobrescrever o `.env` encriptado.
