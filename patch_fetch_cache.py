with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

target = "fetch(`http://${window.location.hostname}:19000/api/trading_settings`)"
replacement = "fetch(`http://${window.location.hostname}:19000/api/trading_settings?t=${Date.now()}`)"

content = content.replace(target, replacement)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)