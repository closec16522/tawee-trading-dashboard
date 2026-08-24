import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 127.0.0.1 in the specific fetch call
old_fetch = "await fetch(`http://127.0.0.1:19000/api/history?symbol=${cleanSymbol}&timeframe=${tfInput.value}&count=200`);"
new_fetch = "await fetch(`http://${window.location.hostname}:19000/api/history?symbol=${cleanSymbol}&timeframe=${tfInput.value}&count=200`);"

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched API URL successfully.")
else:
    print("Could not find the fetch call.")
