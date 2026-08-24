import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove Recent Trades
recent_trades_pattern = re.compile(r'<!-- Recent Trades Table -->.*?<tbody id="dash-recent-tbody"></tbody>\s*</table>\s*</div>', re.DOTALL)
content = recent_trades_pattern.sub('', content)

# 2. Extract Market Overview
market_overview_pattern = re.compile(r'<!-- Market Overview -->.*?<div class="signals-card" style="min-height: 180px;">\s*<span class="signals-title">Market Overview \(Top Movers\)</span>.*?</div>\s*</div>', re.DOTALL)
mo_match = market_overview_pattern.search(content)

if mo_match:
    mo_html = mo_match.group(0)
    # Remove from original place
    content = content.replace(mo_html, '')
    
    # Insert under AI Analysis. 
    # We will put it before Active Signals.
    insert_target = '<!-- Bottom Row: Active Signals -->'
    if insert_target in content:
        content = content.replace(insert_target, mo_html + '\n              ' + insert_target)
    else:
        print("Could not find insert target for Market Overview")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Layout changes applied.')
