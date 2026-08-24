import re

file_path = "index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add "Team Trading" menu button
trade_menu_pattern = r'(<button class="menu-item" data-tab="trade">.*?</button>)'
# We will match the entire block. Let's make it simpler, we just find data-tab="trade" block end.
# Actually, the block spans multiple lines:
#               <button class="menu-item" data-tab="trade">
#                 <span class="menu-item-left">
#                   <span class="menu-item-icon">🎮</span>
#                   <span>AI Office</span>
#                 </span>
#                 <span style="display: flex; align-items: center;">
#                   <span class="badge-demo" style="...">Pixels</span>
#                 </span>
#               </button>

trade_menu_regex = re.compile(r'(<button class="menu-item" data-tab="trade">.*?</button>)', re.DOTALL)
team_menu_html = r'''\1
              <button class="menu-item" data-tab="team">
                <span class="menu-item-left">
                  <span class="menu-item-icon">👥</span>
                  <span>Team Trading</span>
                </span>
                <span class="active-dot"></span>
              </button>'''

content = trade_menu_regex.sub(team_menu_html, content, count=1)

# 2. Add Tab Switcher Logic
# } else if (tab === 'market') {
tab_logic_regex = re.compile(r'(} else if \(tab === \'market\'\) \{)')
team_tab_logic = r'''} else if (tab === 'team') {
          mainContent.innerHTML = getTeamHTML();
          // setTimeout(initTeamLogic, 50);
        \1'''

content = tab_logic_regex.sub(team_tab_logic, content, count=1)

# 3. Add getTeamHTML function
# Let's add it right before function getCommandCenterHTML()
get_team_html = '''
      function getTeamHTML() {
        return `
          <div style="padding: 24px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 24px;">
              <div>
                <h1 style="font-size:24px; font-weight:700; color:#fff; margin-bottom:8px;">Team Trading 🧠</h1>
                <p style="color:var(--text-muted); font-size:14px;">เจาะลึกความสามารถของ AI Agent แต่ละตัว และระบบหลังบ้านที่ขับเคลื่อนมัน</p>
              </div>
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px;">
            
              <!-- Market Analyst -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/market_analyst.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(52, 214, 230, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#34d6e6;">Market Analyst</div>
                    <div style="font-size:12px; color:var(--text-muted);">วิเคราะห์โครงสร้างตลาด (SMC) & กราฟแพทเทิร์น</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>สแกนหา Trend, Order Blocks และ Break of Structure (BOS)</li>
                    <li>ตรวจสอบ Chart Patterns (Double Top/Bottom, Head & Shoulders)</li>
                    <li>ให้คะแนนความเชื่อมั่น (Confidence) สำหรับขาขึ้น/ขาลง</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">Ollama (Local) / Gemini 1.5 Pro</span>
                </div>
              </div>
              
              <!-- SMC Strategist -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/smc_strategy.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(245, 196, 81, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#f5c451;">SMC Strategist</div>
                    <div style="font-size:12px; color:var(--text-muted);">วางแผนกลยุทธ์ SMC & Fibonacci</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>รับข้อมูลดิบมาตีความหาจุดเข้า (Entry), จุดตัดขาดทุน (SL) และทำกำไร (TP)</li>
                    <li>มองหา Liquidity Sweep และ Imbalance (FVG) ในโครงสร้างราคา</li>
                    <li>ปรับเปลี่ยนมุมมองอัตโนมัติรายสัปดาห์ (Weekly Strategy Review)</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">Gemini 1.5 Pro</span>
                </div>
              </div>
              
              <!-- News Analyst -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/news_analyst.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(255, 126, 182, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#ff7eb6;">News Analyst</div>
                    <div style="font-size:12px; color:var(--text-muted);">วิเคราะห์ข่าวสาร/เศรษฐกิจมหภาค</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>ดึงข้อมูลจาก Bloomberg / Reuters (จำลอง)</li>
                    <li>แปลผลกระทบจากตัวเลขเศรษฐกิจ (CPI, Non-Farm, FED Rate)</li>
                    <li>แจ้งเตือนความผันผวนสูง (High Impact) ที่อาจชน SL ได้</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">GLM-3.2 Real-time News Impact</span>
                </div>
              </div>
              
              <!-- Risk Manager -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/risk_manager.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(255, 162, 74, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#ffa24a;">Risk Manager</div>
                    <div style="font-size:12px; color:var(--text-muted);">คำนวณความเสี่ยง/ปรับ Lot Size</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>คำนวณ Risk Per Trade (Max 1% - 2% ของ Equity)</li>
                    <li>เช็คระยะห่าง Stop Loss เพื่อแปลงเป็น Position Size (Lot) ที่เหมาะสมที่สุด</li>
                    <li>ประเมิน Risk/Reward Ratio หากต่ำกว่าเกณฑ์จะสั่ง Reject สัญญาณทันที</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">Gemini 1.5 Pro</span>
                </div>
              </div>
              
              <!-- Portfolio Manager -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/portfolio_manager.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(106, 141, 255, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#6a8dff;">Portfolio Manager</div>
                    <div style="font-size:12px; color:var(--text-muted);">จัดสรรพอร์ต/รักษาระดับ Exposure</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>ดูแลภาพรวมของ Account Balance, Equity และ Free Margin</li>
                    <li>ป้องกันการ Overtrade ในคู่เงินกลุ่มเดียวกัน (เช่น ไม่เปิด USD ซ้อนกันมากเกินไป)</li>
                    <li>หาก Drawdown เริ่มสูง จะปรับโหมดเป็น Defensive ทันที</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">Gemini 1.5 Pro</span>
                </div>
              </div>

              <!-- Supervisor AI -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/supervisor.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(154, 123, 255, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#9a7bff;">Supervisor AI (CEO)</div>
                    <div style="font-size:12px; color:var(--text-muted);">ตรวจทานขั้นสุดท้าย/อนุมัติคำสั่ง</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>รับข้อมูลทั้งหมดจาก Agent ตัวอื่นๆ มารวมกัน (Multi-Agent Consensus)</li>
                    <li>ประเมินน้ำหนักความน่าจะเป็น หากเสียงแตกจะเป็นคนเคาะว่า "ลุย" หรือ "รอ"</li>
                    <li>พิมพ์สรุปเหตุผลการตัดสินใจส่งกลับมาที่ Dashboard (Live System Alert)</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">Gemini 1.5 Pro (Max Reasoning)</span>
                </div>
              </div>

              <!-- Trade Executor -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <img src="https://api.pixelaivision.com/static/characters/trade_executor.png" style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(55, 210, 122, 0.3);">
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#37d27a;">Trade Executor</div>
                    <div style="font-size:12px; color:var(--text-muted);">ยิงคำสั่งเชื่อมต่อ MT5 (Gateway)</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>เชื่อมต่อ API ไปยัง MetaTrader 5 แบบ Latency ต่ำ</li>
                    <li>รับหน้าทียิงออเดอร์, ตั้ง Pending Order (Limit/Stop)</li>
                    <li>จัดการ Trailing Stop ขยับ SL บังทุน (Break Even) อัตโนมัติเมื่อราคาวิ่งไปตามเป้า</li>
                  </ul>
                </div>
                <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:12px;">
                  <span style="color:var(--text-muted);">⚡ AI Engine:</span> <span style="color:#10b981; font-weight:600;">Python C-Binding (Hardcoded Logic)</span>
                </div>
              </div>
              
            </div>
          </div>
        `;
      }
'''

cmd_center_regex = re.compile(r'(function getCommandCenterHTML\(\) \{)')
content = cmd_center_regex.sub(get_team_html + r'\n      \1', content, count=1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Team Trading menu added.")
