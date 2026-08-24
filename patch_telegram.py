import re

with open('mt5_backend/agent_orchestrator.py', 'r', encoding='utf-8') as f:
    content = f.read()

target1 = 'model_used = f"Local {LOCAL_AI_MODEL.capitalize()}"'
replacement1 = 'model_used = f"💻 Local Machine ({LOCAL_AI_MODEL})"'
content = content.replace(target1, replacement1)

target2 = 'model_used = "Google Gemini-2.5-Pro"'
replacement2 = 'model_used = "🌌 Google Gemini (2.5-Flash)"'
content = content.replace(target2, replacement2)

target3 = 'f"🤖 <b>Powered by:</b> {model_used}\\n\\n"'
replacement3 = 'f"🤖 <b>วิเคราะห์โดย AI:</b> {model_used}\\n\\n"'
content = content.replace(target3, replacement3)

with open('mt5_backend/agent_orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Telegram patched")