import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# We need to replace fetch('/api/backtest/run' with the dynamic host logic
old_run = "fetch('/api/backtest/run', { method: 'POST' })"
new_run = """const host = new URLSearchParams(window.location.search).get('gw') || '192.168.0.41';
          fetch(`http://${host}:19000/api/backtest/run`, { method: 'POST' })"""
content = content.replace(old_run, new_run)

old_results = "fetch('/api/backtest/results')"
new_results = """const host = new URLSearchParams(window.location.search).get('gw') || '192.168.0.41';
          fetch(`http://${host}:19000/api/backtest/results`)"""
content = content.replace(old_results, new_results)

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)

print("Patched API endpoints for backtest.")
