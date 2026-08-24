import os

with open("mt5_backend/agent_orchestrator.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                f"🤖 <b>[AI AUTOTRADE SIGNAL]</b>\n\n"
                f"<b>Action:</b> {trade_type} {action_icon}\n"
                f"<b>Symbol:</b> {symbol}\n\"""

replacement = """                f"🤖 <b>[AI AUTOTRADE SIGNAL]</b>\n\n"
                f"<b>Action:</b> {trade_type} {action_icon}\n"
                f"<b>Symbol:</b> {symbol}\n"
                f"✅ <b>Allowed Signal Grades:</b> {', '.join(load_trading_config().get('allowed_grades', ['A', 'B']))}\n\"""

content = content.replace(target, replacement)

with open("mt5_backend/agent_orchestrator.py", "w", encoding="utf-8") as f:
    f.write(content)