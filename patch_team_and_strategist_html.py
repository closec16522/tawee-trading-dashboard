import re

path_index = 'index.html'
with open(path_index, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Coin Hunter AI Card to Team Trading Page
team_card_coin_hunter = '''
              <!-- Coin Hunter AI -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(52, 214, 230, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_35.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:16px; font-weight:700; color:#34d6e6;">Coin Hunter AI (Asset Scanner)</div>
                    <div style="font-size:12px; color:var(--text-muted);">ค้นหาเหรียญและสินทรัพย์ความผันผวนสูงเข้าสู่ระบบเทรดอัตโนมัติ</div>
                  </div>
                </div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6; flex:1;">
                  <ul style="padding-left:16px; margin:0;">
                    <li>สแกนค้นหาเหรียญ Crypto และคู่เงิน Forex ที่มีวอลลุ่มและความผันผวนสูง (Top Movers)</li>
                    <li>ส่งรายชื่อเหรียญที่มี Momentum แรงที่สุดเข้าสู่ทีมวิเคราะห์ AI โดยอัตโนมัติ</li>
                    <li>ช่วยดึงโอกาสการเทรดใหม่ๆ เข้าพอร์ตโดยไม่ต้องคอยเฝ้าสแกนเหรียญด้วยตัวเอง</li>
                  </ul>
                </div>
                <div style="font-size:11.5px; color:#34d6e6; background:rgba(52, 214, 230, 0.1); border:1px solid rgba(52, 214, 230, 0.25); padding:6px 12px; border-radius:8px;">
                  ⚡ AI Engine: Local Machine (Ollama Volatility Screener)
                </div>
              </div>
'''

if 'Coin Hunter AI (Asset Scanner)' not in content:
    content = content.replace('<!-- Market Analyst -->', team_card_coin_hunter + '\n              <!-- Market Analyst -->')

# 2. Add Coin Hunter AI Row to Trade Strategist Page
strategist_row_coin_hunter = '''
                <!-- Coin Hunter AI -->
                <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px;">
                  <div style="display:flex; gap:12px; align-items:center;">
                    <div style="width:42px; height:42px; background:#1e293b; border-radius:10px; display:flex; justify-content:center; align-items:center; overflow:hidden;">
                      <div style="width:16px; height:32px; background-image:url('assets/characters/char_35.png'); background-position:0 0; transform:scale(1.8); image-rendering:pixelated;"></div>
                    </div>
                    <div>
                      <div style="font-size:16px; font-weight:700; color:#34d6e6;">Coin Hunter AI</div>
                      <div style="font-size:12px; color:var(--text-muted);">นักคัดสรรและค้นหาเหรียญอัตโนมัติ</div>
                    </div>
                  </div>
                  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:13px; color:#cbd5e1; line-height:1.6;">
                    <div>
                      <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                      Volatility Screener & Dynamic Asset Discovery
                    </div>
                    <div>
                      <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                      สแกนค้นหาเหรียญและคู่อัตราแลกเปลี่ยนที่มีโมเมนตัมสูง วอลลุ่มทะลัก เพื่อส่งเข้าทีมวิเคราะห์
                    </div>
                    <div>
                      <strong style="color:#fff;">💡 ทำไมต้องใช้ (Why):</strong><br>
                      เพื่อขยายโอกาสการทำกำไรไปยังเหรียญใหม่ๆ และลดเวลาการนั่งสแกนค้นหาเหรียญด้วยตัวเอง
                    </div>
                    <div>
                      <strong style="color:#fff;">⏱️ จะใช้เมื่อไร (When):</strong><br>
                      ทำงานช่วงต้นของทุกรอบสแกน ก่อนที่ Market Analyst จะลงลึกโครงสร้างราคา
                    </div>
                  </div>
                </div>
'''

if 'นักคัดสรรและค้นหาเหรียญอัตโนมัติ' not in content:
    content = content.replace('<!-- Market Analyst -->', strategist_row_coin_hunter + '\n                <!-- Market Analyst -->')

with open(path_index, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.html with Team Trading & Trade Strategist cards for Coin Hunter AI!")
