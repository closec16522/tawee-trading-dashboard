@echo off
cd /d "%~dp0"
echo =======================================
echo MT5 Multi-Agent AI Orchestrator
echo =======================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

echo Starting MT5 Gateway...
start "MT5 Gateway" cmd /c "python mt5_gateway.py"

timeout /t 2 /nobreak >nul

echo Starting Orchestrator...
python agent_orchestrator.py
pause
