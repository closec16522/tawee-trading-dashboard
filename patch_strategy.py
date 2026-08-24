import re
import os
import json

file_path = "mt5_backend/agent_orchestrator.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add get_strategy_context_str function and run_weekly_strategy_review function
new_functions = """
def get_strategy_context_str():
    try:
        strat_path = os.path.join(os.path.dirname(__file__), 'strategy_context.json')
        if os.path.exists(strat_path):
            with open(strat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                directive = data.get("directive", "")
                if directive:
                    return f"\\n\\n[STRATEGY AI DIRECTIVE FOR THIS WEEK]: {directive} -> ให้คุณนำกลยุทธ์นี้ไปปรับใช้ในการประเมินจุดเข้าและตั้ง SL/TP อย่างเคร่งครัด"
    except:
        pass
    return ""

def run_weekly_strategy_review():
    print("🧠 STRATEGY AI: Checking weekly performance for adaptation...")
    strat_path = os.path.join(os.path.dirname(__file__), 'strategy_context.json')
    last_run = 0
    import time
    try:
        if os.path.exists(strat_path):
            with open(strat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_run = data.get("last_run", 0)
    except:
        pass
        
    current_time = time.time()
    # Check if 7 days (604800 seconds) have passed
    if current_time - last_run < 604800:
        return
        
    print("🧠 STRATEGY AI: Running weekly adaptation analysis...")
    now = datetime.now()
    week_start = now - timedelta(days=7)
    deals = mt5.history_deals_get(week_start, now)
    
    profit = 0.0
    wins = 0
    losses = 0
    
    if deals:
        closed_deals = [d for d in deals if d.entry == 1]
        for d in closed_deals:
            profit += d.profit
            if d.profit > 0:
                wins += 1
            elif d.profit < 0:
                losses += 1
                
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    summary = f"Past 7 Days Performance: Total Trades={total_trades}, Win Rate={win_rate:.1f}%, Net Profit=${profit:.2f}"
    print(f"📊 STRATEGY AI: {summary}")
    
    directive = "Maintain current strategy."
    if gemini_model:
        prompt = f"Our Forex bot trading performance for the past 7 days is: Total Trades={total_trades}, Win Rate={win_rate:.1f}%, Net Profit=${profit:.2f}. If we are taking continuous losses or win rate is below 50%, analyze if the market regime has changed (e.g. trending to ranging) and provide a concise 'Strategy Adjustment Directive' in Thai (e.g. 'ลด Lot ลงครึ่งหนึ่งและเน้นเก็บสั้น', 'ตลาดผันผวนสูง ให้ขยับ SL ให้แคบลง'). If performance is good (profitable), just reply 'ลุยตามระบบเดิมต่อไป'. Keep it under 20 words."
        try:
            res = gemini_model.generate_content(prompt)
            directive = res.text.strip().replace('\\n', ' ')
            time.sleep(2)
        except Exception as e:
            print("Error generating strategy directive:", e)
            directive = "ลุยตามระบบเดิมต่อไป (API Error)"
            
    print(f"🎯 STRATEGY AI DIRECTIVE: {directive}")
    
    # Save to file
    new_data = {
        "last_run": current_time,
        "directive": directive,
        "summary": summary
    }
    try:
        with open(strat_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error saving strategy config:", e)

# --- END NEW FUNCTIONS ---
"""

# Insert the functions before send_summary_report
content = content.replace("def send_summary_report():", new_functions + "\ndef send_summary_report():")

# 2. Inject get_strategy_context_str() into recent_data in all 4 places
replacement_str = "recent_data = df.tail(10).to_string(columns=['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI']) + get_strategy_context_str()"
content = re.sub(
    r"recent_data = df\.tail\(10\)\.to_string\(columns=\['time', 'open', 'high', 'low', 'close', 'EMA50', 'EMA200', 'RSI'\]\)",
    replacement_str,
    content
)

# 3. Call run_weekly_strategy_review() inside the while True loop
main_loop_call = """
            run_portfolio_manager()
            run_trade_journal()
            run_weekly_strategy_review()
"""
content = content.replace("            run_portfolio_manager()\n            run_trade_journal()", main_loop_call)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
