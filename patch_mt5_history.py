import os
import re

with open("mt5_backend/mt5_gateway.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                # Fetch today's closed deals
                now = datetime.datetime.now()
                today_start = datetime.datetime(now.year, now.month, now.day)
                deals = mt5.history_deals_get(today_start, now)
                
                if deals:
                    for d in deals:
                        if d.entry == 1: # Closing deal
                            acc_dict["trades_today"] += 1
                            acc_dict["daily_profit"] += d.profit
                            if d.profit > 0:
                                acc_dict["wins_today"] += 1
                                
                if acc_dict["trades_today"] > 0:
                    acc_dict["win_rate"] = (acc_dict["wins_today"] / acc_dict["trades_today"]) * 100
                

            else:"""

replacement = """                # Fetch today's closed deals
                now = datetime.datetime.now()
                today_start = datetime.datetime(now.year, now.month, now.day)
                deals = mt5.history_deals_get(today_start, now)
                
                recent_trades = []
                if deals:
                    for d in deals:
                        if d.entry == 1: # Closing deal
                            acc_dict["trades_today"] += 1
                            acc_dict["daily_profit"] += d.profit
                            if d.profit > 0:
                                acc_dict["wins_today"] += 1
                                
                            # Save recent trade
                            recent_trades.append({
                                "ticket": d.ticket,
                                "symbol": d.symbol,
                                "type": "BUY" if d.type == 1 else "SELL", # deal type 1 is sell, so if deal is sell, position was buy. Wait!
                                "price": d.price,
                                "profit": d.profit
                            })
                            
                    recent_trades.reverse()
                    recent_trades = recent_trades[:10] # send last 10
                                
                if acc_dict["trades_today"] > 0:
                    acc_dict["win_rate"] = (acc_dict["wins_today"] / acc_dict["trades_today"]) * 100
                

            else:
                recent_trades = []"""

# Wait, MT5 deals have more information. A closing deal (entry == 1) closes a position.
# Deal type: 0 (BUY), 1 (SELL).
# If you close a long position (BUY), you SELL, so the deal is SELL. Thus, the original position was BUY.
replacement = """                # Fetch today's closed deals
                now = datetime.datetime.now()
                today_start = now - datetime.timedelta(days=7) # Get last 7 days of deals for history
                deals = mt5.history_deals_get(today_start, now)
                
                recent_trades = []
                if deals:
                    # Sort by time
                    sorted_deals = sorted(deals, key=lambda x: x.time, reverse=True)
                    for d in sorted_deals:
                        if d.entry == 1: # Closing deal
                            # only count today for stats
                            deal_time = datetime.datetime.fromtimestamp(d.time)
                            if deal_time.date() == now.date():
                                acc_dict["trades_today"] += 1
                                acc_dict["daily_profit"] += d.profit
                                if d.profit > 0:
                                    acc_dict["wins_today"] += 1
                                
                            if len(recent_trades) < 15:
                                recent_trades.append({
                                    "ticket": d.position_id,
                                    "symbol": d.symbol,
                                    "type": "BUY" if d.type == 1 else "SELL", # Closing a BUY requires a SELL deal
                                    "entry": 0, # Cannot easily get entry price from closing deal without looking up order
                                    "exit": d.price,
                                    "profit": d.profit
                                })
                                
                if acc_dict["trades_today"] > 0:
                    acc_dict["win_rate"] = (acc_dict["wins_today"] / acc_dict["trades_today"]) * 100
                

            else:
                recent_trades = []"""

content = content.replace(target, replacement)

target2 = """                "signal_history": signal_history"""
replacement2 = """                "signal_history": signal_history,
                "recent_trades": recent_trades"""

content = content.replace(target2, replacement2)

with open("mt5_backend/mt5_gateway.py", "w", encoding="utf-8") as f:
    f.write(content)

print("mt5 gateway patched")