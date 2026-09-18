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
cls
echo ======================================================
echo             Convertifull Installer
echo ======================================================
echo.

where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python detected.
echo [2/3] Installing/updating Python dependencies...
python -m pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Failed to install Python dependencies via pip.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

where ffmpeg >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] FFmpeg detected. Video and audio conversion will be fully supported.
) else (
    echo [NOTE] FFmpeg was not found in PATH.
    echo        Image/vector conversions will work normally.
    echo        To convert video/audio, download FFmpeg and add it to your PATH.
)

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer" /v MultipleInvokePromptMinimum /t REG_DWORD /d 1000 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" /v MultipleInvokePromptMinimum /t REG_DWORD /d 1000 /f >nul 2>&1

echo.
echo [3/3] Registering Windows context menu entries...
python main.py --install
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Failed to register context menu in Windows registry.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo      Convertifull successfully installed!
echo ======================================================
echo You can now right-click supported media files in
echo Windows File Explorer and convert them immediately.
echo.
echo Note: If File Explorer was already open, restart
echo File Explorer or sign out to apply the 15+ files fix.
echo.
echo Press any key to exit.
pause >nul