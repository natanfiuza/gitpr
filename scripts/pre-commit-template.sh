#!/bin/sh
# GitPR Linter Hook - Pre-commit validation

# Cores para o terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔍 GitPR: A validar regras de análise estática...${NC}"

# 1. Tenta executar o comando. 
# Primeiro tenta o binário global 'gitpr', depois tenta via pipenv usando o run.py
if command -v gitpr >/dev/null 2>&1; then
    gitpr --linter
elif [ -f "Pipfile" ] && command -v pipenv >/dev/null 2>&1; then
    pipenv run python run.py --linter
else
    echo "${RED}❌ Erro: Comando 'gitpr' não encontrado.${NC}"
    echo "Certifique-se de que o GitPR está instalado ou que o Pipenv está configurado."
    exit 1
fi

# 2. Captura o código de saída
STATUS=$?

if [ $STATUS -ne 0 ]; then
    echo ""
    echo -e "${RED}🚨 COMMIT BLOQUEADO!${NC}"
    echo "O Linter encontrou violações de código que precisam de correção."
    echo "Dica: Para forçar o commit (não recomendado), use: git commit --no-verify"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Código aprovado! A finalizar commit...${NC}"
exit 0