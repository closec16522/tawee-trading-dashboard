import MetaTrader5 as mt5
from datetime import datetime, time as datetime_time
import pandas as pd

# EA Settings (Configurable by user)
import os
EA_SETTINGS = {
    "DAILY_PROFIT_LIMIT": 50.0,     
    "DAILY_LOSS_LIMIT": -30.0,      
    "ALLOWED_SESSIONS": [(10, 22)], 
    "MIN_CONFIDENCE": 80,           
    "ATR_MULTIPLIER_SL": 1.5,       
    "ATR_MULTIPLIER_TP": 2.5,       
    "BREAK_EVEN_POINTS": 300,       
    "TRAILING_STOP_POINTS": 200,    
    # --- 🚀 NEW INSTITUTIONAL SETTINGS ---
    "MAX_DRAWDOWN_PERCENT": 10.0,   # ป้องกันพอร์ตแตก ถ้า Equity ร่วง -10% จากจุดสูงสุด (High Water Mark) บอทจะหยุดทำงาน
    "RISK_PER_TRADE_PERCENT": 1.0   # ความเสี่ยงต่อ 1 ไม้ (เช่น 1% ของพอร์ต) เพื่อใช้คำนวณ Lot Size อัตโนมัติ
}

# Global state for Drawdown
HIGH_WATER_MARK = 0.0
HWM_FILE = os.path.join(os.path.dirname(__file__), "hwm.txt")

def load_hwm():
    global HIGH_WATER_MARK
    if os.path.exists(HWM_FILE):
        try:
            with open(HWM_FILE, 'r') as f:
                HIGH_WATER_MARK = float(f.read().strip())
        except:
            pass

def save_hwm():
    try:
        with open(HWM_FILE, 'w') as f:
            f.write(str(HIGH_WATER_MARK))
    except:
        pass
load_hwm()


def check_session_and_limits():
    """
    Checks if current time is within allowed sessions and if daily PnL is within limits.
    Returns (True, "") if allowed to trade, (False, "reason") if trading should be halted.
    """
    # 1. Check Session
    current_time = datetime.now() # Assuming local time aligns with MT5 or we can use mt5.symbol_info_tick
    current_hour = current_time.hour
    
    in_session = False
    for start, end in EA_SETTINGS["ALLOWED_SESSIONS"]:
        if start <= current_hour <= end:
            in_session = True
            break
            
    if not in_session:
        return False, f"Outside trading hours ({current_hour}:00)"

    # 2. Check Daily Limit
    today_start = datetime(current_time.year, current_time.month, current_time.day)
    deals = mt5.history_deals_get(today_start, current_time)
    
    daily_pnl = 0.0
    if deals:
        for deal in deals:
            if deal.entry == 1: # OUT deal (closing a position)
                daily_pnl += deal.profit
                
    if daily_pnl >= EA_SETTINGS["DAILY_PROFIT_LIMIT"]:
        return False, f"Daily Profit Limit Reached (${daily_pnl:.2f})"
    if daily_pnl <= EA_SETTINGS["DAILY_LOSS_LIMIT"]:
        return False, f"Daily Loss Limit Reached (${daily_pnl:.2f})"
        
    # 3. Check Global Drawdown Protection
    global HIGH_WATER_MARK
    account_info = mt5.account_info()
    if account_info:
        current_equity = account_info.equity
        if current_equity > HIGH_WATER_MARK:
            HIGH_WATER_MARK = current_equity
            save_hwm()
        
        if HIGH_WATER_MARK > 0:
            drawdown_percent = ((HIGH_WATER_MARK - current_equity) / HIGH_WATER_MARK) * 100.0
            if drawdown_percent >= EA_SETTINGS["MAX_DRAWDOWN_PERCENT"]:
                return False, f"CRITICAL: Max Drawdown Reached ({drawdown_percent:.1f}%). Trading Halted!"
                
    return True, f"PnL OK (${daily_pnl:.2f})"

def calculate_atr_sl_tp(symbol, action, df, price):
    """
    Calculates SL and TP prices based on the latest ATR value.
    """
    if "ATR" not in df.columns:
        # Fallback to fixed points if no ATR
        points = mt5.symbol_info(symbol).point
        fixed_sl = 500 * points
        fixed_tp = 1000 * points
        if action == "BUY":
            return price - fixed_sl, price + fixed_tp
        else:
            return price + fixed_sl, price - fixed_tp
            
    atr = df.iloc[-1]["ATR"]
    if action == "BUY":
        sl = price - (atr * EA_SETTINGS["ATR_MULTIPLIER_SL"])
        tp = price + (atr * EA_SETTINGS["ATR_MULTIPLIER_TP"])
    else:
        sl = price + (atr * EA_SETTINGS["ATR_MULTIPLIER_SL"])
        tp = price - (atr * EA_SETTINGS["ATR_MULTIPLIER_TP"])
        
    return sl, tp

def manage_active_trades():
    """
    Applies Break Even and Trailing Stops to open positions.
    """
    positions = mt5.positions_get()
    if not positions:
        return
        
    for pos in positions:
        symbol = pos.symbol
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            continue
            
        point = symbol_info.point
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            continue
            
        current_price = tick.bid if pos.type == 0 else tick.ask # Type 0 = BUY, Type 1 = SELL
        
        be_points = EA_SETTINGS["BREAK_EVEN_POINTS"] * point
        ts_points = EA_SETTINGS["TRAILING_STOP_POINTS"] * point
        
        new_sl = pos.sl
        modified = False
        
        if pos.type == 0: # BUY
            profit_distance = current_price - pos.price_open
            
            # Break Even
            if profit_distance >= be_points and pos.sl < pos.price_open:
                new_sl = pos.price_open
                modified = True
                
            # Trailing Stop
            if profit_distance > ts_points:
                trail_level = current_price - ts_points
                if trail_level > new_sl:
                    new_sl = trail_level
                    modified = True
                    
        elif pos.type == 1: # SELL
            profit_distance = pos.price_open - current_price
            
            # Break Even
            if profit_distance >= be_points and (pos.sl > pos.price_open or pos.sl == 0):
                new_sl = pos.price_open
                modified = True
                
            # Trailing Stop
            if profit_distance > ts_points:
                trail_level = current_price + ts_points
                if trail_level < new_sl or new_sl == 0:
                    new_sl = trail_level
                    modified = True
                    
        if modified and new_sl != pos.sl:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": pos.ticket,
                "symbol": symbol,
                "sl": new_sl,
                "tp": pos.tp
            }
            res = mt5.order_send(request)
            if res.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Modified SL for {symbol} #{pos.ticket} to {new_sl} (BE/Trailing)")
            else:
                print(f"❌ Failed to modify SL for {symbol} #{pos.ticket}: {res.retcode}")

def get_dynamic_lot_size(symbol, sl_distance):
    """
    Calculates the exact Lot Size so that if SL is hit, we lose exactly RISK_PER_TRADE_PERCENT of our Equity.
    """
    account_info = mt5.account_info()
    symbol_info = mt5.symbol_info(symbol)
    
    if not account_info or not symbol_info or sl_distance <= 0:
        return 0.01 # Fallback to micro lot
        
    equity = account_info.equity
    risk_amount = equity * (EA_SETTINGS["RISK_PER_TRADE_PERCENT"] / 100.0)
    
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    if tick_size == 0 or tick_value == 0:
        return 0.01
        
    sl_points = sl_distance / symbol_info.point
    if sl_points == 0: return 0.01
    
    # Calculate lot size
    # Formula: Risk Amount = Lot Size * SL Points * (Tick Value / Tick Size) * Point
    # Since in MT5, Tick Value is for 1 standard lot.
    loss_for_one_lot = (sl_distance / tick_size) * tick_value
    
    if loss_for_one_lot > 0:
        raw_lot = risk_amount / loss_for_one_lot
        
        # Round to step
        step = symbol_info.volume_step
        min_vol = symbol_info.volume_min
        max_vol = symbol_info.volume_max
        
        lot = round(raw_lot / step) * step
        lot = max(min_vol, min(lot, max_vol))
        return round(lot, 2)
        
    return 0.01
