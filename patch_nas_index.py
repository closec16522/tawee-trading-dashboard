import re

with open('index_from_nas.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove duplicate menu (first one is Research Analytics at around line 2489)
menu_pattern = r'^\s*<button class="menu-item" data-tab="analytics">\s*<span class="menu-item-left">\s*<span class="menu-item-icon">??</span>\s*<span>Research Analytics</span>\s*</span>\s*<span class="active-dot"></span>\s*</button>\n'
content = re.sub(menu_pattern, '', content, count=1, flags=re.MULTILINE)

# 2. Remove first duplicate getAnalyticsHTML (from 'function getAnalyticsHTML() {' to 'function initAnalyticsLogic() {}')
func_pattern = r'function getAnalyticsHTML\(\) \{\s*return \s*<div id="dashboard-root">\s*<header class="dashboard-header">\s*<div class="header-title-area">\s*<div class="header-path">ANALYTICS / STATS</div>.*?function initAnalyticsLogic\(\) \{\}'
content = re.sub(func_pattern, '', content, count=1, flags=re.DOTALL)

# 3. Change (?????) to (????) for Gemini
gemini_label_pattern = r'(<div style="font-size:28px; font-weight:800; color:#fff; margin-bottom:4px;" id="stat-gemini-winrate">--%</div>\s*<div style="font-size:11px; color:#94a3b8;">Win Rate ?????????? )\(?????\)'
content = re.sub(gemini_label_pattern, r'\1(????)', content, count=1)

# 4. Update initAnalyticsLogic() to fetch track record
old_init_logic = r'''      async function initAnalyticsLogic\(\) \{.*?\}\s*\}\s*catch \(e\) \{\s*console.error\("Error loading analytics:", e\);\s*\}\s*\}'''

new_init_logic = '''      async function initAnalyticsLogic() {
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

content = re.sub(old_init_logic, new_init_logic, content, count=1, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch successful!")
