import os

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

panic_code = """
      window.panicCloseAll = async () => {
          if(!confirm("⚠️ ยืนยันการปิดทุกออเดอร์ (Panic Close)?")) return;
          try {
              const host = new URLSearchParams(window.location.search).get('gw') || '127.0.0.1';
              const res = await fetch(`http://${host}:19000/api/close_all`, {
                  method: 'POST'
              });
              if(res.ok) {
                  const data = await res.json();
                  alert(`✅ ปิดออเดอร์สำเร็จจำนวน ${data.closed_count} ออเดอร์`);
              } else {
                  alert("❌ เกิดข้อผิดพลาดในการปิดออเดอร์");
              }
          } catch (err) {
              console.error("Panic Close Error:", err);
              alert("❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้");
          }
      };
      
      // Start Connection"""

content = content.replace("// Start Connection", panic_code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched index.html with panicCloseAll function.")
