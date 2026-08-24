import asyncio
import MetaTrader5 as mt5
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
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

# Allow CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections = []

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
                    "profit": account_info.profit
                }
            else:
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
            symbols_to_watch = ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD"]
            market_data = {}
            for sym in symbols_to_watch:
                tick = mt5.symbol_info_tick(sym)
                if tick:
                    market_data[sym] = {
                        "bid": tick.bid,
                        "ask": tick.ask
                    }

            # Prepare Payload
            payload = {
                "type": "MT5_UPDATE",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "account": acc_dict,
                "positions": pos_list,
                "market": market_data
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


@app.post("/api/agent_update")
async def api_agent_update(update: AgentUpdate):
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
    payload = {
        "type": "SYSTEM_ALERT",
        "title": alert.title,
        "message": alert.message,
        "level": alert.level,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.post("/api/news_update")
async def api_news_update(news: NewsUpdate):
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
    payload = {
        "type": "MARKET_ANALYSIS_UPDATE",
        "symbol": analysis.symbol,
        "data": analysis.data,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.post("/api/signals_update")
async def api_signals_update(update: SignalsUpdate):
    payload = {
        "type": "SIGNALS_UPDATE",
        "signals": update.signals,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mt5_gateway:app", host="0.0.0.0", port=19000, reload=True)
