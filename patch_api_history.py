import os

file_path = os.path.join('mt5_backend', 'mt5_gateway.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

endpoint_code = """
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
        return {"error": f"No data for {symbol}"}
    
    data = []
    for r in rates:
        data.append({
            "time": int(r['time']),
            "open": float(r['open']),
            "high": float(r['high']),
            "low": float(r['low']),
            "close": float(r['close'])
        })
    return {"symbol": symbol, "data": data}
"""

if "@app.get(\"/api/history\")" not in content:
    # insert before track_record
    content = content.replace('@app.get("/api/track_record")', endpoint_code + '\n@app.get("/api/track_record")')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added /api/history to mt5_gateway.py")
else:
    print("Endpoint already exists.")
