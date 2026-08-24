import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        icon = "🟢" if profit > 0 else "🔴"
        msg = f"{icon} <b>TRADE CLOSED</b>\nSymbol: {symbol}\nProfit: ${profit:.2f}\nTicket: {ticket}"
        print(f"✅ Position Closed: {ticket} Profit: {profit}")
        send_telegram_alert(msg)
        return True'''

replacement = '''        icon = "🟢" if profit > 0 else "🔴"
        msg = f"{icon} <b>TRADE CLOSED</b>\nSymbol: {symbol}\nProfit: ${profit:.2f}\nTicket: {ticket}"
        print(f"✅ Position Closed: {ticket} Profit: {profit}")
        
        # --- 🚀 RICH NOTIFICATIONS (Phase 3) ---
        try:
            # Generate a chart showing the exit price (no sl/tp needed for exit)
            chart_path = generate_trade_chart(symbol, "CLOSE", float(price), float(price), float(price))
            send_telegram_alert(msg, chart_path)
        except Exception as e:
            send_telegram_alert(msg)
            
        return True'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Close position patched for Rich Notifications!")
else:
    print("Target not found for Close position.")
