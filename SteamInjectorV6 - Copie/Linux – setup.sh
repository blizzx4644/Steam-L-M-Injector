#!/bin/bash
echo "=========================================="
echo "  Steam Injector - Setup (Linux)"
echo "=========================================="

# Vérification Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 n'est pas installé."
    echo "➡️ Installation de Python 3.8..."
    sudo apt update && sudo apt install -y python3.8 python3.8-venv python3-pip
fi

PY_VER=$(python3 -V 2>&1 | awk '{print $2}')
echo "✅ Python $PY_VER détecté"

echo "📦 Installation des dépendances..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "✅ Installation terminée !"
