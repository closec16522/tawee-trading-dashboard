import codecs
import os
import re

# 1. Patch mt5_backend/strategy_optimizer.py to include 'period'
optimizer_path = os.path.join('mt5_backend', 'strategy_optimizer.py')
with codecs.open(optimizer_path, 'r', 'utf-8') as f:
    opt_content = f.read()

# Add period extraction after fetching df
if 'start_date = df[\'time\'].min()' not in opt_content:
    opt_content = opt_content.replace(
        "df = fetch_historical_data(symbol)\n    if df is None:",
        "df = fetch_historical_data(symbol)\n    if df is None:\n        return {\"error\": \"Failed to fetch MT5 data\"}\n    \n    start_date = df['time'].min().strftime('%Y-%m-%d %H:%M')\n    end_date = df['time'].max().strftime('%Y-%m-%d %H:%M')\n    period_str = f\"{start_date} to {end_date}\"\n"
    )
    # Replace final_result to include period
    opt_content = opt_content.replace(
        "\"symbol\": symbol,\n        \"best_params\": best_params,",
        "\"symbol\": symbol,\n        \"period\": period_str,\n        \"best_params\": best_params,"
    )
    with codecs.open(optimizer_path, 'w', 'utf-8') as f:
        f.write(opt_content)
    print("Patched strategy_optimizer.py")
else:
    print("strategy_optimizer.py already patched")

# 2. Patch index.html
index_path = 'index.html'
with codecs.open(index_path, 'r', 'utf-8') as f:
    idx_content = f.read()

# 2.1 Add Menu Item
menu_search = '<button class="menu-item" data-tab="portfolio">'
menu_insert = """<button class="menu-item" data-tab="training" onclick="switchTab('training')">
<span class="menu-item-left">
<span class="menu-item-icon">🧠</span>
<span>Local AI Training</span>
</span>
<span class="active-dot"></span>
</button>
"""
if 'data-tab="training"' not in idx_content:
    # Insert before Portfolio
    idx_content = idx_content.replace(menu_search, menu_insert + menu_search)
    print("Added menu item to index.html")

# 2.2 Update Backtest rendering to include period
search_html = "html += `<h3 style=\"color: #60a5fa; font-size: 18px; margin-bottom: 15px; border-bottom: 1px solid rgba(96, 165, 250, 0.2); padding-bottom: 8px;\">📊 ${symbol} Optimization</h3>`;"
replace_html = """html += `<h3 style="color: #60a5fa; font-size: 18px; margin-bottom: 5px; border-bottom: 1px solid rgba(96, 165, 250, 0.2); padding-bottom: 8px;">📊 ${symbol} Optimization</h3>`;
                let periodText = data.period ? data.period : 'Last 5000 Bars';
                html += `<div style="font-size: 12px; color: #a1a1aa; margin-bottom: 15px;">⏱️ Period: ${periodText}</div>`;"""

if "⏱️ Period:" not in idx_content:
    idx_content = idx_content.replace(search_html, replace_html)
    print("Added period display to index.html")

with codecs.open(index_path, 'w', 'utf-8') as f:
    f.write(idx_content)

print("Done.")
