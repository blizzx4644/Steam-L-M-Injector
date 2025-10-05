@echo off
title Steam Injector v2.0 - Launcher
color 0B

echo.
echo ========================================
echo    Steam Injector v2.0 - Electron
echo ========================================
echo.

REM Vérifier si Node.js est installé
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Node.js n'est pas installe!
    echo.
    echo Veuillez installer Node.js depuis https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js detecte
echo.

REM Vérifier si node_modules existe
if not exist "node_modules\" (
    echo [INFO] Premiere installation detectee
    echo [INFO] Installation des dependances...
    echo.
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERREUR] L'installation a echoue!
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependances installees avec succes!
    echo.
)

echo [INFO] Demarrage de Steam Injector...
echo.

REM Lancer l'application
call npm start

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] L'application n'a pas pu demarrer!
    pause
    exit /b 1
)

exit /b 0
