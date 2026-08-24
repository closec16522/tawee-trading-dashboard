import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

target_str = '<button onclick="window.runBacktestOptimization()" style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff; padding: 10px 20px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); margin-bottom: 20px;">🚀 Start AI Optimization</button>'

terminal_html = target_str + """
<div id="backtest-terminal-container" style="display: none; margin-top: 20px; margin-bottom: 20px;">
  <h3 style="color: #cbd5e1; font-size: 16px; margin-bottom: 10px;">⚡ AI-Trader MCP Server Terminal</h3>
  <div id="backtest-terminal" style="padding: 15px; background: #0f172a; border-radius: 8px; font-family: 'Courier New', Courier, monospace; font-size: 13px; color: #10b981; overflow-y: auto; height: 250px; border: 1px solid #334155; white-space: pre-wrap; line-height: 1.4;">[System] Ready to start Backtest...</div>
</div>
"""

if target_str in content:
    if 'backtest-terminal-container' not in content:
        content = content.replace(target_str, terminal_html)
        with codecs.open('index.html', 'w', 'utf-8') as f:
            f.write(content)
        print("Terminal inserted successfully.")
    else:
        print("Terminal already exists.")
else:
    print("Could not find target_str")
