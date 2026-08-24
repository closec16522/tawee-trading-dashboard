import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Clear hardcoded Recent Trades
content = re.sub(
    r'<tbody id="dash-recent-tbody">.*?</tbody>',
    r'<tbody id="dash-recent-tbody"></tbody>',
    content,
    flags=re.DOTALL
)

# 2. Clear hardcoded Open Positions (if any, though it looks like it's empty already, but let's be sure)
content = re.sub(
    r'<tbody id="dash-pos-tbody">.*?</tbody>',
    r'<tbody id="dash-pos-tbody"></tbody>',
    content,
    flags=re.DOTALL
)

# 3. Add JS logic for MT5_UPDATE (Positions & Recent Trades)
pos_logic = '''
                 // Open Positions
                 if (data.positions) {
                     const posTitle = document.getElementById("dash-pos-title");
                     if (posTitle) {
                         posTitle.innerText = Open Positions ( ออเดอร์กำลังรัน);
                     }
                     const posBody = document.getElementById("dash-pos-tbody");
                     if (posBody) {
                         let html = "";
                         data.positions.forEach(p => {
                             const sideClass = p.type === "BUY" ? "BUY" : "SELL";
                             const plColor = p.profit >= 0 ? "#10b981" : "#ef4444";
                             html += <tr>
                                 <td><b></b></td>
                                 <td><span class="side "></span></td>
                                 <td></td>
                                 <td></td>
                                 <td></td>
                                 <td><span style="color:; font-weight:700;"></span></td>
                             </tr>;
                         });
                         if (data.positions.length === 0) {
                             html = <tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">ไม่มีออเดอร์ที่กำลังรัน</td></tr>;
                         }
                         posBody.innerHTML = html;
                     }
                 }
                 
                 // Recent Trades
                 if (data.recent_trades) {
                     const recBody = document.getElementById("dash-recent-tbody");
                     if (recBody) {
                         let html = "";
                         data.recent_trades.forEach(t => {
                             const sideClass = t.type === "BUY" ? "BUY" : "SELL";
                             const plColor = t.profit >= 0 ? "#10b981" : "#ef4444";
                             html += <tr>
                                 <td>#</td>
                                 <td><b></b></td>
                                 <td><span class="side "></span></td>
                                 <td></td>
                                 <td></td>
                                 <td><span style="color:; font-weight:700;"></span></td>
                             </tr>;
                         });
                         if (data.recent_trades.length === 0) {
                             html = <tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">ไม่มีประวัติการเทรดล่าสุด</td></tr>;
                         }
                         recBody.innerHTML = html;
                     }
                 }
'''

content = content.replace('// Top Header Updates', pos_logic + '\n                 // Top Header Updates')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Positions and Trades patched.")
