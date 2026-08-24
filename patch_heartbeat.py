import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''            if not can_trade:
                print(f"\\r🤖 EA HALTED: {reason} - Waiting for next session/day...", end="")
                time.sleep(60)
                continue'''

replacement = '''            if not can_trade:
                print(f"\\r🤖 EA HALTED: {reason} - Waiting for next session/day...", end="")
                # Send update to keep frontend heartbeat alive and show status
                update_agent("risk_manager", "HALTED", reason, "#ef4444")
                update_agent("trade_executor", "Standby", "Trading Halted", "#64748b")
                time.sleep(60)
                continue'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched heartbeat in agent orchestrator")
else:
    print("Target not found.")
