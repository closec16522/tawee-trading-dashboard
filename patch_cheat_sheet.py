import re

def svg_card(title, variant, description, svg_content, is_bullish):
    color = "#10b981" if is_bullish else "#ef4444"
    border = f"border-top: 3px solid {color};"
    
    return f"""
              <div class="chart-container-card" style="padding:16px; display:flex; flex-direction:column; gap:12px; {border}">
                <div style="font-size:14px; font-weight:700; color:{color}; display:flex; align-items:center; justify-content:space-between;">
                  {title}
                </div>
                <div style="font-size:10px; color:var(--text-muted); text-transform:uppercase;">{variant}</div>
                <div style="background:#0f172a; border-radius:6px; padding:10px; display:flex; justify-content:center; align-items:center;">
                  <svg viewBox="0 0 100 60" style="width:100%; max-width:200px; height:auto;">
                    {svg_content}
                  </svg>
                </div>
                <div style="font-size:12px; color:#cbd5e1; line-height:1.5; flex:1;">
                  {description}
                </div>
              </div>
"""

# Common stroke styles
price = 'stroke="#38bdf8" stroke-width="2" fill="none" stroke-linejoin="round"'
trend = 'stroke="#f97316" stroke-width="1.5" stroke-dasharray="3,3" fill="none"'
arrow = 'stroke="#f97316" stroke-width="1.5" fill="none" marker-end="url(#arrow)"'

# Defs for arrow
defs = """
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#f97316" />
  </marker>
</defs>
"""

patterns = [
    # Row 1: Symmetrical Triangle
    (
        "Symmetrical Triangle", "Continuation - Bullish Variant", "ราคาแกว่งตัวในกรอบสามเหลี่ยมแคบลงเรื่อยๆ ก่อนเบรคขึ้นไปตามเทรนเดิม",
        f'{defs}<polyline points="10,50 30,10 50,40 70,25 90,35 100,20" {price}/><line x1="20" y1="5" x2="100" y2="40" {trend}/><line x1="10" y1="55" x2="100" y2="30" {trend}/><polyline points="5,55 10,50" {arrow}/>',
        True,
        "Symmetrical Triangle", "Continuation - Bearish Variant", "ราคาแกว่งตัวในกรอบสามเหลี่ยมแคบลงเรื่อยๆ ก่อนเบรคลงไปตามเทรนเดิม",
        f'{defs}<polyline points="10,10 30,50 50,20 70,35 90,25 100,40" {price}/><line x1="20" y1="55" x2="100" y2="20" {trend}/><line x1="10" y1="5" x2="100" y2="30" {trend}/><polyline points="5,5 10,10" {arrow}/>',
        False
    ),
    # Row 2: Ascending / Descending Triangle
    (
        "Ascending Triangle", "Continuation - Bullish Only", "ฐานราคายกสูงขึ้นเรื่อยๆ ชนแนวต้านที่เดิมซ้ำๆ รอระเบิดขึ้น",
        f'{defs}<polyline points="10,50 30,15 50,35 70,15 90,25 100,5" {price}/><line x1="20" y1="15" x2="100" y2="15" {trend}/><line x1="10" y1="55" x2="90" y2="25" {trend}/>',
        True,
        "Descending Triangle", "Continuation - Bearish Only", "ยอดราคาต่ำลงเรื่อยๆ ชนแนวรับที่เดิมซ้ำๆ รอทะลุลง",
        f'{defs}<polyline points="10,10 30,45 50,25 70,45 90,35 100,55" {price}/><line x1="20" y1="45" x2="100" y2="45" {trend}/><line x1="10" y1="5" x2="90" y2="35" {trend}/>',
        False
    ),
    # Row 3: Inverse Head & Shoulders / Head & Shoulders
    (
        "Inverse Head & Shoulders", "Reversal - Bullish Only", "ทำหลุม 3 หลุม โดยหลุมกลางลึกสุด (Head) รอทะลุ Neckline เพื่อกลับตัวเป็นขาขึ้น",
        f'{defs}<polyline points="10,20 20,40 30,20 50,55 70,20 80,40 90,20 100,5" {price}/><line x1="10" y1="20" x2="90" y2="20" {trend}/>',
        True,
        "Head & Shoulders", "Reversal - Bearish Only", "ทำยอด 3 ยอด โดยยอดกลางสูงสุด (Head) รอหลุด Neckline เพื่อกลับตัวเป็นขาลง",
        f'{defs}<polyline points="10,40 20,20 30,40 50,5 70,40 80,20 90,40 100,55" {price}/><line x1="10" y1="40" x2="90" y2="40" {trend}/>',
        False
    ),
    # Row 4: Cup & Handle / Inverse
    (
        "Cup and Handle", "Continuation - Bullish Only", "ราคาโค้งเป็นรูปถ้วย และย่อทำหูจับสั้นๆ ก่อนพุ่งขึ้นต่อ",
        f'{defs}<path d="M 10 20 Q 50 70 80 20 L 85 30 L 95 15" {price}/><line x1="10" y1="20" x2="90" y2="20" {trend}/>',
        True,
        "Inverse Cup and Handle", "Continuation - Bearish Only", "ราคาโค้งคว่ำลงเป็นรูปถ้วยคว่ำ และเด้งทำหูจับสั้นๆ ก่อนร่วงต่อ",
        f'{defs}<path d="M 10 40 Q 50 -10 80 40 L 85 30 L 95 45" {price}/><line x1="10" y1="40" x2="90" y2="40" {trend}/>',
        False
    ),
    # Row 5: Falling / Rising Wedge
    (
        "Falling Wedge", "Neutral - Bullish Only", "ราคาย่อตัวในกรอบเฉียงลง แต่ฐานเริ่มแคบ บ่งบอกถึงแรงขายที่อ่อนล้า รอสวนขึ้น",
        f'{defs}<polyline points="10,10 30,40 50,25 70,45 85,35 100,15" {price}/><line x1="10" y1="5" x2="100" y2="40" {trend}/><line x1="20" y1="50" x2="100" y2="40" {trend}/>',
        True,
        "Rising Wedge", "Neutral - Bearish Only", "ราคาไต่ขึ้นในกรอบเฉียงขึ้น แต่ยอดเริ่มแคบ บ่งบอกถึงแรงซื้อที่อ่อนล้า รอสวนลง",
        f'{defs}<polyline points="10,50 30,20 50,35 70,15 85,25 100,45" {price}/><line x1="10" y1="55" x2="100" y2="20" {trend}/><line x1="20" y1="10" x2="100" y2="20" {trend}/>',
        False
    ),
    # Row 6: Rectangle
    (
        "Rectangle", "Continuation - Bullish Variant", "ราคาพักตัวออกข้างในกรอบสี่เหลี่ยมผืนผ้า (สะสมพลัง) เพื่อขึ้นต่อตามเทรนเดิม",
        f'{defs}<polyline points="10,50 20,15 40,45 60,15 80,45 95,15 100,5" {price}/><line x1="10" y1="15" x2="100" y2="15" {trend}/><line x1="10" y1="45" x2="100" y2="45" {trend}/>',
        True,
        "Rectangle", "Continuation - Bearish Variant", "ราคาพักตัวออกข้างในกรอบสี่เหลี่ยมผืนผ้า (สะสมพลัง) เพื่อลงต่อตามเทรนเดิม",
        f'{defs}<polyline points="10,10 20,45 40,15 60,45 80,15 95,45 100,55" {price}/><line x1="10" y1="15" x2="100" y2="15" {trend}/><line x1="10" y1="45" x2="100" y2="45" {trend}/>',
        False
    ),
    # Row 7: Flag
    (
        "Flag", "Continuation - Bullish Variant", "ราคาวิ่งขึ้นแรงเป็นเสาธง แล้วพักตัวเฉียงลงขนานกันเป็นผืนธง ก่อนทะลุขึ้นต่อ",
        f'{defs}<polyline points="10,55 40,15 50,30 65,20 75,35 90,10" {price}/><line x1="35" y1="10" x2="85" y2="35" {trend}/><line x1="40" y1="35" x2="90" y2="60" {trend}/>',
        True,
        "Flag", "Continuation - Bearish Variant", "ราคาวิ่งลงแรงเป็นเสาธง แล้วพักตัวเฉียงขึ้นขนานกันเป็นผืนธง ก่อนทะลุลงต่อ",
        f'{defs}<polyline points="10,5 40,45 50,30 65,40 75,25 90,50" {price}/><line x1="35" y1="50" x2="85" y2="25" {trend}/><line x1="40" y1="25" x2="90" y2="0" {trend}/>',
        False
    ),
    # Row 8: Pennant
    (
        "Pennant", "Continuation - Bullish Variant", "วิ่งขึ้นแรงเป็นเสาธง แล้วพักตัวเป็นสามเหลี่ยมขนาดเล็ก ก่อนไปต่อ",
        f'{defs}<polyline points="10,55 40,15 55,35 70,25 80,30 90,10" {price}/><line x1="35" y1="10" x2="90" y2="30" {trend}/><line x1="35" y1="45" x2="90" y2="30" {trend}/>',
        True,
        "Pennant", "Continuation - Bearish Variant", "วิ่งลงแรงเป็นเสาธง แล้วพักตัวเป็นสามเหลี่ยมขนาดเล็ก ก่อนไปต่อ",
        f'{defs}<polyline points="10,5 40,45 55,25 70,35 80,30 90,50" {price}/><line x1="35" y1="50" x2="90" y2="30" {trend}/><line x1="35" y1="15" x2="90" y2="30" {trend}/>',
        False
    ),
    # Row 9: Double Bottom / Top
    (
        "Double Bottom", "Reversal - Bullish Only", "ราคาย่อมาทดสอบแนวรับเดิม 2 ครั้งเกิดเป็นตัว W",
        f'{defs}<polyline points="10,20 30,50 50,30 70,50 90,20 100,5" {price}/><line x1="10" y1="50" x2="90" y2="50" {trend}/><line x1="10" y1="30" x2="90" y2="30" {trend}/>',
        True,
        "Double Top", "Reversal - Bearish Only", "ราคาขึ้นมาชนแนวต้านเดิม 2 ครั้งเกิดเป็นตัว M",
        f'{defs}<polyline points="10,40 30,10 50,30 70,10 90,40 100,55" {price}/><line x1="10" y1="10" x2="90" y2="10" {trend}/><line x1="10" y1="30" x2="90" y2="30" {trend}/>',
        False
    ),
    # Row 10: Triple Bottom / Top
    (
        "Triple Bottom", "Reversal - Bullish Only", "ราคาย่อมาทดสอบแนวรับเดิม 3 ครั้ง แต่ไม่หลุด เตรียมกลับตัว",
        f'{defs}<polyline points="10,20 25,50 40,30 55,50 70,30 85,50 100,10" {price}/><line x1="10" y1="50" x2="90" y2="50" {trend}/><line x1="10" y1="30" x2="90" y2="30" {trend}/>',
        True,
        "Triple Top", "Reversal - Bearish Only", "ราคาชนแนวต้านเดิม 3 ครั้ง แต่ไม่ผ่าน เตรียมกลับตัว",
        f'{defs}<polyline points="10,40 25,10 40,30 55,10 70,30 85,10 100,50" {price}/><line x1="10" y1="10" x2="90" y2="10" {trend}/><line x1="10" y1="30" x2="90" y2="30" {trend}/>',
        False
    )
]

bullish_html = ""
bearish_html = ""

for row in patterns:
    bullish_html += svg_card(row[0], row[1], row[2], row[3], row[4])
    bearish_html += svg_card(row[5], row[6], row[7], row[8], row[9])

new_section_b = f'''
            <!-- SECTION B: Cheat Sheet (20 Patterns) -->
            <div style="margin-top:32px; display:flex; justify-content:space-between; align-items:center;">
              <h2 style="font-size:18px; font-weight:700; color:#fff; margin:0; padding-left:4px;">📚 Pattern Cheat Sheet (คู่มือ 20 แพทเทิร์น)</h2>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top:20px;">
              <!-- Left Column (Bullish) -->
              <div>
                <div style="background:rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.3); color:#10b981; padding:12px; border-radius:8px; text-align:center; font-weight:700; margin-bottom:16px;">
                  🟢 ฝั่งกระทิง (BULLISH - ตลาดขาขึ้น)
                </div>
                <div style="display:flex; flex-direction:column; gap:16px;">
                  {bullish_html}
                </div>
              </div>
              
              <!-- Right Column (Bearish) -->
              <div>
                <div style="background:rgba(239, 68, 68, 0.1); border:1px solid rgba(239, 68, 68, 0.3); color:#ef4444; padding:12px; border-radius:8px; text-align:center; font-weight:700; margin-bottom:16px;">
                  🔴 ฝั่งหมี (BEARISH - ตลาดขาลง)
                </div>
                <div style="display:flex; flex-direction:column; gap:16px;">
                  {bearish_html}
                </div>
              </div>
            </div>
          </div>
        `;
      }}
'''

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the old SECTION B with the new one
# The old one starts at <!-- SECTION B: Cheat Sheet --> and ends at </div>\n          </div>\n        `;\n      }
# We can use regex.
pattern_regex = re.compile(r'<!-- SECTION B: Cheat Sheet -->.*?</div>\s*</div>\s*`;\s*}', re.DOTALL)
content = pattern_regex.sub(new_section_b, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cheat sheet patched.")
