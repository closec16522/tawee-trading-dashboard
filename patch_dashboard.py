import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Top Metrics Cards Update
content = re.sub(
    r'<span style="font-size:9\.5px; color:#10b981;">\+6\.53% พอร์ต</span>',
    r'<span id="kpi-equity-growth" style="font-size:9.5px; color:#10b981;">--% พอร์ต</span>',
    content
)

content = re.sub(
    r'<span style="font-size:9\.5px; color:#10b981;">\+12\.2% วันนี้</span>',
    r'<span id="kpi-today-pl-pct" style="font-size:9.5px; color:#10b981;">--% วันนี้</span>',
    content
)

content = re.sub(
    r'<span class="sec-metric-val" style="color:#10b981">42%</span>\s*<span style="font-size:9\.5px; color:#10b981;">\+2\.1% 30d</span>',
    r'<span class="sec-metric-val" id="kpi-winrate" style="color:#10b981">--%</span>\n                    <span id="kpi-winrate-change" style="font-size:9.5px; color:#10b981;">30d info</span>',
    content
)

content = re.sub(
    r'<span class="sec-metric-val">1\.03</span>\s*<span style="font-size:9\.5px; color:var\(--text-muted\);">30d info</span>',
    r'<span class="sec-metric-val" id="kpi-pf">--</span>\n                    <span style="font-size:9.5px; color:var(--text-muted);">30d info</span>',
    content
)

# 2. Add javascript logic in MT5_UPDATE handler (approx line 8100)
# Find the MT5_UPDATE section and insert our logic
kpi_logic = '''
                 const eqGrowthEl = document.getElementById("kpi-equity-growth");
                 if(eqGrowthEl && data.account.equity_growth_30d !== undefined) {
                     eqGrowthEl.innerText = (data.account.equity_growth_30d >= 0 ? "+" : "") + data.account.equity_growth_30d.toFixed(2) + "% พอร์ต";
                     eqGrowthEl.style.color = data.account.equity_growth_30d >= 0 ? "#10b981" : "#ef4444";
                 }
                 const wr30dEl = document.getElementById("kpi-winrate");
                 if(wr30dEl && data.account.win_rate_30d !== undefined) {
                     wr30dEl.innerText = data.account.win_rate_30d.toFixed(1) + "%";
                     wr30dEl.style.color = data.account.win_rate_30d >= 50 ? "#10b981" : "#ef4444";
                 }
                 const pfEl = document.getElementById("kpi-pf");
                 if(pfEl && data.account.profit_factor_30d !== undefined) {
                     pfEl.innerText = data.account.profit_factor_30d.toFixed(2);
                 }
'''

content = content.replace('if(dpEl && data.account.profit !== undefined) {', kpi_logic + '\n                 if(dpEl && data.account.profit !== undefined) {')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Top Metrics patched.")
