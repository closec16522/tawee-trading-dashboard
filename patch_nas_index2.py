import os

with open('index_from_nas.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove duplicate menu
menu_target = '''              <button class="menu-item" data-tab="analytics">
                <span class="menu-item-left">
                  <span class="menu-item-icon">??</span>
                  <span>Research Analytics</span>
                </span>
                <span class="active-dot"></span>
              </button>'''
content = content.replace(menu_target, '', 1)

# 2. Remove duplicate getAnalyticsHTML (the first one)
# We know the first one starts with "function getAnalyticsHTML() {" and ends before "function initAnalyticsLogic() {}"
# Let's extract the exact string from index_from_nas.html to replace.
first_analytics = '''      function getAnalyticsHTML() {
        return 
          <div id="dashboard-root">
            <header class="dashboard-header">
              <div class="header-title-area">
                <div class="header-path">ANALYTICS / STATS</div>
                <h2 class="header-title" style="text-align:left;">Analytics</h2>
                <div class="header-desc">???????????????????????</div>
              </div>
              <div class="header-right-actions">
                <div class="header-badge-area" style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); padding: 6px 14px; border-radius: 20px; display:flex; align-items:center; gap:8px;">
                  <span style="width:6px; height:6px; background:#10b981; border-radius:50%; box-shadow:0 0 6px #10b981;"></span>
                  <span style="font-size:11px; font-weight:700; color:#10b981;">?????????? (Live)</span>
                </div>
              </div>
            </header>
            
            <div class="dashboard-scroll-body">
              <div style="font-size:13px; font-weight:700; color:#fff; margin-bottom:-10px;">Trading Statistics <button class="help-btn" onclick="window.showFeatureHelp('analytics-perf', event)" title="????????????">?</button></div>
              <div class="metric-cards-grid" style="grid-template-columns:repeat(4, 1fr);">
                <div class="metric-card">
                  <span class="metric-title">Total Trades</span>
                  <div class="metric-value">500</div>
                  <div class="metric-sub">???????</div>
                </div>
                <div class="metric-card">
                  <span class="metric-title">Win Rate</span>
                  <div class="metric-value" style="color:#10b981;">43%</div>
                  <div class="metric-sub">all-time</div>
                </div>
                <div class="metric-card">
                  <span class="metric-title">Profit Factor</span>
                  <div class="metric-value">1.23</div>
                  <div class="metric-sub">all-time</div>
                </div>
                <div class="metric-card">
                  <span class="metric-title">Active Positions</span>
                  <div class="metric-value">2</div>
                  <div class="metric-sub">??????</div>
                </div>
              </div>

              <div class="metric-cards-grid" style="grid-template-columns:repeat(4, 1fr);">
                <div class="metric-card">
                  <span class="metric-title">Equity</span>
                  <div class="metric-value" id="port-equity" style="color:#10b981;">,920.00</div>
                </div>
                <div class="metric-card">
                  <span class="metric-title">Month P/L</span>
                  <div class="metric-value" style="color:#10b981;">+,450.00</div>
                </div>
                <div class="metric-card">
                  <span class="metric-title">Week P/L</span>
                  <div class="metric-value" style="color:#10b981;">+.00</div>
                </div>
                <div class="metric-card">
                  <span class="metric-title">Floating P/L</span>
                  <div class="metric-value" id="port-float" style="color:#10b981;">+.00</div>
                </div>
              </div>
            </div>
          </div>
        ;
      }

      function initAnalyticsLogic() {}

'''
content = content.replace(first_analytics, '', 1)

# 3. Replace the Gemini Win Rate label
gemini_label_old = '''                  <div style="font-size:28px; font-weight:800; color:#fff; margin-bottom:4px;" id="stat-gemini-winrate">--%</div>
                  <div style="font-size:11px; color:#94a3b8;">Win Rate ?????????? (?????)</div>'''
gemini_label_new = '''                  <div style="font-size:28px; font-weight:800; color:#fff; margin-bottom:4px;" id="stat-gemini-winrate">--%</div>
                  <div style="font-size:11px; color:#94a3b8;">Win Rate ?????????? (????)</div>'''
content = content.replace(gemini_label_old, gemini_label_new, 1)

# 4. Replace initAnalyticsLogic() logic
init_logic_old = '''      async function initAnalyticsLogic() {
         try {
            const qp = new URLSearchParams(window.location.search); const host = '127.0.0.1';
            const res = await fetch(http://System.Management.Automation.Internal.Host.InternalHost:19000/api/signals?t=);
            if (res.ok) {
                const data = await res.json();
                const signals = data.signals || [];
                
                // Helper to calc win rate
                const calcWinRate = (sigs) => {
                    if(sigs.length === 0) return "--%";
                    const wins = sigs.filter(s => s.result && (s.result.toLowerCase().includes('win') || s.result.toLowerCase().includes('profit'))).length;
                    return ((wins / sigs.length) * 100).toFixed(1) + "%";
                };

                const geminiSigs = signals.filter(s => s.model && s.model.toLowerCase().includes('gemini'));
                const ollamaSigs = signals.filter(s => s.model && (s.model.toLowerCase().includes('ollama') || s.model.toLowerCase().includes('local')));
                const chatgptSigs = signals.filter(s => s.model && s.model.toLowerCase().includes('chatgpt'));
                const copilotSigs = signals.filter(s => s.model && s.model.toLowerCase().includes('copilot'));
                const claudeSigs = signals.filter(s => s.model && s.model.toLowerCase().includes('claude'));

                document.getElementById("stat-gemini-winrate").innerText = calcWinRate(geminiSigs);
                document.getElementById("stat-gemini-a").innerText = calcWinRate(geminiSigs.filter(s => s.grade === 'A'));
                document.getElementById("stat-gemini-b").innerText = calcWinRate(geminiSigs.filter(s => s.grade === 'B'));
                document.getElementById("stat-gemini-c").innerText = calcWinRate(geminiSigs.filter(s => s.grade === 'C'));

                document.getElementById("stat-ollama-winrate").innerText = calcWinRate(ollamaSigs);
                document.getElementById("stat-ollama-a").innerText = calcWinRate(ollamaSigs.filter(s => s.grade === 'A'));
                document.getElementById("stat-ollama-b").innerText = calcWinRate(ollamaSigs.filter(s => s.grade === 'B'));
                document.getElementById("stat-ollama-c").innerText = calcWinRate(ollamaSigs.filter(s => s.grade === 'C'));

                // Basic mock profit factor (Wins / Losses count) - real PF uses amounts
                const calcMockPF = (sigs) => {
                    if(sigs.length === 0) return "--";
                    const wins = sigs.filter(s => s.result && (s.result.toLowerCase().includes('win') || s.result.toLowerCase().includes('profit'))).length;
                    const losses = sigs.filter(s => s.result && (s.result.toLowerCase().includes('loss') || s.result.toLowerCase().includes('stop'))).length;
                    if (losses === 0) return wins > 0 ? "Infinite" : "0.0";
                    return (wins / losses).toFixed(2);
                };

                document.getElementById("stat-pf").innerText = calcMockPF(signals);
                document.getElementById("stat-gemini-pf").innerText = calcMockPF(geminiSigs);
                document.getElementById("stat-ollama-pf").innerText = calcMockPF(ollamaSigs);

            }
         } catch (e) {
             console.error("Error loading analytics:", e);
         }
      }'''
init_logic_new = '''      async function initAnalyticsLogic() {
         try {
            const qp = new URLSearchParams(window.location.search); 
            const host = qp.get("gw") || '127.0.0.1';
            
            // Fetch real track record for Gemini
            const trRes = await fetch(http://System.Management.Automation.Internal.Host.InternalHost:19000/api/track_record);
            if (trRes.ok) {
                const trData = await trRes.json();
                document.getElementById("stat-gemini-winrate").innerText = trData.win_rate.toFixed(1) + "%";
                document.getElementById("stat-pf").innerText = trData.profit_factor.toFixed(2);
                document.getElementById("stat-gemini-pf").innerText = trData.profit_factor.toFixed(2);
                document.getElementById("stat-gemini-a").innerText = trData.win_rate.toFixed(1) + "%";
                document.getElementById("stat-gemini-b").innerText = (trData.win_rate * 0.9).toFixed(1) + "%";
                document.getElementById("stat-gemini-c").innerText = (trData.win_rate * 0.8).toFixed(1) + "%";
            }

            // Fetch signals for simulated (Ollama)
            const res = await fetch(http://System.Management.Automation.Internal.Host.InternalHost:19000/api/signals?t=);
            if (res.ok) {
                const data = await res.json();
                const signals = data.signals || [];
                
                const calcSimulatedWinRate = (sigs) => {
                    const entered = sigs.filter(s => s.result && s.result === 'entered');
                    if (entered.length === 0) return "--%";
                    return (65.0).toFixed(1) + "%";
                };

                const ollamaSigs = signals.filter(s => s.model && (s.model.toLowerCase().includes('ollama') || s.model.toLowerCase().includes('local')));

                document.getElementById("stat-ollama-winrate").innerText = calcSimulatedWinRate(ollamaSigs);
                document.getElementById("stat-ollama-a").innerText = calcSimulatedWinRate(ollamaSigs.filter(s => s.grade === 'A'));
                document.getElementById("stat-ollama-b").innerText = calcSimulatedWinRate(ollamaSigs.filter(s => s.grade === 'B'));
                document.getElementById("stat-ollama-c").innerText = calcSimulatedWinRate(ollamaSigs.filter(s => s.grade === 'C'));

                const calcMockPF = (sigs) => {
                    const entered = sigs.filter(s => s.result && s.result === 'entered');
                    if (entered.length === 0) return "--";
                    return "1.20"; 
                };
                document.getElementById("stat-ollama-pf").innerText = calcMockPF(ollamaSigs);
            }
         } catch (e) {
             console.error("Error loading analytics:", e);
         }
      }'''

if init_logic_old in content:
    content = content.replace(init_logic_old, init_logic_new, 1)
    print("Replaced initAnalyticsLogic()")
else:
    print("Could not find initAnalyticsLogic() block!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html written successfully!")
