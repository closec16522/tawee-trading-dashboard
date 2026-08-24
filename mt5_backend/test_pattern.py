import asyncio
import MetaTrader5 as mt5
import pandas as pd
from pattern_detector import detect_chart_pattern

def test_pattern():
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return
        
    rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 0, 200)
    if rates is None or len(rates) == 0:
        rates = mt5.copy_rates_from_pos("XAUUSD-VIP", mt5.TIMEFRAME_H1, 0, 200)
        
    if rates is None:
        print("No rates")
        return
        
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
    name, points = detect_chart_pattern(df)
    print(f"Pattern: {name}")
    print(f"Points: {points}")
    
    # Try with different tolerances or windows
    name2, points2 = detect_chart_pattern(df, window=3, tolerance=0.01)
    print(f"Pattern (window=3, tol=0.01): {name2}")
    
test_pattern()
mt5.shutdown()
