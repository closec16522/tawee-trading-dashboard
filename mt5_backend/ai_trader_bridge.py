import pandas as pd
import MetaTrader5 as mt5
import backtrader as bt
import yaml
import os

try:
    from ai_trader.utils.backtest import create_cerebro, add_analyzers
    from ai_trader.backtesting.strategies.classic.sma import CrossSMAStrategy
except ImportError:
    pass # Wait for pip install to finish

class CustomEquityAnalyzer(bt.Analyzer):
    def __init__(self):
        self.equity_curve = []
    
    def next(self):
        self.equity_curve.append(self.strategy.broker.getvalue())
        
    def get_analysis(self):
        return {"equity_curve": self.equity_curve}

def fetch_historical_data_for_bt(symbol, timeframe=mt5.TIMEFRAME_M15, num_bars=5000):
    if not mt5.initialize():
        print("MT5 initialization failed")
        return None
        
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    if rates is None or len(rates) == 0:
        return None
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df.rename(columns={'tick_volume': 'volume'}, inplace=True)
    return df

def generate_yaml_config(symbol, start_date, end_date, params):
    """Generate a YAML configuration according to ai-trader specs."""
    config = {
        "broker": {
            "cash": 10000.0,
            "commission": 0.0
        },
        "data": {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        },
        "strategy": {
            "class": "CrossSMAStrategy",
            "params": params
        },
        "sizer": {
            "type": "percent",
            "params": {
                "percents": 95
            }
        }
    }
    
    os.makedirs('backtests', exist_ok=True)
    filepath = f"backtests/{symbol}_config.yaml"
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)
    
    return filepath

def run_ai_trader_simulation(df, strategy_class, params):
    cerebro = create_cerebro(cash=10000.0, commission=0.0)
    
    # Create data feed
    feed = bt.feeds.PandasData(
        dataname=df,
        timeframe=bt.TimeFrame.Minutes,
        compression=15, # M15
        openinterest=-1
    )
    cerebro.adddata(feed)
    
    # Add strategy
    cerebro.addstrategy(strategy_class, **params)
    
    # Add analyzers
    add_analyzers(cerebro, ['trades', 'drawdown', 'sharpe'])
    cerebro.addanalyzer(CustomEquityAnalyzer, _name='equity')
    
    results = cerebro.run()
    strat = results[0]
    
    trades_analyzer = strat.analyzers.trades.get_analysis()
    equity_analyzer = strat.analyzers.equity.get_analysis()
    
    total_trades = trades_analyzer.get('total', {}).get('total', 0)
    won = trades_analyzer.get('won', {}).get('total', 0)
    win_rate = (won / total_trades * 100) if total_trades > 0 else 0
    
    pnl = trades_analyzer.get('pnl', {}).get('net', {}).get('total', 0)
    final_equity = strat.broker.getvalue()
    
    stats = {
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'total_profit': round(pnl, 2),
        'final_equity': round(final_equity, 2),
        'equity_curve': equity_analyzer['equity_curve'][::50] # Sample down
    }
    return stats
