import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# find exactly this line and replace it
old_line = 'msgDiv.innerHTML = <strong style="color:"></strong>: ;'
new_line = 'msgDiv.innerHTML = <strong style="color:"></strong>: ;'
content = content.replace(old_line, new_line)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
