import re

# 1. Patch mt5_backend/agent_orchestrator.py to add Coin Hunter AI logic
path_orchestrator = 'mt5_backend/agent_orchestrator.py'
with open(path_orchestrator, 'r', encoding='utf-8') as f:
    content_orch = f.read()

coin_hunter_func = '''
# --- 8. COIN HUNTER AI (Auto Coin & Symbol Discovery) ---
def run_coin_hunter():
    global SYMBOLS
    print("🔍 COIN HUNTER AI: Scanning Volatile Coins & Forex Pairs...")
    update_agent("coin_hunter", "Scanning Coins", "Scanning Market Volatility...", "#34d6e6")
    time.sleep(1)
    
    try:
        import MetaTrader5 as mt5
        symbols_to_scan = ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "USDJPY", "SOLUSD", "ADAUSD"]
        top_movers = []
        
        for s in symbols_to_scan:
            rates = mt5.copy_rates_from_pos(s, mt5.TIMEFRAME_H1, 0, 24)
            if rates is not None and len(rates) > 0:
                import pandas as pd
                df_c = pd.DataFrame(rates)
                volatility = ((df_c['high'].max() - df_c['low'].min()) / df_c['close'].iloc[-1]) * 100
                top_movers.append((s, volatility))
                
        top_movers.sort(key=lambda x: x[1], reverse=True)
        discovered_symbols = [x[0] for x in top_movers[:4]] if top_movers else ["XAUUSD", "BTCUSD", "ETHUSD"]
        
        top_name = discovered_symbols[0] if discovered_symbols else "XAUUSD"
        print(f"🎯 COIN HUNTER AI: Discovered Top Volatile Coin -> {top_name}")
        update_agent("coin_hunter", "Discovered", f"Discovered Top Pair: {top_name}", "#34d6e6")
        time.sleep(1)
        return discovered_symbols
    except Exception as e:
        print("⚠️ COIN HUNTER AI Error:", e)
        update_agent("coin_hunter", "Standby", "Scanning Complete", "#64748b")
        return ["XAUUSD", "BTCUSD", "ETHUSD"]
'''

# Inject run_coin_hunter before run_news_analyst or at top of agent definitions
if "def run_coin_hunter" not in content_orch:
    content_orch = re.sub(
        r'(def run_news_analyst\(\):)',
        coin_hunter_func + '\n\\1',
        content_orch,
        count=1
    )

# Inject run_coin_hunter() inside the main orchestrator cycle
if "run_coin_hunter()" not in content_orch:
    content_orch = re.sub(
        r'(\s*print\("--- Starting Agent Cycle ---"\))',
        r'\1\n            run_coin_hunter()',
        content_orch,
        count=1
    )

with open(path_orchestrator, 'w', encoding='utf-8') as f:
    f.write(content_orch)
print("Patched agent_orchestrator.py with Coin Hunter AI!")


# 2. Patch index.html to reflect Local AI status and 8th Agent (Coin Hunter AI)
path_index = 'index.html'
with open(path_index, 'r', encoding='utf-8') as f:
    content_index = f.read()

# Update Active Agents count to 8/8
content_index = content_index.replace('7 / 7', '8 / 8')
content_index = content_index.replace('Active Agents: 7/7', 'Active Agents: 8/8')

# Update Local AI Badges
content_index = content_index.replace('MTS Engine Connected - พร้อมระบบคุมความเสี่ยง', '🏠 Local Machine AI Engine (Ollama LLaMA 3 - Zero Rate Limit)')

# Add coin_hunter to agentsData if present
agents_data_target = r"({ key: 'market_analyst', name: 'MARKET ANALYST', level: 18, status: 'Analysing', eff: 93, border: '#3b82f6', charId: 17, skill: 'Scanning Market Supply/Demand & Liquidity Swings' },)"
coin_hunter_agent_data = r"\1\n    { key: 'coin_hunter', name: 'COIN HUNTER AI', level: 15, status: 'Scanning Coins', eff: 95, border: '#34d6e6', charId: 35, skill: 'Auto Volatility Screener & Dynamic Coin Discovery' },"

if "key: 'coin_hunter'" not in content_index:
    content_index = re.sub(agents_data_target, coin_hunter_agent_data, content_index)

with open(path_index, 'w', encoding='utf-8') as f:
    f.write(content_index)
print("Patched index.html with Local AI indicators and Coin Hunter AI agent data!")
