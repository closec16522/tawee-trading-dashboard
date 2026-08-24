import os

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_script = '<script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>'
new_script = '<script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>'

if old_script in content:
    content = content.replace(old_script, new_script)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched script tag successfully.")
else:
    print("Script tag not found.")
