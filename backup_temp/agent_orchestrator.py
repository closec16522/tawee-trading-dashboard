import time
import requests
import json
import os
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import google.generativeai as genai
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf
import random

# Configuration
TELEGRAM_TOKEN = "8899582441:AAFVy4Ab23ilqcO1BBue5zo18RbmmJAVAAI"
CHAT_ID = "1828172350"
GATEWAY_URL = "http://127.0.0.1:19000"

# Load settings from config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
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

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    gemini_model = None
    if AI_PROVIDER == "gemini":
        print("⚠️ WARNING: Gemini API Key not set in config.json. AI will not function properly.")

# Global State
news_impact = "low"
current_trends = {}
approved_trades = {}
last_report_hour = -1
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

def send_telegram_alert(msg, image_path=None):
    try:
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            with open(image_path, 'rb') as photo:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML"}, files={"photo": photo}, timeout=10, proxies=LOCAL_PROXIES)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Telegram Error:", e)

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

def update_agent(agent_id, status, activity=None, color=None):
    try:
        payload = {"agent_id": agent_id, "status": status}
        if activity: payload["activity"] = activity
        if color: payload["color"] = color
        r = requests.post(f"{GATEWAY_URL}/api/agent_update", json=payload, timeout=2, proxies=LOCAL_PROXIES)
        if r.status_code != 200:
            print(f"⚠️ Gateway Error: {r.status_code}. (Did you restart start_gateway.bat?)")
    except Exception as e:
        print("⚠️ Gateway update failed (Is the Gateway running?):", e)

def update_system_alert(title, message, level="info"):
    try:
        r = requests.post(f"{GATEWAY_URL}/api/system_alert", json={"title": title, "message": message, "level": level}, timeout=2, proxies=LOCAL_PROXIES)
        if r.status_code != 200:
            print(f"⚠️ Gateway Error: {r.status_code}. (Did you restart start_gateway.bat?)")
    except:
        pass

def update_market_analysis(symbol, data):
    try:
        payload = {"symbol": symbol, "data": data}
        r = requests.post(f"{GATEWAY_URL}/api/market_analysis_update", json=payload, timeout=2, proxies=LOCAL_PROXIES)
    except:
        pass

def update_signals(signals):
    try:
        payload = {"signals": signals}
        r = requests.post(f"{GATEWAY_URL}/api/signals_update", json=payload, timeout=2, proxies=LOCAL_PROXIES)
    except:
        pass

def init_mt5():
    if not mt5.initialize():
        print("MT5 Init Failed")
        return False
    return True

def generate_trade_chart(symbol, decision, entry, sl, tp):
    try:
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 50)
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
def run_news_analyst():
    global news_impact, last_news_fetch_time, cached_news_impact
    print("📰 NEWS ANALYST: Checking ForexFactory Calendar...")
    update_agent("news_analyst", "Checking News")
    time.sleep(2)
    
    current_time = time.time()
    try:
        # Update every 4 hours (14400 seconds)
        if current_time - last_news_fetch_time > 14400 or last_news_fetch_time == 0:
            try:
                r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=5, headers={"User-Agent": "Mozilla/5.0"}, proxies=LOCAL_PROXIES)
                if r.status_code == 200:
                    root = ET.fromstring(r.content)
                    high_impact_usd = False
                    today = datetime.now().strftime("%m-%d-%Y")
                    
                    for event in root.findall("event"):
                        date = event.find("date").text
                        currency = event.find("country").text
                        impact = event.find("impact").text
                        if date == today and currency == "USD" and impact == "High":
                            high_impact_usd = True
                            break
                    cached_news_impact = high_impact_usd
                    last_news_fetch_time = current_time
                elif r.status_code == 429:
                    print("📰 NEWS ANALYST: API Rate Limited (429). Using cached/default data.")
                else:
                    print(f"📰 NEWS ANALYST: API Error {r.status_code}")
            except Exception as req_e:
                print("📰 NEWS ANALYST: Network/API Exception:", req_e)
                # Keep cached_news_impact as is, or default False
        
        if cached_news_impact:
            news_impact = "high"
            activity = "High Impact USD News Detected!"
            color = "#ef4444"
            print("📰 NEWS ANALYST: 🚨 High Impact USD News Detected!")
            news_payload = {
                "summary_risk": "เสี่ยงสูง",
                "summary_text": "ตลาดแกว่งตัวผันผวนรุนแรง ตรวจพบข่าวสำคัญที่มีผลกระทบสูงต่อ USD (High Impact USD News) แนะนำให้เพิ่มความระมัดระวังในการเทรดคู่เงินหลัก",
                "pairs": [
                    {"symbol": "XAUUSD", "impact": "ผันผวนสูง", "text": "ราคาทองคำมักจะตอบสนองรุนแรงต่อข่าว USD อาจเห็นการแกว่งตัวในกรอบกว้าง", "color": "#f59e0b"},
                    {"symbol": "EURUSD", "impact": "ผันผวนสูง", "text": "เฝ้าระวังแรงเทขายหรือแรงซื้อฉับพลันจากตัวเลขเศรษฐกิจ USD", "color": "#f59e0b"},
                    {"symbol": "GBPUSD", "impact": "ผันผวนสูง", "text": "คาดการณ์การแกว่งตัวรุนแรงตามดัชนีดอลลาร์", "color": "#f59e0b"},
                    {"symbol": "BTCUSD", "impact": "เอนขาขึ้น", "text": "ตลาดคริปโตอาจได้รับผลกระทบทางอ้อม หาก USD อ่อนค่า", "color": "#10b981"},
                    {"symbol": "ETHUSD", "impact": "เอนขาขึ้น", "text": "ทิศทางสอดคล้องกับภาพรวมของตลาดคริปโตที่รับแรงหนุนจากสภาพคล่อง", "color": "#10b981"}
                ]
            }
        else:
            news_impact = "low"
            activity = "No High Impact USD News"
            color = "#37d27a"
            print("📰 NEWS ANALYST: ✅ No High Impact USD News.")
            news_payload = {
                "summary_risk": "เสี่ยงต่ำ",
                "summary_text": "สภาวะตลาดโดยรวมปกติ ไม่มีข่าวสำคัญที่มีผลกระทบสูงต่อ USD ในวันนี้ ตลาดมีแนวโน้มเคลื่อนไหวตามกรอบเทคนิคอล",
                "pairs": [
                    {"symbol": "XAUUSD", "impact": "เอนขาขึ้น", "text": "แรงหนุนจากกรอบโครงสร้างราคาเดิม ไร้ปัจจัยข่าวกดดัน", "color": "#10b981"},
                    {"symbol": "EURUSD", "impact": "ทรงตัว", "text": "เคลื่อนไหวในกรอบสะสมพลัง รอจังหวะการเลือกทาง", "color": "#f59e0b"},
                    {"symbol": "GBPUSD", "impact": "เอนขาลง", "text": "โมเมนตัมฝั่งขายยังคุมตลาดตามโครงสร้างรอง", "color": "#ef4444"},
                    {"symbol": "BTCUSD", "impact": "เอนขาขึ้น", "text": "รักษาระดับเหนือแนวรับสำคัญได้ดี มีลุ้นทดสอบแนวต้าน", "color": "#10b981"},
                    {"symbol": "ETHUSD", "impact": "เอนขาขึ้น", "text": "แกว่งตัวสอดคล้องกับ BTC ในโซนบวก", "color": "#10b981"}
                ]
            }
            
        update_agent("news_analyst", "Standby", activity, color)
        try:
            requests.post(f"{GATEWAY_URL}/api/news_update", json=news_payload, timeout=2, proxies=LOCAL_PROXIES)
        except Exception as e:
            pass
            
    except Exception as e:
        print("📰 NEWS ANALYST: General Exception occurred:", e)
        update_agent("news_analyst", "Standby", "News check failed", "#f59e0b")

# 2. Market Analyst & SMC Strategist (AI Powered)
def analyze_market_with_ai(symbol, df):
    if not gemini_model:
        return None

    # Convert OHLC data to a string summary
    recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close'])
    
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
            "setup": "อธิบายจุดเข้าเทรด SMC (เช่น ราคาชน OB, ปิด FVG) 1-2 ประโยคแบบมืออาชีพ",
            "decision": "BUY / SELL / HOLD"
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
        print(f"⚠️ Gemini API Error on {symbol}:", e)
        return None

def analyze_market_with_local_ai(symbol, df):
    # Convert OHLC data to a string summary
    recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close'])
    
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
            "setup": "อธิบายจุดเข้าเทรด SMC (เช่น ราคาชน OB, ปิด FVG) 1-2 ประโยคแบบมืออาชีพ",
            "decision": "BUY / SELL / HOLD"
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

def run_ai_analysis():
    global current_trends, approved_trades
    update_agent("market_analyst", "Analysing", "Starting Market Analysis...", "#3b82f6")
    update_agent("smc_strategy", "Standby", "Waiting for Market Data...", "#64748b")
    
    print("🤖 AI TEAM: Scanning MT5 Quotes for multiple symbols...")
    time.sleep(1)
    
    approved_trades.clear()
    
    for symbol in SYMBOLS:
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 50)
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            print(f"📊 {symbol}: AI Team is processing...")
            update_agent("market_analyst", "Analysing", f"Scanning {symbol} Structure...", "#3b82f6")
            
            if AI_PROVIDER == "local":
                result = analyze_market_with_local_ai(symbol, df)
                model_used = f"Local {LOCAL_AI_MODEL.capitalize()}"
            else:
                result = analyze_market_with_ai(symbol, df)
                model_used = "Google Gemini-2.5-Pro"
            
            if result:
                ma_data = result.get("market_analyst", {})
                smc_data = result.get("smc_strategist", {})
                
                # Broadcase Market Analyst Data
                update_market_analysis(symbol, ma_data)
                
                trend = ma_data.get("trend", "Unknown")
                ma_analysis = ma_data.get("analysis", "")
                decision = str(smc_data.get("decision", "HOLD")).strip().upper()
                smc_setup = smc_data.get("setup", "")
                
                # Update global trend for Portfolio Manager
                if decision in ["BUY", "SELL"]:
                    current_trends[symbol] = decision
                
                
                print(f"📈 MARKET ANALYST [{symbol}]: Trend={trend} -> {ma_analysis}")
                update_agent("market_analyst", "Analyzed", f"[{symbol}] {trend}", "#8b5cf6")
                time.sleep(1) # Simulate handoff
                
                print(f"🧠 SMC STRATEGIST [{symbol}]: {decision} -> {smc_setup}")
                color = "#37d27a" if decision == "BUY" else ("#ef4444" if decision == "SELL" else "#f59e0b")
                update_agent("smc_strategy", f"Building Setup", f"Evaluating {symbol}...", "#3b82f6")
                time.sleep(1)
                update_agent("smc_strategy", f"[{symbol}] {decision}", smc_setup, color)
                
                if decision in ["BUY", "SELL"]:
                    approved_trades[symbol] = {
                        "decision": decision,
                        "analysis": ma_analysis,
                        "setup": smc_setup,
                        "model": model_used
                    }
            else:
                print(f"⚠️ {symbol}: Analysis failed (HOLD).")
                
        else:
            print(f"📊 MARKET ANALYST: Failed to get rates for {symbol}")
            
        print("⏳ Waiting 5 seconds to avoid Gemini API Rate Limits...")
        time.sleep(5)
            
    if not approved_trades:
        update_agent("market_analyst", "Standby", "Market scan complete", "#64748b")
        update_agent("smc_strategy", "Standby", "No Trade Setup Found", "#64748b")
    else:
        update_agent("market_analyst", "Standby", f"Analyzed {len(SYMBOLS)} symbols", "#37d27a")
        update_agent("smc_strategy", "Found Setups", f"Found {len(approved_trades)} SMC Setups", "#37d27a")

# 4. Risk Manager
def run_risk_manager():
    print("🛡️ RISK MANAGER: Calculating Dynamic Lot Size...")
    update_agent("risk_manager", "Calculating Risk")
    time.sleep(1)
    
    acc_info = mt5.account_info()
    if acc_info:
        balance = acc_info.balance
        calculated_lot = round(max(0.01, (balance / 1000) * 0.01), 2)
        calculated_lot = min(calculated_lot, 1.00)
        print(f"🛡️ RISK MANAGER: Balance=${balance:.2f} -> Lot={calculated_lot}")
        update_agent("risk_manager", "Risk Calculated", f"Risk 1% -> Lot: {calculated_lot}", "#f59e0b")
        return calculated_lot
    else:
        update_agent("risk_manager", "Standby")
        return 0.01

# 5. Supervisor AI
def run_supervisor(lot_size):
    global approved_trades
    print("👑 SUPERVISOR AI: Reviewing Trade Proposals...")
    update_agent("supervisor", "Reviewing")
    time.sleep(1)
    
    if not approved_trades:
        print("👑 SUPERVISOR AI: Standby (No trades)")
        update_agent("supervisor", "Standby")
        update_signals([])
        return []
        
    if news_impact == "high":
        print("👑 SUPERVISOR AI: REJECTED ALL! Blocked due to High Impact News.")
        update_agent("supervisor", "Rejected", "REJECTED: High Impact News", "#ef4444")
        update_system_alert("TRADE REJECTED", "Supervisor blocked trades due to news volatility.", "warn")
        approved_trades.clear()
        update_signals([])
        return []
        
    print(f"👑 SUPERVISOR AI: APPROVED {len(approved_trades)} trades.")
    update_agent("supervisor", "Approved", f"APPROVED {len(approved_trades)} Trades", "#37d27a")
    
    # Format and broadcast signals to the frontend
    signals_list = []
    for sym, trade_data in approved_trades.items():
        decision = trade_data["decision"]
        tick = mt5.symbol_info_tick(sym)
        price = tick.ask if decision == "BUY" else tick.bid if tick else 0
        signals_list.append({
            "symbol": sym,
            "type": decision,
            "price": price,
            "confidence": 85 # Mock confidence or extract from analysis
        })
    update_signals(signals_list)
    
    return list(approved_trades.items())

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
        
        # SL 50 pips, TP 100 pips (assuming standard broker, 1 pip = 10 points)
        sl_points = 500 * point
        tp_points = 1000 * point
        
        if trade_type == "BUY":
            sl = price - sl_points
            tp = price + tp_points
        else:
            sl = price + sl_points
            tp = price - tp_points
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),
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
        
        result = mt5.order_send(request)
        if result and result.retcode != mt5.TRADE_RETCODE_DONE:
            request["type_filling"] = mt5.ORDER_FILLING_FOK
            result = mt5.order_send(request)
            
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"⚡ TRADE EXECUTOR: Order SUCCESS (Ticket: {result.order})")
            chart_path = generate_trade_chart(symbol, trade_type, price, sl, tp)
            
            action_icon = "🔵" if trade_type == "BUY" else "🔴"
            emotion = get_emotion("OPEN")
            
            msg = (
                f"🤖 <b>[AI AUTOTRADE SIGNAL]</b>\n\n"
                f"<b>Action:</b> {trade_type} {action_icon}\n"
                f"<b>Symbol:</b> {symbol}\n"
                f"<b>Volume:</b> {lot}\n"
                f"<b>Entry Price:</b> {price}\n"
                f"<b>Stop Loss (SL):</b> {sl}\n"
                f"<b>Take Profit (TP):</b> {tp}\n\n"
                f"🧠 <b>AI Analysis (Market Analyst):</b>\n{ma_analysis}\n\n"
                f"🎯 <b>AI Setup (SMC Strategist):</b>\n{smc_setup}\n\n"
                f"🤖 <b>Powered by:</b> {model_used}\n\n"
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

    if acc:
        color = "#ef4444" if acc.profit < 0 else "#37d27a"
        msg = f"Floating P/L: ${acc.profit:.2f}"
        if closed_count > 0:
            msg += f" (Closed {closed_count})"
        print(f"💼 PORTFOLIO MANAGER: Floating P/L = ${acc.profit:.2f}")
        update_agent("portfolio_manager", "Standby", msg, color)

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

def main_loop():
    global last_report_hour
    if not init_mt5(): return
    print("🤖 Multi-Agent Orchestrator (Autonomous Mode) Started")
    update_system_alert("SYSTEM ONLINE", "AI Orchestrator connected and running.")
    send_telegram_alert("🤖 Multi-Agent Orchestrator (AI Powered) Started!")
    
    while True:
        try:
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
            print("--- Cycle Complete ---")
        except Exception as e:
            print("Cycle Error:", e)
            
        time.sleep(60) # Scan every 60 seconds

if __name__ == "__main__":
    main_loop()
