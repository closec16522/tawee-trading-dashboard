import json
from collections import Counter

try:
    with open('mt5_backend/journal.json', 'r', encoding='utf-8') as f:
        journal = json.load(f)
        
    print(f"Total trades in journal: {len(journal)}")
    
    wins = [t for t in journal if t.get('profit', 0) > 0]
    losses = [t for t in journal if t.get('profit', 0) <= 0]
    print(f"Wins: {len(wins)}, Losses: {len(losses)}")
    
    total_profit = sum(t.get('profit', 0) for t in journal)
    print(f"Total Net Profit: {total_profit:.2f}")
    
    print("\nLast 5 trades:")
    for t in journal[-5:]:
        print(f"Date: {t.get('date')} | Symbol: {t.get('symbol')} | Type: {t.get('type')} | Profit: {t.get('profit')} | Insight: {t.get('insight', '')[:150]}")
        
except Exception as e:
    print(f"Error reading journal: {e}")
