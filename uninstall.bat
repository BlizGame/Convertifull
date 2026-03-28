@echo off
chcp 65001 >nul

net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process -FilePath '%~dpnx0' -Verb RunAs"
    exit /b
)

:run
cd /d "%~dp0"
echo Uninstalling Convertifull...
python main.py --uninstall
echo.
echo Done. Press any key to exit.
pause >nul