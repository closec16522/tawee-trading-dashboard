import pandas as pd
import numpy as np


def detect_chart_pattern(df, window=5, tolerance=0.005):
    # Try multiple configurations to increase detection rate
    configs = [
        (window, tolerance),
        (5, 0.01),
        (4, 0.01),
        (3, 0.015),
        (3, 0.02)
    ]
    for w, t in configs:
        name, pts = _detect_pattern_impl(df, window=w, tolerance=t)
        if name != "None":
            return name, pts
    return "None", []

def _detect_pattern_impl(df, window=5, tolerance=0.005):
    """
    Detects basic chart patterns from a DataFrame with 'time', 'high', 'low', 'close' columns.
    Tolerance is the % difference allowed between peaks/troughs to be considered equal.
    Returns: (pattern_name, list_of_points)
    where list_of_points = [{"time": t, "value": v}, ...]
    """
    if len(df) < window * 3:
        return "None", []
        
    df = df.copy()
    
    df['peak'] = df['high'][(df['high'] == df['high'].rolling(window=window*2+1, center=True).max())]
    df['trough'] = df['low'][(df['low'] == df['low'].rolling(window=window*2+1, center=True).min())]
    
    # We need the time for drawing
    # Assuming df has 'time' column
    if 'time' not in df.columns:
        df['time'] = df.index

    peaks = df[df['peak'].notna()][['time', 'peak']].to_dict('records') # [{'time': t, 'peak': v}]
    troughs = df[df['trough'].notna()][['time', 'trough']].to_dict('records')
    
    extremums = []
    for p in peaks:
        t_val = p['time']
        if hasattr(t_val, 'timestamp'): t_val = t_val.timestamp()
        extremums.append({'time': int(t_val), 'type': 'peak', 'val': p['peak']})
    for t in troughs:
        t_val = t['time']
        if hasattr(t_val, 'timestamp'): t_val = t_val.timestamp()
        extremums.append({'time': int(t_val), 'type': 'trough', 'val': t['trough']})
        
    extremums.sort(key=lambda x: x['time'])
    
    cleaned_ext = []
    for e in extremums:
        if not cleaned_ext:
            cleaned_ext.append(e)
        else:
            # If a single candle is both peak and trough, ignore the second one or handle it
            if cleaned_ext[-1]['time'] == e['time']:
                continue
                
            if cleaned_ext[-1]['type'] == e['type']:
                if e['type'] == 'peak':
                    if e['val'] > cleaned_ext[-1]['val']:
                        cleaned_ext[-1] = e
                else:
                    if e['val'] < cleaned_ext[-1]['val']:
                        cleaned_ext[-1] = e
            else:
                cleaned_ext.append(e)
                
    if len(cleaned_ext) < 3:
        return "None", []
        
    recent = cleaned_ext[-5:]
    
    def is_equal(v1, v2, tol=tolerance):
        return abs(v1 - v2) / max(v1, v2) <= tol
        
    # Get the latest candle to extend the line to current price
    current_candle = df.iloc[-1]
    current_time = current_candle['time']
    if hasattr(current_time, 'timestamp'): 
        current_time = current_time.timestamp()
    current_time = int(current_time)
    current_price = current_candle['close']

    def to_points(ext_list):
        pts = [{"time": e['time'], "value": e['val']} for e in ext_list]
        if len(pts) == 0 or current_time > pts[-1]["time"]:
            pts.append({"time": current_time, "value": current_price})
        return pts

    if len(recent) >= 3:
        p1, p2, p3 = recent[-3], recent[-2], recent[-1]
        if p1['type'] == 'peak' and p2['type'] == 'trough' and p3['type'] == 'peak':
            if is_equal(p1['val'], p3['val']):
                return "Double Top", to_points([p1, p2, p3])
                
        if p1['type'] == 'trough' and p2['type'] == 'peak' and p3['type'] == 'trough':
            if is_equal(p1['val'], p3['val']):
                return "Double Bottom", to_points([p1, p2, p3])

    if len(recent) >= 5:
        p1, p2, p3, p4, p5 = recent[-5], recent[-4], recent[-3], recent[-2], recent[-1]
        if (p1['type'] == 'peak' and p2['type'] == 'trough' and 
            p3['type'] == 'peak' and p4['type'] == 'trough' and p5['type'] == 'peak'):
            if p3['val'] > p1['val'] and p3['val'] > p5['val']:
                if is_equal(p1['val'], p5['val'], tol=tolerance*2):
                    return "Head & Shoulders", to_points([p1, p2, p3, p4, p5])
                    
        if (p1['type'] == 'trough' and p2['type'] == 'peak' and 
            p3['type'] == 'trough' and p4['type'] == 'peak' and p5['type'] == 'trough'):
            if p3['val'] < p1['val'] and p3['val'] < p5['val']:
                if is_equal(p1['val'], p5['val'], tol=tolerance*2):
                    return "Inverse Head & Shoulders", to_points([p1, p2, p3, p4, p5])

    if len(recent) >= 4:
        p1, p2, p3, p4 = recent[-4], recent[-3], recent[-2], recent[-1]
        if p1['type'] == 'trough' and p2['type'] == 'peak' and p3['type'] == 'trough' and p4['type'] == 'peak':
            if p3['val'] > p1['val'] and p4['val'] > p2['val']:
                return "Higher Highs & Lows (Uptrend)", to_points([p1, p2, p3, p4])
        if p1['type'] == 'peak' and p2['type'] == 'trough' and p3['type'] == 'peak' and p4['type'] == 'trough':
            if p3['val'] < p1['val'] and p4['val'] < p2['val']:
                return "Lower Highs & Lows (Downtrend)", to_points([p1, p2, p3, p4])

    return "None", []

def detect_support_resistance(df, window=15, num_lines=2, tolerance=0.002):
    """
    Detects major support and resistance levels.
    Returns: [{"price": float, "type": "support" | "resistance"}, ...]
    """
    if len(df) < window * 2:
        return []
        
    df = df.copy()
    
    # Find rolling max/min
    df['peak'] = df['high'][(df['high'] == df['high'].rolling(window=window*2+1, center=True).max())]
    df['trough'] = df['low'][(df['low'] == df['low'].rolling(window=window*2+1, center=True).min())]
    
    peaks = df['peak'].dropna().tolist()
    troughs = df['trough'].dropna().tolist()
    
    # Function to cluster nearby levels
    def cluster_levels(levels, tol):
        clusters = []
        for val in sorted(levels):
            matched = False
            for c in clusters:
                avg = sum(c) / len(c)
                if abs(val - avg) / avg <= tol:
                    c.append(val)
                    matched = True
                    break
            if not matched:
                clusters.append([val])
        return clusters

    peak_clusters = cluster_levels(peaks, tolerance)
    trough_clusters = cluster_levels(troughs, tolerance)
    
    # Sort clusters by number of touches (len) descending, then by recentness (we don't have time here easily, so just touches)
    peak_clusters.sort(key=lambda x: len(x), reverse=True)
    trough_clusters.sort(key=lambda x: len(x), reverse=True)
    
    sr_lines = []
    
    # Add top resistance lines
    for c in peak_clusters[:num_lines]:
        avg_price = sum(c) / len(c)
        sr_lines.append({"price": round(avg_price, 5), "type": "resistance"})
        
    # Add top support lines
    for c in trough_clusters[:num_lines]:
        avg_price = sum(c) / len(c)
        sr_lines.append({"price": round(avg_price, 5), "type": "support"})
        
    return sr_lines
