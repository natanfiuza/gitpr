# 🚀 Sugestão de Pull Request

**Commit Message Recomendada:**
```text
test: adiciona suite de testes unitários com pytest e atualiza documentação
```

---

### Resumo

Esta PR introduz a infraestrutura inicial de testes unitários para o projeto utilizando o Pytest, cria os primeiros testes focados no módulo `core` e aprimora a documentação. Além disso, remove um arquivo temporário de descrição de PR que havia ficado residualmente na branch de desenvolvimento.

### Mudanças Técnicas

* Adicionada a dependência `pytest` no `Pipfile` sob o grupo `[dev-packages]`.
* Criado o arquivo `tests/test_core.py` contendo testes unitários que utilizam `unittest.mock` para cobrir as funções `get_current_branch` e `get_git_diff` sem a necessidade de comandos reais no shell.
* Atualizado o `README.md` para incluir:
  * A menção ao `Pytest` como uma biblioteca chave.
  * Notas técnicas aprofundadas sobre a compilação via Pyinstaller (uso das flags `--onefile` e `--paths` e as saídas nas pastas `build` e `dist`).
  * Uma nova subseção ensinando como instalar as ferramentas de desenvolvimento e executar os testes (`pipenv run pytest -v`).
* Deletado o arquivo obsoleto `develop_natan_20260421135636_PR_DESC.md`.

### Impacto

* **Manutenibilidade:** A adição dos testes garante que regressões na captura do `git diff` e da identificação de branchs sejam detectadas com antecedência.
* **Onboarding:** As notas adicionais no README sobre as compilações do executável e a inclusão das instruções de execução dos testes garantem que qualquer desenvolvedor contribuidor saiba rapidamente como modificar, validar e buildar a ferramenta localmente.
