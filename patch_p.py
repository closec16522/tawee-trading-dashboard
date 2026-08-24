import codecs

with codecs.open('mt5_backend/strategy_optimizer.py', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('"best_stats": best_stats,', '"period": f"{df.index[0].strftime(\'%Y-%m-%d\')} to {df.index[-1].strftime(\'%Y-%m-%d\')} (H1, 5000 Bars)",\n        "best_stats": best_stats,')

with codecs.open('mt5_backend/strategy_optimizer.py', 'w', 'utf-8') as f:
    f.write(content)
print("Done")
