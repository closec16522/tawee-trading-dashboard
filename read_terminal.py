import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    lines = f.readlines()
    
for i in range(10135, 10150):
    line_clean = lines[i].rstrip('\n').encode('ascii', 'replace').decode('ascii')
    print(f'{i+1}: {line_clean}')
