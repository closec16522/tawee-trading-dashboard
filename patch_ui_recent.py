import re
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

target1 = """<table class="dtable" style="margin-top:6px;">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>SYMBOL</th>
                      <th>SIDE</th>
                      <th>ENTRY</th>
                      <th>EXIT</th>
                      <th>P/L</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>"""

replacement1 = """<table class="dtable" style="margin-top:6px;">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>SYMBOL</th>
                      <th>SIDE</th>
                      <th>ENTRY</th>
                      <th>EXIT</th>
                      <th>P/L</th>
                    </tr>
                  </thead>
                  <tbody id="dash-recent-tbody">
                    <tr>"""

content = content.replace(target1, replacement1)

target2 = """                    const tsTbody = document.getElementById("trades-pos-tbody");
                   if (tsTbody) tsTbody.innerHTML = html;
                   const tsTitle = document.getElementById("trades-pos-title");
                   if (tsTitle) tsTitle.innerText = `Open Positions (${posCount})`;
                   
                   // --- Update Right Panel (Live Trades) ---"""

replacement2 = """                    const tsTbody = document.getElementById("trades-pos-tbody");
                   if (tsTbody) tsTbody.innerHTML = html;
                   const tsTitle = document.getElementById("trades-pos-title");
                   if (tsTitle) tsTitle.innerText = `Open Positions (${posCount})`;
                   
                   // --- Update Recent Trades ---
                   if (data.recent_trades) {
                       let rtHtml = "";
                       if (data.recent_trades.length === 0) {
                           rtHtml = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#64748b;">ไม่มีประวัติการเทรดล่าสุด</td></tr>`;
                       } else {
                           data.recent_trades.forEach(rt => {
                               const plColor = rt.profit >= 0 ? "#10b981" : "#ef4444";
                               const sideClass = rt.type === "BUY" ? "side BUY" : "side SELL";
                               rtHtml += `<tr>
                                   <td>#${rt.ticket}</td>
                                   <td><b>${rt.symbol}</b></td>
                                   <td><span class="${sideClass}">${rt.type}</span></td>
                                   <td>${rt.entry}</td>
                                   <td>${rt.exit}</td>
                                   <td><span style="color:${plColor}; font-weight:700;">${formatCurrency(rt.profit)}</span></td>
                               </tr>`;
                           });
                       }
                       const rtTbody = document.getElementById("dash-recent-tbody");
                       if (rtTbody) rtTbody.innerHTML = rtHtml;
                   }
                   
                   // --- Update Right Panel (Live Trades) ---"""

content = content.replace(target2, replacement2)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("index.html recent trades patched")