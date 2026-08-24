import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add switchTab logic
switch_tab_code = """        } else if (tab === 'backtest') {
          mainContent.innerHTML = getBacktestHTML();
"""
if "tab === 'backtest'" not in content:
    idx = content.find("} else if (tab === 'news') {")
    if idx != -1:
        content = content[:idx] + switch_tab_code + content[idx:]

# 2. Add getBacktestHTML function
html_func = """
      function getBacktestHTML() {
        return `
          <div id="dashboard-root">
            <header class="dashboard-header">
              <div class="header-title-area">
                <div class="header-path">MARKETS / DATA BACKTEST</div>
                <h2 class="header-title" style="text-align:left;">Data Backtest & AI Optimization</h2>
                <div class="header-desc">AI Data Driven Trading Backtest Simulator</div>
              </div>
            </header>
            <div class="dashboard-scroll-body" style="padding:20px;">
              <button onclick="window.runBacktestOptimization()" style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff; padding: 10px 20px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); margin-bottom: 20px;">🚀 Start AI Optimization</button>
              
              <div class="card" style="padding: 20px;">
                <h3 style="color: #cbd5e1; font-size: 16px; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Optimization Results</h3>
                <div id="backtest-results-container" style="color: #94a3b8; font-size: 14px; min-height: 100px;">
                  <i>No optimization results loaded yet. Click 'Start AI Optimization' or refresh.</i>
                </div>
                
                <button onclick="window.fetchBacktestResults()" style="margin-top: 15px; background: rgba(255,255,255,0.05); color: #cbd5e1; padding: 8px 15px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; cursor: pointer;">🔄 Refresh Results</button>
              </div>
            </div>
          </div>
        `;
      }
"""
if "function getBacktestHTML" not in content:
    idx = content.find('function getAnalyticsHTML()')
    if idx != -1:
        content = content[:idx] + html_func + content[idx:]

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)

print("Added switchTab and getBacktestHTML logic.")
