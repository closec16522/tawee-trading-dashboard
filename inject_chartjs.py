import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Add Chart.js script to <head> if not exists
if 'cdn.jsdelivr.net/npm/chart.js' not in content:
    content = content.replace('</head>', '    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n</head>')
    with codecs.open('index.html', 'w', 'utf-8') as f:
        f.write(content)
    print("Chart.js injected into <head>.")
else:
    print("Chart.js already exists.")
