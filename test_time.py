import pandas as pd
import numpy as np
import json

def generate_points():
    current_time = 1600000000
    current_price = 1900.5
    
    ext_list = [
        {'time': 1599990000, 'val': 1905.0},
        {'time': 1600000000, 'val': 1900.5}
    ]
    
    pts = [{"time": e['time'], "value": e['val']} for e in ext_list]
    
    # Only append if time is strictly greater
    if current_time > pts[-1]["time"]:
        pts.append({"time": current_time, "value": current_price})
        
    return pts

print(generate_points())
