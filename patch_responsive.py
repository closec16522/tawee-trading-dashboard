import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update .body
body_css = "#command-center-root .body{display:flex !important;flex-direction:row !important;flex-wrap:nowrap !important;min-height:0;height:100%;width:100% !important;max-width:100% !important;overflow-x:hidden !important;box-sizing:border-box !important;padding-right:24px !important;}"
content = re.sub(r'#command-center-root \.body\{[^\}]+\}', body_css, content)

# 2. Update .center
center_css = "#command-center-root .center { flex: 1 1 0% !important; width: auto !important; min-width: 0 !important; max-width: none !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; }"
content = re.sub(r'#command-center-root \.center \{[^\}]+\}', center_css, content)

# 3. Update .rightcol
rightcol_css = "#command-center-root .rightcol { flex: 0 0 350px !important; width: 350px !important; min-width: 350px !important; max-width: 350px !important; overflow-y: auto !important; height: 100% !important; min-height: 0 !important; padding: 8px !important; box-sizing: border-box !important; }"
content = re.sub(r'#command-center-root \.rightcol \{[^\}]+\}', rightcol_css, content)

# 4. Update .stage
stage_css = "#command-center-root .stage { resize: horizontal; overflow: hidden !important; width: 100%; min-width: 300px !important; max-width: 100% !important; position:relative; flex:1; min-height:0; border-radius:10px; border:1px solid #1e2740; background:radial-gradient(1200px 760px at 82% 16%,#0a1730 0%,#04060f 55%,#010205 100%); }"
content = re.sub(r'#command-center-root \.stage \{[^\}]+\}', stage_css, content)
# Ensure we don't have duplicate .stage blocks
content = re.sub(r'#command-center-root \.stage\{position:relative;[^\}]+\}', '', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched robust flexbox layout.')
