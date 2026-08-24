import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace send_telegram_alert(msg) with chart generation for closures
target = '''        send_telegram_alert(msg)'''

replacement = '''        # --- 🚀 RICH NOTIFICATIONS (Phase 3) ---
        try:
            chart_path = generate_trade_chart(symbol, "CLOSE", float(price), 0, 0)
            send_telegram_alert(msg, chart_path)
        except Exception:
            send_telegram_alert(msg)'''

# This will replace multiple occurrences, which is good (one in close_position, one in monitor)
# Let's be safe and apply it only where we see `f"<i>{emotion}</i>"\n        )\n        \n        send_telegram_alert(msg)`
target_specific = '''        )
        
        send_telegram_alert(msg)'''

replacement_specific = '''        )
        
        # --- 🚀 RICH NOTIFICATIONS (Phase 3) ---
        try:
            chart_path = generate_trade_chart(symbol, "CLOSE", float(price), 0, 0)
            send_telegram_alert(msg, chart_path)
        except Exception:
            send_telegram_alert(msg)'''

if target_specific in content:
    content = content.replace(target_specific, replacement_specific)
    
target_specific_2 = '''                    )
                    
                    send_telegram_alert(msg)'''

replacement_specific_2 = '''                    )
                    
                    # --- 🚀 RICH NOTIFICATIONS (Phase 3) ---
                    try:
                        chart_path = generate_trade_chart(symbol, "CLOSE", float(price), 0, 0)
                        send_telegram_alert(msg, chart_path)
                    except Exception:
                        send_telegram_alert(msg)'''

if target_specific_2 in content:
    content = content.replace(target_specific_2, replacement_specific_2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Rich Notifications Patch applied!")
