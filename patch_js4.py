import re
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("item.pair", "item.symbol")
content = content.replace("item.side", "item.type")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed pair->symbol and side->type")