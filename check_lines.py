import codecs
with codecs.open('index.html', 'r', 'utf-8') as f:
    lines = f.readlines()
print(f'Line 3924: {lines[3923].strip().encode("cp1252", "replace").decode("cp1252")}')
print(f'Line 10042: {lines[10041].strip().encode("cp1252", "replace").decode("cp1252")}')
