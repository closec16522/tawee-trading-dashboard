import re

gw_file = 'mt5_backend/mt5_gateway.py'
with open(gw_file, 'r', encoding='utf-8') as f:
    gw_code = f.read()

endpoint_code = """
@app.get("/api/track_record")
async def api_track_record():
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=365)
    deals = mt5.history_deals_get(start, now)
    
    if not deals:
        return {"total_return": 0, "win_rate": 0, "profit_factor": 0, "avg_win_r": 0, "total_trades": 0, "curve": [], "trades": []}
        
    closed = [d for d in deals if d.entry == 1]
    sorted_closed = sorted(closed, key=lambda x: x.time)
    
    total_trades = len(closed)
    if total_trades == 0:
        return {"total_return": 0, "win_rate": 0, "profit_factor": 0, "avg_win_r": 0, "total_trades": 0, "curve": [], "trades": []}
        
    wins = [d for d in closed if d.profit > 0]
    losses = [d for d in closed if d.profit < 0]
    win_rate = (len(wins) / total_trades * 100)
    
    gross_profit = sum(d.profit for d in wins)
    gross_loss = sum(abs(d.profit) for d in losses)
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
    
    avg_win = (gross_profit / len(wins)) if len(wins) > 0 else 0
    avg_loss = (gross_loss / len(losses)) if len(losses) > 0 else 0
    avg_r = (avg_win / avg_loss) if avg_loss > 0 else avg_win
    
    acc_info = mt5.account_info()
    eq = acc_info.equity if acc_info else 10000
    net_profit = gross_profit - gross_loss
    initial_bal = eq - net_profit
    total_return_pct = (net_profit / initial_bal * 100) if initial_bal > 0 else 0
    
    curve = []
    cum = 0
    for d in sorted_closed:
        cum += d.profit
        curve.append({
            "time": datetime.datetime.fromtimestamp(d.time).strftime("%d %b"),
            "pct": (cum / initial_bal * 100) if initial_bal > 0 else 0
        })
        
    recent50 = []
    for d in reversed(sorted_closed[-50:]):
        recent50.append({
            "ticket": d.position_id,
            "symbol": d.symbol,
            "type": "BUY" if d.type == 1 else "SELL",
            "profit": d.profit,
            "time": datetime.datetime.fromtimestamp(d.time).strftime("%d %b %H:%M"),
            "pct": (d.profit / initial_bal * 100) if initial_bal > 0 else 0
        })
        
    return {
        "total_return": total_return_pct,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win_r": avg_r,
        "total_trades": total_trades,
        "curve": curve,
        "trades": recent50
    }
"""
gw_code = gw_code + "\n" + endpoint_code

with open(gw_file, 'w', encoding='utf-8') as f:
    f.write(gw_code)
print("Added /api/track_record to mt5_gateway.py")

# Now patch index.html
html_file = 'index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Add IDs to track record KPI cards
html = html.replace('<div class="metric-value" style="color:#10b981;">+109.8%</div>', '<div class="metric-value" id="tr-total-return" style="color:#10b981;">...</div>')
html = html.replace('<div class="metric-sub" style="color:#10b981;">+109.8R ที่เสี่ยง 1%/ไม้</div>', '<div class="metric-sub" id="tr-total-return-sub" style="color:#10b981;">...</div>')
html = html.replace('<div class="metric-value">42.9%</div>', '<div class="metric-value" id="tr-winrate">...</div>')
html = html.replace('<div class="metric-sub">503 ไม้</div>', '<div class="metric-sub" id="tr-winrate-sub">...</div>')
html = html.replace('<div class="metric-value">1.42</div>', '<div class="metric-value" id="tr-pf">...</div>')
html = html.replace('<div class="metric-sub" style="color:#10b981;">กำไรดีมาก</div>', '<div class="metric-sub" id="tr-pf-sub" style="color:#10b981;">...</div>')
html = html.replace('<div class="metric-value">+1.72R</div>', '<div class="metric-value" id="tr-avgr">...</div>')
html = html.replace('<div class="metric-value">503</div>', '<div class="metric-value" id="tr-totaltrades">...</div>')

# Add ID to table body
html = re.sub(r'<tbody id="port-exposure-tbody">.*?</tbody>', r'<tbody id="tr-recent50-tbody"></tbody>', html, flags=re.DOTALL)

# Inject logic into initTrackRecordLogic
js_inject = """
      function initTrackRecordLogic() {
        const cv = document.getElementById('track-record-canvas');
        if (!cv) return;
        const ctx = cv.getContext('2d');
        cv.width = cv.parentElement.clientWidth - 40;
        cv.height = 200;
        
        fetch('/api/track_record')
          .then(res => res.json())
          .then(data => {
            const elTR = document.getElementById('tr-total-return');
            const elTRsub = document.getElementById('tr-total-return-sub');
            if (elTR) {
                elTR.innerText = (data.total_return >= 0 ? "+" : "") + data.total_return.toFixed(2) + "%";
                elTR.style.color = data.total_return >= 0 ? "#10b981" : "#ef4444";
            }
            if (elTRsub) {
                elTRsub.innerText = (data.total_return >= 0 ? "+" : "") + data.total_return.toFixed(2) + "R ที่เสี่ยง 1%/ไม้";
                elTRsub.style.color = data.total_return >= 0 ? "#10b981" : "#ef4444";
            }
            const elWR = document.getElementById('tr-winrate');
            const elWRsub = document.getElementById('tr-winrate-sub');
            if (elWR) elWR.innerText = data.win_rate.toFixed(1) + "%";
            if (elWRsub) elWRsub.innerText = data.total_trades + " ไม้";
            
            const elPF = document.getElementById('tr-pf');
            const elPFsub = document.getElementById('tr-pf-sub');
            if (elPF) elPF.innerText = data.profit_factor.toFixed(2);
            if (elPFsub) {
                if (data.profit_factor > 1.5) { elPFsub.innerText = "กำไรดีมาก"; elPFsub.style.color = "#10b981"; }
                else if (data.profit_factor > 1) { elPFsub.innerText = "กำไรพอใช้"; elPFsub.style.color = "#f59e0b"; }
                else { elPFsub.innerText = "ขาดทุน"; elPFsub.style.color = "#ef4444"; }
            }
            const elAvgR = document.getElementById('tr-avgr');
            if (elAvgR) elAvgR.innerText = (data.avg_win_r > 0 ? "+" : "") + data.avg_win_r.toFixed(2) + "R";
            const elTot = document.getElementById('tr-totaltrades');
            if (elTot) elTot.innerText = data.total_trades;
            
            // Render Table
            const tbody = document.getElementById('tr-recent50-tbody');
            if (tbody) {
                if (data.trades.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-muted);">ไม่มีประวัติการเทรด</td></tr>';
                } else {
                    let tHtml = "";
                    data.trades.forEach(t => {
                        let win = t.profit >= 0;
                        let rText = win ? "+" + t.pct.toFixed(2) + "%" : t.pct.toFixed(2) + "%";
                        tHtml += `<tr>
                          <td style="text-align:left; font-weight:800; color:#fff;">${t.symbol}</td>
                          <td style="text-align:center;"><span class="sig-badge ${t.type === 'BUY'?'buy':'sell'}">${t.type}</span></td>
                          <td style="text-align:center; color:${win?'#10b981':'#ef4444'};">${win?'ชนะ':'แพ้'}</td>
                          <td style="text-align:center; color:var(--text-muted);">-</td>
                          <td style="text-align:right; font-weight:700; color:${win?'#10b981':'#ef4444'};">${rText}</td>
                          <td style="text-align:right; color:var(--text-muted); font-size:11px;">${t.time}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = tHtml;
                }
            }
            
            // Draw simple equity curve
            if (data.curve.length > 0) {
                ctx.clearRect(0, 0, cv.width, cv.height);
                ctx.beginPath();
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 2;
                let minP = Math.min(0, ...data.curve.map(c => c.pct));
                let maxP = Math.max(1, ...data.curve.map(c => c.pct));
                let range = maxP - minP;
                let stepX = cv.width / Math.max(1, (data.curve.length - 1));
                
                data.curve.forEach((c, i) => {
                    let x = i * stepX;
                    let y = cv.height - ((c.pct - minP) / range) * cv.height * 0.8 - (cv.height * 0.1);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();
            }
          })
          .catch(e => console.error("Error fetching track record:", e));
"""

# Replace the original function body
html = re.sub(r'function initTrackRecordLogic\(\) \{.*?(?=function)', js_inject + "\n      ", html, flags=re.DOTALL)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html")
