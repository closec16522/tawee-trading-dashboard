import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    for i, line in enumerate(f):
        if 'Start AI Optimization' in line:
            print(f'Line {i+1}: {line.strip().encode("ascii", "ignore").decode("ascii")}')
