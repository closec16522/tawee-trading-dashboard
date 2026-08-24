import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Replace gwHost with host
content = content.replace('gwHost', 'host')

# Add Chart.js if missing
if 'chart.js' not in content.lower():
    # Insert right before </head>
    head_end = content.find('</head>')
    if head_end != -1:
        content = content[:head_end] + '  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n' + content[head_end:]

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)
