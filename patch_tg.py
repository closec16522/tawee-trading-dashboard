import codecs

with codecs.open('mt5_backend/agent_orchestrator.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add AGENT_TELEGRAM_TOKEN
token_str = 'TELEGRAM_TOKEN = "8899582441:AAFVy4Ab23ilqcO1BBue5zo18RbmmJAVAAI"'
new_token_str = token_str + '\nAGENT_TELEGRAM_TOKEN = "8646665032:AAFzTrhY0CMvr1pA9Fo_32dK1T11lp42jeY"'
content = content.replace(token_str, new_token_str)

# 2. Add send_agent_telegram_alert function right below send_telegram_alert
send_tg_func = """def send_telegram_alert(msg, image_path=None):"""

send_agent_func = """def send_agent_telegram_alert(msg):
    global AGENT_TELEGRAM_TOKEN, CHAT_ID
    if not AGENT_TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{AGENT_TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Telegram Agent Error:", e)

def send_telegram_alert(msg, image_path=None):"""

content = content.replace(send_tg_func, send_agent_func)

# 3. Update update_agent to use send_agent_telegram_alert
update_agent_call = """LAST_TG_MSG[agent_id] = tg_msg
                send_telegram_alert(tg_msg)"""
new_update_agent_call = """LAST_TG_MSG[agent_id] = tg_msg
                send_agent_telegram_alert(tg_msg)"""
content = content.replace(update_agent_call, new_update_agent_call)

with codecs.open('mt5_backend/agent_orchestrator.py', 'w', 'utf-8') as f:
    f.write(content)
print("agent_orchestrator.py patched.")
