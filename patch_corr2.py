import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

correlation_function = '''
    # --- 🚀 CORRELATION MATRIX (Phase 2) ---
    def check_correlation(new_symbol, new_decision):
        positions = mt5.positions_get()
        if not positions:
            return False, "" # No correlation issue
            
        import pandas as pd
        import MetaTrader5 as mt5
        
        rates_new = mt5.copy_rates_from_pos(new_symbol, mt5.TIMEFRAME_H1, 0, 100)
        if rates_new is None or len(rates_new) == 0:
            return False, ""
        
        df_new = pd.DataFrame(rates_new)['close']
        
        for pos in positions:
            open_symbol = pos.symbol
            open_type = "BUY" if pos.type == 0 else "SELL"
            
            if open_symbol == new_symbol: continue
                
            rates_open = mt5.copy_rates_from_pos(open_symbol, mt5.TIMEFRAME_H1, 0, 100)
            if rates_open is None or len(rates_open) == 0:
                continue
                
            df_open = pd.DataFrame(rates_open)['close']
            
            # Ensure same length
            min_len = min(len(df_new), len(df_open))
            corr = df_new.tail(min_len).corr(df_open.tail(min_len))
            
            if pd.isna(corr): continue
                
            if corr > 0.8:
                if new_decision == open_type:
                    return True, f"High Positive Corr ({corr:.2f}) with {open_symbol} ({open_type})"
            elif corr < -0.8:
                if new_decision != open_type:
                    return True, f"High Negative Corr ({corr:.2f}) with {open_symbol} ({open_type})"
                    
        return False, ""
'''

# 1. Inject check_correlation right after run_supervisor signature
content = re.sub(
    r'(def run_supervisor\(lot_size\):\n\s*global approved_trades)',
    r'\1\n' + correlation_function,
    content,
    count=1
)

# 2. Inject the call inside the loop
# We need to find: `grade = t["grade"]`
target_loop = '''        symbol = t["symbol"]
        trend = t["trend"]
        decision = t["decision"]
        confidence = t["confidence"]
        setup = t["setup"]
        grade = t.get("grade", "C")'''

target_loop_alt = '''        grade = t["grade"]'''

replacement_loop = '''        grade = t.get("grade", "C")
        
        # --- Check Correlation ---
        is_correlated, corr_msg = check_correlation(symbol, decision)
        if is_correlated:
            print(f"🛑 SUPERVISOR BLOCKED: {symbol} {decision} due to Correlation: {corr_msg}")
            t["status"] = "Rejected"
            t["rejection_reason"] = f"Correlation Block: {corr_msg}"
            signals_list.append(t)
            continue
'''

if target_loop in content:
    content = content.replace(target_loop, target_loop.replace('grade = t.get("grade", "C")', replacement_loop))
elif target_loop_alt in content:
    content = content.replace(target_loop_alt, replacement_loop)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Correlation Patch applied!")
