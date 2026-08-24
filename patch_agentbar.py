import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update .agentbar
agentbar_css = "#command-center-root .agentbar{display:flex !important;flex-direction:row !important;align-items:center !important;gap:14px !important;padding:8px 14px !important;background:#090e1a !important;border-top:1px solid #1e293b !important;width:100% !important;box-sizing:border-box !important; overflow-x: auto !important;}"
content = re.sub(r'#command-center-root \.agentbar\{[^\}]+\}', agentbar_css, content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched agentbar overflow-x.')
