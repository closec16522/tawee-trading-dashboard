import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('z-index: 100;', 'z-index: 9999;')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated z-index to 9999 for ai-meeting-room")
