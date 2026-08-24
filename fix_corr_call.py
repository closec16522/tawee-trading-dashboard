import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        for sym, trade_data in list(approved_trades.items()):
        decision = trade_data["decision"]'''

# Let's use regex to find where to inject it.
# We will inject it right after `decision = trade_data["decision"]`
regex_target = r'(for sym, trade_data in list\(approved_trades\.items\(\)\):\s*\n\s*decision = trade_data\["decision"\])'

replacement = r'''\1
        
        # --- Check Correlation ---
        is_correlated, corr_msg = check_correlation(sym, decision)
        if is_correlated:
            print(f"🛑 SUPERVISOR BLOCKED: {sym} {decision} due to Correlation: {corr_msg}")
            trade_data["status"] = "Rejected"
            trade_data["rejection_reason"] = f"Correlation Block: {corr_msg}"
            trade_data["grade"] = trade_data.get("grade", "C")
            trade_data["symbol"] = sym
            trade_data["trend"] = trade_data.get("trend", "Unknown")
            trade_data["setup"] = trade_data.get("setup", "")
            signals_list.append(trade_data)
            continue
'''

if re.search(regex_target, content):
    content = re.sub(regex_target, replacement, content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected check_correlation call")
else:
    print("Regex target not found")
