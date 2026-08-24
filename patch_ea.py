import sys
import re

try:
    with open('mt5_backend/agent_orchestrator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add import
    if 'import ea_logic' not in content:
        content = content.replace('import json\nimport time', 'import json\nimport time\nimport ea_logic')

    # 2. Add Daily Limit Check in main_loop
    if 'ea_logic.check_session_and_limits()' not in content:
        target = 'reload_config()\n'
        replacement = '''reload_config()
            can_trade, reason = ea_logic.check_session_and_limits()
            if not can_trade:
                print(f"\\r🛑 EA HALTED: {reason} - Waiting for next session/day...", end="")
                time.sleep(60)
                continue\n'''
        content = content.replace(target, replacement)

    # 3. Add Trade Management (Trailing/BE) in run_portfolio_manager
    if 'ea_logic.manage_active_trades()' not in content:
        target = 'def run_portfolio_manager():\n'
        replacement = '''def run_portfolio_manager():
    try:
        ea_logic.manage_active_trades()
    except Exception as e:
        print("Error in Active Trade Management:", e)\n'''
        content = content.replace(target, replacement)

    # 4. Use ATR for SL/TP in run_supervisor
    if 'ea_logic.EA_SETTINGS["ATR_MULTIPLIER_SL"]' not in content:
        old_sl_logic = r'if symbol_info and tick:.*?tp = price - tp_points'
        new_sl_logic = '''if symbol_info and tick:
            # --- NEW ATR-BASED SL/TP ---
            point = symbol_info.point
            if trade_atr > 0:
                sl_dist = trade_atr * ea_logic.EA_SETTINGS["ATR_MULTIPLIER_SL"]
                tp_dist = trade_atr * ea_logic.EA_SETTINGS["ATR_MULTIPLIER_TP"]
            else:
                sl_dist = 500 * point
                tp_dist = 1000 * point
                
            if decision == "BUY":
                sl = price - sl_dist
                tp = price + tp_dist
            else:
                sl = price + sl_dist
                tp = price - tp_dist'''
        
        content = re.sub(old_sl_logic, new_sl_logic, content, flags=re.DOTALL)

    with open('mt5_backend/agent_orchestrator.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print('Successfully patched agent_orchestrator.py')
except Exception as e:
    print('Patch failed:', e)
