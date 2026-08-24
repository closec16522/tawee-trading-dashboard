import codecs
import re

with codecs.open('mt5_backend/strategy_optimizer.py', 'r', 'utf-8') as f:
    content = f.read()

old_code = r"""res = {
        "symbol": sym,
        "best_params": best_params,
        "best_stats": best_stats,
        "history": history
    }"""

new_code = r"""res = {
        "symbol": sym,
        "period": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')} (H1, 5000 Bars)",
        "best_params": best_params,
        "best_stats": best_stats,
        "history": history
    }"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with codecs.open('mt5_backend/strategy_optimizer.py', 'w', 'utf-8') as f:
        f.write(content)
    print("strategy_optimizer.py patched to include exact period dates")
else:
    print("Could not find old_code in strategy_optimizer.py")
