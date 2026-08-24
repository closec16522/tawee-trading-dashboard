import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    lines = f.readlines()
    
start = max(0, 10196 - 20)
end = min(len(lines), 10196 + 20)

for i in range(start, end):
    line_clean = lines[i].rstrip('\n').encode('ascii', 'replace').decode('ascii')
    print(f'{i+1}: {line_clean}')
