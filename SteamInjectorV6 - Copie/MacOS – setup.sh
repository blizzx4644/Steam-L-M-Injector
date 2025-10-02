#!/bin/bash
echo "=========================================="
echo "  Steam Injector - Setup (macOS)"
echo "=========================================="

# Vérification Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 n'est pas installé."
    echo "➡️ Installation via Homebrew..."
    if ! command -v brew >/dev/null 2>&1; then
        echo "❌ Homebrew n'est pas installé. Installez-le d'abord :"
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    brew install python@3.8
fi

PY_VER=$(python3 -V 2>&1 | awk '{print $2}')
echo "✅ Python $PY_VER détecté"

echo "📦 Installation des dépendances..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "✅ Installation terminée !"
