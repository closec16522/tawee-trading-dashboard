import re

file_path = "index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add "Chart Pattern" menu button under "Trading"
trading_menu_regex = re.compile(r'(<button class="menu-item" data-tab="trading">.*?</button>)', re.DOTALL)
pattern_menu_html = r'''\1
              <button class="menu-item" data-tab="patterns">
                <span class="menu-item-left">
                  <span class="menu-item-icon">📈</span>
                  <span>Chart Pattern</span>
                </span>
                <span class="active-dot"></span>
              </button>'''
content = trading_menu_regex.sub(pattern_menu_html, content, count=1)

# 2. Add Tab Switcher Logic
tab_logic_regex = re.compile(r'(} else if \(tab === \'team\'\) \{)')
pattern_tab_logic = r'''} else if (tab === 'patterns') {
          mainContent.innerHTML = getPatternsHTML();
          setTimeout(initPatternsLogic, 50);
        \1'''
content = tab_logic_regex.sub(pattern_tab_logic, content, count=1)

# 3. Add getPatternsHTML function and initPatternsLogic
get_patterns_html = '''
      function getPatternsHTML() {
        return `
          <div style="padding: 24px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 24px;">
              <div>
                <h1 style="font-size:24px; font-weight:700; color:#fff; margin-bottom:8px;">Chart Pattern Monitor 📈</h1>
                <p style="color:var(--text-muted); font-size:14px;">สถานะแพทเทิร์นล่าสุดที่ AI ตรวจพบในทุกคู่เงินที่เฝ้าระวัง และคู่มือการใช้งาน</p>
              </div>
            </div>
            
            <!-- SECTION A: Live Monitor -->
            <div class="chart-container-card" style="padding:20px; margin-bottom:24px;">
              <h2 style="font-size:16px; font-weight:600; color:#fff; margin-top:0; margin-bottom:16px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:12px;">🔴 Live Pattern Status (ทุกเหรียญที่เฝ้าระวัง)</h2>
              <div id="pattern-monitor-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                <div style="color:var(--text-muted); font-size:12px;">กำลังดึงข้อมูลจาก AI...</div>
              </div>
            </div>
            
            <!-- SECTION B: Cheat Sheet -->
            <h2 style="font-size:16px; font-weight:600; color:#fff; margin-top:32px; margin-bottom:16px; padding-left:4px;">📚 Pattern Cheat Sheet (คู่มือแพทเทิร์น)</h2>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            
              <!-- Double Top -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; border-top:3px solid #ef4444;">
                <div style="font-size:16px; font-weight:700; color:#ef4444; display:flex; align-items:center; justify-content:space-between;">
                  Double Top <span>〽️</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted);">Bearish Reversal (เตรียมกลับตัวลง)</div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
                  โครงสร้างราคาชนแนวต้านเดิม 2 ครั้งแต่ไม่ผ่าน (เกิดเป็นตัว M) แสดงถึงแรงซื้อที่หมดลง AI จะมองหาโอกาสเซลล์ (SELL) ทันทีถ้าราคาหลุด Neckline
                </div>
              </div>

              <!-- Double Bottom -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; border-top:3px solid #10b981;">
                <div style="font-size:16px; font-weight:700; color:#10b981; display:flex; align-items:center; justify-content:space-between;">
                  Double Bottom <span>〰️</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted);">Bullish Reversal (เตรียมกลับตัวขึ้น)</div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
                  โครงสร้างราคาย่อมาทดสอบแนวรับเดิม 2 ครั้งแต่ไม่หลุด (เกิดเป็นตัว W) แสดงถึงแรงขายที่หมดลง AI จะมองหาโอกาสบาย (BUY) หากทะลุ Neckline ขึ้นมาได้
                </div>
              </div>
              
              <!-- Head & Shoulders -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; border-top:3px solid #ef4444;">
                <div style="font-size:16px; font-weight:700; color:#ef4444; display:flex; align-items:center; justify-content:space-between;">
                  Head & Shoulders <span>👤</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted);">Bearish Reversal (จุดสูงสุดของรอบ)</div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
                  ราคาทำยอดแหลม 3 ยอด โดยยอดกลางสูงที่สุด (Head) ขนาบด้วยยอดเตี้ย 2 ข้าง (Shoulders) AI จะตีความว่าเทรนขาขึ้นจบลงแล้ว และเตรียมเปลี่ยนเป็นขาลง
                </div>
              </div>
              
              <!-- Inverse Head & Shoulders -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; border-top:3px solid #10b981;">
                <div style="font-size:16px; font-weight:700; color:#10b981; display:flex; align-items:center; justify-content:space-between;">
                  Inverse Head & Shoulders <span>🤸</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted);">Bullish Reversal (จุดต่ำสุดของรอบ)</div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
                  ราคาทำหลุม 3 หลุม โดยหลุมกลางลึกที่สุด (Head) ขนาบด้วยหลุมตื้น 2 ข้าง (Shoulders) AI จะตีความว่าเทรนขาลงสิ้นสุด และเตรียมดีดตัวกลับเป็นขาขึ้นเต็มตัว
                </div>
              </div>

              <!-- Uptrend Structure -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; border-top:3px solid #3b82f6;">
                <div style="font-size:16px; font-weight:700; color:#3b82f6; display:flex; align-items:center; justify-content:space-between;">
                  Higher Highs & Higher Lows <span>📈</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted);">Uptrend Structure (โครงสร้างขาขึ้น)</div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
                  ราคาทำจุดสูงสุดใหม่ (HH) และยกจุดต่ำสุดใหม่ (HL) ต่อเนื่อง เป็นการคอนเฟิร์มว่าแนวโน้มหลักยังเป็นขาขึ้นชัดเจน AI จะหาจังหวะ Follow Buy ตามน้ำ
                </div>
              </div>

              <!-- Downtrend Structure -->
              <div class="chart-container-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; border-top:3px solid #f97316;">
                <div style="font-size:16px; font-weight:700; color:#f97316; display:flex; align-items:center; justify-content:space-between;">
                  Lower Highs & Lower Lows <span>📉</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted);">Downtrend Structure (โครงสร้างขาลง)</div>
                <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
                  ราคาทำจุดต่ำสุดใหม่ (LL) และทำจุดสูงสุดต่ำลงเรื่อยๆ (LH) เป็นการคอนเฟิร์มว่าแนวโน้มหลักยังเป็นขาลงชัดเจน AI จะหาจังหวะ Follow Sell ตามน้ำ
                </div>
              </div>

            </div>
          </div>
        `;
      }

      function initPatternsLogic() {
         renderLivePatternMonitor();
         // Update every 3 seconds to keep it live
         if (window._patternInterval) clearInterval(window._patternInterval);
         window._patternInterval = setInterval(renderLivePatternMonitor, 3000);
      }

      function renderLivePatternMonitor() {
         const container = document.getElementById('pattern-monitor-grid');
         if (!container) return;
         
         const symbolsToWatch = ['XAUUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD'];
         let html = '';
         
         symbolsToWatch.forEach(sym => {
            // Find latest signal for this symbol
            let pat = "ไม่มี (None)";
            let badgeStyle = "background:rgba(255,255,255,0.05); color:var(--text-muted); border:1px solid rgba(255,255,255,0.1);";
            let timeStr = "--";
            
            if (window.signalsHistory && window.signalsHistory.length > 0) {
                const latest = window.signalsHistory.find(s => s.symbol === sym);
                if (latest) {
                    if (latest.chart_pattern && latest.chart_pattern !== "None") {
                        pat = latest.chart_pattern;
                        // Color coding based on bullish/bearish
                        if (pat.includes("Bullish") || pat.includes("Uptrend")) {
                            badgeStyle = "background:rgba(16, 185, 129, 0.1); color:#10b981; border:1px solid rgba(16, 185, 129, 0.3);";
                        } else if (pat.includes("Bearish") || pat.includes("Downtrend")) {
                            badgeStyle = "background:rgba(239, 68, 68, 0.1); color:#ef4444; border:1px solid rgba(239, 68, 68, 0.3);";
                        } else {
                            badgeStyle = "background:rgba(252, 211, 77, 0.1); color:#fcd34d; border:1px solid rgba(252, 211, 77, 0.3);";
                        }
                    } else {
                        pat = "กำลังค้นหา... (None)";
                    }
                    
                    const dt = new Date(latest.timestamp * 1000);
                    timeStr = dt.toLocaleTimeString('th-TH', {hour:'2-digit', minute:'2-digit'});
                } else {
                    pat = "รอรับข้อมูล...";
                }
            } else {
                pat = "กำลังเชื่อมต่อ...";
            }
            
            html += `
              <div style="background:#0f172a; border-radius:8px; padding:16px; border:1px solid rgba(255,255,255,0.05);">
                 <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="font-weight:700; font-size:14px; color:#fff;">${sym}</div>
                    <div style="font-size:10px; color:var(--text-muted);">อัปเดต: ${timeStr}</div>
                 </div>
                 <div style="font-size:12px; padding:6px 10px; border-radius:6px; text-align:center; font-weight:600; line-height:1.4; ${badgeStyle}">
                    ${pat}
                 </div>
              </div>
            `;
         });
         
         container.innerHTML = html;
      }
'''

# Find a good place to inject getPatternsHTML (before getTeamHTML)
team_html_regex = re.compile(r'(function getTeamHTML\(\) \{)')
content = team_html_regex.sub(get_patterns_html + r'\n      \1', content, count=1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Chart Pattern UI patched.")
