import codecs
import re

with codecs.open('index.html', 'r', 'utf-8') as f:
    html = f.read()

# Try to find common layout structures
body_idx = html.find('<body')
if body_idx != -1:
    print(html[body_idx:body_idx+2000])
