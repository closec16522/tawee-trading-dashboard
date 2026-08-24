import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Clear hardcoded Top Movers
content = re.sub(
    r'<div class="signals-card" style="min-height: 180px;">\s*<span class="signals-title">Market Overview \(Top Movers\)</span>.*?</div>\s*</div>',
    r'''<div class="signals-card" style="min-height: 180px;">
                  <span class="signals-title">Market Overview (Top Movers)</span>
                  <div id="dash-top-movers" style="display:flex; flex-direction:column; gap:8px; margin-top:4px;">
                  </div>
                </div>''',
    content,
    flags=re.DOTALL
)

# 2. Add dash-macro-briefing id
content = re.sub(
    r'<p style="font-size:12px; color:#e2e8f0; line-height:1\.6; margin-bottom:8px;">\s*<b>🌟 สรุปภาพรวมสัปดาห์นี้:</b>.*?</p>',
    r'<p id="dash-macro-briefing" style="font-size:12px; color:#e2e8f0; line-height:1.6; margin-bottom:8px;"><b>🌟 สรุปภาพรวมสัปดาห์นี้:</b> รอข้อมูลวิเคราะห์จาก AI...</p>',
    content,
    flags=re.DOTALL
)

# 3. Clear Calendar Table body
content = re.sub(
    r'<tbody style="font-size:11\.5px; color:#e2e8f0;">.*?</tbody>',
    r'<tbody id="dash-calendar-tbody" style="font-size:11.5px; color:#e2e8f0;"></tbody>',
    content,
    flags=re.DOTALL
)

# 4. Add logic to NEWS_UPDATE for Calendar and Macro
news_logic = '''
            if (data.type === "NEWS_UPDATE") {
                 const briefEl = document.getElementById("dash-macro-briefing");
                 if (briefEl && data.summary && data.summary.macro_briefing) {
                     briefEl.innerHTML = <b>🌟 สรุปภาพรวม:</b> ;
                 }
                 const calBody = document.getElementById("dash-calendar-tbody");
                 if (calBody && data.summary && data.summary.calendar_events) {
                     let html = "";
                     data.summary.calendar_events.forEach(ev => {
                         const impactColor = ev.impact === "High" ? "#ef4444" : (ev.impact === "Medium" ? "#f59e0b" : "#3b82f6");
                         const impactBg = ev.impact === "High" ? "rgba(239,68,68,0.18)" : (ev.impact === "Medium" ? "rgba(245,158,11,0.18)" : "rgba(59,130,246,0.18)");
                         html += <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                             <td style="padding:10px; font-family:monospace; color:#38bdf8;"></td>
                             <td style="padding:10px;"><b></b></td>
                             <td style="padding:10px;"></td>
                             <td style="padding:10px; text-align:center;"><span style="background:; color:; border:1px solid ; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:800;"></span></td>
                             <td style="padding:10px; text-align:right; font-weight:800; color:#10b981;"></td>
                             <td style="padding:10px; text-align:right; color:#94a3b8;"></td>
                             <td style="padding:10px; text-align:right; color:#94a3b8;"></td>
                         </tr>;
                     });
                     calBody.innerHTML = html;
                 }
'''
content = content.replace('if (data.type === "NEWS_UPDATE") {', news_logic)

# 5. Add logic to MT5_UPDATE for Top Movers
movers_logic = '''
                 // Top Movers
                 if (data.market) {
                     const moversBody = document.getElementById("dash-top-movers");
                     if (moversBody) {
                         let html = "";
                         // Sort by absolute change pct
                         const symbols = Object.keys(data.market).sort((a,b) => Math.abs(data.market[b].change_pct || 0) - Math.abs(data.market[a].change_pct || 0));
                         symbols.slice(0, 5).forEach(sym => {
                             const chg = data.market[sym].change_pct || 0;
                             const color = chg >= 0 ? "#10b981" : "#ef4444";
                             html += <div style="display:flex; justify-content:space-between; font-size:11.5px;">
                                 <b></b>
                                 <span style="color:; font-weight:700;">%</span>
                             </div>;
                         });
                         moversBody.innerHTML = html;
                     }
                 }
'''
content = content.replace('// Open Positions', movers_logic + '\n                 // Open Positions')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Calendar, Macro, and Top Movers patched.")
