import os
import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'(window\._patternSeries\.setData\(data\.pattern_points\);)',
    r'try { \1 } catch(e) { console.error("Pattern Series Error:", e); }',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched index.html successfully.")
