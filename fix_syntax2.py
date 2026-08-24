import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Fix the broken literal newline in the string
broken_str = 'term.innerHTML = "[System] Starting AI Optimization Process in backend...\n";'
fixed_str = 'term.innerHTML = "[System] Starting AI Optimization Process in backend...\\n";'

if broken_str in content:
    content = content.replace(broken_str, fixed_str)
    with codecs.open('index.html', 'w', 'utf-8') as f:
        f.write(content)
    print("Fixed syntax error.")
else:
    print("Broken string not found.")
