import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import datetime
import json

def fetch_historical_data(symbol, timeframe=mt5.TIMEFRAME_M15, num_bars=5000):
    """
    Fetch historical OHLC data from MT5 for backtesting.
    """
    if not mt5.initialize():
        print("MT5 initialization failed")
        return None
        
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    if rates is None or len(rates) == 0:
        return None
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Pre-calculate common indicators
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean()
    
    # ATR for dynamic SL/TP
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    return df

def run_simulation(df, params):
    """
    Simulate trading over historical data using provided strategy parameters.
    """
    sl_multiplier = params.get('sl_multiplier', 1.5)
    rr_ratio = params.get('rr_ratio', 2.0)
    use_trend_filter = params.get('use_trend_filter', True)
    
    trades = []
    equity = 10000.0  # Starting balance
    equity_curve = [equity]
    
    # State tracking
    open_position = None
    
    for i in range(200, len(df)):
        row = df.iloc[i]
        
        # Check for open position resolution
        if open_position:
            if open_position['type'] == 'BUY':
                if row['low'] <= open_position['sl']:
                    # Stop loss hit
                    loss = open_position['sl'] - open_position['entry']
                    equity += loss * 100 # Approx multiplier
                    open_position['exit'] = open_position['sl']
                    open_position['profit'] = loss * 100
                    trades.append(open_position)
                    open_position = None
                elif row['high'] >= open_position['tp']:
                    # Take profit hit
                    profit = open_position['tp'] - open_position['entry']
                    equity += profit * 100
                    open_position['exit'] = open_position['tp']
                    open_position['profit'] = profit * 100
                    trades.append(open_position)
                    open_position = None
            elif open_position['type'] == 'SELL':
                if row['high'] >= open_position['sl']:
                    loss = open_position['entry'] - open_position['sl']
                    equity += loss * 100
                    open_position['exit'] = open_position['sl']
                    open_position['profit'] = loss * 100
                    trades.append(open_position)
                    open_position = None
                elif row['low'] <= open_position['tp']:
                    profit = open_position['entry'] - open_position['tp']
                    equity += profit * 100
                    open_position['exit'] = open_position['tp']
                    open_position['profit'] = profit * 100
                    trades.append(open_position)
                    open_position = None
            
            equity_curve.append(equity)
            continue
            
        equity_curve.append(equity)
            
        # Entry Logic (Simulating SMC + EMA crossover)
        trend_is_bullish = row['EMA50'] > row['EMA200']
        trend_is_bearish = row['EMA50'] < row['EMA200']
        
        # Simulate an entry signal: e.g. price touches EMA50 in direction of trend
        entry_signal = None
        if use_trend_filter:
            if trend_is_bullish and row['low'] <= row['EMA50'] and row['close'] > row['EMA50']:
                entry_signal = 'BUY'
            elif trend_is_bearish and row['high'] >= row['EMA50'] and row['close'] < row['EMA50']:
                entry_signal = 'SELL'
        else:
            # Reversion signal
            if row['close'] < row['EMA200'] - (row['ATR'] * 2):
                entry_signal = 'BUY'
            elif row['close'] > row['EMA200'] + (row['ATR'] * 2):
                entry_signal = 'SELL'
                
        if entry_signal:
            entry_price = row['close']
            atr = row['ATR']
            sl_dist = atr * sl_multiplier
            tp_dist = sl_dist * rr_ratio
            
            if entry_signal == 'BUY':
                sl = entry_price - sl_dist
                tp = entry_price + tp_dist
            else:
                sl = entry_price + sl_dist
                tp = entry_price - tp_dist
                
            open_position = {
                'type': entry_signal,
                'entry': entry_price,
                'sl': sl,
                'tp': tp,
                'time': row['time'].isoformat(),
                'profit': 0
            }
            
    # Calculate stats
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t['profit'] > 0)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    total_profit = sum(t['profit'] for t in trades)
    
    stats = {
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'total_profit': round(total_profit, 2),
        'final_equity': round(equity, 2),
        'equity_curve': equity_curve[::50] # Sampled down for chart rendering
    }
    return stats
