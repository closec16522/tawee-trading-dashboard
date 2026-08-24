import codecs
with codecs.open('index.html', 'r', 'utf-8') as f:
    html = f.read()

idx = html.find('<div class="tab-pane" id="tab-analytics">')
print('Found tab-analytics at:', idx)
if idx != -1:
    print(html[max(0, idx-200):idx].encode('cp1252', 'replace').decode('cp1252'))
