path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

bad_string = """            msg = f"✈️ <b>CO-PILOT MODE ALERT</b>
AI wants to <b>{trade_type} {symbol}</b>.
Please execute manually in MT5 if you approve.\""""

good_string = """            msg = f"✈️ <b>CO-PILOT MODE ALERT</b>\\nAI wants to <b>{trade_type} {symbol}</b>.\\nPlease execute manually in MT5 if you approve.\""""

# If encoding broke the airplane emoji, let's just use regex to fix any multiline msg = f"..."
import re

new_content = re.sub(
    r'msg = f"✈️ <b>CO-PILOT MODE ALERT</b>\nAI wants to <b>\{trade_type\} \{symbol\}</b>.\nPlease execute manually in MT5 if you approve."',
    r'msg = f"✈️ <b>CO-PILOT MODE ALERT</b>\\nAI wants to <b>{trade_type} {symbol}</b>.\\nPlease execute manually in MT5 if you approve."',
    content
)

# Alternative regex if emoji is weird:
new_content = re.sub(
    r'msg = f"(.*?)<b>CO-PILOT MODE ALERT</b>\nAI wants to <b>\{trade_type\} \{symbol\}</b>.\nPlease execute manually in MT5 if you approve."',
    r'msg = f"\1<b>CO-PILOT MODE ALERT</b>\\nAI wants to <b>{trade_type} {symbol}</b>.\\nPlease execute manually in MT5 if you approve."',
    new_content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Syntax error fixed!")
