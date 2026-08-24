import codecs
with codecs.open('index.html', 'r', 'utf-8') as f:
    lines = f.readlines()
for i in range(max(0, 10065), min(len(lines), 10075)):
    print(f'Line {i+1}: {lines[i].strip().encode("cp1252", "replace").decode("cp1252")}')
