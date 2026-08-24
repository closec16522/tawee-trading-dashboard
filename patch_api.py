import codecs
import re

with codecs.open('mt5_backend/mt5_gateway.py', 'r', 'utf-8') as f:
    content = f.read()

# Replace run_backtest function
old_run_backtest = """@app.post("/api/backtest/run")
async def run_backtest():
    # Run the backtest script in background so it doesn't block
    script_path = os.path.join(os.path.dirname(__file__), "strategy_optimizer.py")
    subprocess.Popen(["python", script_path])
    return {"status": "Backtest optimization started"}"""

new_run_backtest = """@app.post("/api/backtest/run")
async def run_backtest():
    script_path = os.path.join(os.path.dirname(__file__), "strategy_optimizer.py")
    log_path = os.path.join(os.path.dirname(__file__), "backtest_ai.log")
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("[System] Initializing AI-Trader MCP Server...\\n")
        
    f_log = open(log_path, 'a', encoding='utf-8')
    # Use python with unbuffered output
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.Popen(["python", "-u", script_path], stdout=f_log, stderr=subprocess.STDOUT, env=env)
    return {"status": "Backtest optimization started"}

@app.get("/api/backtest/logs")
async def get_backtest_logs():
    log_path = os.path.join(os.path.dirname(__file__), "backtest_ai.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return {"logs": "".join(lines[-100:])}
        except Exception:
            pass
    return {"logs": "[System] Waiting for initialization..."}"""

if old_run_backtest in content:
    content = content.replace(old_run_backtest, new_run_backtest)
else:
    print("Could not find old_run_backtest in mt5_gateway.py")

with codecs.open('mt5_backend/mt5_gateway.py', 'w', 'utf-8') as f:
    f.write(content)
print("mt5_gateway.py patched")
