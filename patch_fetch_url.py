with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

target1 = "fetch('/api/trading_settings')"
replacement1 = "fetch(`http://${window.location.hostname}:19000/api/trading_settings`)"
content = content.replace(target1, replacement1)

target2 = "fetch('/api/trading_settings', {"
replacement2 = "fetch(`http://${window.location.hostname}:19000/api/trading_settings`, {"
content = content.replace(target2, replacement2)

target3 = "fetch('/api/close_all'"
replacement3 = "fetch(`http://${window.location.hostname}:19000/api/close_all`"
content = content.replace(target3, replacement3)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)