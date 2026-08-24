from replace import replace_file_content

code = '''
# 30-Day Stats Cache
stats_30d = {
    "win_rate_30d": 0.0,
    "profit_factor_30d": 0.0,
    "equity_growth_30d": 0.0,
    "profit_30d": 0.0
}

async def update_30d_stats_loop():
    global stats_30d
    while True:
        if not mt5.terminal_info():
            await asyncio.sleep(5)
            continue
            
        try:
            now = datetime.datetime.now()
            start_30d = now - datetime.timedelta(days=30)
            deals = mt5.history_deals_get(start_30d, now)
            
            if deals:
                gross_profit = 0.0
                gross_loss = 0.0
                wins = 0
                total_trades = 0
                total_profit = 0.0
                
                for d in deals:
                    if d.entry == 1: # Closing deal
                        total_trades += 1
                        total_profit += d.profit
                        if d.profit > 0:
                            wins += 1
                            gross_profit += d.profit
                        elif d.profit < 0:
                            gross_loss += abs(d.profit)
                            
                win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0.0
                pf = gross_profit / gross_loss if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
                
                # Approximation for equity growth if we don't have historical equity
                # Using total profit over balance (not 100% accurate but close for dashboard)
                account_info = mt5.account_info()
                growth = 0.0
                if account_info and account_info.balance > 0:
                    starting_balance = account_info.balance - total_profit
                    if starting_balance > 0:
                        growth = (total_profit / starting_balance) * 100
                
                stats_30d["win_rate_30d"] = win_rate
                stats_30d["profit_factor_30d"] = pf
                stats_30d["equity_growth_30d"] = growth
                stats_30d["profit_30d"] = total_profit
                
        except Exception as e:
            print("Error updating 30d stats:", e)
            
        await asyncio.sleep(300) # Update every 5 minutes
'''

with open('patch_30d.py', 'w', encoding='utf-8') as f:
    f.write(code)
