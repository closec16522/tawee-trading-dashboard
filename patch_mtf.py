import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update run_ai_analysis to fetch M15 and M5 and create mtf_context_str
target_run_ai = '''            # Fetch H4 data for Trend Context
            h4_trend = "Unknown"
            h4_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 50)
            if h4_rates is not None and len(h4_rates) > 0:
                df_h4 = pd.DataFrame(h4_rates)
                df_h4['EMA50'] = df_h4['close'].ewm(span=50, adjust=False).mean()
                if df_h4['close'].iloc[-1] > df_h4['EMA50'].iloc[-1]:
                    h4_trend = "BULLISH"
                else:
                    h4_trend = "BEARISH"'''

replacement_run_ai = '''            # --- 🚀 MULTI-TIMEFRAME ANALYSIS (Phase 2) ---
            def get_trend(symbol, timeframe):
                rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 50)
                if rates is not None and len(rates) > 0:
                    df_tf = pd.DataFrame(rates)
                    df_tf['EMA50'] = df_tf['close'].ewm(span=50, adjust=False).mean()
                    return "BULLISH" if df_tf['close'].iloc[-1] > df_tf['EMA50'].iloc[-1] else "BEARISH"
                return "Unknown"

            h4_trend = get_trend(symbol, mt5.TIMEFRAME_H4)
            m15_trend = get_trend(symbol, mt5.TIMEFRAME_M15)
            m5_trend = get_trend(symbol, mt5.TIMEFRAME_M5)
            
            mtf_context = f"H4 Trend: {h4_trend} | M15 Trend: {m15_trend} | M5 Trend: {m5_trend}"
            '''

if target_run_ai in content:
    content = content.replace(target_run_ai, replacement_run_ai)
else:
    print("Could not find run_ai_analysis target.")

# 2. Update the analyze_market calls to pass mtf_context instead of h4_trend
content = content.replace('h4_trend=h4_trend', 'h4_trend=mtf_context')

# 3. Update analyze_market_with_ai definition
content = content.replace('h4_trend="Unknown"', 'h4_trend="H4 Trend: Unknown | M15 Trend: Unknown | M5 Trend: Unknown"')

# 4. Update the prompt string construction inside the analyze functions
target_prompt_string = '''    recent_data += f"\\n\\n*** IMPORTANT CONTEXT (HIGHER TIMEFRAME - H4) ***\\nThe current Trend on the 4-Hour (H4) Timeframe is: {h4_trend}\\nPlease prioritize setups that align with this H4 Trend. Avoid counter-trend setups unless confidence is very high.\\n*************************************************\\n"'''
replacement_prompt_string = '''    recent_data += f"\\n\\n*** 🚀 MULTI-TIMEFRAME (MTF) CONTEXT ***\\nMulti-Timeframe Structure: {h4_trend}\\nPlease prioritize setups that align across multiple timeframes. A strong setup should have M5 and M15 aligning with the H4 direction.\\n*************************************************\\n"'''
content = content.replace(target_prompt_string, replacement_prompt_string)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("MTF Patch applied!")
