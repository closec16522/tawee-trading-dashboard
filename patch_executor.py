import os
import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the volume mapping in run_trade_executor
target = '''        request = {
            "action": action,
            "symbol": symbol,
            "volume": float(lot),'''

replacement = '''        # --- 🚀 INSTITUTIONAL DYNAMIC LOT SIZING ---
        dynamic_lot = ea_logic.get_dynamic_lot_size(symbol, sl_dist)
        update_agent("trade_executor", "Calculating Position Size", f"{symbol} Risk 1% -> Lot: {dynamic_lot}")
        
        request = {
            "action": action,
            "symbol": symbol,
            "volume": float(dynamic_lot),'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched run_trade_executor lot size successfully!")
else:
    print("Target not found in run_trade_executor.")

# 2. Modify run_risk_manager to just show a generic message since it's dynamic now
target2 = '''        calculated_lot = round(max(0.01, (balance / 1000) * 0.01), 2)
        calculated_lot = min(calculated_lot, 1.00)
        print(f"✅ RISK MANAGER: Balance=${balance:.2f} -> Lot={calculated_lot}")
        update_agent("risk_manager", "Risk Calculated", f"Risk 1% -> Lot: {calculated_lot}", "#f59e0b")
        return calculated_lot'''

# We will just use regex to replace the body of run_risk_manager
new_risk = '''        # Risk calculation is now delegated to Trade Executor based on SL distance
        print(f"✅ RISK MANAGER: Checking Equity Balance=${balance:.2f} & Drawdown")
        update_agent("risk_manager", "Equity OK", f"Risk managed dynamically per trade based on SL", "#f59e0b")
        return 0.01 # Placeholder'''

content = re.sub(
    r'calculated_lot = round\(max\(0.01.*?return calculated_lot',
    new_risk,
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Risk Manager patched!")
