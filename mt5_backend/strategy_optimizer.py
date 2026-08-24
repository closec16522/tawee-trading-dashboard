from local_ai import gemini_model
import json
import datetime
import time
import os

from ai_trader_bridge import fetch_historical_data_for_bt, run_ai_trader_simulation, generate_yaml_config

from ai_trader.backtesting.strategies.classic.sma import CrossSMAStrategy

MAIN_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
GEMINI_API_KEY = ""
if os.path.exists(MAIN_CONFIG_PATH):
    with open(MAIN_CONFIG_PATH, 'r', encoding='utf-8') as f:
        _config = json.load(f)
        GEMINI_API_KEY = _config.get("gemini_api_key", "")

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "backtest_results.json")

def setup_gemini():
    if not GEMINI_API_KEY:
        return None
    
    return genai.GenerativeModel('gemini-2.5-flash')

def optimize_strategy(symbol="XAUUSD-VIP"):
    model = setup_gemini()
    if not model:
        print("Gemini API missing.")
        return {"error": "Missing Gemini API Key"}
        
    print(f"Fetching historical data for {symbol}...")
    df = fetch_historical_data_for_bt(symbol)
    if df is None:
        return {"error": "Failed to fetch MT5 data"}
    
    start_date = df.index.min().strftime('%Y-%m-%d %H:%M')
    end_date = df.index.max().strftime('%Y-%m-%d %H:%M')
    period_str = f"{start_date} to {end_date}"
    
    # We will optimize a CrossSMAStrategy using ai-trader
    current_params = {
        "fast": 10,
        "slow": 30
    }
    
    best_stats = None
    best_params = None
    
    history_log = []
    
    for iteration in range(1, 3):
        print(f"\n--- Optimization Loop {iteration} ---")
        print(f"Testing params: {current_params}")
        
        # 1. Config-Driven: Generate YAML
        yaml_path = generate_yaml_config(symbol, start_date, end_date, current_params)
        print(f"Generated Config: {yaml_path}")
        
        # 2. Run simulation via ai-trader
        stats = run_ai_trader_simulation(df, CrossSMAStrategy, current_params)
        print(f"Results: Win Rate: {stats['win_rate']}%, Profit: ${stats['total_profit']}")
        
        history_log.append({
            "iteration": iteration,
            "params": current_params,
            "stats": stats
        })
        
        if best_stats is None or stats['total_profit'] > best_stats['total_profit']:
            best_stats = stats
            best_params = current_params.copy()
            
        # Ask AI to analyze
        prompt = f"""
        You are a quantitative trading AI using the 'ai-trader' framework (Backtrader engine).
        You are optimizing the CrossSMAStrategy for {symbol}.
        In iteration {iteration}, the strategy parameters were: {json.dumps(current_params)}
        The backtest results over the period are:
        - Total Trades: {stats['total_trades']}
        - Win Rate: {stats['win_rate']}%
        - Total Profit: ${stats['total_profit']}
        
        Propose a NEW set of parameters ('fast' and 'slow' period) to improve profitability.
        Respond ONLY in valid JSON format:
        {{
            "analysis": "Brief reason for changes",
            "new_params": {{
                "fast": <int>,
                "slow": <int>
            }}
        }}
        """
        
        try:
            res = model.generate_content(prompt)
            text = res.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            ai_response = json.loads(text.strip())
            print("AI Insight:", ai_response.get("analysis", ""))
            current_params = ai_response.get("new_params", current_params)
        except Exception as e:
            print("AI Optimization error:", e)
            break
            
        time.sleep(3)
        
    final_result = {
        "symbol": symbol,
        "period": period_str,
        "best_params": best_params,
        "period": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')} (H1, 5000 Bars)",
        "best_stats": best_stats,
        "history": history_log,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    return final_result

def run_all_optimizations():
    print("Starting Multi-Symbol Backtest Optimization using AI-Trader Framework...")
    if not os.path.exists(MAIN_CONFIG_PATH):
        symbols = ["XAUUSD-VIP"]
    else:
        with open(MAIN_CONFIG_PATH, 'r', encoding='utf-8') as f:
            _config = json.load(f)
            symbols = _config.get("symbols", ["XAUUSD-VIP"])
            
    all_results = {}
    for sym in symbols:
        res = optimize_strategy(sym)
        all_results[sym] = res
        
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
        
    print("Multi-Symbol Backtest Optimization Complete!")

if __name__ == "__main__":
    run_all_optimizations()
