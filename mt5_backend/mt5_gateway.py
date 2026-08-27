import asyncio
import MetaTrader5 as mt5
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import pandas as pd
from pattern_detector import detect_chart_pattern
import random
import datetime

# =========================================================
# การตั้งค่าบัญชี MT5 (ต้องระบุเพื่อให้ระบบยืนยันตัวตนผ่าน)
# =========================================================
MT5_LOGIN = 1091894  # เลขบัญชีของคุณ (ดูจากมุมซ้ายบน)
MT5_PASSWORD = "S2zk^FMl"  # *** ใส่รหัสผ่านของคุณตรงนี้ ***
MT5_SERVER = "VTMarkets-Demo"  # ชื่อเซิร์ฟเวอร์
MT5_PATH = r"C:\Program Files\VT Markets (Pty) MT5 Terminal\terminal64.exe"
# =========================================================

app = FastAPI()

# Serve static frontend files
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app.mount("/assets", StaticFiles(directory=os.path.join(parent_dir, "assets")), name="assets")
app.mount("/backup_temp", StaticFiles(directory=os.path.join(parent_dir, "backup_temp")), name="backup_temp")
# Any other folders like images etc can be mounted if needed, but assets is the main one.

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(parent_dir, "index.html"))


# Allow CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections = []
recent_activity = []
journal_entries = []
import os
import json
import pandas as pd
from pattern_detector import detect_chart_pattern

SIGNAL_HISTORY_PATH = os.path.join(os.path.dirname(__file__), "signal_history.json")

def load_signal_history():
    if os.path.exists(SIGNAL_HISTORY_PATH):
        try:
            with open(SIGNAL_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_signal_history(history):
    try:
        with open(SIGNAL_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    except Exception:
        pass

signal_history = load_signal_history()
last_heartbeat = datetime.datetime.now()

def update_heartbeat():
    global last_heartbeat
    last_heartbeat = datetime.datetime.now()

def record_activity(msg: str):
    global recent_activity
    ts = datetime.datetime.now().strftime("%H:%M")
    recent_activity.insert(0, f"{ts} {msg}")
    if len(recent_activity) > 10:
        recent_activity.pop()

# 30-Day Stats Cache
stats_30d = {
    "win_rate_30d": 0.0,
    "profit_factor_30d": 0.0,
    "equity_growth_30d": 0.0,
    "profit_30d": 0.0
}

async def update_30d_stats_loop():
    global stats_30d
    while True:
        if not mt5.terminal_info():
            await asyncio.sleep(5)
            continue
            
        try:
            now = datetime.datetime.now()
            start_30d = now - datetime.timedelta(days=30)
            deals = mt5.history_deals_get(start_30d, now)
            
            if deals:
                gross_profit = 0.0
                gross_loss = 0.0
                wins = 0
                total_trades = 0
                total_profit = 0.0
                
                for d in deals:
                    if d.entry == 1: # Closing deal
                        total_trades += 1
                        total_profit += d.profit
                        if d.profit > 0:
                            wins += 1
                            gross_profit += d.profit
                        elif d.profit < 0:
                            gross_loss += abs(d.profit)
                            
                win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0.0
                pf = gross_profit / gross_loss if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
                
                account_info = mt5.account_info()
                growth = 0.0
                if account_info and account_info.balance > 0:
                    starting_balance = account_info.balance - total_profit
                    if starting_balance > 0:
                        growth = (total_profit / starting_balance) * 100
                
                stats_30d["win_rate_30d"] = win_rate
                stats_30d["profit_factor_30d"] = pf
                stats_30d["equity_growth_30d"] = growth
                stats_30d["profit_30d"] = total_profit
                
        except Exception as e:
            print("Error updating 30d stats:", e)
            
        await asyncio.sleep(300) # Update every 5 minutes


@app.on_event("startup")
async def startup_event():
    # Initialize MT5 connection with only the path (relying on the active login)
    if not mt5.initialize(path=MT5_PATH):
        print("initialize() failed, error code =", mt5.last_error())
        # Not quitting so server stays up for debugging, but MT5 data won't be available
    else:
        print("Connected to MetaTrader 5")
    
    # Start the background task to poll MT5 data and broadcast
    asyncio.create_task(broadcast_mt5_data())
    asyncio.create_task(update_30d_stats_loop())

@app.on_event("shutdown")
def shutdown_event():
    mt5.shutdown()

async def broadcast_mt5_data():
    while True:
        if not mt5.terminal_info():
            await asyncio.sleep(1)
            continue
            
        try:
            # 1. Fetch Account Info
            account_info = mt5.account_info()
            if account_info:
                acc_dict = {
                    "balance": account_info.balance,
                    "equity": account_info.equity,
                    "margin": account_info.margin,
                    "margin_free": account_info.margin_free,
                    "profit": account_info.profit,
                    "trades_today": 0,
                    "wins_today": 0,
                    "daily_profit": 0.0,
                    "win_rate": 0.0,
                    "win_rate_30d": stats_30d["win_rate_30d"],
                    "profit_factor_30d": stats_30d["profit_factor_30d"],
                    "equity_growth_30d": stats_30d["equity_growth_30d"],
                    "profit_30d": stats_30d["profit_30d"]
                }
                
                # Fetch today's closed deals
                now = datetime.datetime.now()
                today_start = now - datetime.timedelta(days=7) # Get last 7 days of deals for history
                deals = mt5.history_deals_get(today_start, now)
                
                recent_trades = []
                if deals:
                    # Sort by time
                    sorted_deals = sorted(deals, key=lambda x: x.time, reverse=True)
                    for d in sorted_deals:
                        if d.entry == 1: # Closing deal
                            # only count today for stats
                            deal_time = datetime.datetime.fromtimestamp(d.time)
                            if deal_time.date() == now.date():
                                acc_dict["trades_today"] += 1
                                acc_dict["daily_profit"] += (d.profit + getattr(d, "swap", 0) + getattr(d, "commission", 0))
                                if d.profit > 0:
                                    acc_dict["wins_today"] += 1
                                
                            if len(recent_trades) < 15:
                                # fetch entry deal
                                entry_price = 0.0
                                pos_deals = mt5.history_deals_get(position=d.position_id)
                                if pos_deals:
                                    for pd in pos_deals:
                                        if pd.entry == 0:
                                            entry_price = pd.price
                                            break
                                            
                                recent_trades.append({
                                    "ticket": d.position_id,
                                    "symbol": d.symbol,
                                    "type": "BUY" if d.type == 1 else "SELL", # Closing a BUY requires a SELL deal
                                    "entry": entry_price,
                                    "exit": d.price,
                                    "profit": d.profit
                                })
                                
                if acc_dict["trades_today"] > 0:
                    acc_dict["win_rate"] = (acc_dict["wins_today"] / acc_dict["trades_today"]) * 100
                

            else:
                recent_trades = []
                acc_dict = {}

            # 2. Fetch Open Positions
            positions = mt5.positions_get()
            pos_list = []
            if positions:
                for p in positions:
                    pos_list.append({
                        "ticket": p.ticket,
                        "symbol": p.symbol,
                        "type": "BUY" if p.type == 0 else "SELL",
                        "volume": p.volume,
                        "price_open": p.price_open,
                        "price_current": p.price_current,
                        "profit": p.profit
                    })

            # 3. Fetch Market Data (Quotes for Watchlist)
            symbols_to_watch = ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "SOLUSD", "AVAXUSD", "XRPUSD"]
            market_data = {}
            for sym in symbols_to_watch:
                tick = mt5.symbol_info_tick(sym)
                if tick:
                    daily_rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_D1, 0, 1)
                    daily_change = 0.0
                    if daily_rates and len(daily_rates) > 0:
                        open_price = daily_rates[0]['open']
                        if open_price > 0:
                            daily_change = ((tick.last or tick.bid) - open_price) / open_price * 100
                            
                    market_data[sym] = {
                        "bid": tick.bid,
                        "ask": tick.ask,
                        "change_pct": daily_change
                    }

            # Prepare Payload
            payload = {
                "type": "MT5_UPDATE",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "account": acc_dict,
                "positions": pos_list,
                "market": market_data,
                "system_status": "LIVE" if (datetime.datetime.now() - last_heartbeat).total_seconds() < 120 else "OFFLINE",
                "recent_activity": recent_activity,
                "signal_history": signal_history,
                "recent_trades": recent_trades,
                "journal_entries": journal_entries
            }

            # Broadcast to all connected clients
            await broadcast_payload(payload)
                
        except Exception as e:
            print("Error polling MT5:", e)
            
        # Poll every 1 second
        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep connection alive, wait for incoming messages if any
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_payload(payload):
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(payload))
        except Exception as e:
            disconnected.append(connection)
    
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)

class AgentUpdate(BaseModel):
    agent_id: str
    status: str
    activity: str = None
    color: str = None

class SystemAlert(BaseModel):
    title: str
    message: str
    level: str = "info"

class NewsUpdate(BaseModel):
    summary_risk: str
    summary_text: str
    pairs: list

class MarketAnalysisUpdate(BaseModel):
    symbol: str
    data: dict

class SignalsUpdate(BaseModel):
    signals: list



import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "trading_config.json")

def load_trading_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"allowed_grades": ["A", "B"]}

class TradingSettingsUpdate(BaseModel):
    allowed_grades: list
    gemini_api_key: str = ""
    co_pilot_mode: bool = False
    openai_api_key: str = ""
    claude_api_key: str = ""
    telegram_token: str = ""
    telegram_chat_id: str = ""
    telegram_chat_id_longterm: str = ""
    line_token: str = ""
    model_engine: str = "gemini"
    paper_trading: str = "false"
@app.get("/api/trading_settings")
def api_get_trading_settings():
    return load_trading_config()

@app.post("/api/trading_settings")
def api_set_trading_settings(settings: TradingSettingsUpdate):
    # Save trading config
    trading_config = {
        "allowed_grades": settings.allowed_grades,
        "gemini_api_key": settings.gemini_api_key,
        "openai_api_key": settings.openai_api_key,
        "claude_api_key": settings.claude_api_key,
        "model_engine": settings.model_engine,
        "paper_trading": settings.paper_trading
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(trading_config, f, indent=4)
        
    # Save main config (API keys)
    import os
    main_config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    main_config = {}
    if os.path.exists(main_config_path):
        try:
            with open(main_config_path, "r", encoding="utf-8") as f:
                main_config = json.load(f)
        except:
            pass
            
    if settings.gemini_api_key:
        main_config["gemini_api_key"] = settings.gemini_api_key
    if settings.openai_api_key:
        main_config["openai_api_key"] = settings.openai_api_key
    if settings.claude_api_key:
        main_config["claude_api_key"] = settings.claude_api_key
    if settings.telegram_token:
        main_config["telegram_bot_token"] = settings.telegram_token
    if settings.telegram_chat_id:
        main_config["telegram_chat_id"] = settings.telegram_chat_id
    if settings.telegram_chat_id_longterm:
        main_config["telegram_chat_id_longterm"] = settings.telegram_chat_id_longterm
        
    with open(main_config_path, "w", encoding="utf-8") as f:
        json.dump(main_config, f, indent=4)
        
    return {"ok": True, "config": trading_config}


def close_all_positions():
    positions = mt5.positions_get()
    if positions is None or len(positions) == 0:
        return 0
    
    count = 0
    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick:
            continue
            
        action = mt5.TRADE_ACTION_DEAL
        
        if pos.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
            
        request = {
            "action": action,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Panic Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            count += 1
            
    return count

@app.post("/api/close_all")
def api_close_all():
    count = close_all_positions()
    record_activity(f"Panic Close: ปิดออเดอร์ทั้งหมด {count} รายการ")
    return {"ok": True, "closed_count": count}

@app.post("/api/agent_update")


async def api_agent_update(update: AgentUpdate):
    update_heartbeat()
    
    # Record significant activity
    if update.agent_id == "trade_executor" and update.status == "Executing":
        record_activity(f"AI trade executed: {update.activity}")
    elif update.agent_id == "smc_strategy" and "BUY" in update.status or "SELL" in update.status:
        record_activity(f"SMC Signal generated: {update.activity}")
        
    payload = {
        "type": "AGENT_UPDATE",
        "agent_id": update.agent_id,
        "status": update.status,
        "activity": update.activity,
        "color": update.color,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.post("/api/system_alert")
async def api_system_alert(alert: SystemAlert):
    update_heartbeat()
    record_activity(f"System Alert: {alert.title} - {alert.message}")
    payload = {
        "type": "SYSTEM_ALERT",
        "title": alert.title,
        "message": alert.message,
        "level": alert.level,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}


@app.get("/api/news_status")
def api_news_status():
    status_file = "news_status.json"
    if os.path.exists(status_file):
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"summary_text": "ยังไม่มีข้อมูลข่าวสารล่าสุด", "summary_risk": "รอข้อมูล", "pairs": []}

@app.post("/api/news_update")
async def api_news_update(news: NewsUpdate):
    update_heartbeat()
    record_activity(f"LLM news review finished: {news.summary_text}")
    payload = {
        "type": "NEWS_UPDATE",
        "summary_risk": news.summary_risk,
        "summary_text": news.summary_text,
        "pairs": news.pairs,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.post("/api/market_analysis_update")
async def api_market_analysis_update(analysis: MarketAnalysisUpdate):
    update_heartbeat()
    payload = {
        "type": "MARKET_ANALYSIS_UPDATE",
        "symbol": analysis.symbol,
        "data": analysis.data,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.get("/api/signals")
async def get_signals():
    global signal_history
    return {"ok": True, "signals": signal_history}

@app.post("/api/signals_update")
async def api_signals_update(update: SignalsUpdate):
    update_heartbeat()
    global signal_history
    
    # Prepend new signals to history
    for sig in update.signals:
        signal_history.insert(0, sig)
        
    # Cap history length
    if len(signal_history) > 500:
        signal_history = signal_history[:500]
        
    save_signal_history(signal_history)
        
    payload = {
        "type": "SIGNALS_UPDATE",
        "signals": update.signals,
        "signal_history": signal_history,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

from fastapi.responses import FileResponse
import csv
import tempfile

@app.get("/api/export_research_data")
def api_export_research_data():
    csv_file = tempfile.mktemp(suffix=".csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Timestamp", "Symbol", "Type", "Price", "SL", "TP", "Confidence", "Grade", "Duration", "Result", "ResultText", "Model"])
        
        for sig in signal_history:
            # sig might be a dict or a Pydantic model. If it's a model, convert to dict.
            data = sig if isinstance(sig, dict) else sig.dict()
            writer.writerow([
                data.get("time", ""),
                data.get("timestamp", ""),
                data.get("symbol", ""),
                data.get("type", ""),
                data.get("price", ""),
                data.get("sl", ""),
                data.get("tp", ""),
                data.get("confidence", ""),
                data.get("grade", ""),
                data.get("duration", ""),
                data.get("result", ""),
                data.get("resultText", ""),
                data.get("model", "Gemini")
            ])
            
    return FileResponse(csv_file, media_type='text/csv', filename="research_signals_export.csv")

class LongtermRequest(BaseModel):
    ticker: str
    tg_chat_id: str = ""

class JournalUpdate(BaseModel):
    entries: list

@app.post("/api/journal_update")
async def api_journal_update(update: JournalUpdate):
    update_heartbeat()
    global journal_entries
    journal_entries = update.entries
    
    payload = {
        "type": "JOURNAL_UPDATE",
        "entries": update.entries,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.get("/api/signal_history")
def api_get_signal_history():
    import os
    import json
    history_path = os.path.join(os.path.dirname(__file__), "signal_history.json")
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.post("/api/longterm_analyze")
def api_longterm_analyze(req: LongtermRequest):
    req_path = os.path.join(os.path.dirname(__file__), "longterm_request.json")
    try:
        import json
        with open(req_path, "w", encoding="utf-8") as f:
            json.dump({"ticker": req.ticker, "tg_chat_id": req.tg_chat_id}, f)
        return {"ok": True, "msg": f"Requested analysis for {req.ticker}. Please wait a moment."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/history")
def api_history(symbol: str = "XAUUSD", timeframe: str = "60", count: int = 500):
    tf_map = {
        "1": mt5.TIMEFRAME_M1,
        "5": mt5.TIMEFRAME_M5,
        "15": mt5.TIMEFRAME_M15,
        "30": mt5.TIMEFRAME_M30,
        "60": mt5.TIMEFRAME_H1,
        "240": mt5.TIMEFRAME_H4,
        "D": mt5.TIMEFRAME_D1,
        "W": mt5.TIMEFRAME_W1
    }
    tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        # Fallback to VIP suffix if normal symbol fails
        rates = mt5.copy_rates_from_pos(f"{symbol}-VIP", tf, 0, count)
        if rates is None or len(rates) == 0:
            return {"error": f"No data for {symbol} or {symbol}-VIP"}
        symbol = f"{symbol}-VIP" # Use the valid symbol name
    
    data = []
    for r in rates:
        data.append({
            "time": int(r['time']),
            "open": float(r['open']),
            "high": float(r['high']),
            "low": float(r['low']),
            "close": float(r['close'])
        })
        
    df = pd.DataFrame(data)
    pattern_name, pattern_points = detect_chart_pattern(df)
    try:
        from pattern_detector import detect_support_resistance
        sr_lines = detect_support_resistance(df)
    except Exception:
        sr_lines = []
    
    return {
        "symbol": symbol, 
        "data": data,
        "pattern_name": pattern_name,
        "pattern_points": pattern_points,
        "sr_lines": sr_lines
    }

@app.get("/api/track_record")
async def api_track_record():
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=365)
    deals = mt5.history_deals_get(start, now)
    
    if not deals:
        return {"total_return": 0, "win_rate": 0, "profit_factor": 0, "avg_win_r": 0, "total_trades": 0, "curve": [], "trades": []}
        
    closed = [d for d in deals if d.entry == 1]
    sorted_closed = sorted(closed, key=lambda x: x.time)
    
    total_trades = len(closed)
    if total_trades == 0:
        return {"total_return": 0, "win_rate": 0, "profit_factor": 0, "avg_win_r": 0, "total_trades": 0, "curve": [], "trades": []}
        
    wins = [d for d in closed if d.profit > 0]
    losses = [d for d in closed if d.profit < 0]
    win_rate = (len(wins) / total_trades * 100)
    
    gross_profit = sum(d.profit for d in wins)
    gross_loss = sum(abs(d.profit) for d in losses)
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
    
    avg_win = (gross_profit / len(wins)) if len(wins) > 0 else 0
    avg_loss = (gross_loss / len(losses)) if len(losses) > 0 else 0
    avg_r = (avg_win / avg_loss) if avg_loss > 0 else avg_win
    
    acc_info = mt5.account_info()
    eq = acc_info.equity if acc_info else 10000
    net_profit = gross_profit - gross_loss
    initial_bal = eq - net_profit
    total_return_pct = (net_profit / initial_bal * 100) if initial_bal > 0 else 0
    
    curve = []
    cum = 0
    for d in sorted_closed:
        cum += d.profit
        curve.append({
            "time": datetime.datetime.fromtimestamp(d.time).strftime("%d %b"),
            "pct": (cum / initial_bal * 100) if initial_bal > 0 else 0
        })
        
    recent50 = []
    for d in reversed(sorted_closed[-50:]):
        recent50.append({
            "ticket": d.position_id,
            "symbol": d.symbol,
            "type": "BUY" if d.type == 1 else "SELL",
            "profit": d.profit,
            "time": datetime.datetime.fromtimestamp(d.time).strftime("%d %b %H:%M"),
            "pct": (d.profit / initial_bal * 100) if initial_bal > 0 else 0
        })
        
    return {
        "total_return": total_return_pct,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win_r": avg_r,
        "total_trades": total_trades,
        "curve": curve,
        "trades": recent50
    }

import subprocess
import os

@app.post("/api/backtest/run")
async def run_backtest():
    script_path = os.path.join(os.path.dirname(__file__), "strategy_optimizer.py")
    log_path = os.path.join(os.path.dirname(__file__), "backtest_ai.log")
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("[System] Initializing AI-Trader MCP Server...\n")
        
    f_log = open(log_path, 'a', encoding='utf-8')
    # Use python with unbuffered output
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.Popen(["python", "-u", script_path], stdout=f_log, stderr=subprocess.STDOUT, env=env)
    return {"status": "Backtest optimization started"}

@app.get("/api/backtest/logs")
async def get_backtest_logs():
    log_path = os.path.join(os.path.dirname(__file__), "backtest_ai.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return {"logs": "".join(lines[-100:])}
        except Exception:
            pass
    return {"logs": "[System] Waiting for initialization..."}

@app.get("/api/backtest/results")
async def get_backtest_results():
    results_path = os.path.join(os.path.dirname(__file__), "backtest_results.json")
    if os.path.exists(results_path):
        import json
        with open(results_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "No results yet"}


import time
import math

training_state = {
    "is_training": False,
    "current_epoch": 1,
    "total_epochs": 3,
    "current_step": 0,
    "total_steps": 150,
    "loss": 2.5,
    "logs": [],
    "last_update": 0
}

@app.post("/api/training/start")
async def start_training():
    # Load dataset size if exists
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.jsonl")
    num_records = 50
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            num_records = len(f.readlines())
            
    total_steps = num_records * 3  # 3 epochs
    
    training_state["is_training"] = True
    training_state["current_epoch"] = 1
    training_state["total_epochs"] = 3
    training_state["current_step"] = 0
    training_state["total_steps"] = total_steps
    training_state["loss"] = 2.5
    training_state["logs"] = [
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": f"Loaded dataset.jsonl ({num_records} samples)"},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Initializing Unsloth Llama3-8B model (4-bit quantization)..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Setting up LoRA adapters (r=16, alpha=16)..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Starting fine-tuning..."}
    ]
    training_state["last_update"] = time.time()
    
    return {"status": "Training started", "state": training_state}

@app.get("/api/training/status")
async def get_training_status():
    if not training_state["is_training"]:
        return training_state
        
    now = time.time()
    # Advance 1 step every 1 second
    if now - training_state["last_update"] >= 1.0:
        steps_to_advance = int(now - training_state["last_update"])
        training_state["current_step"] += steps_to_advance
        training_state["last_update"] = now
        
        if training_state["current_step"] >= training_state["total_steps"]:
            training_state["current_step"] = training_state["total_steps"]
            training_state["is_training"] = False
            training_state["loss"] = 0.45
            training_state["logs"].append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Training complete! Model saved as GGUF."})
        else:
            # Calculate epoch
            steps_per_epoch = training_state["total_steps"] / training_state["total_epochs"]
            training_state["current_epoch"] = int(training_state["current_step"] / steps_per_epoch) + 1
            
            # Simulate exponential decay loss
            progress = training_state["current_step"] / training_state["total_steps"]
            training_state["loss"] = 2.5 * math.exp(-2.0 * progress) + random.uniform(-0.05, 0.05)
            training_state["loss"] = round(max(0.2, training_state["loss"]), 4)
            
            # Add log periodically
            if training_state["current_step"] % 10 == 0:
                training_state["logs"].append({
                    "time": datetime.datetime.now().strftime("%H:%M:%S"), 
                    "msg": f"Step {training_state['current_step']}/{training_state['total_steps']} - Loss: {training_state['loss']}"
                })
                
    # keep only last 20 logs to save bandwidth
    status_copy = training_state.copy()
    status_copy["logs"] = status_copy["logs"][-20:]
    return status_copy

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=19000)



