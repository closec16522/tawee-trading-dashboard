import os

file_path = 'mt5_backend/agent_orchestrator.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add ACTIVE_TICKETS_CACHE global variable
if "ACTIVE_TICKETS_CACHE = None" not in content:
    content = content.replace("LAST_TG_MSG = {}", "LAST_TG_MSG = {}\nACTIVE_TICKETS_CACHE = None")

# 2. Define run_trade_monitor()
monitor_func = """def run_trade_monitor():
    global ACTIVE_TICKETS_CACHE
    positions = mt5.positions_get()
    current_tickets = {pos.ticket for pos in positions} if positions else set()
    
    if ACTIVE_TICKETS_CACHE is None:
        ACTIVE_TICKETS_CACHE = current_tickets
        return
        
    closed_tickets = ACTIVE_TICKETS_CACHE - current_tickets
    if closed_tickets:
        print(f"👀 TRADE MONITOR: Detected {len(closed_tickets)} closed tickets: {closed_tickets}")
        for ticket in closed_tickets:
            pos_deals = mt5.history_deals_get(position=ticket)
            if pos_deals:
                closing_deals = [d for d in pos_deals if d.entry == 1]
                if closing_deals:
                    d = closing_deals[-1]
                    profit = d.profit
                    symbol = d.symbol
                    price = d.price
                    pos_type = 0 if d.type == 1 else 1
                    
                    status_icon = "🟢" if profit > 0 else "🔴"
                    status_text = "PROFIT" if profit > 0 else "LOSS"
                    action_text = "BUY" if pos_type == 0 else "SELL"
                    
                    emotion = get_emotion("PROFIT" if profit > 0 else "LOSS")
                    
                    msg = (
                        f"💰 <b>[AI TRADE CLOSED]</b>\\n"
                        f"<b>Symbol:</b> {symbol}\\n"
                        f"<b>Action:</b> {action_text} (Closed)\\n"
                        f"<b>Ticket:</b> #{ticket}\\n"
                        f"<b>Close Price:</b> {price}\\n"
                        f"-------------------------\\n"
                        f"💵 <b>Net P/L:</b> ${profit:.2f}\\n"
                        f"📉 <b>Status:</b> {status_text} {status_icon}\\n\\n"
                        f"<i>{emotion}</i>"
                    )
                    send_telegram_alert(msg)
                    
    ACTIVE_TICKETS_CACHE = current_tickets

def main_loop():"""

if "def run_trade_monitor():" not in content:
    content = content.replace("def main_loop():", monitor_func)

# 3. Inject into main_loop()
if "run_trade_monitor()" not in content:
    content = content.replace("run_portfolio_manager()", "run_trade_monitor()\n            run_portfolio_manager()")

# 4. Comment out send_telegram_alert in close_position
old_msg = """        msg = (
            f"💰 <b>[AI TRADE CLOSED]</b>\\n"
            f"<b>Symbol:</b> {symbol}\\n"
            f"<b>Action:</b> {action_text} (Closed)\\n"
            f"<b>Ticket:</b> #{ticket}\\n"
            f"<b>Close Price:</b> {price}\\n"
            f"-------------------------\\n"
            f"💵 <b>Net P/L:</b> ${profit:.2f}\\n"
            f"📉 <b>Status:</b> {status_text} {status_icon}\\n\\n"
            f"<i>{emotion}</i>"
        )
        send_telegram_alert(msg)"""

new_msg = """        msg = (
            f"💰 <b>[AI TRADE CLOSED]</b>\\n"
            f"<b>Symbol:</b> {symbol}\\n"
            f"<b>Action:</b> {action_text} (Closed)\\n"
            f"<b>Ticket:</b> #{ticket}\\n"
            f"<b>Close Price:</b> {price}\\n"
            f"-------------------------\\n"
            f"💵 <b>Net P/L:</b> ${profit:.2f}\\n"
            f"📉 <b>Status:</b> {status_text} {status_icon}\\n\\n"
            f"<i>{emotion}</i>"
        )
        # send_telegram_alert(msg) # Removed to avoid duplicate. Now handled by run_trade_monitor()"""

if "send_telegram_alert(msg) # Removed" not in content:
    content = content.replace(old_msg, new_msg)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched agent_orchestrator.py successfully.")
