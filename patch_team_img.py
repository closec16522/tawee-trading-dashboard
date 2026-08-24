import re

file_path = "index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

def replace_agent_img(agent_name, cid, border_color):
    global content
    old_pattern = f'<img src="https://api.pixelaivision.com/static/characters/{agent_name}.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid {border_color};">'
    
    new_html = f'''<div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid {border_color}; display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_{cid}.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>'''
    
    content = content.replace(old_pattern, new_html)

replace_agent_img("market_analyst", "17", "rgba(52, 214, 230, 0.3)")
replace_agent_img("smc_strategy", "29", "rgba(245, 196, 81, 0.3)")
replace_agent_img("news_analyst", "21", "rgba(255, 126, 182, 0.3)")
replace_agent_img("risk_manager", "26", "rgba(255, 162, 74, 0.3)")
replace_agent_img("portfolio_manager", "57", "rgba(106, 141, 255, 0.3)")
replace_agent_img("supervisor", "1", "rgba(154, 123, 255, 0.3)")
replace_agent_img("trade_executor", "54", "rgba(55, 210, 122, 0.3)")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Team Trading images patched to pixel art.")
