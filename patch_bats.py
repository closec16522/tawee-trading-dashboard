import codecs
import re

for filename in ['start_trader.bat', 'start_all_systems.bat']:
    try:
        with codecs.open(f'mt5_backend/{filename}', 'r', 'utf-8') as f:
            content = f.read()
        
        # Replace ai_trader.py with ai_trader_old.py
        content = content.replace('ai_trader.py', 'ai_trader_old.py')
        
        with codecs.open(f'mt5_backend/{filename}', 'w', 'utf-8') as f:
            f.write(content)
        print(f"Patched {filename}")
    except Exception as e:
        print(f"Error patching {filename}: {e}")
