import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix Active Signals
bad_sigs = """html += <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:10px 14px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:12px; color:#fff;"></b>
                    <span style="font-size:11px; font-weight:700; color:;"></span>
                    <span style="font-size:10px; color:var(--text-muted);">Entry  • Conf %</span>
                </div>;"""

good_sigs = """html += `<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:10px 14px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:12px; color:#fff;">${s.symbol}</b>
                    <span style="font-size:11px; font-weight:700; color:${sideColor};">${sideText}</span>
                    <span style="font-size:10px; color:var(--text-muted);">Entry ${s.entry || s.price} • Conf ${s.confidence || 80}%</span>
                </div>`;"""

content = content.replace(bad_sigs, good_sigs)

# 2. Fix Top Movers
bad_movers = """html += <div style="display:flex; justify-content:space-between; font-size:11.5px;">
                                 <b></b>
                                 <span style="color:; font-weight:700;">%</span>
                             </div>;"""

good_movers = """html += `<div style="display:flex; justify-content:space-between; font-size:11.5px;">
                                 <b>${sym}</b>
                                 <span style="color:${color}; font-weight:700;">${chg >= 0 ? "+" : ""}${chg.toFixed(2)}%</span>
                             </div>`;"""
content = content.replace(bad_movers, good_movers)


# 3. Fix Open Positions
bad_pos = """html += <tr>
                                 <td><b></b></td>
                                 <td><span class="side "></span></td>
                                 <td></td>
                                 <td></td>
                                 <td></td>
                                 <td><span style="color:; font-weight:700;"></span></td>
                             </tr>;"""
good_pos = """html += `<tr>
                                 <td><b>${p.symbol}</b></td>
                                 <td><span class="side ${sideClass}">${p.type}</span></td>
                                 <td>${p.volume.toFixed(2)}</td>
                                 <td>${p.price_open.toFixed(5)}</td>
                                 <td>${p.price_current.toFixed(5)}</td>
                                 <td><span style="color:${plColor}; font-weight:700;">${p.profit >= 0 ? "+$" : "-$"}${Math.abs(p.profit).toFixed(2)}</span></td>
                             </tr>`;"""
content = content.replace(bad_pos, good_pos)


# 4. Fix Recent Trades
bad_trades = """html += <tr>
                                 <td>#</td>
                                 <td><b></b></td>
                                 <td><span class="side "></span></td>
                                 <td></td>
                                 <td></td>
                                 <td><span style="color:; font-weight:700;"></span></td>
                             </tr>;"""
good_trades = """html += `<tr>
                                 <td>#${t.ticket}</td>
                                 <td><b>${t.symbol}</b></td>
                                 <td><span class="side ${sideClass}">${t.type}</span></td>
                                 <td>${t.entry.toFixed(5)}</td>
                                 <td>${t.exit.toFixed(5)}</td>
                                 <td><span style="color:${plColor}; font-weight:700;">${t.profit >= 0 ? "+$" : "-$"}${Math.abs(t.profit).toFixed(2)}</span></td>
                             </tr>`;"""
content = content.replace(bad_trades, good_trades)


# 5. Fix Economic Calendar
bad_cal = """html += <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                             <td style="padding:10px; font-family:monospace; color:#38bdf8;"></td>
                             <td style="padding:10px;"><b></b></td>
                             <td style="padding:10px;"></td>
                             <td style="padding:10px; text-align:center;"><span style="background:; color:; border:1px solid ; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:800;"></span></td>
                             <td style="padding:10px; text-align:right; font-weight:800; color:#10b981;"></td>
                             <td style="padding:10px; text-align:right; color:#94a3b8;"></td>
                             <td style="padding:10px; text-align:right; color:#94a3b8;"></td>
                         </tr>;"""
good_cal = """html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                             <td style="padding:10px; font-family:monospace; color:#38bdf8;">${ev.time}</td>
                             <td style="padding:10px;"><b>${ev.currency}</b></td>
                             <td style="padding:10px;">${ev.title}</td>
                             <td style="padding:10px; text-align:center;"><span style="background:${impactBg}; color:${impactColor}; border:1px solid ${impactColor}; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:800;">${ev.impact}</span></td>
                             <td style="padding:10px; text-align:right; font-weight:800; color:#10b981;">${ev.actual || "-"}</td>
                             <td style="padding:10px; text-align:right; color:#94a3b8;">${ev.forecast || "-"}</td>
                             <td style="padding:10px; text-align:right; color:#94a3b8;">${ev.previous || "-"}</td>
                         </tr>`;"""
content = content.replace(bad_cal, good_cal)


# 6. Fix Macro Briefing
bad_macro = """briefEl.innerHTML = `<b>🌟 สรุปภาพรวม:</b> `;"""
good_macro = """briefEl.innerHTML = `<b>🌟 สรุปภาพรวม:</b> ${data.summary.macro_briefing}`;"""
content = content.replace(bad_macro, good_macro)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html fixed!")
