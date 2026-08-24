import re

html_file = 'index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add IDs to the portfolio HTML
html = html.replace('<div class="metric-value">$10,250.00</div>', '<div class="metric-value" id="port-balance">$10,250.00</div>')
html = html.replace('<div class="metric-value" style="color:#10b981;">$10,920.00</div>', '<div class="metric-value" id="port-equity" style="color:#10b981;">$10,920.00</div>')
html = html.replace('<div class="metric-value" style="color:#10b981;">+$670.00</div>', '<div class="metric-value" id="port-float" style="color:#10b981;">+$670.00</div>')
html = html.replace('<div class="metric-value">$8,450.00</div>', '<div class="metric-value" id="port-margin">$8,450.00</div>')

# 2. Add ID to tbody
html = re.sub(r'(<table class="signals-table" style="margin-top:14px;">\s*<thead>.*?</thead>\s*)<tbody>', r'\1<tbody id="port-exposure-tbody">', html, flags=re.DOTALL)

# 3. Inject JS logic into ws.onmessage
js_inject = """
                 if (data.account) {
                     const pb = document.getElementById("port-balance");
                     const pe = document.getElementById("port-equity");
                     const pf = document.getElementById("port-float");
                     const pm = document.getElementById("port-margin");
                     
                     if (pb) pb.innerText = "$" + data.account.balance.toLocaleString(undefined, {minimumFractionDigits: 2});
                     if (pe) pe.innerText = "$" + data.account.equity.toLocaleString(undefined, {minimumFractionDigits: 2});
                     if (pf) {
                         pf.innerText = (data.account.profit >= 0 ? "+$" : "-$") + Math.abs(data.account.profit).toLocaleString(undefined, {minimumFractionDigits: 2});
                         pf.style.color = data.account.profit >= 0 ? "#10b981" : "#ef4444";
                     }
                     if (pm) pm.innerText = "$" + data.account.margin_free.toLocaleString(undefined, {minimumFractionDigits: 2});
                 }
                 
                 if (data.positions && data.account) {
                     const pt = document.getElementById("port-exposure-tbody");
                     if (pt) {
                         let expHtml = "";
                         let expMap = {};
                         let totalProfit = 0;
                         data.positions.forEach(p => {
                             if (!expMap[p.symbol]) expMap[p.symbol] = { vol: 0, profit: 0 };
                             expMap[p.symbol].vol += p.volume;
                             expMap[p.symbol].profit += p.profit;
                             totalProfit += p.profit;
                         });
                         
                         let keys = Object.keys(expMap);
                         if (keys.length === 0) {
                             expHtml = `<tr><td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted);">ไม่มีออเดอร์ที่กำลังรัน</td></tr>`;
                         } else {
                             keys.forEach(sym => {
                                 let market = "Forex";
                                 let mColor = "#f59e0b";
                                 if (sym.includes("BTC") || sym.includes("ETH")) { market = "Crypto"; mColor = "#a855f7"; }
                                 else if (sym.includes("NVDA") || sym.includes("AAPL")) { market = "Stocks"; mColor = "#3b82f6"; }
                                 
                                 let pl = expMap[sym].profit;
                                 let plStr = (pl >= 0 ? "+$" : "-$") + Math.abs(pl).toLocaleString(undefined, {minimumFractionDigits:2});
                                 let plColor = pl >= 0 ? "#10b981" : "#ef4444";
                                 
                                 let eqPct = data.account.equity > 0 ? (Math.abs(pl) / data.account.equity * 100).toFixed(2) + "%" : "0.00%";
                                 
                                 expHtml += `<tr>
                                   <td style="text-align:left; color:${mColor}; font-weight:700;">${market}</td>
                                   <td style="text-align:left; font-weight:800; color:#fff;">${sym}</td>
                                   <td style="text-align:right; font-family:monospace; color:#fff;">${expMap[sym].vol.toFixed(2)} Lot</td>
                                   <td style="text-align:right; font-family:monospace; color:${plColor};">${plStr}</td>
                                   <td style="text-align:right; font-weight:700; color:#10b981;">P/L Impact: ${eqPct}</td>
                                 </tr>`;
                             });
                         }
                         pt.innerHTML = expHtml;
                     }
                 }
                 """

# Find where to inject in ws.onmessage
target_str = "// Open Positions"
html = html.replace(target_str, js_inject + "\n\n                 " + target_str)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html")
