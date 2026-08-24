import os

file_path = os.path.join('mt5_backend', 'pattern_detector.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_func = """
def detect_support_resistance(df, window=15, num_lines=2, tolerance=0.002):
    \"\"\"
    Detects major support and resistance levels.
    Returns: [{"price": float, "type": "support" | "resistance"}, ...]
    \"\"\"
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
"""

if "def detect_support_resistance" not in content:
    content += new_func
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added detect_support_resistance to pattern_detector.py")
else:
    print("Function already exists.")
