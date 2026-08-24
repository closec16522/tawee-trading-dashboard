import os
import re

with open("mt5_backend/mt5_gateway.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                if deals:
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
                                })"""

replacement = """                if deals:
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
                                # fetch entry deal
                                entry_price = 0.0
                                pos_deals = mt5.history_deals_get(position=d.position_id)
                                if pos_deals:
                                    for pd in pos_deals:
                                        if pd.entry == 0:
                                            entry_price = pd.price
                                            break
                                            
                                recent_trades.append({
                                    "ticket": d.position_id,
                                    "symbol": d.symbol,
                                    "type": "BUY" if d.type == 1 else "SELL", # Closing a BUY requires a SELL deal
                                    "entry": entry_price,
                                    "exit": d.price,
                                    "profit": d.profit
                                })"""

content = content.replace(target, replacement)

with open("mt5_backend/mt5_gateway.py", "w", encoding="utf-8") as f:
    f.write(content)

print("mt5 gateway patched again")