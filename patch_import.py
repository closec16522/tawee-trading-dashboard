import os

file_path = os.path.join('mt5_backend', 'mt5_gateway.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from .pattern_detector import detect_chart_pattern' in content:
    content = content.replace('from .pattern_detector import detect_chart_pattern', 'from pattern_detector import detect_chart_pattern')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched import successfully.")
else:
    print("Could not find the import statement.")
