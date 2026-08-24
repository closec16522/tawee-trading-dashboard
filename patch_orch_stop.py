import os
with open("mt5_backend/agent_orchestrator.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """if msg and msg.strip().lower() == "/closeall":"""
replacement = """if msg and msg.strip().lower() in ["/closeall", "หยุด"]:"""

content = content.replace(target, replacement)

with open("mt5_backend/agent_orchestrator.py", "w", encoding="utf-8") as f:
    f.write(content)

print("orchestrator stop command patched")