import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = r'(\s*print\(f"\\r.*?EA HALTED: \{reason\}.*?end=""\)\n\s*time\.sleep\(60\)\n\s*continue)'
replacement = r'\n                print(f"\\r🤖 EA HALTED: {reason} - Waiting for next session/day...", end="")\n                update_agent("risk_manager", "HALTED", reason, "#ef4444")\n                update_agent("trade_executor", "Standby", "Trading Halted", "#64748b")\n                time.sleep(60)\n                continue'

if re.search(target, content):
    content = re.sub(target, replacement, content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched heartbeat in agent orchestrator (regex)")
else:
    print("Target not found using regex.")
