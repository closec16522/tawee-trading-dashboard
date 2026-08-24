import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),'''

replacement = '''        # --- 🚀 INSTITUTIONAL DYNAMIC LOT SIZING ---
        dynamic_lot = ea_logic.get_dynamic_lot_size(symbol, sl_dist)
        update_agent("trade_executor", "Calculating Position Size", f"{symbol} Risk 1% -> Lot: {dynamic_lot}")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(dynamic_lot),'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched run_trade_executor lot size successfully!")
else:
    print("Target not found.")
