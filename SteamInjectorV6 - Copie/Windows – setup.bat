@echo off
setlocal

echo ==========================================
echo   Steam Injector - Setup (Windows)
echo ==========================================

REM Vérifier si Python 3.8+ est installé
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python n'est pas installé.
    echo Téléchargement et installation de Python 3.8...
    powershell -Command "Start-Process https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe"
    echo ➡️ Installez Python manuellement puis relancez ce script.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version') do set PY_VER=%%v
echo ✅ Python %PY_VER% détecté

echo 📦 Installation des dépendances...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ✅ Installation terminée !
pause
