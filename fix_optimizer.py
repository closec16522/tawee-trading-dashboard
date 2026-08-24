import codecs
import re

with codecs.open('mt5_backend/strategy_optimizer.py', 'r', 'utf-8') as f:
    content = f.read()

# Fix config loading
old_config_import = """from config import config
from ai_backtester import fetch_historical_data, run_simulation

GEMINI_API_KEY = config.get("gemini_api_key", "")"""

new_config_import = """from ai_backtester import fetch_historical_data, run_simulation

MAIN_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
GEMINI_API_KEY = ""
if os.path.exists(MAIN_CONFIG_PATH):
    with open(MAIN_CONFIG_PATH, 'r', encoding='utf-8') as f:
        _config = json.load(f)
        GEMINI_API_KEY = _config.get("gemini_api_key", "")
"""
content = content.replace(old_config_import, new_config_import)

# Fix RESULTS_PATH
content = content.replace('RESULTS_PATH = "backtest_results.json"', 'RESULTS_PATH = os.path.join(os.path.dirname(__file__), "backtest_results.json")')

with codecs.open('mt5_backend/strategy_optimizer.py', 'w', 'utf-8') as f:
    f.write(content)

print("Fixed strategy_optimizer.py")
