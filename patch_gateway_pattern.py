import os

file_path = os.path.join('mt5_backend', 'mt5_gateway.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I need to add import pandas as pd and import pattern_detector
if 'import pandas as pd' not in content:
    content = content.replace('import json\n', 'import json\nimport pandas as pd\nfrom .pattern_detector import detect_chart_pattern\n')

# And I need to update the api_history endpoint
old_history = """@app.get("/api/history")
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
    return {"symbol": symbol, "data": data}"""

new_history = """@app.get("/api/history")
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
        
    df = pd.DataFrame(data)
    pattern_name, pattern_points = detect_chart_pattern(df)
    
    return {
        "symbol": symbol, 
        "data": data,
        "pattern_name": pattern_name,
        "pattern_points": pattern_points
    }"""

if old_history in content:
    content = content.replace(old_history, new_history)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched mt5_gateway.py successfully.")
else:
    print("Could not find the exact old api_history block.")
