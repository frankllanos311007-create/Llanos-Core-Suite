@echo off
title Llanos Core - System Launcher
color 0A
cls

echo ========================================
echo   LLANOS CORE - INICIANDO SISTEMA
echo ========================================

:: 1. Verificar dependencias
echo [1/3] Verificando librerias...
python -m pip install requests --quiet

:: 2. Sincronizar datos (Silencioso)
echo [2/3] Sincronizando datos de la nube...
pythonw -c "import database; database.sincronizar_nube()"

:: 3. Lanzar aplicación (Sin ventana de comandos)
echo [3/3] Abriendo interfaz principal...
start pythonw main.py

:: Salir del CMD inmediatamente
exit
