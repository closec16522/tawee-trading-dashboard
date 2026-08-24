import codecs
with codecs.open('index.html', 'r', 'utf-8') as f:
    for i, line in enumerate(f):
        if 'Terminal Console Log' in line or ('id="' in line and 'terminal' in line.lower()):
            print(f'Line {i+1}: {line.strip().encode("ascii", "ignore").decode("ascii")}')
