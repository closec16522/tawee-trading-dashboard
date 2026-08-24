import re

with open("mt5_backend/agent_orchestrator.py", "r", encoding="utf-8") as f:
    content = f.read()

target1 = """def run_news_analyst():"""
replacement1 = """def reload_config():
    global GEMINI_API_KEY, gemini_model
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            import json
            c = json.load(f)
            new_key = c.get("gemini_api_key", "")
            if new_key and new_key != GEMINI_API_KEY and new_key != "YOUR_GEMINI_API_KEY_HERE":
                GEMINI_API_KEY = new_key
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ API Key reloaded dynamically.")
    except Exception as e:
        pass

def run_news_analyst():"""

content = content.replace(target1, replacement1)

target2 = """    while True:
        try:
            current_hour = datetime.now().hour"""
replacement2 = """    while True:
        try:
            reload_config()
            current_hour = datetime.now().hour"""

content = content.replace(target2, replacement2)

with open("mt5_backend/agent_orchestrator.py", "w", encoding="utf-8") as f:
    f.write(content)

print("orchestrator patched")