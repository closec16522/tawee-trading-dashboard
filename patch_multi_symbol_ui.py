import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# We need to replace the rendering logic in fetchBacktestResults.
# Currently it looks like:
#              let html = `<div style="display: grid; ...
#              ...
#              container.innerHTML = html;

old_logic = """              let html = `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px;">
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
              
              container.innerHTML = html;"""

new_logic = """              let html = '';
              
              // Handle old format (single symbol)
              let symbolDataMap = data.history ? { "XAUUSD-VIP": data } : data;
              
              for (const [symbol, symData] of Object.entries(symbolDataMap)) {
                  if (symData.error) continue; // Skip failed optimizations
                  
                  html += `<div style="margin-bottom: 30px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">`;
                  html += `<h3 style="color: #60a5fa; font-size: 18px; margin-bottom: 15px; border-bottom: 1px solid rgba(96, 165, 250, 0.2); padding-bottom: 8px;">📊 ${symbol} Optimization</h3>`;
                  
                  html += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px;">
                      <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px; border-radius: 8px;">
                          <div style="font-size: 11px; color: #10b981;">Best Win Rate</div>
                          <div style="font-size: 20px; font-weight: bold; color: #fff;">${symData.best_stats?.win_rate || 0}%</div>
                      </div>
                      <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 12px; border-radius: 8px;">
                          <div style="font-size: 11px; color: #3b82f6;">Total Profit</div>
                          <div style="font-size: 20px; font-weight: bold; color: #fff;">$${symData.best_stats?.total_profit || 0}</div>
                      </div>
                      <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 8px;">
                          <div style="font-size: 11px; color: #f59e0b;">Best SL Multiplier</div>
                          <div style="font-size: 20px; font-weight: bold; color: #fff;">${symData.best_params?.sl_multiplier || 0}x</div>
                      </div>
                  </div>`;
                  
                  html += `<h4 style="color:#cbd5e1; font-size: 13px; margin-bottom:10px;">Optimization History</h4>
                           <table style="width:100%; text-align:left; border-collapse: collapse;">
                              <thead>
                                  <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color:#94a3b8; font-size:11px;">
                                      <th style="padding: 6px 5px;">Iter</th>
                                      <th style="padding: 6px 5px;">SL Mult</th>
                                      <th style="padding: 6px 5px;">R:R Ratio</th>
                                      <th style="padding: 6px 5px;">Win Rate</th>
                                      <th style="padding: 6px 5px;">Profit</th>
                                  </tr>
                              </thead>
                              <tbody>`;
                              
                  if(symData.history) {
                      symData.history.forEach(h => {
                          html += `<tr style="border-bottom: 1px solid rgba(255,255,255,0.05); color:#cbd5e1; font-size:12px;">
                              <td style="padding: 6px 5px;">${h.iteration}</td>
                              <td style="padding: 6px 5px;">${h.params.sl_multiplier}</td>
                              <td style="padding: 6px 5px;">${h.params.rr_ratio}</td>
                              <td style="padding: 6px 5px; color:${h.stats?.win_rate >= 50 ? '#10b981' : '#ef4444'};">${h.stats?.win_rate || 0}%</td>
                              <td style="padding: 6px 5px; color:${h.stats?.total_profit >= 0 ? '#10b981' : '#ef4444'};">$${h.stats?.total_profit || 0}</td>
                          </tr>`;
                      });
                  }
                  html += `</tbody></table></div>`;
              }
              
              if (html === '') {
                  html = '<i>No valid results found.</i>';
              }
              
              container.innerHTML = html;"""

content = content.replace(old_logic, new_logic)

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)

print("Updated index.html to support multiple symbols in backtest.")
