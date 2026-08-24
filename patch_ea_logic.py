import json

path = 'mt5_backend/ea_logic.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update EA_SETTINGS
old_settings = '''EA_SETTINGS = {
    "DAILY_PROFIT_LIMIT": 50.0,     # กำไรถึง $50 (ประมาณ 5% ของพอร์ต 1000$) ให้หยุดพัก ล็อคกำไรรายวัน
    "DAILY_LOSS_LIMIT": -30.0,      # ขาดทุนถึง -$30 (ประมาณ 3%) ให้หยุดเทรด ป้องกันพอร์ตแตก
    "ALLOWED_SESSIONS": [(10, 22)], # เทรดเฉพาะช่วง London & NY (10:00-22:00 เวลา Server) เลี่ยงช่วงไซด์เวย์
    "MIN_CONFIDENCE": 80,           # ความมั่นใจขั้นต่ำของ AI
    "ATR_MULTIPLIER_SL": 1.5,       # SL กว้าง 1.5 เท่าของความผันผวน (ไม่แคบเกินไป)
    "ATR_MULTIPLIER_TP": 2.5,       # TP 2.5 เท่า (ได้ Risk/Reward Ratio ที่ดี > 1:1.5)
    "BREAK_EVEN_POINTS": 300,       # กำไร 300 จุด (30 pips) ดึง SL มาบังหน้าทุน (กันเหนียว ไม่โดนสวิงกินง่าย)
    "TRAILING_STOP_POINTS": 200     # ตามราคาทุกๆ 200 จุด (20 pips)
}'''

new_settings = '''import os
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
'''
content = content.replace(old_settings, new_settings)

# 2. Update check_session_and_limits
old_check = '''    if daily_pnl >= EA_SETTINGS["DAILY_PROFIT_LIMIT"]:
        return False, f"Daily Profit Limit Reached (${daily_pnl:.2f})"
    if daily_pnl <= EA_SETTINGS["DAILY_LOSS_LIMIT"]:
        return False, f"Daily Loss Limit Reached (${daily_pnl:.2f})"
        
    return True, f"PnL OK (${daily_pnl:.2f})"'''

new_check = '''    if daily_pnl >= EA_SETTINGS["DAILY_PROFIT_LIMIT"]:
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
                
    return True, f"PnL OK (${daily_pnl:.2f})"'''
content = content.replace(old_check, new_check)

# 3. Add get_dynamic_lot_size
new_func = '''
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
'''
content = content + new_func

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("ea_logic patched!")
