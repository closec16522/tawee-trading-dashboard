import json

config_path = 'roseai/config.json'
with open(config_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

cfg['geminiKey'] = ''
cfg['model'] = 'gemini-1.5-pro'

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

# Update index.html
with open('roseai/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace gemini-3.1-pro with gemini-1.5-pro
html = html.replace('value="gemini-3.1-pro"', 'value="gemini-1.5-pro"')
html = html.replace('Gemini 3.1 Pro (ฉลาด)', 'Gemini 1.5 Pro (ฉลาด)')
html = html.replace('value="gemini-3.6-flash"', 'value="gemini-1.5-flash"')
html = html.replace('Gemini 3.6 Flash (เร็ว)', 'Gemini 1.5 Flash (เร็ว)')

with open('roseai/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated config and html")
