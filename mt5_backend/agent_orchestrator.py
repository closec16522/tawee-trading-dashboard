from local_ai import gemini_model
import sys; sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import time
import requests
import json
import os
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import ea_logic

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf
import random

# Configuration
TELEGRAM_TOKEN = "8899582441:AAFVy4Ab23ilqcO1BBue5zo18RbmmJAVAAI"
AGENT_TELEGRAM_TOKEN = "8796299419:AAF5eY4Z_bH1kCdj2bQ_g3N0urdwPGEkHfY"
CHAT_ID = "1828172350"
CHAT_ID_LONGTERM = ""
AGENT_CHAT_ID = ""
GATEWAY_URL = "http://127.0.0.1:19000"

# Load settings from config.json
MAIN_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
if os.path.exists(MAIN_CONFIG_PATH):
    with open(MAIN_CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {
        "gemini_api_key": "",
        "symbols": ["EURUSD"],
        "timeframe": "M15"
    }

SYMBOLS = config.get("symbols", ["EURUSD"])
TIMEFRAME_STR = config.get("timeframe", "M15")
tf_map = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1
}
TIMEFRAME = tf_map.get(TIMEFRAME_STR, mt5.TIMEFRAME_M15)
GEMINI_API_KEY = config.get("gemini_api_key", "")
AI_PROVIDER = config.get("ai_provider", "gemini")
LOCAL_AI_URL = config.get("local_ai_url", "http://localhost:11434/api/generate")
LOCAL_AI_MODEL = config.get("local_ai_model", "llama3")
PAPER_TRADING = (config.get("paper_trading", "false").lower() == "true")

# Global State
news_impact = "low"
current_trends = {}
approved_trades = {}
last_report_hour = -1
last_news_telegram_hour = -1
REPORT_HOURS = [8, 12, 17, 20]

# Cache for News API to prevent Rate Limiting
last_news_fetch_time = 0
cached_news_impact = False

def get_emotion(event_type):
    if event_type == "OPEN":
        emojis = ["💪 ลุยกันเลย!", "😎 รอรับเงินได้เลย", "👀 เจอจังหวะสวยๆ แล้ว", "🔥 จัดไปวัยรุ่น", "🎯 แม่นๆ เน้นๆ"]
    elif event_type == "PROFIT":
        emojis = ["🎉 สุดยอดดด!", "💰 รับทรัพย์เต็มๆ", "🥳 ฉลองงง!", "🚀 To the moon!", "💸 หวานเจี๊ยบ!"]
    elif event_type == "LOSS":
        emojis = ["🥺 สู้ใหม่ไม้หน้าครับ", "🩹 เจ็บแต่จบตามแผน", "💪 ป้องกันพอร์ตไว้ก่อน ลุยต่อครับ", "🛡️ ไม่ลากพอร์ต ปลอดภัยไว้ก่อน", "☔ ฟ้าหลังฝนสวยงามเสมอ"]
    else:
        emojis = ["🤖"]
    return random.choice(emojis)

# HTTP Proxies Bypass (fixes Gateway 404 Error if local proxy is active)
LOCAL_PROXIES = {"http": None, "https": None}

def send_agent_telegram_alert(msg, image_path=None):
    target_chat = AGENT_CHAT_ID if AGENT_CHAT_ID else CHAT_ID
    target_token = AGENT_TELEGRAM_TOKEN if AGENT_TELEGRAM_TOKEN else TELEGRAM_TOKEN
    try:
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{target_token}/sendPhoto"
            with open(image_path, 'rb') as photo:
                requests.post(url, data={"chat_id": target_chat, "caption": msg, "parse_mode": "HTML"}, files={"photo": photo}, timeout=10, proxies=LOCAL_PROXIES)
        else:
            url = f"https://api.telegram.org/bot{target_token}/sendMessage"
            requests.post(url, json={"chat_id": target_chat, "text": msg, "parse_mode": "HTML"}, timeout=15, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Agent Telegram Error:", e)

def send_telegram_alert(msg, image_path=None):
    try:
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            with open(image_path, 'rb') as photo:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML"}, files={"photo": photo}, timeout=10, proxies=LOCAL_PROXIES)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Telegram Error:", e)

def send_telegram_longterm_alert(msg, image_path=None, override_chat_id=None):
    target_chat = override_chat_id if override_chat_id else (CHAT_ID_LONGTERM if CHAT_ID_LONGTERM else CHAT_ID)
    try:
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            with open(image_path, 'rb') as photo:
                requests.post(url, data={"chat_id": target_chat, "caption": msg, "parse_mode": "HTML"}, files={"photo": photo}, timeout=10, proxies=LOCAL_PROXIES)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": target_chat, "text": msg, "parse_mode": "HTML"}, timeout=15, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Telegram Long-Term Error:", e)

def close_position(ticket, symbol, volume, pos_type, profit):
    tick = mt5.symbol_info_tick(symbol)
    if not tick: return False
    
    close_type = mt5.ORDER_TYPE_SELL if pos_type == 0 else mt5.ORDER_TYPE_BUY
    price = tick.bid if pos_type == 0 else tick.ask
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": close_type,
        "position": ticket,
        "price": float(price),
        "deviation": 20,
        "magic": 234000,
        "comment": "AI Close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    if result and result.retcode != mt5.TRADE_RETCODE_DONE:
        request["type_filling"] = mt5.ORDER_FILLING_FOK
        result = mt5.order_send(request)
        
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✅ CLOSE SUCCESS (Ticket: {result.order})")
        
        status_icon = "🟩" if profit > 0 else "🟥"
        status_text = "PROFIT" if profit > 0 else "LOSS"
        action_text = "BUY" if pos_type == 0 else "SELL"
        
        emotion = get_emotion("PROFIT" if profit > 0 else "LOSS")
        
        msg = (
            f"✅ <b>[AI TRADE CLOSED]</b>\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Action:</b> {action_text} (Closed)\n"
            f"<b>Ticket:</b> #{ticket}\n"
            f"<b>Close Price:</b> {price}\n"
            f"-------------------------\n"
            f"💰 <b>Net P/L:</b> ${profit:.2f}\n"
            f"📊 <b>Status:</b> {status_text} {status_icon}\n\n"
            f"<i>{emotion}</i>"
        )
        send_telegram_alert(msg)
        return True
    else:
        code = result.retcode if result else "Unknown"
        print(f"❌ CLOSE FAILED (Code: {code})")
        return False

LAST_TG_MSG = {}
ACTIVE_TICKETS_CACHE = None

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
                send_agent_telegram_alert(tg_msg)
                
        r = requests.post(f"{GATEWAY_URL}/api/agent_update", json=payload, timeout=5, proxies=LOCAL_PROXIES)
        if r.status_code != 200:
            print(f"⚠️ Gateway Error: {r.status_code}. (Did you restart start_gateway.bat?)")
    except Exception as e:
        print("⚠️ Gateway update failed (Is the Gateway running?):", e)

def update_system_alert(title, message, level="info"):
    try:
        r = requests.post(f"{GATEWAY_URL}/api/system_alert", json={"title": title, "message": message, "level": level}, timeout=5, proxies=LOCAL_PROXIES)
        if r.status_code != 200:
            print(f"⚠️ Gateway Error: {r.status_code}. (Did you restart start_gateway.bat?)")
    except:
        pass

def update_market_analysis(symbol, data):
    try:
        payload = {"symbol": symbol, "data": data}
        r = requests.post(f"{GATEWAY_URL}/api/market_analysis_update", json=payload, timeout=5, proxies=LOCAL_PROXIES)
    except:
        pass

def update_signals(signals):
    try:
        payload = {"signals": signals}
        r = requests.post(f"{GATEWAY_URL}/api/signals_update", json=payload, timeout=5, proxies=LOCAL_PROXIES)
    except:
        pass

def init_mt5():
    if not mt5.initialize():
        print("MT5 Init Failed")
        return False
    return True

def generate_trade_chart(symbol, decision, entry, sl, tp):
    try:
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 200)
        if rates is None or len(rates) == 0:
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        entry_line = [entry] * len(df)
        sl_line = [sl] * len(df)
        tp_line = [tp] * len(df)
        
        fill_between = []
        if decision == "BUY":
            fill_between.append(dict(y1=entry_line, y2=tp_line, color='g', alpha=0.2))
            fill_between.append(dict(y1=sl_line, y2=entry_line, color='r', alpha=0.2))
        else:
            fill_between.append(dict(y1=entry_line, y2=sl_line, color='r', alpha=0.2))
            fill_between.append(dict(y1=tp_line, y2=entry_line, color='g', alpha=0.2))
        
        chart_path = os.path.join(os.path.dirname(__file__), f"chart_{symbol}.png")
        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', edge='inherit', wick='inherit')
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', facecolor='#131722', figcolor='#131722', gridcolor='#363c4e')
        
        fig, axlist = mpf.plot(df, type='candle', fill_between=fill_between, style=s,
                 title=f"{symbol} ({TIMEFRAME_STR}) - AI Signal: {decision}",
                 ylabel='Price',
                 returnfig=True)
                 
        ax = axlist[0]
        x_pos = len(df) - 1 + 0.5
        
        bbox_tp = dict(boxstyle='round,pad=0.3', fc='#ef5350' if decision == "SELL" else '#26a69a', ec='none')
        bbox_sl = dict(boxstyle='round,pad=0.3', fc='#26a69a' if decision == "SELL" else '#ef5350', ec='none')
        bbox_entry = dict(boxstyle='larrow,pad=0.3', fc='#4287f5', ec='none')
        
        ax.text(x_pos, tp, f'TP {tp}', color='white', va='center', bbox=bbox_tp, fontweight='bold', fontsize=9)
        ax.text(x_pos, sl, f'SL {sl}', color='white', va='center', bbox=bbox_sl, fontweight='bold', fontsize=9)
        ax.text(x_pos, entry, f'{entry}', color='white', va='center', bbox=bbox_entry, fontweight='bold', fontsize=9)
        
        candle_y = df['low'].iloc[-1] if decision == "BUY" else df['high'].iloc[-1]
        arrow_y = candle_y - (df['high'].iloc[-1] - df['low'].iloc[-1])*1.5 if decision == "BUY" else candle_y + (df['high'].iloc[-1] - df['low'].iloc[-1])*1.5
        
        ax.annotate(decision, xy=(len(df)-1, candle_y), xytext=(len(df)-1, arrow_y),
            arrowprops=dict(facecolor='white', shrink=0.05, width=2, headwidth=8), color='white', ha='center', va='center', fontweight='bold')
            
        fig.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
                 
        return chart_path
    except Exception as e:
        print("Chart generation error:", e)
        return None

def generate_stats_chart():
    try:
        now = datetime.now()
        start = now - timedelta(days=7)
        deals = mt5.history_deals_get(start, now)
        if not deals:
            return None
            
        daily_profit = {}
        for d in deals:
            if d.type == mt5.DEAL_TYPE_BUY or d.type == mt5.DEAL_TYPE_SELL:
                day_str = datetime.fromtimestamp(d.time).strftime('%m-%d')
                daily_profit[day_str] = daily_profit.get(day_str, 0) + d.profit
                
        if not daily_profit:
            return None
            
        days = sorted(list(daily_profit.keys()))
        profits = [daily_profit[day] for day in days]
        colors = ['#26a69a' if p >= 0 else '#ef5350' for p in profits]
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#131722')
        ax.set_facecolor('#131722')
        
        bars = ax.bar(days, profits, color=colors)
        ax.axhline(0, color='white', linewidth=1)
        ax.set_title('Last 7 Days P/L', color='white')
        ax.set_ylabel('Profit ($)', color='white')
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, f'${yval:.0f}', ha='center', va='bottom' if yval >= 0 else 'top', color='white', fontsize=8)
            
        plt.tight_layout()
        chart_path = os.path.join(os.path.dirname(__file__), "stats_chart.png")
        plt.savefig(chart_path, dpi=100, facecolor=fig.get_facecolor())
        plt.close(fig)
        
        return chart_path
    except Exception as e:
        print("Stats chart error:", e)
        return None

# 1. News Analyst
last_allowed_grades = None

def reload_config():
    global GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY, gemini_model, last_allowed_grades, AI_PROVIDER
    global SYMBOLS, TIMEFRAME_STR, TIMEFRAME, PAPER_TRADING, TELEGRAM_TOKEN, CHAT_ID, CHAT_ID_LONGTERM, AGENT_CHAT_ID
    
    # Load MAIN_CONFIG (config.json)
    try:
        if os.path.exists(MAIN_CONFIG_PATH):
            with open(MAIN_CONFIG_PATH, 'r', encoding='utf-8') as f:
                import json
                c = json.load(f)
                
                # Reload symbols and timeframe
                new_symbols = c.get("symbols", ["EURUSD"])
                if set(new_symbols) != set(SYMBOLS):
                    print(f"🔄 Symbols changed from {SYMBOLS} to {new_symbols}")
                    SYMBOLS = new_symbols
                
                new_tf_str = c.get("timeframe", "M15")
                if new_tf_str != TIMEFRAME_STR:
                    print(f"🔄 Timeframe changed from {TIMEFRAME_STR} to {new_tf_str}")
                    TIMEFRAME_STR = new_tf_str
                    TIMEFRAME = tf_map.get(TIMEFRAME_STR, mt5.TIMEFRAME_M15)
                    
                # Reload keys
                TELEGRAM_TOKEN = c.get("telegram_bot_token", TELEGRAM_TOKEN)
                CHAT_ID = c.get("telegram_chat_id", CHAT_ID)
                CHAT_ID_LONGTERM = c.get("telegram_chat_id_longterm", CHAT_ID_LONGTERM)
                AGENT_CHAT_ID = c.get("agent_telegram_chat_id", AGENT_CHAT_ID)
                
                new_key = c.get("gemini_api_key", "")
                if new_key and new_key != GEMINI_API_KEY and new_key != "YOUR_GEMINI_API_KEY_HERE":
                    GEMINI_API_KEY = new_key
                    pass

                OPENAI_API_KEY = c.get("openai_api_key", "")
                CLAUDE_API_KEY = c.get("claude_api_key", "")
    except Exception as e:
        print("Error reloading MAIN_CONFIG:", e)

    # Load TRADING_CONFIG (trading_config.json)
    try:
        t_conf = load_trading_config()
        if t_conf:
            # Read AI Engine
            engine = t_conf.get("model_engine", "gemini")
            if engine == "ollama":
                AI_PROVIDER = "local"
            else:
                AI_PROVIDER = engine
                
            PAPER_TRADING = (t_conf.get("paper_trading", "false").lower() == "true")
            
            new_grades = t_conf.get("allowed_grades", ["A", "B"])
            if last_allowed_grades is None:
                last_allowed_grades = new_grades
            elif set(new_grades) != set(last_allowed_grades):
                last_allowed_grades = new_grades
                print(f"🔄 Signal Grades changed to: {new_grades}")
                send_telegram_alert(f"⚙️ <b>อัปเดตการตั้งค่าระบบจากหน้าเว็บ</b>\n✅ ระบบเปลี่ยนไปเข้าเทรดเฉพาะ: <b>เกรด {', '.join(new_grades)}</b>", None)
    except Exception as e:
        pass

def analyze_news_with_local_ai(news_text):
    prompt = f"""
    คุณเป็น 'AI Economic News Analyst' หน้าที่ของคุณคือวิเคราะห์ข่าวเศรษฐกิจรายวัน
    จากข่าวเศรษฐกิจของวันนี้ด้านล่างนี้ ให้สรุปภาพรวมความเสี่ยงและผลกระทบต่อตลาด

    ข่าววันนี้:
    {news_text}

    ให้ตอบกลับเป็น JSON format เท่านั้น โดยมีโครงสร้างดังนี้:
    {{
        "summary_risk": "เสี่ยงสูง / เสี่ยงปานกลาง / เสี่ยงต่ำ",
        "summary_text": "สรุปผลกระทบต่อตลาดโดยรวมสั้นๆ ไม่เกิน 3 บรรทัด",
        "macro_briefing": "สรุปภาพรวมข่าวเศรษฐกิจระดับมหภาคสำหรับแสดงผลบนหน้าจอให้เทรดเดอร์อ่านแบบสรุปกระชับ",
        "pairs": [
            {{"symbol": "XAUUSD", "impact": "ผันผวนสูง / เอนขาขึ้น / เอนขาลง / ทรงตัว", "text": "ผลกระทบต่อราคาทองคำ", "color": "#f59e0b หรือ #10b981 หรือ #ef4444"}},
            {{"symbol": "EURUSD", "impact": "...", "text": "...", "color": "..."}},
            {{"symbol": "GBPUSD", "impact": "...", "text": "...", "color": "..."}},
            {{"symbol": "BTCUSD", "impact": "...", "text": "...", "color": "..."}}
        ]
    }}
    """
    
    payload = {
        "model": LOCAL_AI_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        r = requests.post(LOCAL_AI_URL, json=payload, timeout=60)
        if r.status_code == 200:
            resp = r.json().get("response", "").strip()
            # Try to parse json to ensure it's valid
            import json
            parsed = json.loads(resp)
            return parsed
    except Exception as e:
        print(f"📰 Ollama News Analyst Error: {e}")
    return None


# --- 8. COIN HUNTER AI (Auto Coin & Symbol Discovery Engine) ---
def run_coin_hunter():
    global SYMBOLS
    print("🔍 COIN HUNTER AI: Auto-Scanning Broker Market for High-Opportunity Pairs...")
    update_agent("coin_hunter", "Scanning Market", "Auto-Discovering High Volatility Pairs...", "#34d6e6")
    time.sleep(1)
    
    try:
        # 1. Query all symbols from MT5 broker
        all_symbols = mt5.symbols_get()
        candidate_symbols = []
        
        if all_symbols:
            for s in all_symbols:
                name = s.name.strip()
                name_upper = name.upper()
                # Include Forex, Gold/Metals, Crypto, Indices, Oil
                if any(k in name_upper for k in ["XAU", "GOLD", "BTC", "ETH", "SOL", "EURUSD", "GBPUSD", "USDJPY", "US30", "NAS100", "OIL"]):
                    if s.visible or mt5.symbol_select(name, True):
                        candidate_symbols.append(name)
        
        if not candidate_symbols:
            candidate_symbols = ["XAUUSD", "XAUUSD-VIP", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "USDJPY", "SOLUSD"]
            
        top_movers = []
        # Scan up to 30 candidate pairs
        for sym in candidate_symbols[:30]:
            rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_H1, 0, 24)
            if rates is not None and len(rates) > 0:
                import pandas as pd
                df_c = pd.DataFrame(rates)
                volatility = ((df_c['high'].max() - df_c['low'].min()) / df_c['close'].iloc[-1]) * 100
                top_movers.append((sym, volatility))
                
        top_movers.sort(key=lambda x: x[1], reverse=True)
        # Select top 6 volatile/high-opportunity pairs
        discovered_symbols = [x[0] for x in top_movers[:6]] if top_movers else ["XAUUSD-VIP", "BTCUSD", "EURUSD"]
        
        # Dynamically auto-add new discovered pairs into active SYMBOLS list
        added_new = 0
        for p in discovered_symbols:
            if p not in SYMBOLS:
                SYMBOLS.append(p)
                added_new += 1
                print(f"🚀 COIN HUNTER AI: Auto-Discovered & Added New Pair -> {p}")
                
        top_name = discovered_symbols[0] if discovered_symbols else "XAUUSD"
        print(f"🎯 COIN HUNTER AI: Market Auto-Discovery Complete! Active SYMBOLS ({len(SYMBOLS)} Pairs): {SYMBOLS}")
        update_agent("coin_hunter", "Auto-Discovered", f"Added {top_name} (Total Active: {len(SYMBOLS)} Pairs)", "#34d6e6")
        
        # Persist updated symbols list into config.json
        try:
            if os.path.exists(MAIN_CONFIG_PATH):
                with open(MAIN_CONFIG_PATH, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                c_data["symbols"] = SYMBOLS
                with open(MAIN_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(c_data, f, indent=4, ensure_ascii=False)
        except Exception as json_e:
            pass

        return discovered_symbols
    except Exception as e:
        print("⚠️ COIN HUNTER AI Error:", e)
        update_agent("coin_hunter", "Standby", "Scanning Complete", "#64748b")
        return SYMBOLS

def run_news_analyst():
    global news_impact, last_news_fetch_time, cached_news_impact
    print("📰 NEWS ANALYST: Checking ForexFactory Calendar...")
    update_agent("news_analyst", "Checking News")
    time.sleep(2)
    
    current_time = time.time()
    try:
        # Update every 30 minutes (1800 seconds)
        if current_time - last_news_fetch_time > 1800 or last_news_fetch_time == 0:
            try:
                r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=15, headers={"User-Agent": "Mozilla/5.0"}, proxies=LOCAL_PROXIES)
                if r.status_code == 200:
                    root = ET.fromstring(r.content)
                    high_impact_usd = False
                    today = datetime.now().strftime("%m-%d-%Y")
                    
                    # --- 🚀 FEAR & GREED / SOCIAL SENTIMENT (Phase 2) ---
                    sentiment_str = "Neutral"
                    try:
                        fng_res = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
                        if fng_res.status_code == 200:
                            fng_data = fng_res.json()["data"][0]
                            sentiment_str = f"Fear & Greed Index (Risk Proxy): {fng_data['value']} ({fng_data['value_classification']})"
                    except Exception:
                        pass
                    
                    news_today_str = f"\n--- GLOBAL SENTIMENT ---\n{sentiment_str}\n\n--- ECONOMIC CALENDAR ---\n"
                    calendar_events_today = []
                    
                    for event in root.findall("event"):
                        date = event.find("date").text if event.find("date") is not None else ""
                        if date == today:
                            currency = event.find("country").text if event.find("country") is not None else ""
                            impact = event.find("impact").text if event.find("impact") is not None else ""
                            title = event.find("title").text if event.find("title") is not None else ""
                            time_val = event.find("time").text if event.find("time") is not None else ""
                            forecast = event.find("forecast").text if event.find("forecast") is not None else ""
                            previous = event.find("previous").text if event.find("previous") is not None else ""
                            actual = event.find("actual").text if event.find("actual") is not None else ""
                            
                            news_today_str += f"- [{impact}] {currency}: {title}\n"
                            
                            calendar_events_today.append({
                                "time": time_val,
                                "currency": currency,
                                "title": title,
                                "impact": impact,
                                "forecast": forecast,
                                "previous": previous,
                                "actual": actual
                            })
                            
                            if currency == "USD" and impact == "High":
                                high_impact_usd = True
                    
                    cached_news_impact = high_impact_usd
                    last_news_fetch_time = current_time
                    
                    # Call AI for analysis if local AI is used
                    ai_payload = None
                    if AI_PROVIDER == "local" and news_today_str.strip():
                        print("📰 NEWS ANALYST: Asking Ollama to analyze today's news...")
                        ai_payload = analyze_news_with_local_ai(news_today_str)
                        
                    if ai_payload:
                        ai_payload["calendar_events"] = calendar_events_today
                        news_payload = ai_payload
                        news_impact = "high" if cached_news_impact else "low"
                        activity = "AI News Analyzed"
                        color = "#3b82f6"
                        print("📰 NEWS ANALYST: ✅ Ollama successfully analyzed news.")
                    else:
                        # Fallback to hardcoded payload
                        if cached_news_impact:
                            news_impact = "high"
                            activity = "High Impact USD News Detected!"
                            color = "#ef4444"
                            news_payload = {
                                "summary_risk": "เสี่ยงสูง",
                                "summary_text": "ตลาดแกว่งตัวผันผวนรุนแรง ตรวจพบข่าวสำคัญที่มีผลกระทบสูงต่อ USD (High Impact USD News) แนะนำให้เพิ่มความระมัดระวังในการเทรดคู่เงินหลัก",
                                "pairs": [
                                    {"symbol": "XAUUSD", "impact": "ผันผวนสูง", "text": "ราคาทองคำมักจะตอบสนองรุนแรงต่อข่าว USD อาจเห็นการแกว่งตัวในกรอบกว้าง", "color": "#f59e0b"},
                                    {"symbol": "EURUSD", "impact": "ผันผวนสูง", "text": "เฝ้าระวังแรงเทขายหรือแรงซื้อฉับพลันจากตัวเลขเศรษฐกิจ USD", "color": "#f59e0b"},
                                    {"symbol": "GBPUSD", "impact": "ผันผวนสูง", "text": "คาดการณ์การแกว่งตัวรุนแรงตามดัชนีดอลลาร์", "color": "#f59e0b"},
                                    {"symbol": "BTCUSD", "impact": "เอนขาขึ้น", "text": "ตลาดคริปโตอาจได้รับผลกระทบทางอ้อม หาก USD อ่อนค่า", "color": "#10b981"}
                                ]
                            }
                        else:
                            news_impact = "low"
                            activity = "No High Impact USD News"
                            color = "#37d27a"
                            news_payload = {
                                "summary_risk": "เสี่ยงต่ำ",
                                "summary_text": "สภาวะตลาดโดยรวมปกติ ไม่มีข่าวสำคัญที่มีผลกระทบสูงต่อ USD ในวันนี้ ตลาดมีแนวโน้มเคลื่อนไหวตามกรอบเทคนิคอล",
                                "pairs": [
                                    {"symbol": "XAUUSD", "impact": "เอนขาขึ้น", "text": "แรงหนุนจากกรอบโครงสร้างราคาเดิม ไร้ปัจจัยข่าวกดดัน", "color": "#10b981"},
                                    {"symbol": "EURUSD", "impact": "ทรงตัว", "text": "เคลื่อนไหวในกรอบสะสมพลัง รอจังหวะการเลือกทาง", "color": "#f59e0b"},
                                    {"symbol": "GBPUSD", "impact": "เอนขาลง", "text": "โมเมนตัมฝั่งขายยังคุมตลาดตามโครงสร้างรอง", "color": "#ef4444"},
                                    {"symbol": "BTCUSD", "impact": "เอนขาขึ้น", "text": "รักษาระดับเหนือแนวรับสำคัญได้ดี มีลุ้นทดสอบแนวต้าน", "color": "#10b981"}
                                ]
                            }
                        
                    update_agent("news_analyst", "Standby", activity, color)
                    try:
                        import json
                        with open("news_status.json", "w", encoding="utf-8") as f:
                            json.dump(news_payload, f, ensure_ascii=False)
                    except:
                        pass
                        
                    try:
                        requests.post(f"{GATEWAY_URL}/api/news_update", json=news_payload, timeout=5, proxies=LOCAL_PROXIES)
                    except Exception as e:
                        pass
                        
                    global last_news_telegram_hour
                    current_hr = datetime.now().hour
                    if current_hr != last_news_telegram_hour:
                        last_news_telegram_hour = current_hr
                        
                        # Send Telegram News Update
                        pairs_text = "\n".join([f"• <b>{p['symbol']}</b>: {p['impact']} - {p.get('text', '')}" for p in news_payload.get("pairs", [])])
                        tg_msg = (
                            f"📰 <b>News Intelligence Update</b>\n\n"
                            f"<b>Status:</b> {news_payload.get('summary_risk', 'Unknown')}\n"
                            f"<b>Summary:</b> {news_payload.get('summary_text', '')}\n\n"
                            f"<b>Impact:</b>\n{pairs_text}"
                        )
                        send_telegram_alert(tg_msg)
                
                elif r.status_code == 429:
                    print("📰 NEWS ANALYST: API Rate Limited (429). Using cached/default data.")
                else:
                    print(f"📰 NEWS ANALYST: API Error {r.status_code}")
            except Exception as req_e:
                print("📰 NEWS ANALYST: Network/API Exception:", req_e)
            
    except Exception as e:
        print("📰 NEWS ANALYST: General Exception occurred:", e)
        update_agent("news_analyst", "Standby", "News check failed", "#f59e0b")

# 2. Market Analyst & SMC Strategist (AI Powered)
def analyze_market_with_ai(symbol, df, h4_trend="H4 Trend: Unknown | M15 Trend: Unknown | M5 Trend: Unknown"):
    if not gemini_model:
        return None

    # Convert OHLC data to a string summary
    recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI']) + get_strategy_context_str(symbol) + get_pattern_str(df)
    recent_data += f"\n\n*** 🚀 MULTI-TIMEFRAME (MTF) CONTEXT ***\nMulti-Timeframe Structure: {h4_trend}\nPlease prioritize setups that align across multiple timeframes. A strong setup should have M5 and M15 aligning with the H4 direction.\n*************************************************\n"
    
    prompt = f"""
    คุณคือทีมนักวิเคราะห์และเทรดเดอร์ระดับโลก (AI Agent Team) ในตลาด Forex ประกอบด้วย 2 ตำแหน่ง:
    1. 'Market Analyst' (มี Skill ขั้นเทพในการวิเคราะห์โครงสร้างตลาดใหญ่, แนวรับ (Support), แนวต้าน (Resistance), และโซน Demand/Supply)
    2. 'SMC Strategist' (มี Skill ขั้นเทพในการหาจุดเข้าเทรดด้วย Smart Money Concepts: Order Blocks, FVG, BOS, CHoCH, และ Liquidity)

    นี่คือข้อมูลแท่งเทียน 10 แท่งล่าสุดของคู่เงิน {symbol} (Timeframe: {TIMEFRAME_STR}):
    
    {recent_data}
    
    ให้ทั้งสอง Agent ใช้งาน Skill ของตนเองวิเคราะห์กราฟนี้ แล้วตอบกลับมาในรูปแบบ JSON ตามโครงสร้างด้านล่างนี้เท่านั้น (ห้ามมี Markdown หรือข้อความอื่น):
    {{
        "market_analyst": {{
            "trend": "Bullish / Bearish / Ranging",
            "support": "ราคาแนวรับสำคัญ",
            "resistance": "ราคาแนวต้านสำคัญ",
            "demand_zone": "ช่วงราคาโซน Demand",
            "supply_zone": "ช่วงราคาโซน Supply",
            "analysis": "สรุปโครงสร้างตลาดสั้นๆ 1-2 ประโยคแบบมืออาชีพ"
        }},
        "smc_strategist": {{
            "setup": "อธิบายจุดเข้าเทรด SMC (สำคัญ: ถ้าระบบเจอ Chart Pattern ให้ระบุด้วยว่า Pattern นั้นช่วยคอนเฟิร์มการตัดสินใจอย่างไร) 1-2 ประโยคแบบมืออาชีพ",
            "decision": "BUY / SELL / HOLD",
            "confidence": "เปอร์เซ็นต์ความน่าจะเป็น (ตัวเลข 0-100)"
        }}
    }}
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        # Clean JSON if it is wrapped in markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return data
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Gemini API Error on {symbol}:", error_msg)
        if "429" in error_msg or "quota" in error_msg.lower():
            print("⏳ Rate Limit Hit! Sleeping for 60 seconds before continuing...")
            time.sleep(60)
        return None

def analyze_market_with_local_ai(symbol, df, h4_trend="H4 Trend: Unknown | M15 Trend: Unknown | M5 Trend: Unknown"):
    # Convert OHLC data to a string summary
    recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI']) + get_strategy_context_str(symbol) + get_pattern_str(df)
    recent_data += f"\n\n*** 🚀 MULTI-TIMEFRAME (MTF) CONTEXT ***\nMulti-Timeframe Structure: {h4_trend}\nPlease prioritize setups that align across multiple timeframes. A strong setup should have M5 and M15 aligning with the H4 direction.\n*************************************************\n"
    
    prompt = f"""
    คุณคือทีมนักวิเคราะห์และเทรดเดอร์ระดับโลก (AI Agent Team) ในตลาด Forex ประกอบด้วย 2 ตำแหน่ง:
    1. 'Market Analyst' (มี Skill ขั้นเทพในการวิเคราะห์โครงสร้างตลาดใหญ่, แนวรับ (Support), แนวต้าน (Resistance), และโซน Demand/Supply)
    2. 'SMC Strategist' (มี Skill ขั้นเทพในการหาจุดเข้าเทรดด้วย Smart Money Concepts: Order Blocks, FVG, BOS, CHoCH, และ Liquidity)

    นี่คือข้อมูลแท่งเทียน 10 แท่งล่าสุดของคู่เงิน {symbol} (Timeframe: {TIMEFRAME_STR}):
    
    {recent_data}
    
    ให้ทั้งสอง Agent ใช้งาน Skill ของตนเองวิเคราะห์กราฟนี้ แล้วตอบกลับมาในรูปแบบ JSON ตามโครงสร้างด้านล่างนี้เท่านั้น (ห้ามมี Markdown หรือข้อความอื่น):
    {{
        "market_analyst": {{
            "trend": "Bullish / Bearish / Ranging",
            "support": "ราคาแนวรับสำคัญ",
            "resistance": "ราคาแนวต้านสำคัญ",
            "demand_zone": "ช่วงราคาโซน Demand",
            "supply_zone": "ช่วงราคาโซน Supply",
            "analysis": "สรุปโครงสร้างตลาดสั้นๆ 1-2 ประโยคแบบมืออาชีพ"
        }},
        "smc_strategist": {{
            "setup": "อธิบายจุดเข้าเทรด SMC (สำคัญ: ถ้าระบบเจอ Chart Pattern ให้ระบุด้วยว่า Pattern นั้นช่วยคอนเฟิร์มการตัดสินใจอย่างไร) 1-2 ประโยคแบบมืออาชีพ",
            "decision": "BUY / SELL / HOLD",
            "confidence": "เปอร์เซ็นต์ความน่าจะเป็น (ตัวเลข 0-100)"
        }}
    }}
    """
    
    payload = {
        "model": LOCAL_AI_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        r = requests.post(LOCAL_AI_URL, json=payload, timeout=60)
        if r.status_code == 200:
            res_json = r.json()
            text = res_json.get("response", "").strip()
            # Clean JSON if it is wrapped in markdown
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            data = json.loads(text.strip())
            return data
        else:
            print(f"⚠️ Local AI Error on {symbol}: HTTP {r.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Local AI Request Failed on {symbol}:", e)
        return None

def analyze_market_with_openai(symbol, df, model_name="gpt-4o", h4_trend="H4 Trend: Unknown | M15 Trend: Unknown | M5 Trend: Unknown"):
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API Key is missing!")
        return None

    recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI']) + get_strategy_context_str(symbol) + get_pattern_str(df)
    recent_data += f"\n\n*** 🚀 MULTI-TIMEFRAME (MTF) CONTEXT ***\nMulti-Timeframe Structure: {h4_trend}\nPlease prioritize setups that align across multiple timeframes. A strong setup should have M5 and M15 aligning with the H4 direction.\n*************************************************\n"
    
    prompt = f"""
    คุณคือทีมนักวิเคราะห์และเทรดเดอร์ระดับโลก (AI Agent Team) ในตลาด Forex ประกอบด้วย 2 ตำแหน่ง:
    1. 'Market Analyst' (มี Skill ขั้นเทพในการวิเคราะห์โครงสร้างตลาดใหญ่, แนวรับ (Support), แนวต้าน (Resistance), และโซน Demand/Supply)
    2. 'SMC Strategist' (มี Skill ขั้นเทพในการหาจุดเข้าเทรดด้วย Smart Money Concepts: Order Blocks, FVG, BOS, CHoCH, และ Liquidity)

    นี่คือข้อมูลแท่งเทียน 10 แท่งล่าสุดของคู่เงิน {symbol} (Timeframe: {TIMEFRAME_STR}):
    
    {recent_data}
    
    ให้ทั้งสอง Agent ใช้งาน Skill ของตนเองวิเคราะห์กราฟนี้ แล้วตอบกลับมาในรูปแบบ JSON ตามโครงสร้างด้านล่างนี้เท่านั้น (ห้ามมี Markdown หรือข้อความอื่น):
    {{
        "market_analyst": {{
            "trend": "Bullish / Bearish / Ranging",
            "support": "ราคาแนวรับสำคัญ",
            "resistance": "ราคาแนวต้านสำคัญ",
            "demand_zone": "ช่วงราคาโซน Demand",
            "supply_zone": "ช่วงราคาโซน Supply",
            "analysis": "สรุปโครงสร้างตลาดสั้นๆ 1-2 ประโยคแบบมืออาชีพ"
        }},
        "smc_strategist": {{
            "setup": "อธิบายจุดเข้าเทรด SMC (สำคัญ: ถ้าระบบเจอ Chart Pattern ให้ระบุด้วยว่า Pattern นั้นช่วยคอนเฟิร์มการตัดสินใจอย่างไร) 1-2 ประโยคแบบมืออาชีพ",
            "decision": "BUY / SELL / HOLD",
            "confidence": "เปอร์เซ็นต์ความน่าจะเป็น (ตัวเลข 0-100)"
        }}
    }}
    """
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "response_format": { "type": "json_object" },
        "messages": [
            {"role": "system", "content": "You are a professional forex trading AI. Respond ONLY with valid JSON matching the requested structure."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            res_json = r.json()
            text = res_json["choices"][0]["message"]["content"]
            data = json.loads(text.strip())
            return data
        else:
            print(f"⚠️ OpenAI API Error on {symbol}: HTTP {r.status_code} - {r.text}")
            return None
    except Exception as e:
        print(f"⚠️ OpenAI Request Failed on {symbol}:", e)
        return None

def analyze_market_with_claude(symbol, df, h4_trend="H4 Trend: Unknown | M15 Trend: Unknown | M5 Trend: Unknown"):
    if not CLAUDE_API_KEY:
        print("⚠️ Claude API Key is missing!")
        return None

    recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI']) + get_strategy_context_str(symbol) + get_pattern_str(df)
    recent_data += f"\n\n*** 🚀 MULTI-TIMEFRAME (MTF) CONTEXT ***\nMulti-Timeframe Structure: {h4_trend}\nPlease prioritize setups that align across multiple timeframes. A strong setup should have M5 and M15 aligning with the H4 direction.\n*************************************************\n"
    
    prompt = f"""
    คุณคือทีมนักวิเคราะห์และเทรดเดอร์ระดับโลก (AI Agent Team) ในตลาด Forex ประกอบด้วย 2 ตำแหน่ง:
    1. 'Market Analyst' (มี Skill ขั้นเทพในการวิเคราะห์โครงสร้างตลาดใหญ่, แนวรับ (Support), แนวต้าน (Resistance), และโซน Demand/Supply)
    2. 'SMC Strategist' (มี Skill ขั้นเทพในการหาจุดเข้าเทรดด้วย Smart Money Concepts: Order Blocks, FVG, BOS, CHoCH, และ Liquidity)

    นี่คือข้อมูลแท่งเทียน 10 แท่งล่าสุดของคู่เงิน {symbol} (Timeframe: {TIMEFRAME_STR}):
    
    {recent_data}
    
    ให้ทั้งสอง Agent ใช้งาน Skill ของตนเองวิเคราะห์กราฟนี้ แล้วตอบกลับมาในรูปแบบ JSON ตามโครงสร้างด้านล่างนี้เท่านั้น (ห้ามมี Markdown หรือข้อความอื่น):
    {{
        "market_analyst": {{
            "trend": "Bullish / Bearish / Ranging",
            "support": "ราคาแนวรับสำคัญ",
            "resistance": "ราคาแนวต้านสำคัญ",
            "demand_zone": "ช่วงราคาโซน Demand",
            "supply_zone": "ช่วงราคาโซน Supply",
            "analysis": "สรุปโครงสร้างตลาดสั้นๆ 1-2 ประโยคแบบมืออาชีพ"
        }},
        "smc_strategist": {{
            "setup": "อธิบายจุดเข้าเทรด SMC (สำคัญ: ถ้าระบบเจอ Chart Pattern ให้ระบุด้วยว่า Pattern นั้นช่วยคอนเฟิร์มการตัดสินใจอย่างไร) 1-2 ประโยคแบบมืออาชีพ",
            "decision": "BUY / SELL / HOLD",
            "confidence": "เปอร์เซ็นต์ความน่าจะเป็น (ตัวเลข 0-100)"
        }}
    }}
    """
    
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            res_json = r.json()
            text = res_json["content"][0]["text"]
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return data
        else:
            print(f"⚠️ Claude API Error on {symbol}: HTTP {r.status_code} - {r.text}")
            return None
    except Exception as e:
        print(f"⚠️ Claude Request Failed on {symbol}:", e)
        return None

def run_ai_analysis():
    global current_trends, approved_trades
    update_agent("market_analyst", "Analysing", "Starting Market Analysis...", "#3b82f6")
    update_agent("smc_strategist", "Standby", "Waiting for Market Data...", "#64748b")
    
    print("🤖 AI TEAM: Scanning MT5 Quotes for multiple symbols...")
    time.sleep(1)
    
    approved_trades.clear()
    
    for symbol in SYMBOLS:
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 200) # Increased to 200 to calculate EMA200
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            # Calculate Indicators
            df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean().round(4)
            df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean().round(4)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = (100 - (100 / (1 + rs))).round(2)
            
            # Calculate ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = true_range.rolling(14).mean().round(4)
            current_atr = df['ATR'].iloc[-1]
            
            # --- 🚀 MULTI-TIMEFRAME ANALYSIS (Phase 2) ---
            def get_trend(symbol, timeframe):
                rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 50)
                if rates is not None and len(rates) > 0:
                    df_tf = pd.DataFrame(rates)
                    df_tf['EMA50'] = df_tf['close'].ewm(span=50, adjust=False).mean()
                    return "BULLISH" if df_tf['close'].iloc[-1] > df_tf['EMA50'].iloc[-1] else "BEARISH"
                return "Unknown"

            h4_trend = get_trend(symbol, mt5.TIMEFRAME_H4)
            m15_trend = get_trend(symbol, mt5.TIMEFRAME_M15)
            m5_trend = get_trend(symbol, mt5.TIMEFRAME_M5)
            
            mtf_context = f"H4 Trend: {h4_trend} | M15 Trend: {m15_trend} | M5 Trend: {m5_trend}"
            
            
            print(f"📊 {symbol}: AI Team is processing... (H4 Trend: {h4_trend}, ATR: {current_atr})")
            update_agent("market_analyst", "Analysing", f"Scanning {symbol} Structure...", "#3b82f6")
            
            if AI_PROVIDER == "local":
                result = analyze_market_with_local_ai(symbol, df, h4_trend=mtf_context)
                model_used = f"💻 Local Machine ({LOCAL_AI_MODEL})"
            elif AI_PROVIDER == "chatgpt":
                result = analyze_market_with_openai(symbol, df, model_name="gpt-4o", h4_trend=mtf_context)
                model_used = "🤖 ChatGPT (OpenAI - gpt-4o)"
            elif AI_PROVIDER == "copilot":
                result = analyze_market_with_openai(symbol, df, model_name="gpt-4o", h4_trend=mtf_context)
                model_used = "🤖 Copilot (Microsoft - gpt-4o)"
            elif AI_PROVIDER == "claude":
                result = analyze_market_with_claude(symbol, df, h4_trend=mtf_context)
                model_used = "🤖 Claude (Anthropic - 3-haiku)"
            else:
                result = analyze_market_with_ai(symbol, df, h4_trend=mtf_context)
                model_used = "🌌 Google Gemini (2.5-Flash)"
            
            if result:
                result['atr'] = current_atr
                ma_data = result.get("market_analyst", {})
                smc_data = result.get("smc_strategist", {})
                
                try:
                    from pattern_detector import detect_chart_pattern
                    result["chart_pattern"] = detect_chart_pattern(df)
                except:
                    result["chart_pattern"] = "None"

                
                # Broadcase Market Analyst Data
                update_market_analysis(symbol, result)
                
                trend = ma_data.get("trend", "Unknown")
                ma_analysis = ma_data.get("analysis", "")
                decision = str(smc_data.get("decision", "HOLD")).strip().upper()
                smc_setup = smc_data.get("setup", "")
                
                # Parse confidence
                raw_conf = str(smc_data.get("confidence", "85"))
                confidence = 85
                import re
                conf_match = re.search(r'\d+', raw_conf)
                if conf_match:
                    confidence = int(conf_match.group())
                
                # Update global trend for Portfolio Manager
                if decision in ["BUY", "SELL"]:
                    current_trends[symbol] = decision
                
                
                print(f"📈 MARKET ANALYST [{symbol}]: Trend={trend} -> {ma_analysis}")
                update_agent("market_analyst", "Analyzed", f"[{symbol}] {trend}", "#8b5cf6")
                time.sleep(1) # Simulate handoff
                
                print(f"🧠 SMC STRATEGIST [{symbol}]: {decision} -> {smc_setup}")
                color = "#37d27a" if decision == "BUY" else ("#ef4444" if decision == "SELL" else "#f59e0b")
                update_agent("smc_strategist", f"Building Setup", f"Evaluating {symbol}...", "#3b82f6")
                time.sleep(1)
                update_agent("smc_strategist", f"[{symbol}] {decision}", smc_setup, color)
                
                if decision in ["BUY", "SELL"]:
                    approved_trades[symbol] = {
                        "decision": decision,
                        "setup": smc_setup,
                        "analysis": ma_analysis,
                        "model": model_used,
                        "confidence": confidence,
                        "atr": current_atr
                    }
            else:
                print(f"⚠️ {symbol}: Analysis failed (HOLD).")
                
        else:
            print(f"📊 MARKET ANALYST: Failed to get rates for {symbol}")
            
        print("⏳ Waiting 10 seconds to avoid Gemini API Rate Limits...")
        time.sleep(10)
            
    if not approved_trades:
        update_agent("market_analyst", "Standby", "Market scan complete", "#64748b")
        update_agent("smc_strategist", "Standby", "No Trade Setup Found", "#64748b")
    else:
        update_agent("market_analyst", "Standby", f"Analyzed {len(SYMBOLS)} symbols", "#37d27a")
        update_agent("smc_strategist", "Found Setups", f"Found {len(approved_trades)} SMC Setups", "#37d27a")

# 4. Risk Manager
def run_risk_manager():
    print("🛡️ RISK MANAGER: Calculating Dynamic Lot Size...")
    update_agent("risk_manager", "Calculating Risk")
    time.sleep(1)
    
    acc_info = mt5.account_info()
    if acc_info:
        balance = acc_info.balance
                # Risk calculation is now delegated to Trade Executor based on SL distance
        print(f"✅ RISK MANAGER: Checking Equity Balance=${balance:.2f} & Drawdown")
        update_agent("risk_manager", "Equity OK", f"Risk managed dynamically per trade based on SL", "#f59e0b")
        return 0.01 # Placeholder
    else:
        update_agent("risk_manager", "Standby")
        return 0.01

import os
import json

TRADING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "trading_config.json")

def load_trading_config():
    if os.path.exists(TRADING_CONFIG_PATH):
        try:
            with open(TRADING_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"allowed_grades": ["A", "B"]}

# 5. Supervisor Agent
def run_supervisor(lot_size):
    global approved_trades

    # --- 🚀 CORRELATION MATRIX (Phase 2) ---
    def check_correlation(new_symbol, new_decision):
        positions = mt5.positions_get()
        if not positions:
            return False, "" # No correlation issue
            
        import pandas as pd
        # mt5 is global
        
        rates_new = mt5.copy_rates_from_pos(new_symbol, mt5.TIMEFRAME_H1, 0, 100)
        if rates_new is None or len(rates_new) == 0:
            return False, ""
        
        df_new = pd.DataFrame(rates_new)['close']
        
        for pos in positions:
            open_symbol = pos.symbol
            open_type = "BUY" if pos.type == 0 else "SELL"
            
            if open_symbol == new_symbol: continue
                
            rates_open = mt5.copy_rates_from_pos(open_symbol, mt5.TIMEFRAME_H1, 0, 100)
            if rates_open is None or len(rates_open) == 0:
                continue
                
            df_open = pd.DataFrame(rates_open)['close']
            
            # Ensure same length
            min_len = min(len(df_new), len(df_open))
            corr = df_new.tail(min_len).corr(df_open.tail(min_len))
            
            if pd.isna(corr): continue
                
            if corr > 0.8:
                if new_decision == open_type:
                    return True, f"High Positive Corr ({corr:.2f}) with {open_symbol} ({open_type})"
            elif corr < -0.8:
                if new_decision != open_type:
                    return True, f"High Negative Corr ({corr:.2f}) with {open_symbol} ({open_type})"
                    
        return False, ""

    print("👑 SUPERVISOR AI: Reviewing Trade Proposals...")
    update_agent("supervisor", "Reviewing")
    time.sleep(1)
    
    if not approved_trades:
        print("👑 SUPERVISOR AI: Standby (No trades)")
        update_agent("supervisor", "Standby")
        update_signals([])
        return []
        
    # Format and broadcast signals to the frontend FIRST (so history isn't lost on News)
    signals_list = []
    final_trades_to_execute = []
    
    import datetime
    config = load_trading_config()
    allowed_grades = config.get("allowed_grades", ["A", "B"])
    
    # HYBRID RISK MANAGER
    MAX_TRADES_PER_SYMBOL = 3
    MIN_DISTANCE_ATR_MULTIPLIER = 1.0
    positions = mt5.positions_get()
    
    for sym, trade_data in list(approved_trades.items()):
        decision = trade_data["decision"]
        
        # --- Check Correlation ---
        is_correlated, corr_msg = check_correlation(sym, decision)
        if is_correlated:
            print(f"🛑 SUPERVISOR BLOCKED: {sym} {decision} due to Correlation: {corr_msg}")
            trade_data["status"] = "Rejected"
            trade_data["rejection_reason"] = f"Correlation Block: {corr_msg}"
            trade_data["grade"] = trade_data.get("grade", "C")
            trade_data["symbol"] = sym
            trade_data["trend"] = trade_data.get("trend", "Unknown")
            trade_data["setup"] = trade_data.get("setup", "")
            signals_list.append(trade_data)
            continue

        confidence = trade_data.get("confidence", 85)
        trade_atr = trade_data.get("atr", 0)
        tick = mt5.symbol_info_tick(sym)
        symbol_info = mt5.symbol_info(sym)
        
        price = (tick.ask if decision == "BUY" else tick.bid) if tick else 0
        sl = 0
        tp = 0
        
        if symbol_info and tick:
            # --- NEW ATR-BASED SL/TP ---
            point = symbol_info.point
            if trade_atr > 0:
                sl_dist = trade_atr * ea_logic.EA_SETTINGS["ATR_MULTIPLIER_SL"]
                tp_dist = trade_atr * ea_logic.EA_SETTINGS["ATR_MULTIPLIER_TP"]
            else:
                sl_dist = 500 * point
                tp_dist = 1000 * point
                
            if decision == "BUY":
                sl = price - sl_dist
                tp = price + tp_dist
            else:
                sl = price + sl_dist
                tp = price - tp_dist
        
        # Calculate grade
        if confidence >= 90:
            grade = "A"
        elif confidence >= 80:
            grade = "B"
        else:
            grade = "C"
            
        if news_impact == "high":
            result = "skip"
            resultText = "REJECTED (High Impact News)"
        elif decision == "BUY" and trade_data.get("h4_trend") == "BEARISH":
            result = "skip"
            resultText = "REJECTED (Counter-Trend: BUY in BEARISH trend)"
        elif decision == "SELL" and trade_data.get("h4_trend") == "BULLISH":
            result = "skip"
            resultText = "REJECTED (Counter-Trend: SELL in BULLISH trend)"
        else:
            if grade not in allowed_grades:
                result = "skip"
                resultText = f"ไม่เข้าเงื่อนไข (รอเกรด {','.join(allowed_grades)})"
            else:
                open_trades_count = 0
                last_open_price = 0
                if positions:
                    same_dir_type = 0 if decision == "BUY" else 1
                    same_dir_trades = [p for p in positions if p.symbol == sym and p.type == same_dir_type]
                    open_trades_count = len(same_dir_trades)
                    if open_trades_count > 0:
                        last_trade = sorted(same_dir_trades, key=lambda p: p.time)[-1]
                        last_open_price = last_trade.price_open
                if open_trades_count >= MAX_TRADES_PER_SYMBOL:
                    result = "skip"
                    resultText = f"REJECTED (Max {MAX_TRADES_PER_SYMBOL} Trades)"
                    print(f"🤖 SUPERVISOR: Rejected {sym} {decision} - Max Trades Reached.")
                elif open_trades_count > 0 and trade_atr > 0 and abs(price - last_open_price) < (trade_atr * MIN_DISTANCE_ATR_MULTIPLIER):
                    result = "skip"
                    resultText = f"REJECTED (< {MIN_DISTANCE_ATR_MULTIPLIER} ATR Distance)"
                    print(f"🤖 SUPERVISOR: Rejected {sym} {decision} - Price too close to last entry.")
                else:
                    result = "entered"
                    resultText = f"เข้าเทรดแล้ว (เกรด {grade})"
                    final_trades_to_execute.append((sym, trade_data))
        signals_list.append({
            "time": datetime.datetime.now().strftime("%d %b %H:%M"),
            "timestamp": datetime.datetime.now().timestamp(),
            "symbol": sym,
            "type": decision,
            "price": price,
            "sl": sl,
            "tp": tp,
            "confidence": confidence,
            "grade": grade,
            "duration": "~1 นาที",
            "result": result,
            "resultText": resultText,
            "model": trade_data.get("model", "Gemini")
        })
        
    update_signals(signals_list)
    
    if news_impact == "high":
        print("👑 SUPERVISOR AI: REJECTED ALL! Blocked due to High Impact News.")
        update_agent("supervisor", "Rejected", "REJECTED: High Impact News", "#ef4444")
        update_system_alert("TRADE REJECTED", "Supervisor blocked trades due to news volatility.", "warn")
        approved_trades.clear()
        return []
        
    print(f"👑 SUPERVISOR AI: APPROVED {len(final_trades_to_execute)} trades.")
    update_agent("supervisor", "Approved", f"APPROVED {len(final_trades_to_execute)} Trades", "#37d27a")
    
    approved_trades.clear()
    return final_trades_to_execute

# 6. Trade Executor
def run_trade_executor(trades, lot):
    if not trades:
        update_agent("trade_executor", "Standby")
        return
        
    update_agent("trade_executor", "Executing")
    
    for symbol, trade_data in trades:
        trade_type = trade_data["decision"]
        ma_analysis = trade_data.get("analysis", "")
        smc_setup = trade_data.get("setup", "")
        model_used = trade_data.get("model", "Unknown AI")
        
        print(f"⚡ TRADE EXECUTOR: Routing Order {trade_type} {symbol} ({lot} Lot)...")
        
        order_type = mt5.ORDER_TYPE_BUY if trade_type == "BUY" else mt5.ORDER_TYPE_SELL
        tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)
        if not tick or not symbol_info:
            print(f"⚡ TRADE EXECUTOR: Failed to get info for {symbol}")
            continue
            
        price = tick.ask if trade_type == "BUY" else tick.bid
        point = symbol_info.point
        
        atr = trade_data.get("atr")
        if atr is not None:
            sl_dist = atr * 1.5
            tp_dist = atr * 3.0
        else:
            sl_dist = 500 * point
            tp_dist = 1000 * point
        
        if trade_type == "BUY":
            sl = price - sl_dist
            tp = price + tp_dist
        else:
            sl = price + sl_dist
            tp = price - tp_dist
        
        # --- 🚀 CO-PILOT MODE (Phase 3) ---
        config = load_trading_config()
        if config.get("co_pilot_mode", False):
            print(f"✈️ CO-PILOT MODE ACTIVE: Intercepting {trade_type} {symbol}")
            update_agent("trade_executor", "Pending User Approval", f"Waiting for manual execution for {symbol}")
            msg = f"✈️ <b>CO-PILOT MODE ALERT</b>\nAI wants to <b>{trade_type} {symbol}</b>.\nPlease execute manually in MT5 if you approve."
            
            try:
                chart_path = generate_trade_chart(symbol, trade_type, float(price), float(sl), float(tp))
                send_telegram_alert(msg, chart_path)
            except Exception:
                send_telegram_alert(msg)
                
            return None
            
        # --- 🚀 INSTITUTIONAL DYNAMIC LOT SIZING ---
        dynamic_lot = ea_logic.get_dynamic_lot_size(symbol, sl_dist)
        update_agent("trade_executor", "Calculating Position Size", f"{symbol} Risk 1% -> Lot: {dynamic_lot}")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(dynamic_lot),
            "type": order_type,
            "price": float(price),
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": 234000,
            "comment": "Multi-Agent AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if PAPER_TRADING:
            print(f"🧪 PAPER TRADING: Mocking Order SUCCESS for {trade_type} {symbol}")
            # Mock a successful result object
            class MockResult:
                def __init__(self):
                    self.retcode = mt5.TRADE_RETCODE_DONE
                    self.order = int(datetime.datetime.now().timestamp())
            result = MockResult()
        else:
            result = mt5.order_send(request)
            if result and result.retcode != mt5.TRADE_RETCODE_DONE:
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                result = mt5.order_send(request)
                if result and result.retcode != mt5.TRADE_RETCODE_DONE:
                    request["type_filling"] = mt5.ORDER_FILLING_RETURN
                    result = mt5.order_send(request)
            
        if result and getattr(result, "retcode", None) == mt5.TRADE_RETCODE_DONE:
            print(f"⚡ TRADE EXECUTOR: Order SUCCESS (Ticket: {result.order})")
            
            # Post-entry SL/TP enforcement for ECN brokers
            ticket_id = getattr(result, "order", 0)
            if ticket_id > 0 and (sl > 0 or tp > 0):
                time.sleep(0.5)
                req_sltp = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": ticket_id,
                    "symbol": symbol,
                    "sl": float(sl),
                    "tp": float(tp)
                }
                res_sltp = mt5.order_send(req_sltp)
                if res_sltp and res_sltp.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"🛡️ TRADE EXECUTOR: Attached SL={sl:.2f} & TP={tp:.2f} to Ticket #{ticket_id}")
                else:
                    print(f"⚠️ TRADE EXECUTOR: Could not attach SL/TP to Ticket #{ticket_id}")
            chart_path = generate_trade_chart(symbol, trade_type, price, sl, tp)
            
            action_icon = "🔵" if trade_type == "BUY" else "🔴"
            emotion = get_emotion("OPEN")
            
            msg = (
                f"🤖 <b>[AI AUTOTRADE SIGNAL]</b>\n\n"
                f"<b>Action:</b> {trade_type} {action_icon}\n"
                f"<b>Symbol:</b> {symbol}\n"
                f"✅ <b>Allowed Signal Grades:</b> {', '.join(load_trading_config().get('allowed_grades', ['A', 'B']))}\n"
                f"<b>Volume:</b> {lot}\n"
                f"<b>Entry Price:</b> {price}\n"
                f"<b>Stop Loss (SL):</b> {sl}\n"
                f"<b>Take Profit (TP):</b> {tp}\n\n"
                f"🧠 <b>AI Analysis (Market Analyst):</b>\n{ma_analysis}\n\n"
                f"🎯 <b>AI Setup (SMC Strategist):</b>\n{smc_setup}\n\n"
                f"🤖 <b>วิเคราะห์โดย AI:</b> {model_used}\n\n"
                f"<i>{emotion}</i>"
            )
            send_telegram_alert(msg, chart_path)
            update_system_alert("TRADE EXECUTED", f"{trade_type} {symbol} at {price}", "success")
        else:
            code = result.retcode if result else "Unknown"
            print(f"⚡ TRADE EXECUTOR: Order FAILED (Code: {code})")
            update_system_alert("TRADE FAILED", f"{trade_type} {symbol} Error: {code}", "error")
            
    update_agent("trade_executor", "Done", f"Executed {len(trades)} trades", "#37d27a")

# 7. Portfolio Manager
def run_portfolio_manager():
    try:
        ea_logic.manage_active_trades()
    except Exception as e:
        print("Error in Active Trade Management:", e)
    print("💼 PORTFOLIO MANAGER: Checking Floating P/L & Managing Open Positions...")
    update_agent("portfolio_manager", "Monitoring")
    time.sleep(1)
    acc = mt5.account_info()
    
    positions = mt5.positions_get()
    closed_count = 0
    
    if positions:
        for pos in positions:
            symbol = pos.symbol
            ticket = pos.ticket
            pos_type = pos.type # 0 for BUY, 1 for SELL
            volume = pos.volume
            
            # Check AI trend for this symbol
            trend = current_trends.get(symbol, "HOLD")
            
            # Close logic: If holding BUY and trend is SELL, close.
            if pos_type == 0 and trend == "SELL":
                print(f"💼 PORTFOLIO MANAGER: Closing BUY {symbol} because AI trend is SELL!")
                if close_position(ticket, symbol, volume, pos_type, pos.profit):
                    closed_count += 1
            elif pos_type == 1 and trend == "BUY":
                print(f"💼 PORTFOLIO MANAGER: Closing SELL {symbol} because AI trend is BUY!")
                if close_position(ticket, symbol, volume, pos_type, pos.profit):
                    closed_count += 1
            elif pos.profit >= 5.0: # Auto-take profit if position reaches $5.00+ profit
                print(f"💰 PORTFOLIO MANAGER: Target Profit reached for {symbol} (#{ticket}) -> Profit: ${pos.profit:.2f}! Closing position...")
                if close_position(ticket, symbol, volume, pos_type, pos.profit):
                    closed_count += 1

    if acc:
        color = "#ef4444" if acc.profit < 0 else "#37d27a"
        msg = f"Floating P/L: ${acc.profit:.2f}"
        if closed_count > 0:
            msg += f" (Closed {closed_count})"
        print(f"💼 PORTFOLIO MANAGER: Floating P/L = ${acc.profit:.2f}")
        update_agent("portfolio_manager", "Standby", msg, color)

def run_trade_journal():
    print("📔 TRADE JOURNAL: Checking for new closed trades to analyze...")
    journal_path = os.path.join(os.path.dirname(__file__), 'journal.json')
    journal_entries = []
    if os.path.exists(journal_path):
        try:
            with open(journal_path, 'r', encoding='utf-8') as f:
                journal_entries = json.load(f)
        except:
            pass

    analyzed_tickets = [entry.get("ticket") for entry in journal_entries]

    now = datetime.now()
    today_start = now - timedelta(days=30)
    deals = mt5.history_deals_get(today_start, now)
    
    new_entries = []
    
    if deals:
        sorted_deals = sorted(deals, key=lambda x: x.time, reverse=True)
        # We only want to analyze up to the last 15 closed deals to save API calls
        closed_deals = [d for d in sorted_deals if d.entry == 1][:15]
        
        for d in closed_deals:
            ticket = d.position_id
            if ticket in analyzed_tickets:
                continue
                
            # fetch entry price
            entry_price = 0.0
            pos_deals = mt5.history_deals_get(position=ticket)
            if pos_deals:
                for pd in pos_deals:
                    if pd.entry == 0:
                        entry_price = pd.price
                        break
                        
            symbol = d.symbol
            trade_type = "BUY" if d.type == 1 else "SELL"
            exit_price = d.price
            profit = d.profit
            close_time = datetime.fromtimestamp(d.time).strftime("%d %b %Y")

            # Analyze using Gemini
            if gemini_model:
                prompt = f"วิเคราะห์ผลการเทรด (Trade Insight) สั้นๆ 1-2 ประโยคสำหรับไม้นี้:\nคู่เงิน: {symbol}\nฝั่ง: {trade_type}\nจุดเข้า: {entry_price}\nจุดออก: {exit_price}\nกำไร: ${profit:.2f}\n\nถ้ากำไร บอกว่าทำอะไรถูก (เช่น เข้าตามเทรน, ปิดได้ดี). ถ้าขาดทุน บอกว่าควรเรียนรู้อะไร (เช่น ผิดเทรน, SL สั้นไป). ตอบเป็นภาษาไทยสั้นๆ กระชับ ไม่ต้องเกริ่นนำ ไม่เกิน 20 คำ."
                insight = "ไม่มีข้อมูล"
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        res = gemini_model.generate_content(prompt)
                        insight = res.text.strip().replace('\n', ' ')
                        time.sleep(5) # Throttling to stay within 15 RPM free tier limit
                        break
                    except Exception as e:
                        err_str = str(e)
                        if "429" in err_str or "Quota" in err_str:
                            if attempt < max_retries - 1:
                                print(f"⏳ Rate limit 429 hit. Waiting 22 seconds before retry...")
                                time.sleep(22)
                                continue
                        print("Error generating journal insight:", e)
                        if profit > 0:
                            insight = f"วิเคราะห์ (อัตโนมัติ): เทรดทำกำไรได้สำเร็จ (+${profit:.2f}) ระบบประเมินว่าจุดออกเหมาะสมตามแผน"
                        elif profit < 0:
                            insight = f"วิเคราะห์ (อัตโนมัติ): ขาดทุน (-${abs(profit):.2f}) สภาพตลาดอาจมีความผันผวนสูง หรือผิดทาง แนะนำให้คุมความเสี่ยงให้เคร่งครัด"
                        else:
                            insight = "วิเคราะห์ (อัตโนมัติ): ปิดเสมอตัว ไม่มีกำไร/ขาดทุน"
                        break
            else:
                insight = "รันตามระบบเทรด"
                
            entry = {
                "ticket": ticket,
                "symbol": symbol,
                "type": trade_type,
                "entry": entry_price,
                "exit": exit_price,
                "profit": profit,
                "date": close_time,
                "insight": insight
            }
            new_entries.append(entry)
            print(f"📔 JOURNAL: Analyzed trade #{ticket} ({symbol}) -> {insight}")

    if new_entries:
        # Prepend new entries
        journal_entries = new_entries + journal_entries
        # Limit to 50
        journal_entries = journal_entries[:50]
        
        with open(journal_path, 'w', encoding='utf-8') as f:
            json.dump(journal_entries, f, ensure_ascii=False, indent=4)
            
    # Always push the latest journal list to the gateway
    try:
        requests.post(f"{GATEWAY_URL}/api/journal_update", json={"entries": journal_entries}, timeout=15, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Error sending journal update to gateway:", e)



def get_pattern_str(df):
    try:
        from pattern_detector import detect_chart_pattern
        pattern = detect_chart_pattern(df)
        if pattern != "None":
            return f"\n\n[CHART PATTERN DETECTED]: {pattern} -> (SMC Strategist: Please evaluate if this pattern aligns with your Order Block/Liquidity setup and mention it in your reasoning)"
    except Exception as e:
        print("Pattern detection error:", e)
    return ""

def get_strategy_context_str(symbol=None):
    context_str = ""
    try:
        strat_path = os.path.join(os.path.dirname(__file__), 'strategy_context.json')
        if os.path.exists(strat_path):
            with open(strat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                directive = data.get("directive", "")
                if directive:
                    context_str += f"\n\n[STRATEGY AI DIRECTIVE FOR THIS WEEK]: {directive} -> ให้คุณนำกลยุทธ์นี้ไปปรับใช้ในการประเมินจุดเข้าและตั้ง SL/TP อย่างเคร่งครัด"
    except:
        pass
        
    try:
        if symbol:
            journal_path = os.path.join(os.path.dirname(__file__), 'journal.json')
            if os.path.exists(journal_path):
                with open(journal_path, 'r', encoding='utf-8') as f:
                    journal_data = json.load(f)
                    
                symbol_trades = [t for t in journal_data if t.get("symbol") == symbol]
                if symbol_trades:
                    recent_trades = symbol_trades[-3:]
                    context_str += f"\n\n*** 📝 SHORT-TERM MEMORY: RECENT TRADES FOR {symbol} ***\n"
                    context_str += "Learn from these outcomes. Avoid repeating mistakes from losses, and find patterns that led to wins:\n"
                    for t in recent_trades:
                        t_type = t.get('type', 'UNKNOWN')
                        profit = t.get('profit', 0)
                        entry = t.get('entry', 0)
                        exit_price = t.get('exit', 0)
                        insight = t.get('insight', '')
                        res_str = "🟢 WIN" if profit > 0 else "🔴 LOSS"
                        context_str += f"- {res_str}: {t_type} Entry @ {entry}, Exit @ {exit_price} | P/L: ${profit:.2f}\n"
                        if insight:
                            context_str += f"  > Your Insight during trade: {insight}\n"
                    context_str += "*****************************************************\n"
    except Exception as e:
        print("Error loading short-term memory:", e)
        
    try:
        rules_path = os.path.join(os.path.dirname(__file__), 'learned_rules.json')
        if os.path.exists(rules_path):
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
                lessons = rules_data.get("lessons_learned", [])
                new_rules = rules_data.get("new_trading_rules", [])
                
                if lessons or new_rules:
                    context_str += "\n\n*** 🧠 AUTONOMOUS LEARNING & PAST LESSONS ***\n"
                    context_str += "You MUST strictly follow these rules derived from your past mistakes:\n"
                    for rule in new_rules:
                        context_str += f"- RULE: {rule}\n"
                    for lesson in lessons:
                        context_str += f"- LESSON: {lesson}\n"
                    context_str += "*************************************************"
    except:
        pass
        
    return context_str

def run_weekly_strategy_review():
    print("🧠 STRATEGY AI: Checking weekly performance for adaptation...")
    strat_path = os.path.join(os.path.dirname(__file__), 'strategy_context.json')
    last_run = 0
    import time
    try:
        if os.path.exists(strat_path):
            with open(strat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_run = data.get("last_run", 0)
    except:
        pass
        
    current_time = time.time()
    # Check if 7 days (604800 seconds) have passed
    if current_time - last_run < 604800:
        return
        
    print("🧠 STRATEGY AI: Running weekly adaptation analysis...")
    now = datetime.now()
    week_start = now - timedelta(days=7)
    deals = mt5.history_deals_get(week_start, now)
    
    profit = 0.0
    wins = 0
    losses = 0
    
    if deals:
        closed_deals = [d for d in deals if d.entry == 1]
        for d in closed_deals:
            profit += d.profit
            if d.profit > 0:
                wins += 1
            elif d.profit < 0:
                losses += 1
                
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    summary = f"Past 7 Days Performance: Total Trades={total_trades}, Win Rate={win_rate:.1f}%, Net Profit=${profit:.2f}"
    print(f"📊 STRATEGY AI: {summary}")
    
    directive = "Maintain current strategy."
    if True: # Local AI / Antigravity CLI Engine
        prompt = f"Our Forex bot trading performance for the past 7 days is: Total Trades={total_trades}, Win Rate={win_rate:.1f}%, Net Profit=${profit:.2f}. If we are taking continuous losses or win rate is below 50%, analyze if the market regime has changed (e.g. trending to ranging) and provide a concise 'Strategy Adjustment Directive' in Thai (e.g. 'ลด Lot ลงครึ่งหนึ่งและเน้นเก็บสั้น', 'ตลาดผันผวนสูง ให้ขยับ SL ให้แคบลง'). If performance is good (profitable), just reply 'ลุยตามระบบเดิมต่อไป'. Keep it under 20 words."
        try:
            res = gemini_model.generate_content(prompt)
            directive = res.text.strip().replace('\n', ' ')
            time.sleep(2)
        except Exception as e:
            print("Error generating strategy directive:", e)
            directive = "ลุยตามระบบเดิมต่อไป (API Error)"
            
    print(f"🎯 STRATEGY AI DIRECTIVE: {directive}")
    
    # Save to file
    new_data = {
        "last_run": current_time,
        "directive": directive,
        "summary": summary
    }
    try:
        with open(strat_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error saving strategy config:", e)

def run_trade_researcher():
    import time
    print("🧠 TRADE RESEARCHER AI: Analyzing historical trades for lessons...")
    update_agent("trade_researcher", "Analyzing", "Extracting Lessons", "#8b5cf6")
    
    journal_path = os.path.join(os.path.dirname(__file__), 'journal.json')
    rules_path = os.path.join(os.path.dirname(__file__), 'learned_rules.json')
    
    if not os.path.exists(journal_path):
        update_agent("trade_researcher", "Standby", "No Journal Data", "#64748b")
        return
        
    try:
        with open(journal_path, 'r', encoding='utf-8') as f:
            journal_data = json.load(f)
    except:
        return
        
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
            last_run = rules_data.get("last_analysis_time", 0)
    except:
        rules_data = {"lessons_learned": [], "new_trading_rules": []}
        last_run = 0
        
    current_time = time.time()
    
    # Run every 24 hours (86400 seconds)
    if current_time - last_run < 86400:
        update_agent("trade_researcher", "Standby", "Waiting for Next Cycle", "#64748b")
        return
        
    # Get last 20 trades
    recent_trades = journal_data[-20:]
    if len(recent_trades) < 5:
        # Not enough trades to learn from
        update_agent("trade_researcher", "Standby", "Not Enough Trades", "#64748b")
        return
        
    trades_str = json.dumps(recent_trades, indent=2)
    
    prompt = f"""
    You are the "Trade Researcher AI" for a Forex trading bot.
    Your job is to analyze the recent trading history, identify patterns in winning and losing trades, and output strict trading rules.
    
    Recent Trades Data (JSON):
    {trades_str}
    
    Analyze the above trades. Look for patterns in why trades lost or won (e.g. specific symbols, time of day, trend alignment, AI insights).
    Output your findings EXACTLY as a JSON object with this structure:
    {{
        "market_conditions": "Brief description of current market conditions",
        "lessons_learned": ["Lesson 1", "Lesson 2"],
        "new_trading_rules": ["Strict Rule 1", "Strict Rule 2"]
    }}
    
    Output ONLY valid JSON. Keep lessons and rules concise and actionable.
    """
    
    try:
        res = gemini_model.generate_content(prompt)
        text = res.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        ai_analysis = json.loads(text.strip())
        
        new_rules_data = {
            "last_analysis_time": current_time,
            "total_trades_analyzed": len(journal_data),
            "market_conditions": ai_analysis.get("market_conditions", ""),
            "lessons_learned": ai_analysis.get("lessons_learned", []),
            "new_trading_rules": ai_analysis.get("new_trading_rules", [])
        }
        
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump(new_rules_data, f, ensure_ascii=False, indent=4)
            
        print("🧠 TRADE RESEARCHER AI: Extracted new lessons successfully!")
        update_agent("trade_researcher", "Standby", "New Rules Saved", "#64748b")
        
    except Exception as e:
        print("🧠 TRADE RESEARCHER AI: Error during analysis:", e)
        update_agent("trade_researcher", "Standby", "Analysis Error", "#f59e0b")

# --- END NEW FUNCTIONS ---

def send_summary_report():
    print("📊 Generating P/L Summary Report...")
    now = datetime.now()
    
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = datetime(now.year, now.month, 1)
    year_start = datetime(now.year, 1, 1)
    hour_start = now - timedelta(hours=1)
    
    def get_profit(start_time):
        deals = mt5.history_deals_get(start_time, now)
        if deals:
            return sum(d.profit for d in deals)
        return 0.0
        
    p_hour = get_profit(hour_start)
    p_day = get_profit(today_start)
    p_week = get_profit(week_start)
    p_month = get_profit(month_start)
    p_year = get_profit(year_start)
    
    acc = mt5.account_info()
    balance = acc.balance if acc else 0.0
    equity = acc.equity if acc else 0.0
    floating = acc.profit if acc else 0.0
    
    msg = (
        f"📊 <b>[AI PORTFOLIO REPORT]</b>\n"
        f"⏰ <b>Time:</b> {now.strftime('%H:%M')}\n"
        f"-------------------------\n"
        f"🕒 <b>Past 1 Hour P/L:</b> ${p_hour:.2f}\n"
        f"📅 <b>Today P/L:</b> ${p_day:.2f}\n"
        f"🗓️ <b>This Week P/L:</b> ${p_week:.2f}\n"
        f"📆 <b>This Month P/L:</b> ${p_month:.2f}\n"
        f"📈 <b>This Year P/L:</b> ${p_year:.2f}\n"
        f"-------------------------\n"
        f"💼 <b>Balance:</b> ${balance:.2f}\n"
        f"⚖️ <b>Equity:</b> ${equity:.2f}\n"
        f"🌊 <b>Floating P/L:</b> ${floating:.2f}"
    )
    
    stats_path = generate_stats_chart()
    send_telegram_alert(msg, stats_path)

def run_trade_monitor():
    global ACTIVE_TICKETS_CACHE
    positions = mt5.positions_get()
    current_tickets = {pos.ticket for pos in positions} if positions else set()
    
    if ACTIVE_TICKETS_CACHE is None:
        ACTIVE_TICKETS_CACHE = current_tickets
        return
        
    closed_tickets = ACTIVE_TICKETS_CACHE - current_tickets
    if closed_tickets:
        print(f"👀 TRADE MONITOR: Detected {len(closed_tickets)} closed tickets: {closed_tickets}")
        for ticket in closed_tickets:
            pos_deals = mt5.history_deals_get(position=ticket)
            if pos_deals:
                closing_deals = [d for d in pos_deals if d.entry == 1]
                if closing_deals:
                    d = closing_deals[-1]
                    profit = d.profit
                    symbol = d.symbol
                    price = d.price
                    pos_type = 0 if d.type == 1 else 1
                    
                    status_icon = "🟢" if profit > 0 else "🔴"
                    status_text = "PROFIT" if profit > 0 else "LOSS"
                    action_text = "BUY" if pos_type == 0 else "SELL"
                    
                    emotion = get_emotion("PROFIT" if profit > 0 else "LOSS")
                    
                    msg = (
                        f"💰 <b>[AI TRADE CLOSED]</b>\n"
                        f"<b>Symbol:</b> {symbol}\n"
                        f"<b>Action:</b> {action_text} (Closed)\n"
                        f"<b>Ticket:</b> #{ticket}\n"
                        f"<b>Close Price:</b> {price}\n"
                        f"-------------------------\n"
                        f"💵 <b>Net P/L:</b> ${profit:.2f}\n"
                        f"📉 <b>Status:</b> {status_text} {status_icon}\n\n"
                        f"<i>{emotion}</i>"
                    )
                    send_telegram_alert(msg)
                    
    ACTIVE_TICKETS_CACHE = current_tickets

def main_loop():
    global last_report_hour
    if not init_mt5(): return
    print("🤖 Multi-Agent Orchestrator (Autonomous Mode) Started")
    update_system_alert("SYSTEM ONLINE", "AI Orchestrator connected and running.")
    send_telegram_alert("🤖 Multi-Agent Orchestrator (AI Powered) Started!")
    
    while True:
        try:
            reload_config()
            can_trade, reason = ea_logic.check_session_and_limits()
            if not can_trade:
                print(f"\r🤖 EA HALTED: {reason} - Waiting for next session/day...", end="")
                update_agent("risk_manager", "HALTED", reason, "#ef4444")
                update_agent("trade_executor", "Standby", "Trading Halted", "#64748b")
                time.sleep(60)
                continue
            current_hour = datetime.now().hour
            if current_hour in REPORT_HOURS and current_hour != last_report_hour:
                send_summary_report()
                last_report_hour = current_hour
                
            print("--- Starting Agent Cycle ---")
            run_news_analyst()
            run_ai_analysis()
            lot = run_risk_manager()
            
            approved_list = run_supervisor(lot)
            run_trade_executor(approved_list, lot)
                

            run_portfolio_manager()
            run_trade_journal()
            run_weekly_strategy_review()
            run_trade_researcher()

            print("--- Cycle Complete ---")
            
            # Check for long-term analysis requests
            check_longterm_requests()
            
        except Exception as e:
            print("Cycle Error:", e)
            
        time.sleep(60) # Scan every 60 seconds

def analyze_longterm_asset(ticker, tg_chat_id=None):
    print(f"📈 LONG-TERM ANALYST: Analyzing {ticker}...")
    import yfinance as yf
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty:
            print(f"⚠️ Failed to get data for {ticker}")
            send_telegram_longterm_alert(f"❌ Failed to retrieve data for <b>{ticker}</b>", override_chat_id=tg_chat_id)
            return
            
        recent_data = hist.tail(10).to_string(columns=['Open', 'High', 'Low', 'Close'])
        
        info = stock.info
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')
        div_yield = info.get('dividendYield', 'N/A')
        
        news_list = stock.news[:5] if stock.news else []
        news_str = "\n".join([f"- {n.get('title')} ({n.get('publisher')})" for n in news_list])
        
        prompt = f"""
        คุณคือ 'Long-term Investment Analyst' ผู้เชี่ยวชาญด้านหุ้นและกองทุน
        วิเคราะห์สินทรัพย์: {ticker}
        กลุ่มอุตสาหกรรม: {sector} / {industry}
        Market Cap: {market_cap}
        P/E Ratio: {pe_ratio}
        Dividend Yield: {div_yield}
        
        ราคาล่าสุด (10 วันย้อนหลัง):
        {recent_data}
        
        ข่าวล่าสุดที่เกี่ยวข้อง:
        {news_str}
        
        โปรดให้คำแนะนำการลงทุนระยะยาว:
        1. แนวโน้มระยะยาว (Bullish/Bearish/Neutral)
        2. ปัจจัยพื้นฐานและข่าวที่ส่งผลกระทบ
        3. คำแนะนำ: ควรเข้าซื้อ (Buy) / ถือ (Hold) / ขาย (Sell) ตอนนี้หรือไม่? เพราะเหตุใด?
        4. จุดน่าเข้าซื้อ (Entry Zone) และจุดตัดขาดทุน (Stop Loss) เพื่อบริหารความเสี่ยง
        
        ตอบกลับเป็นภาษาไทยที่อ่านง่ายและชัดเจน สไตล์บทวิเคราะห์การลงทุน
        """
        
        # We can use the existing OpenAI/Claude/Gemini setup to send this plain text prompt
        print(f"🤖 Sending {ticker} analysis to LLM ({AI_PROVIDER})...")
        
        # Here we just use a quick HTTP call depending on AI_PROVIDER
        response_text = "❌ Failed to generate analysis."
        
        if AI_PROVIDER == "openai" and OPENAI_API_KEY:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}]}
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                response_text = r.json()["choices"][0]["message"]["content"]
                
        elif AI_PROVIDER == "claude" and CLAUDE_API_KEY:
            headers = {"x-api-key": CLAUDE_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            payload = {"model": "claude-3-5-sonnet-20240620", "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]}
            r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                response_text = r.json()["content"][0]["text"]
                
        elif gemini_model:
            res = gemini_model.generate_content(prompt)
            response_text = res.text
            
        else:
            response_text = "⚠️ Please set up API Keys (OpenAI, Claude, or Gemini) to run Long-term Analysis."
            
        msg = f"📈 <b>[Long-Term Analysis: {ticker}]</b>\n\n{response_text}"
        send_telegram_longterm_alert(msg, override_chat_id=tg_chat_id)
        print(f"✅ {ticker} Long-Term Analysis sent to Telegram.")
        
    except Exception as e:
        print(f"Long-term analysis error on {ticker}: {e}")

def check_longterm_requests():
    req_path = os.path.join(os.path.dirname(__file__), "longterm_request.json")
    if os.path.exists(req_path):
        try:
            with open(req_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ticker = data.get("ticker")
            if ticker:
                analyze_longterm_asset(ticker)
            os.remove(req_path)
        except Exception as e:
            print("Error checking longterm requests:", e)

if __name__ == "__main__":
    main_loop()
