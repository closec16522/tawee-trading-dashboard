import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\\n                       const msgDiv', '\n                       const msgDiv')
content = content.replace('</strong>: ;', '</strong>: ;')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
