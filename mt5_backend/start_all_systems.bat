@echo off
cd /d "%~dp0"
title Tawee Trading Intelligence - Master Launcher

echo ==================================================
echo Tawee Trading Intelligence - Master Startup Script
echo ==================================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b
)

echo.
echo [1/3] Starting MT5 Gateway Server...
start "MT5 Gateway (Port 19000)" cmd /k "python mt5_gateway.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Multi-Agent Orchestrator...
start "AI Orchestrator" cmd /k "python agent_orchestrator.py"
timeout /t 3 /nobreak >nul

echo [3/4] Starting AI Basic Trader (Optional)...
start "AI Trader Bot" cmd /k "python ai_trader_old.py"

echo [4/4] Starting Developer Agent (Telegram Coder)...
start "Developer Agent" cmd /k "cd .. && python developer_agent.py"

echo.
echo ==================================================
echo All systems have been launched in separate windows!
echo You can minimize them, but do not close them while trading.
echo ==================================================
pause
