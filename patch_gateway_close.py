import os
with open("mt5_backend/mt5_gateway.py", "r", encoding="utf-8") as f:
    content = f.read()

close_all_logic = """
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
"""

content = content.replace("@app.post(\"/api/agent_update\")", close_all_logic)

with open("mt5_backend/mt5_gateway.py", "w", encoding="utf-8") as f:
    f.write(content)

print("gateway closed logic patched")