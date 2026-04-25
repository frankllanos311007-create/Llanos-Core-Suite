@echo off
set "SCRIPT_PATH=%~dp0run_monitor.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Instalando Monitor de Llanos Core en el Inicio de Windows...
copy /y "%SCRIPT_PATH%" "%STARTUP_FOLDER%\LlanosCoreMonitor.vbs"

echo.
echo [!] Monitor instalado con exito. 
echo [!] El sistema se abrira SOLO cada vez que llegue un cliente nuevo.
echo [!] Tambien se activara automaticamente al encender la PC.
pause
