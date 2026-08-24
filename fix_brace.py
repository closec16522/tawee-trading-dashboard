html_file = 'index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Add the missing brace right before the next function definition, or just replace the end of my injected catch statement.
html = html.replace('.catch(e => console.error("Error fetching track record:", e));', '.catch(e => console.error("Error fetching track record:", e));\n      }')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)
print("Added missing brace to index.html")
