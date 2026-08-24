import os
with open("mt5_backend/agent_orchestrator.py", "r", encoding="utf-8") as f:
    content = f.read()

telegram_logic = """
import requests
import threading

def close_all_positions():
    positions = mt5.positions_get()
    if positions is None or len(positions) == 0:
        return 0
    count = 0
    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick: continue
        action = mt5.TRADE_ACTION_DEAL
        if pos.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        request = {
            "action": action, "symbol": pos.symbol, "volume": pos.volume,
            "type": order_type, "position": pos.ticket, "price": price,
            "deviation": 20, "magic": 234000, "comment": "Panic Close",
            "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            count += 1
    return count

last_update_id = 0
def poll_telegram_commands():
    global last_update_id
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 10}
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("result", []):
                    last_update_id = item["update_id"]
                    msg = item.get("message", {}).get("text", "")
                    if msg and msg.strip().lower() == "/closeall":
                        print("🚨 PANIC CLOSE: Received /closeall from Telegram!")
                        count = close_all_positions()
                        send_telegram_alert(f"⚠️ คำสั่งฉุกเฉินรับทราบ: ปิดออเดอร์ทั้งหมดสำเร็จแล้วจำนวน {count} ออเดอร์")
        except Exception:
            pass
        time.sleep(2)

# Start telegram polling thread
tg_thread = threading.Thread(target=poll_telegram_commands, daemon=True)
tg_thread.start()

# --- Shared State ---
"""

content = content.replace("# --- Shared State ---", telegram_logic)

with open("mt5_backend/agent_orchestrator.py", "w", encoding="utf-8") as f:
    f.write(content)

print("orchestrator tg logic patched")