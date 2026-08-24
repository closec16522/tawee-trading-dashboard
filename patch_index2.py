import re

file_path = "index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add the DOM element
old_html = """<b>โครงสร้างตลาด:</b> <span id="ai-analysis-struct">เทส Demand Zone H1 ไม่ผ่านเตรียมกลับตัว</span><br/><br/>"""
new_html = """<b>โครงสร้างตลาด:</b> <span id="ai-analysis-struct">เทส Demand Zone H1 ไม่ผ่านเตรียมกลับตัว</span><br/><br/>
                      <b>Chart Pattern:</b> <span id="ai-analysis-pattern" style="color:#fcd34d; font-weight:600;">สแกนหา...</span><br/><br/>"""
content = content.replace(old_html, new_html)

# 2. Add to updateDashAiAnalysis bindings
old_js1 = "const elStruct = document.getElementById('ai-analysis-struct');"
new_js1 = "const elStruct = document.getElementById('ai-analysis-struct');\n            const elPattern = document.getElementById('ai-analysis-pattern');"
content = content.replace(old_js1, new_js1)

# 3. Add to updateDashAiAnalysis logic
old_js2 = "if (elStruct) elStruct.textContent = recent.reason || `พบสัญญาณ ${recent.grade || 'A'} ในตลาด`;"
new_js2 = """if (elStruct) elStruct.textContent = recent.reason || `พบสัญญาณ ${recent.grade || 'A'} ในตลาด`;
            if (elPattern) elPattern.textContent = (recent.chart_pattern && recent.chart_pattern !== "None") ? `📈 ${recent.chart_pattern}` : "ไม่มี (None)";
"""
content = content.replace(old_js2, new_js2)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html patched.")
