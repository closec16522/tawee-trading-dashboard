@echo off
cd /d "%~dp0"
echo =======================================
echo MT5 Basic AI Trading Bot Startup
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

echo Checking dependencies...
pip show pandas >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing pandas...
    pip install pandas
)

echo.
echo Starting AI Trading Bot...
echo Please make sure MetaTrader 5 is open, logged in, and Auto-Trading is allowed!
echo.
python ai_trader_old.py

pause
