import re
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

target1 = """<span class="chart-title" id="dash-pos-title">Open Positions (0 ออเดอร์กำลังรัน)</span>"""
replacement1 = """<div style="display:flex; justify-content:space-between; align-items:center;">
                  <span class="chart-title" id="dash-pos-title">Open Positions (0 ออเดอร์กำลังรัน)</span>
                  <button onclick="window.panicCloseAll()" style="background:#ef4444; color:#fff; border:none; padding:5px 12px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer; box-shadow:0 0 10px rgba(239, 68, 68, 0.4);">🛑 ปิดทุกออเดอร์</button>
                </div>"""

content = content.replace(target1, replacement1)

target2 = """                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                      <span class="chart-title">Open Positions</span>
                      <span style="font-size:10px; color:#10b981; font-weight:700;" id="trade-pos-title">● 0 Active Orders</span>
                    </div>"""
replacement2 = """                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                      <div style="display:flex; align-items:center; gap:10px;">
                        <span class="chart-title">Open Positions</span>
                        <span style="font-size:10px; color:#10b981; font-weight:700;" id="trade-pos-title">● 0 Active Orders</span>
                      </div>
                      <button onclick="window.panicCloseAll()" style="background:#ef4444; color:#fff; border:none; padding:5px 12px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer; box-shadow:0 0 10px rgba(239, 68, 68, 0.4);">🛑 ปิดทุกออเดอร์</button>
                    </div>"""

content = content.replace(target2, replacement2)

js_logic = """
      // --- Panic Close ---
      window.panicCloseAll = function() {
        if(confirm("🚨 ยืนยันการสั่งปิดออเดอร์ทั้งหมดที่กำลังเปิดอยู่ใช่หรือไม่? (ระบบจะทยอยปิด Market Order ทีละออเดอร์ทันที)")) {
          fetch('/api/close_all', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
              if (data.ok) {
                alert(`✅ สั่งปิดออเดอร์สำเร็จทั้งหมด ${data.closed_count} รายการ`);
              } else {
                alert("❌ เกิดข้อผิดพลาดในการสั่งปิดออเดอร์");
              }
            })
            .catch(err => {
              console.error(err);
              alert("❌ ไม่สามารถติดต่อเซิร์ฟเวอร์ได้");
            });
        }
      };
      
      // --- Helper: Update Settings Form ---
"""

content = content.replace("      // --- Helper: Update Settings Form ---", js_logic)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("panic buttons added")