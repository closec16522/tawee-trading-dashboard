import os
import re

file_path = os.path.join('mt5_backend', 'mt5_gateway.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """    df = pd.DataFrame(data)
    pattern_name, pattern_points = detect_chart_pattern(df)
    
    return {
        "symbol": symbol, 
        "data": data,
        "pattern_name": pattern_name,
        "pattern_points": pattern_points
    }"""

new_code = """    df = pd.DataFrame(data)
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
    }"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched mt5_gateway.py successfully.")
else:
    print("Could not find target code in mt5_gateway.py.")
