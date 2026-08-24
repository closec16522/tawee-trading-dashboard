import re
import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add sidebar menu item
menu_item = """<button class="menu-item" data-tab="backtest">
<span class="menu-item-left">
<span class="menu-item-icon">🧪</span>
<span>Data Backtest</span>
</span>
<span class="active-dot"></span>
</button>
"""

# Insert after Track Record menu item
if 'data-tab="backtest"' not in content:
    content = re.sub(
        r'(<button class="menu-item" data-tab="track-record">[\s\S]*?</button>)',
        r'\1\n' + menu_item,
        content,
        count=1
    )

# 2. Add Tab Pane
tab_pane = """
        <!-- Data Backtest Tab -->
        <div class="tab-pane" id="tab-backtest">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <h2 style="font-size: 24px; font-weight: 800; color: #fff; margin:0;">🧪 Data Backtest & AI Optimization</h2>
            <button onclick="runBacktestOptimization()" style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff; padding: 10px 20px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);">🚀 Start AI Optimization</button>
          </div>
          
          <div class="card" style="margin-bottom: 20px; padding: 20px;">
            <h3 style="color: #cbd5e1; font-size: 16px; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Optimization Results</h3>
            <div id="backtest-results-container" style="color: #94a3b8; font-size: 14px; min-height: 100px;">
              <i>No optimization results loaded yet. Click 'Start AI Optimization' or refresh.</i>
            </div>
            
            <button onclick="fetchBacktestResults()" style="margin-top: 15px; background: rgba(255,255,255,0.05); color: #cbd5e1; padding: 8px 15px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; cursor: pointer;">🔄 Refresh Results</button>
          </div>
          
          <!-- Embedded Scripts for functionality -->
          <script>
            function runBacktestOptimization() {
                alert('⏳ Starting AI Optimization Process in backend... This may take a few minutes.');
                fetch('/api/backtest/run', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    console.log('Backtest triggered:', data);
                })
                .catch(err => alert('Error triggering backtest'));
            }
            
            function fetchBacktestResults() {
                const container = document.getElementById('backtest-results-container');
                container.innerHTML = '<div style="color: #3b82f6;">⏳ Fetching latest results...</div>';
                
                fetch('/api/backtest/results')
                .then(res => res.json())
                .then(data => {
                    if(data.error) {
                        container.innerHTML = `<div style="color: #ef4444;">❌ ${data.error}</div>`;
                        return;
                    }
                    
                    let html = `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 15px; border-radius: 8px;">
                            <div style="font-size: 12px; color: #10b981;">Best Win Rate</div>
                            <div style="font-size: 24px; font-weight: bold; color: #fff;">${data.best_stats?.win_rate || 0}%</div>
                        </div>
                        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 8px;">
                            <div style="font-size: 12px; color: #3b82f6;">Total Profit</div>
                            <div style="font-size: 24px; font-weight: bold; color: #fff;">$${data.best_stats?.total_profit || 0}</div>
                        </div>
                        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 15px; border-radius: 8px;">
                            <div style="font-size: 12px; color: #f59e0b;">Best SL Multiplier</div>
                            <div style="font-size: 24px; font-weight: bold; color: #fff;">${data.best_params?.sl_multiplier || 0}x</div>
                        </div>
                    </div>`;
                    
                    html += `<h4 style="color:#fff; margin-bottom:10px;">Optimization History</h4>
                             <table style="width:100%; text-align:left; border-collapse: collapse;">
                                <thead>
                                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color:#94a3b8; font-size:12px;">
                                        <th style="padding: 8px 5px;">Iteration</th>
                                        <th style="padding: 8px 5px;">SL Mult</th>
                                        <th style="padding: 8px 5px;">R:R Ratio</th>
                                        <th style="padding: 8px 5px;">Win Rate</th>
                                        <th style="padding: 8px 5px;">Profit</th>
                                    </tr>
                                </thead>
                                <tbody>`;
                                
                    if(data.history) {
                        data.history.forEach(h => {
                            html += `<tr style="border-bottom: 1px solid rgba(255,255,255,0.05); color:#cbd5e1; font-size:13px;">
                                <td style="padding: 8px 5px;">${h.iteration}</td>
                                <td style="padding: 8px 5px;">${h.params.sl_multiplier}</td>
                                <td style="padding: 8px 5px;">${h.params.rr_ratio}</td>
                                <td style="padding: 8px 5px; color:${h.stats.win_rate >= 50 ? '#10b981' : '#ef4444'};">${h.stats.win_rate}%</td>
                                <td style="padding: 8px 5px; color:${h.stats.total_profit >= 0 ? '#10b981' : '#ef4444'};">$${h.stats.total_profit}</td>
                            </tr>`;
                        });
                    }
                    html += `</tbody></table>`;
                    
                    container.innerHTML = html;
                })
                .catch(err => {
                    container.innerHTML = `<div style="color: #ef4444;">❌ Error fetching results: ${err.message}</div>`;
                });
            }
          </script>
        </div>
"""

# Insert Tab Pane right before the ending </div> of the tab container.
# In index.html, we know there are many `<div class="tab-pane" id="...">`
if 'id="tab-backtest"' not in content:
    content = re.sub(
        r'(<div class="tab-pane" id="tab-analytics">[\s\S]*?</div>\s*</div>\s*<!-- END OF TABS)', 
        r'\1\n' + tab_pane,
        content,
        count=1
    )
    # If the above fails to match, let's just append it before `</main>`
    if 'id="tab-backtest"' not in content:
        content = re.sub(
            r'(</main>)',
            tab_pane + r'\n\1',
            content
        )

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)
print("Dashboard Backtest added to index.html successfully.")
