import codecs

with codecs.open('mt5_backend/strategy_optimizer.py', 'r', 'utf-8') as f:
    content = f.read()

bad_string = '''    if df is None:
        return {"error": "Failed to fetch MT5 data"}
    
    start_date = df['time'].min().strftime('%Y-%m-%d %H:%M')
    end_date = df['time'].max().strftime('%Y-%m-%d %H:%M')
    period_str = f"{start_date} to {end_date}"

        return {"error": "Failed to fetch MT5 data"}'''

good_string = '''    if df is None:
        return {"error": "Failed to fetch MT5 data"}
    
    start_date = df['time'].min().strftime('%Y-%m-%d %H:%M')
    end_date = df['time'].max().strftime('%Y-%m-%d %H:%M')
    period_str = f"{start_date} to {end_date}"'''

content = content.replace(bad_string, good_string)

with codecs.open('mt5_backend/strategy_optimizer.py', 'w', 'utf-8') as f:
    f.write(content)
