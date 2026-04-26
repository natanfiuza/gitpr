#!/bin/sh
# GitPR Hook - Preenche a mensagem de commit automaticamente com IA

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Se o usuário já passou uma mensagem manual com 'git commit -m', aborta a IA
if [ "$COMMIT_SOURCE" = "message" ]; then
    exit 0
fi

echo "\033[0;36m🤖 GitPR: A pedir sugestão de commit à IA...\033[0m"

# Chama o GitPR repassando o caminho do arquivo ($1) para a nossa nova flag --hook
if command -v gitpr >/dev/null 2>&1; then
    gitpr --commit --hook "$COMMIT_MSG_FILE"
elif [ -f "Pipfile" ] && command -v pipenv >/dev/null 2>&1; then
    pipenv run python run.py --commit --hook "$COMMIT_MSG_FILE"
else
    echo "\033[0;31m❌ Aviso: GitPR não encontrado. Prosseguindo sem IA.\033[0m"
fi