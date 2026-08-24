import re

file_path = "index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Inject the DOM element using regex to avoid encoding issues with Thai characters
pattern = r'(<span id="ai-analysis-struct">.*?</span><br/><br/>)'
replacement = r'\1\n                      <b>Chart Pattern:</b> <span id="ai-analysis-pattern" style="color:#fcd34d; font-weight:600;">ไม่มี (None)</span><br/><br/>'

content = re.sub(pattern, replacement, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html HTML structure patched.")
