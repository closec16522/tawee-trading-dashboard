import re

file_path = "mt5_backend/agent_orchestrator.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Add RSI and EMA columns to the dataframe right after it's created in `get_data` or `copy_rates_from_pos`.
# In agent_orchestrator.py, `df` is created in two places:
# 1. generate_trade_chart
# 2. Inside the main loop:
#    rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 50)
#    if rates is not None and len(rates) > 0:
#        df = pd.DataFrame(rates)
#        df['time'] = pd.to_datetime(df['time'], unit='s')

old_main_loop = """        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 50)
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')"""

new_main_loop = """        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 200) # Increased to 200 to calculate EMA200
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            # Calculate Indicators
            df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean().round(4)
            df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean().round(4)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = (100 - (100 / (1 + rs))).round(2)"""

code = code.replace(old_main_loop, new_main_loop)


# Now update the prompts in analyze_market_with_openai, analyze_market_with_claude, analyze_market_with_local_ai
# They all do:
# recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close'])

old_recent_data = "recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close'])"
new_recent_data = "recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI'])"
code = code.replace(old_recent_data, new_recent_data)


# Update generate_trade_chart
old_chart = """        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        entry_line = [entry] * len(df)
        sl_line = [sl] * len(df)
        tp_line = [tp] * len(df)
        
        fill_between = []
        if decision == "BUY":
            fill_between.append(dict(y1=entry_line, y2=tp_line, color='g', alpha=0.2))
            fill_between.append(dict(y1=sl_line, y2=entry_line, color='r', alpha=0.2))
        else:
            fill_between.append(dict(y1=entry_line, y2=sl_line, color='r', alpha=0.2))
            fill_between.append(dict(y1=tp_line, y2=entry_line, color='g', alpha=0.2))
        
        chart_path = os.path.join(os.path.dirname(__file__), f"chart_{symbol}.png")
        
        mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', wick='inherit', volume='in', ohlc='i')
        s  = mpf.make_mpf_style(marketcolors=mc, style='nightclouds')
        
        mpf.plot(df, type='candle', style=s, 
                 fill_between=fill_between,
                 title=f"{symbol} - {decision} Signal",
                 savefig=chart_path)"""

new_chart = """        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 200) # Get enough data for indicators
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Calculate Indicators
        df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # We only want to plot the last 50 candles to keep the chart zoomed in
        df_plot = df.tail(50).copy()
        
        entry_line = [entry] * len(df_plot)
        sl_line = [sl] * len(df_plot)
        tp_line = [tp] * len(df_plot)
        
        fill_between = []
        if decision == "BUY":
            fill_between.append(dict(y1=entry_line, y2=tp_line, color='g', alpha=0.2))
            fill_between.append(dict(y1=sl_line, y2=entry_line, color='r', alpha=0.2))
        else:
            fill_between.append(dict(y1=entry_line, y2=sl_line, color='r', alpha=0.2))
            fill_between.append(dict(y1=tp_line, y2=entry_line, color='g', alpha=0.2))
        
        chart_path = os.path.join(os.path.dirname(__file__), f"chart_{symbol}.png")
        
        mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', wick='inherit', volume='in', ohlc='i')
        s  = mpf.make_mpf_style(marketcolors=mc, style='nightclouds')
        
        # Add plots for EMA and RSI
        apds = [
            mpf.make_addplot(df_plot['EMA50'], color='blue', width=1.5),
            mpf.make_addplot(df_plot['EMA200'], color='orange', width=1.5),
            mpf.make_addplot(df_plot['RSI'], panel=1, color='purple', ylabel='RSI (14)')
        ]
        
        mpf.plot(df_plot, type='candle', style=s, 
                 fill_between=fill_between,
                 addplot=apds,
                 panel_ratios=(3,1),
                 title=f"{symbol} - {decision} Signal",
                 savefig=chart_path)"""

# Also need to replace the `rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 50)` inside generate_trade_chart
code = code.replace("rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 50)\n        if rates is None", "rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 200)\n        if rates is None")
code = code.replace(old_chart, new_chart)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)
print("agent_orchestrator.py patched successfully.")
