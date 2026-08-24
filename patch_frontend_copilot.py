import re

path = 'index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Co-Pilot Mode Toggle to HTML UI
target_ui = '''                  <div style="font-weight:700; color:#cbd5e1; margin-bottom:6px;">Paper Trading (No Real Execution)</div>'''
replacement_ui = '''                  <div style="font-weight:700; color:#cbd5e1; margin-bottom:6px;">Co-Pilot Mode (Require Approval via MT5)</div>
                  <label class="switch" style="margin-bottom:12px;">
                    <input type="checkbox" id="set-copilot">
                    <span class="slider round"></span>
                  </label>
                  <div style="font-weight:700; color:#cbd5e1; margin-bottom:6px;">Paper Trading (No Real Execution)</div>'''

if target_ui in content:
    content = content.replace(target_ui, replacement_ui)

# 2. Add loading of co_pilot_mode
target_load = '''                        document.getElementById('set-paper').checked = data.config.paper_trading || false;'''
replacement_load = '''                        document.getElementById('set-paper').checked = data.config.paper_trading || false;
                        if(document.getElementById('set-copilot')) document.getElementById('set-copilot').checked = data.config.co_pilot_mode || false;'''

if target_load in content:
    content = content.replace(target_load, replacement_load)

# 3. Add saving of co_pilot_mode
target_save = '''                const paperTrading = document.getElementById('set-paper').checked;'''
replacement_save = '''                const paperTrading = document.getElementById('set-paper').checked;
                const coPilotMode = document.getElementById('set-copilot') ? document.getElementById('set-copilot').checked : false;'''

target_save_fetch = '''                    model_engine: modelEngine,
                    paper_trading: paperTrading'''
replacement_save_fetch = '''                    model_engine: modelEngine,
                    paper_trading: paperTrading,
                    co_pilot_mode: coPilotMode'''

if target_save in content:
    content = content.replace(target_save, replacement_save)
if target_save_fetch in content:
    content = content.replace(target_save_fetch, replacement_save_fetch)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Frontend Copilot patched!")
