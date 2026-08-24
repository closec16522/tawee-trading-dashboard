import time
import requests
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
import json

# --- LOCAL OLLAMA INTEGRATION ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1"



TELEGRAM_TOKEN = "8899582441:AAFVy4Ab23ilqcO1BBue5zo18RbmmJAVAAI"
CHAT_ID = "1828172350"

def send_telegram_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# ==========================================
# BASIC AI TRADER - SMA CROSSOVER STRATEGY
# ==========================================

SYMBOL = "XAUUSD-VIP"
LOT = 0.01
TIMEFRAME = mt5.TIMEFRAME_M1
FAST_SMA = 5
SLOW_SMA = 15

def initialize_mt5():
    print("Initializing MetaTrader 5...")
    # Relying on active terminal login, so no credentials provided
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return False
    print("Connected to MT5!")
    return True

def get_data(symbol, timeframe, n_candles):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_candles)
    if rates is None:
        print(f"Failed to get data for {symbol}")
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def send_order(symbol, lot, order_type, news_reason_global="N/A"):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"{symbol} not found.")
        return False

    if not symbol_info.visible:
        print(f"{symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print(f"symbol_select({symbol}) failed")
            return False

    point = symbol_info.point
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    
    # Calculate SL and TP (e.g., 50 pips)
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "AI Bot Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed, retcode={result.retcode}")
        # Sometimes filling mode IOC fails, try FOK or RETURN
        request["type_filling"] = mt5.ORDER_FILLING_FOK
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed again, retcode={result.retcode}")
            return False
    
    action_str = 'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL'
    print(f"Trade Success: {action_str} {symbol} at {price}")
    send_telegram_alert(f"✅ AI Trade Executed!\n\nAction: {action_str}\nSymbol: {symbol}\nVolume: {lot}\nPrice: {price}\n\n📰 News Analysis: {news_reason_global}")
    return True

def run_bot():
    if not initialize_mt5():
        return

    print(f"--- AI Trader Started on {SYMBOL} ---")
    print("Strategy: SMA Crossover (Fast: 5, Slow: 15) on M1 timeframe")
    send_telegram_alert(f"🤖 AI Trader Bot Started!\n\nSymbol: {SYMBOL}\nStrategy: SMA Crossover\nStatus: Monitoring...")
    
    last_signal = None

    while True:
        df = get_data(SYMBOL, TIMEFRAME, 30)
        if df is not None:
            # --- WORLD MONITOR SENTIMENT CHECK ---
            sentiment_bullish = False
            sentiment_bearish = False
            
            news_reason = "No News Data"
            sentiment_bullish = False
            sentiment_bearish = False
            
            try:
                # Fetch ForexFactory High Impact News for USD
                r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                news_titles = []
                if r.status_code == 200:
                    root = ET.fromstring(r.content)
                    today = datetime.now().strftime("%m-%d-%Y")
                    for event in root.findall("event"):
                        if event.find("date").text == today and event.find("impact").text == "High":
                            news_titles.append(event.find("title").text)
                
                if news_titles:
                    news_text = ", ".join(news_titles)
                    print(f"[{current_time}] High Impact News Today: {news_text}")
                    # Send to Ollama
                    prompt = f"Analyze the following economic news for the US Dollar: {news_text}. Does this indicate a BULLISH or BEARISH sentiment for the USD? Reply with ONLY the word BULLISH or BEARISH."
                    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
                    ollama_res = requests.post(OLLAMA_URL, json=payload, timeout=10)
                    if ollama_res.status_code == 200:
                        ans = ollama_res.json().get("response", "").strip().upper()
                        print(f"[{current_time}] Llama-3.1 Sentiment Analysis: {ans}")
                        
                        if "BEARISH" in ans:
                            sentiment_bearish = True
                            news_reason = f"Llama-3.1 Analysis: Bearish News -> {news_text}"
                        elif "BULLISH" in ans:
                            sentiment_bullish = True
                            news_reason = f"Llama-3.1 Analysis: Bullish News -> {news_text}"
                        else:
                            news_reason = f"Llama-3.1 Analysis: Neutral -> {news_text}"
                else:
                    news_reason = "No High Impact News Today (Neutral)"
            except Exception as e:
                news_reason = f"Ollama / News API Error: {e}"
                pass

            # Calculate SMAs
            df['sma_fast'] = df['close'].rolling(window=FAST_SMA).mean()
            df['sma_slow'] = df['close'].rolling(window=SLOW_SMA).mean()
            
            # Get latest closed candle
            latest_fast = df['sma_fast'].iloc[-2]
            latest_slow = df['sma_slow'].iloc[-2]
            prev_fast = df['sma_fast'].iloc[-3]
            prev_slow = df['sma_slow'].iloc[-3]

            current_time = datetime.now().strftime("%H:%M:%S")

            # Check for crossover
            if prev_fast <= prev_slow and latest_fast > latest_slow:
                # Add sentiment confirmation if available
                if not sentiment_bearish:
                    print(f"[{current_time}] BUY Signal detected! Fast SMA crossed ABOVE Slow SMA.")
                    if last_signal != 'BUY':
                        send_order(SYMBOL, LOT, mt5.ORDER_TYPE_BUY, news_reason_global=news_reason)
                        last_signal = 'BUY'
                else:
                    print(f"[{current_time}] BUY Signal IGNORED due to Bearish Llama-3.1 Sentiment.")
                    send_telegram_alert(f"⚠️ AI Signal IGNORED\n\nSymbol: {SYMBOL}\nSetup: BUY (SMA Cross)\nReason: News is BEARISH (Llama-3.1)\nAnalysis: {news_reason}")
            elif prev_fast >= prev_slow and latest_fast < latest_slow:
                if not sentiment_bullish:
                    print(f"[{current_time}] SELL Signal detected! Fast SMA crossed BELOW Slow SMA.")
                    if last_signal != 'SELL':
                        send_order(SYMBOL, LOT, mt5.ORDER_TYPE_SELL, news_reason_global=news_reason)
                        last_signal = 'SELL'
                else:
                    print(f"[{current_time}] SELL Signal IGNORED due to Bullish Llama-3.1 Sentiment.")
                    send_telegram_alert(f"⚠️ AI Signal IGNORED\n\nSymbol: {SYMBOL}\nSetup: SELL (SMA Cross)\nReason: News is BULLISH (Llama-3.1)\nAnalysis: {news_reason}")
            else:
                print(f"[{current_time}] Monitoring {SYMBOL} (Price: {df['close'].iloc[-1]}) | Fast SMA: {latest_fast:.2f} | Slow SMA: {latest_slow:.2f}")

        # Wait for 10 seconds before next check
        time.sleep(10)

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        mt5.shutdown()
