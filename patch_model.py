import codecs
with codecs.open('mt5_backend/strategy_optimizer.py', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("gemini-1.5-flash", "gemini-2.5-flash")

with codecs.open('mt5_backend/strategy_optimizer.py', 'w', 'utf-8') as f:
    f.write(content)
