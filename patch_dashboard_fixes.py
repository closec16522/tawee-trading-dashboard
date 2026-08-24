import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# --- 1. LOCAL STORAGE INIT ---
init_js = """
      // Initialize KPIs from localStorage
      window._kpiTotal = parseInt(localStorage.getItem('kpiTotal') || "522175");
      window._kpiToday = parseInt(localStorage.getItem('kpiToday') || "733");
      window._kpiReq = parseInt(localStorage.getItem('kpiReq') || "42");
      window._kpiWinRate = parseFloat(localStorage.getItem('kpiWinRate') || "25.9");
      window._kpiProfitFactor = parseFloat(localStorage.getItem('kpiProfitFactor') || "1.01");
      
      // Initialize AI Analysis from localStorage
      const cachedAi = localStorage.getItem('aiAnalysisStr');
      if (cachedAi) {
         try {
             window.aiDict = JSON.parse(cachedAi);
         } catch(e) {}
      }
"""
content = content.replace("function initDashboardLogic() {", "function initDashboardLogic() {\n" + init_js)


# --- 2. REPLACE MOCK VALUES IN HTML ---
content = content.replace("${(window._kpiTotal || 522175).toLocaleString()}", "${(window._kpiTotal).toLocaleString()}")
content = content.replace("${(window._kpiToday || 733).toLocaleString()}", "${(window._kpiToday).toLocaleString()}")
content = content.replace("${(window._kpiReq || 42).toLocaleString()}", "${(window._kpiReq).toLocaleString()}")

content = content.replace('<span class="sec-metric-val" id="kpi-winrate" style="color:#10b981">25.9%</span>', '<span class="sec-metric-val" id="kpi-winrate" style="color:#10b981">${window._kpiWinRate.toFixed(1)}%</span>')
content = content.replace('<span class="sec-metric-val" id="kpi-winrate" style="color:#10b981">--%</span>', '<span class="sec-metric-val" id="kpi-winrate" style="color:#10b981">${window._kpiWinRate.toFixed(1)}%</span>')

content = content.replace('<span class="sec-metric-val" id="kpi-pf">1.01</span>', '<span class="sec-metric-val" id="kpi-pf">${window._kpiProfitFactor.toFixed(2)}</span>')
content = content.replace('<span class="sec-metric-val" id="kpi-pf">--</span>', '<span class="sec-metric-val" id="kpi-pf">${window._kpiProfitFactor.toFixed(2)}</span>')


# --- 3. SET CLOCK LOGIC ---
# In updateClocks()
set_logic = """
          const setDate = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Bangkok' }));
          const setEl = document.getElementById('clock-set');
          if (setEl) {
             setEl.innerText = String(setDate.getHours()).padStart(2, '0') + ':' + 
                               String(setDate.getMinutes()).padStart(2, '0') + ':' + 
                               String(setDate.getSeconds()).padStart(2, '0');
          }
"""
content = content.replace("const nyDate = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));", "const nyDate = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));\n" + set_logic)


# --- 4. WEBSOCKET UPDATE LOGIC (Save to localStorage) ---
update_logic_old = """               window._kpiTotal = (window._kpiTotal || 522175) + 1;
               window._kpiToday = (window._kpiToday || 733) + 1;"""

update_logic_new = """               window._kpiTotal = (window._kpiTotal || 522175) + 1;
               window._kpiToday = (window._kpiToday || 733) + 1;
               window._kpiReq = (window._kpiReq || 42) + 1;
               localStorage.setItem('kpiTotal', window._kpiTotal);
               localStorage.setItem('kpiToday', window._kpiToday);
               localStorage.setItem('kpiReq', window._kpiReq);
               if(window.aiDict) localStorage.setItem('aiAnalysisStr', JSON.stringify(window.aiDict));
               """
content = content.replace(update_logic_old, update_logic_new)

# For WinRate and ProfitFactor pseudo-randomness
wr_pf_old = """                   wrEl.innerText = curWr.toFixed(1) + "%";
                   wrEl.style.color = curWr >= 50 ? "#10b981" : "#ef4444";
               }
               const pfEl = document.getElementById("kpi-profit-factor");
               if(pfEl && Math.random() < 0.05) {
                   let curPf = parseFloat(pfEl.innerText);
                   curPf += (Math.random() * 0.1 - 0.05);
                   if(curPf < 0.1) curPf = 0.1;
                   pfEl.innerText = curPf.toFixed(2);
               }"""

wr_pf_new = """                   wrEl.innerText = curWr.toFixed(1) + "%";
                   wrEl.style.color = curWr >= 50 ? "#10b981" : "#ef4444";
                   window._kpiWinRate = curWr;
                   localStorage.setItem('kpiWinRate', curWr);
               }
               const pfEl = document.getElementById("kpi-pf");
               if(pfEl && Math.random() < 0.05) {
                   let curPf = parseFloat(pfEl.innerText);
                   if (isNaN(curPf)) curPf = window._kpiProfitFactor;
                   curPf += (Math.random() * 0.1 - 0.05);
                   if(curPf < 0.1) curPf = 0.1;
                   pfEl.innerText = curPf.toFixed(2);
                   window._kpiProfitFactor = curPf;
                   localStorage.setItem('kpiProfitFactor', curPf);
               }"""
content = content.replace(wr_pf_old, wr_pf_new)


with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Pass 1: Data persistence and Clocks applied.")
