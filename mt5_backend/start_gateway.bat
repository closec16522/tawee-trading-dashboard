@echo off
cd /d "%~dp0"
echo =======================================
echo MT5 Gateway Server Startup
echo =======================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation.
    pause
    exit /b
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Gateway Server on Port 18789...
echo Please make sure MetaTrader 5 is open and logged in!
echo.
python mt5_gateway.py

pause
