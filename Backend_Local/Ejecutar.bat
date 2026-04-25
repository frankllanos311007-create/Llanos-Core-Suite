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

:: 2. Ejecutar Sincronizacion
echo [2/3] Sincronizando datos de la nube...
python -c "import database; database.sincronizar_nube()"

:: 3. Lanzar aplicacion
echo [3/3] Abriendo interfaz principal...
start /b python main.py

echo ========================================
echo        SISTEMA OPERATIVO
echo ========================================
exit
