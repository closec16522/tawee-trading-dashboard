import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded notif-list contents in index.html
target_start = '<div class="notif-list">'
target_end = '<!-- End: Signal Notifications -->'
import re
match = re.search(r'<div class="notif-list">.*?<!-- End: Signal Notifications -->', content, re.DOTALL)
if match:
    replacement = '<div class="notif-list">\n                  <div style="color:var(--text-muted); font-size:12px; padding:10px; text-align:center;">กำลังรอสัญญาณ AI...</div>\n                </div>\n                <!-- End: Signal Notifications -->'
    content = content[:match.start()] + replacement + content[match.end():]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Hardcoded items removed")