import codecs
import re

with codecs.open('mt5_backend/strategy_optimizer.py', 'r', 'utf-8') as f:
    content = f.read()

# Change the end block to loop over all symbols
old_main = """if __name__ == "__main__":
    optimize_strategy("XAUUSD-VIP")"""

new_main = """def run_all_optimizations():
    print("Starting Multi-Symbol Backtest Optimization...")
    if not os.path.exists(MAIN_CONFIG_PATH):
        print("Config file not found, defaulting to XAUUSD-VIP")
        symbols = ["XAUUSD-VIP"]
    else:
        with open(MAIN_CONFIG_PATH, 'r', encoding='utf-8') as f:
            _config = json.load(f)
            symbols = _config.get("symbols", ["XAUUSD-VIP"])
            
    all_results = {}
    for sym in symbols:
        res = optimize_strategy(sym)
        all_results[sym] = res
        
    # Save the aggregated results
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
        
    print("Multi-Symbol Backtest Optimization Complete!")

if __name__ == "__main__":
    run_all_optimizations()"""

content = content.replace(old_main, new_main)

# Also we need to modify optimize_strategy to NOT write the RESULTS_PATH itself,
# so we remove the file saving part from inside optimize_strategy

old_save_block = """    # Save to file
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=4)
        
    return final_result"""

new_save_block = """    return final_result"""

content = content.replace(old_save_block, new_save_block)

# Let's reduce iterations to 2 to speed it up
content = content.replace("for iteration in range(1, 4): # Max 3 iterations for demo speed", "for iteration in range(1, 3): # Max 2 iterations for multi-symbol speed")

with codecs.open('mt5_backend/strategy_optimizer.py', 'w', 'utf-8') as f:
    f.write(content)

print("Updated strategy_optimizer.py for multi-symbol support.")
