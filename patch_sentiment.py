import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find the `news_today_str = ""` block in `run_news_analyst`
target = '''                    news_today_str = ""
                    calendar_events_today = []
                    
                    for event in root.findall("event"):'''

replacement = '''                    # --- 🚀 FEAR & GREED / SOCIAL SENTIMENT (Phase 2) ---
                    sentiment_str = "Neutral"
                    try:
                        fng_res = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
                        if fng_res.status_code == 200:
                            fng_data = fng_res.json()["data"][0]
                            sentiment_str = f"Fear & Greed Index (Risk Proxy): {fng_data['value']} ({fng_data['value_classification']})"
                    except Exception:
                        pass
                    
                    news_today_str = f"\\n--- GLOBAL SENTIMENT ---\\n{sentiment_str}\\n\\n--- ECONOMIC CALENDAR ---\\n"
                    calendar_events_today = []
                    
                    for event in root.findall("event"):'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sentiment Patch applied!")
else:
    print("Target not found for Sentiment patch.")
