import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('.ai-meeting-room {', '#command-center-root .ai-meeting-room {')
html = html.replace('.ai-meeting-header {', '#command-center-root .ai-meeting-header {')
html = html.replace('.ai-meeting-log {', '#command-center-root .ai-meeting-log {')
html = html.replace('.ai-msg {', '#command-center-root .ai-msg {')
html = html.replace('.system-msg {', '#command-center-root .system-msg {')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Added #command-center-root prefix to AI meeting CSS.")
