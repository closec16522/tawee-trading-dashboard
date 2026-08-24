import codecs
import re

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add backtest-terminal below the button
button_html = r'(<button onclick="window\.runBacktestOptimization\(\)".*?>\s*<i.*?></i> Start AI Optimization</button>|<button onclick="window\.runBacktestOptimization\(\)".*?> Start AI Optimization</button>)'

terminal_html = r"""\1
                <div id="backtest-terminal-container" style="display: none; margin-top: 20px; margin-bottom: 20px;">
                  <h3 style="color: #cbd5e1; font-size: 16px; margin-bottom: 10px;">⚡ AI-Trader MCP Server Terminal</h3>
                  <div id="backtest-terminal" style="padding: 15px; background: #0f172a; border-radius: 8px; font-family: 'Courier New', Courier, monospace; font-size: 13px; color: #10b981; overflow-y: auto; height: 250px; border: 1px solid #334155; white-space: pre-wrap; line-height: 1.4;">[System] Ready to start Backtest...</div>
                </div>"""

if 'backtest-terminal-container' not in content:
    content = re.sub(button_html, terminal_html, content)

# 2. Update runBacktestOptimization logic
old_js = r"""window\.runBacktestOptimization = function\(\) \{
\s*alert\('⏳ Starting AI Optimization Process in backend\.\.\. This may take a few minutes\.'\);
\s*const host = new URLSearchParams\(window\.location\.search\)\.get\('gw'\) \|\| '192\.168\.0\.41';
\s*fetch\(`http://\$\{host\}:19000/api/backtest/run`, \{ method: 'POST' \}\)
\s*\.then\(res => res\.json\(\)\)
\s*\.then\(data => \{
\s*console\.log\('Backtest triggered:', data\);
\s*\}\)
\s*\.catch\(err => alert\('Error triggering backtest'\)\);
\s*\};"""

new_js = """window.runBacktestOptimization = function() {
          const btn = event.currentTarget || document.querySelector('button[onclick="window.runBacktestOptimization()"]');
          if (btn) btn.disabled = true;
          
          document.getElementById('backtest-terminal-container').style.display = 'block';
          const term = document.getElementById('backtest-terminal');
          term.innerHTML = "[System] Starting AI Optimization Process in backend...\\n";
          
          const host = new URLSearchParams(window.location.search).get('gw') || '192.168.0.41';
          fetch(`http://${host}:19000/api/backtest/run`, { method: 'POST' })
          .then(res => res.json())
          .then(data => {
              console.log('Backtest triggered:', data);
          })
          .catch(err => alert('Error triggering backtest: ' + err));
          
          // Poll logs
          if(window.backtestLogInterval) clearInterval(window.backtestLogInterval);
          window.backtestLogInterval = setInterval(() => {
              fetch(`http://${host}:19000/api/backtest/logs`)
              .then(res => res.json())
              .then(data => {
                  term.innerHTML = data.logs;
                  term.scrollTop = term.scrollHeight;
                  if(data.logs.includes('Multi-Symbol Backtest Optimization Complete!')) {
                      clearInterval(window.backtestLogInterval);
                      if (btn) btn.disabled = false;
                      window.fetchBacktestResults(); // Auto refresh results
                  }
              });
          }, 2000);
      };"""

content = re.sub(old_js, new_js, content)

# 3. Fix training-terminal -> training-console
content = content.replace('getElementById("training-terminal")', 'getElementById("training-console")')

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)
print("index.html patched")
