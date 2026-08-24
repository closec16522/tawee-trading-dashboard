import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Replace the literal \n strings that were accidentally injected
content = content.replace('\\n<button class="menu-item" data-tab="backtest">', '\n<button class="menu-item" data-tab="backtest">')
content = content.replace('</button>\n\\n', '</button>\n\n')

# Also fix the one near connectMT5Gateway();
content = content.replace('\\nconnectMT5Gateway();', '\nconnectMT5Gateway();')

# Fix any stray \n that might have been injected
if '\\n\\n' in content:
    content = content.replace('\\n\\n', '\n\n')

# Just to be sure, let's fix the specific instances exactly as they appear
content = content.replace('ผลงานจริง</span>\n                </span>\n                <span class="active-dot"></span>\n              </button>\\n<button', 'ผลงานจริง</span>\n                </span>\n                <span class="active-dot"></span>\n              </button>\n<button')

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)

print("Fixed literal \\n characters in index.html.")
