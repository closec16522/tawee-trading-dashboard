import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        # --- 🚀 INSTITUTIONAL DYNAMIC LOT SIZING ---'''

replacement = '''        # --- 🚀 CO-PILOT MODE (Phase 3) ---
        config = load_trading_config()
        if config.get("co_pilot_mode", False):
            print(f"✈️ CO-PILOT MODE ACTIVE: Intercepting {trade_type} {symbol}")
            update_agent("trade_executor", "Pending User Approval", f"Waiting for manual execution for {symbol}")
            msg = f"✈️ <b>CO-PILOT MODE ALERT</b>\nAI wants to <b>{trade_type} {symbol}</b>.\nPlease execute manually in MT5 if you approve."
            
            try:
                chart_path = generate_trade_chart(symbol, trade_type, float(price), float(sl), float(tp))
                send_telegram_alert(msg, chart_path)
            except Exception:
                send_telegram_alert(msg)
                
            return None
            
        # --- 🚀 INSTITUTIONAL DYNAMIC LOT SIZING ---'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Co-Pilot Patch applied!")
else:
    print("Target not found for Co-Pilot patch.")
