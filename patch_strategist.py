import os
import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert Sidebar Menu
sidebar_btn = """              <button class="menu-item" data-tab="team">
                <span class="menu-item-left">
                  <span class="menu-item-icon">👥</span>
                  <span>Team Trading</span>
                </span>
                <span class="active-dot"></span>
              </button>
              <button class="menu-item" data-tab="strategist">
                <span class="menu-item-left">
                  <span class="menu-item-icon">🧠</span>
                  <span>Trade Strategist</span>
                </span>
                <span class="active-dot"></span>
              </button>"""
content = content.replace("""              <button class="menu-item" data-tab="team">
                <span class="menu-item-left">
                  <span class="menu-item-icon">👥</span>
                  <span>Team Trading</span>
                </span>
                <span class="active-dot"></span>
              </button>""", sidebar_btn)

# 2. Insert Javascript Router Logic
router_logic = """        } else if (tab === 'strategist') {
          mainContent.innerHTML = getStrategistHTML();
        } else if (tab === 'team') {"""
content = content.replace("        } else if (tab === 'team') {", router_logic)


# 3. Insert getStrategistHTML function
strategist_html = """      function getStrategistHTML() {
        return `
          <div style="padding: 24px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 24px;">
              <div>
                <h1 style="font-size:24px; font-weight:700; color:#fff; margin-bottom:8px;">Trade Strategist 🧠</h1>
                <p style="color:var(--text-muted); font-size:14px;">เจาะลึกกลยุทธ์การเทรดของ AI Agent แต่ละตัว ว่าใช้วิธีอะไร ทำไมถึงใช้ และควรใช้ในจังหวะไหน</p>
              </div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr; gap: 20px;">
            
              <!-- Market Analyst -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(52, 214, 230, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_17.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#34d6e6;">Market Analyst</div>
                    <div style="font-size:13px; color:var(--text-muted);">นักวิเคราะห์โครงสร้างตลาดและแนวโน้ม</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Price Action & Chart Patterns
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    วิเคราะห์แนวรับ-แนวต้านหลัก และค้นหารูปแบบกราฟคลาสสิก (เช่น Double Top, Head & Shoulders) ในหลาย Timeframe
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    เพื่อทำความเข้าใจพฤติกรรมมวลชนและโครงสร้างตลาดในภาพรวม ช่วยให้ทีมไม่เทรดสวนเทรนด์หลัก
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    เป็นด่านแรกของการวิเคราะห์ ทำงานทุกครั้งที่แท่งเทียนปิด เพื่ออัปเดตมุมมองทิศทางตลาด (Directional Bias)
                  </div>
                </div>
              </div>

              <!-- SMC Strategist -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(245, 196, 81, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_29.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#f5c451;">SMC Strategist</div>
                    <div style="font-size:13px; color:var(--text-muted);">ผู้เชี่ยวชาญการหาจุดเข้าเทรดระดับสถาบัน</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Smart Money Concepts & Fibonacci OTE
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    แกะรอยรายใหญ่โดยหา Liquidity Sweep, Fair Value Gap (FVG), Order Blocks และกาง Fibonacci หาจุดเข้า
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    เพื่อหลีกเลี่ยงกับดักรายย่อย (Retail Traps) และหาจุดเข้าเทรดที่มีความแม่นยำสูงพร้อม Stop Loss ที่สั้น (High R:R)
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    ใช้ทันทีหลังจาก Market Analyst ยืนยันเทรนด์ เพื่อรอจังหวะย่อตัว (Pullback) เข้าสู่โซนพรีเมียม
                  </div>
                </div>
              </div>

              <!-- News Analyst -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(255, 126, 182, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_21.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#ff7eb6;">News Analyst</div>
                    <div style="font-size:13px; color:var(--text-muted);">นักวิเคราะห์ข่าวเศรษฐกิจมหภาค</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Fundamental Analysis & Event-Driven Filter
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    มอนิเตอร์ข่าวเศรษฐกิจแบบ Real-time (CPI, Non-Farm, FED) และวิเคราะห์ผลกระทบที่มีต่อกราฟ
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    เพราะข่าวแรงๆ สามารถทำลายโครงสร้างทางเทคนิค (Technical Analysis) ได้ในเสี้ยววินาที จึงต้องมีไว้กรองความเสี่ยง
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    ทำงานตลอดเวลาอยู่เบื้องหลัง โดยจะส่งสัญญาณเตือนให้หยุดเทรด 30 นาทีก่อนและหลังข่าวแดง (High Impact)
                  </div>
                </div>
              </div>

              <!-- Risk Manager -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(255, 162, 74, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_26.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#ffa24a;">Risk Manager</div>
                    <div style="font-size:13px; color:var(--text-muted);">ผู้พิทักษ์เงินทุนและคำนวณความเสี่ยง</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Capital Preservation & Dynamic Position Sizing
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    คำนวณ Lot Size อัตโนมัติจากระยะ Stop Loss โดยบังคับความเสี่ยงสูงสุดไม่เกิน 1-2% ของเงินทุน (Equity)
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    กลยุทธ์ที่ดีแค่ไหนก็พอร์ตแตกได้ถ้า Overtrade การจำกัดความเสี่ยงคือหัวใจสำคัญของการเทรดระยะยาว
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    ก่อนการส่งคำสั่งซื้อขายทุกครั้ง หาก Trade Setup มี R:R ที่ไม่คุ้มค่า เอเจนต์ตัวนี้จะ Reject สัญญาณนั้นทิ้งทันที
                  </div>
                </div>
              </div>
              
              <!-- Portfolio Manager -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(106, 141, 255, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_57.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#6a8dff;">Portfolio Manager</div>
                    <div style="font-size:13px; color:var(--text-muted);">ผู้ดูแลภาพรวมและกำไรที่กำลังวิ่ง</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Drawdown Management & Exposure Control
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    คอยดูภาพรวมทั้งหมดว่าเปิดออเดอร์ทับซ้อนกันมากไปหรือไม่ และดูแลไม้ที่กำลังลบไม่ให้กระทบ Margin
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    เพื่อป้องกันเหตุการณ์ "เทรดหลายคู่แต่เป็นทิศทางเดียวกันหมด" ซึ่งจะทำให้พอร์ตรับความเสี่ยงเกินจริง
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    เฝ้าดูตลอดเวลา หากเริ่มมีการเสียติดต่อกัน (Losing Streak) จะแนะนำให้พักหรือลด Lot Size
                  </div>
                </div>
              </div>

              <!-- Trade Executor -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(55, 210, 122, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_54.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#37d27a;">Trade Executor</div>
                    <div style="font-size:13px; color:var(--text-muted);">มือปืนส่งคำสั่งความเร็วสูง</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Low-Latency Execution & Trade Management
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    ยิงคำสั่งผ่าน MT5 API (Market, Limit, Stop) และทำการเลื่อน Stop Loss กันทุน (Break Even) อัตโนมัติ
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    เพื่อให้ได้ราคาเข้าที่ดีที่สุด (Slippage น้อยสุด) และปกป้องกำไรที่ได้มาแล้วไม่ให้กลับกลายเป็นขาดทุน
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    เมื่อ Supervisor อนุมัติแผนการเทรด และคอยดูแลออเดอร์นั้นไปจนกว่าจะชน TP หรือ SL
                  </div>
                </div>
              </div>

              <!-- Supervisor AI -->
              <div class="chart-container-card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
                <div style="display:flex; gap:16px; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
                  <div style="width:64px; height:64px; background:linear-gradient(180deg,#1a2236,#10172a); border-radius:12px; border:1px solid rgba(139, 92, 246, 0.3); display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <div style="width:16px; height:32px; background-image:url('assets/characters/char_1.png'); background-position:0 0; transform:scale(2); image-rendering:pixelated;"></div>
                  </div>
                  <div>
                    <div style="font-size:18px; font-weight:700; color:#8b5cf6;">Supervisor AI</div>
                    <div style="font-size:13px; color:var(--text-muted);">หัวหน้าทีมและผู้อนุมัติขั้นสุดท้าย</div>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                  <div>
                    <strong style="color:#fff;">🎯 กลยุทธ์ (Strategy):</strong><br>
                    Multi-Agent Consensus (มติเอกฉันท์)
                  </div>
                  <div>
                    <strong style="color:#fff;">⚙️ วิธีทำงาน (Method):</strong><br>
                    รวบรวมข้อมูลจาก Analyst ทุกตัว เช็คความเสี่ยง และเช็คข่าว หากทุกคนเห็นพ้องต้องกันจึงจะสั่งยิง
                  </div>
                  <div>
                    <strong style="color:#fff;">💡 ทำไมถึงใช้ (Why):</strong><br>
                    เพื่อป้องกันไม่ให้ AI ตัวใดตัดสินใจพลาด การใช้เสียงข้างมากและด่านกรองหลายชั้นช่วยเพิ่ม Win Rate
                  </div>
                  <div>
                    <strong style="color:#fff;">⏱️ จังหวะที่ใช้ (When):</strong><br>
                    เป็นด่านสุดท้ายก่อนส่งออเดอร์ และทำหน้าที่สรุปรายงานรายวันแจ้งให้มนุษย์ทราบ
                  </div>
                </div>
              </div>

            </div>
          </div>
        `;
      }
      
      function getTeamHTML() {"""

content = content.replace("      function getTeamHTML() {", strategist_html)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched index.html with Strategist view.")
