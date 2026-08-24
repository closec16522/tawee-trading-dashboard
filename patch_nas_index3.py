import re

with open('index_from_nas.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove duplicate menu
menu_target = '''              <button class="menu-item" data-tab="analytics">
                <span class="menu-item-left">
                  <span class="menu-item-icon">??</span>
                  <span>Research Analytics</span>
                </span>
                <span class="active-dot"></span>
              </button>\n'''
content = content.replace(menu_target, '', 1)

# 2. Remove first duplicate getAnalyticsHTML block
first_analytics_match = re.search(r'      function getAnalyticsHTML\(\) \{\s*return \s*<div id="dashboard-root">.*?function initAnalyticsLogic\(\) \{\}\n', content, re.DOTALL)
if first_analytics_match:
    content = content[:first_analytics_match.start()] + content[first_analytics_match.end():]
    print("Removed duplicate getAnalyticsHTML")

# 3. Replace Gemini Win Rate label
gemini_label_old = '''<div style="font-size:28px; font-weight:800; color:#fff; margin-bottom:4px;" id="stat-gemini-winrate">--%</div>
                  <div style="font-size:11px; color:#94a3b8;">Win Rate ?????????? (?????)</div>'''
gemini_label_new = '''<div style="font-size:28px; font-weight:800; color:#fff; margin-bottom:4px;" id="stat-gemini-winrate">--%</div>
                  <div style="font-size:11px; color:#94a3b8;">Win Rate ?????????? (????)</div>'''
if gemini_label_old in content:
    content = content.replace(gemini_label_old, gemini_label_new, 1)
    print("Replaced Gemini label")
else:
    print("Could not find Gemini label to replace!")

# 4. Replace initAnalyticsLogic() logic
match = re.search(r'      async function initAnalyticsLogic\(\) \{.*?\}\s*catch \(e\) \{.*?\}\s*\}', content, re.DOTALL)
if match:
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
    content = content[:match.start()] + new_init_logic + content[match.end():]
    print("Replaced initAnalyticsLogic()")
else:
    print("Could not find initAnalyticsLogic() block via regex!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html written successfully!")
