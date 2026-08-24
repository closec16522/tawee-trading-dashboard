import codecs
with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()
idx = content.find('<div class="tab-pane" id="tab-analytics">')
print(content[idx:idx+2500].encode('cp1252', 'replace').decode('cp1252'))
