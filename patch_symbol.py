import os

file_path = os.path.join('mt5_backend', 'mt5_gateway.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        return {"error": f"No data for {symbol}"}"""

new_code = """    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        # Fallback to VIP suffix if normal symbol fails
        rates = mt5.copy_rates_from_pos(f"{symbol}-VIP", tf, 0, count)
        if rates is None or len(rates) == 0:
            return {"error": f"No data for {symbol} or {symbol}-VIP"}
        symbol = f"{symbol}-VIP" # Use the valid symbol name"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched mt5_gateway.py for symbol fallback.")
else:
    print("Could not find the code block to patch in mt5_gateway.")
