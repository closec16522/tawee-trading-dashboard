import sys

target = '''def update_agent(agent_id, status, activity=None, color=None):
    try:
        payload = {"agent_id": agent_id, "status": status}
        if activity: payload["activity"] = activity
        if color: payload["color"] = color
        r = requests.post(f"{GATEWAY_URL}/api/agent_update", json=payload, timeout=2, proxies=LOCAL_PROXIES)
        if r.status_code != 200:
            print(f"⚠️ Gateway Error: {r.status_code}. (Did you restart start_gateway.bat?)")
    except Exception as e:
        print("⚠️ Gateway update failed (Is the Gateway running?):", e)'''

replacement = '''LAST_TG_MSG = {}

def translate_casual_for_tg(agent_id, text):
    import re
    t = text.lower()
    r = text
    id_lower = agent_id.lower()
    
    if "scanning" in t and "structure" in t:
        match = re.search(r"Scanning (.*?) Structure", text, re.IGNORECASE)
        p = match.group(1) if match else "กราฟ"
        r = f"เห้ยๆ ขอดูกราฟ {p} แป๊บนะ ขอส่องโครงสร้างแป๊บ 👀"
    elif "waiting for market data" in t:
        r = f"รอข้อมูลตลาดแป๊บนึงนะวัยรุ่น... เน็ตช้าหรือตลาดนิ่งเนี่ย 🥱"
    elif "bullish" in t:
        match = re.search(r"\[(.*?)\]", text)
        p = match.group(1) if match else ""
        r = f"{p} ทรงนี้กระทิงดุจัดๆ 🚀 ซื้อดิคร้าบบบรอไร!"
    elif "bearish" in t:
        match = re.search(r"\[(.*?)\]", text)
        p = match.group(1) if match else ""
        r = f"{p} หมีมาเต็มๆ เตรียมทุบเลยลูกพี่! 🐻📉"
    elif "evaluating" in t:
        match = re.search(r"Evaluating (.*?)\.\.\.", text, re.IGNORECASE)
        p = match.group(1) if match else "กราฟ"
        r = f"กำลังเพ่ง {p} แบบละเอียดๆ อยู่ฮะ ขอใช้สมองแป๊บ 🧐"
    elif "จุดเข้าเทรดที่น่าสนใจ" in t:
        r = text.replace("จุดเข้าเทรดที่น่าสนใจคือเมื่อพิจารณาจาก", "เจอจุดเข้าสวยๆ ละพวก! ส่องจาก").replace("และ", "บวกกับ") + " เตรียมซิ่งเลยนะ 😎"
    elif "trade rejected" in t or "volatility" in t:
        r = f"โอ้ยยย กราฟเหวี่ยงเกิ๊นนน ยกเลิกออเดอร์ก่อน ไม่เสี่ยงดีกว่า 🛑"
    elif "calculating risk" in t:
        r = f"กำลังดีดลูกคิดคำนวณความเสี่ยงแป๊บนะพี่น้อง 🧮💸"
    elif "executing" in t:
        r = f"จัดไปชุดใหญ่ไฟกระพริบ! กำลังเคาะขวายิงออเดอร์ปิ้วๆ 🔫💥"
    elif "monitoring" in t:
        r = f"เฝ้าพอร์ตให้แบบตาไม่กระพริบเลยครับเจ้านาย 👁️👁️"
    elif "ราคาจะถอยไปที่โซน" in t:
        r = text.replace("ราคาจะถอยไปที่โซน", "ระวังนะ ราคามันน่าจะย่อไปเทสแถวๆ โซน").replace("และสามารถเห็นการปิด", "แล้วถ้าปิดแบบ") + " ลองจับตาดูดีๆ วัยรุ่น! 🤓"
    elif "ใกล้ๆ กับจุดนั้น" in t:
        r = text.replace("ใกล้ๆ กับจุดนั้น", "แถวๆ นั้นแหละ")
    else:
        if id_lower == 'market_analyst': r = text + ' ว่าไงวัยรุ่น? 🕵️‍♂️'
        elif id_lower == 'smc_strategist': r = text + ' ทรงนี้จัดมั้ยเซียน? 🧠'
        elif id_lower == 'risk_manager': r = text + ' ใจร่มๆ ไว้ก่อนนะ 🛡️'
        elif id_lower == 'trade_executor': r = text + ' พร้อมลุยเสมอ! ⚡'
        else: r = text
        
    return f"🗣 [{agent_id.upper()}]: {r}"

def update_agent(agent_id, status, activity=None, color=None):
    try:
        payload = {"agent_id": agent_id, "status": status}
        if activity: payload["activity"] = activity
        if color: payload["color"] = color
        
        # Send translated message to Telegram if activity is provided
        if activity:
            tg_msg = translate_casual_for_tg(agent_id, activity)
            if LAST_TG_MSG.get(agent_id) != tg_msg:
                LAST_TG_MSG[agent_id] = tg_msg
                send_telegram_alert(tg_msg)
                
        r = requests.post(f"{GATEWAY_URL}/api/agent_update", json=payload, timeout=2, proxies=LOCAL_PROXIES)
        if r.status_code != 200:
            print(f"⚠️ Gateway Error: {r.status_code}. (Did you restart start_gateway.bat?)")
    except Exception as e:
        print("⚠️ Gateway update failed (Is the Gateway running?):", e)'''

with open('mt5_backend/agent_orchestrator.py', 'r', encoding='utf8') as f:
    text = f.read()

if target in text:
    text = text.replace(target, replacement)
    with open('mt5_backend/agent_orchestrator.py', 'w', encoding='utf8') as f:
        f.write(text)
    print("PATCH SUCCESSFUL")
else:
    print("TARGET NOT FOUND IN agent_orchestrator.py")
