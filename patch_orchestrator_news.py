import os
import re

file_path = os.path.join('mt5_backend', 'agent_orchestrator.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add global state for last_news_telegram_hour
if "last_news_telegram_hour = -1" not in content:
    content = content.replace("last_report_hour = -1", "last_report_hour = -1\nlast_news_telegram_hour = -1")

# 2. Add saving to news_status.json and sending Telegram alert
old_code_block = """                    update_agent("news_analyst", "Standby", activity, color)
                    try:
                        requests.post(f"{GATEWAY_URL}/api/news_update", json=news_payload, timeout=2, proxies=LOCAL_PROXIES)
                    except Exception as e:
                        pass"""

new_code_block = """                    update_agent("news_analyst", "Standby", activity, color)
                    try:
                        import json
                        with open("news_status.json", "w", encoding="utf-8") as f:
                            json.dump(news_payload, f, ensure_ascii=False)
                    except:
                        pass
                        
                    try:
                        requests.post(f"{GATEWAY_URL}/api/news_update", json=news_payload, timeout=2, proxies=LOCAL_PROXIES)
                    except Exception as e:
                        pass
                        
                    global last_news_telegram_hour
                    current_hr = datetime.now().hour
                    if current_hr != last_news_telegram_hour:
                        last_news_telegram_hour = current_hr
                        
                        # Send Telegram News Update
                        pairs_text = "\\n".join([f"• <b>{p['symbol']}</b>: {p['impact']} - {p.get('text', '')}" for p in news_payload.get("pairs", [])])
                        tg_msg = (
                            f"📰 <b>News Intelligence Update</b>\\n\\n"
                            f"<b>Status:</b> {news_payload.get('summary_risk', 'Unknown')}\\n"
                            f"<b>Summary:</b> {news_payload.get('summary_text', '')}\\n\\n"
                            f"<b>Impact:</b>\\n{pairs_text}"
                        )
                        send_telegram_alert(tg_msg)"""

if old_code_block in content:
    content = content.replace(old_code_block, new_code_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched agent_orchestrator.py")
else:
    print("Could not find the code block in agent_orchestrator.py")
