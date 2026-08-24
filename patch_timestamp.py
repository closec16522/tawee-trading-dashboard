import os
import re

file_path = os.path.join('mt5_backend', 'pattern_detector.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

def patch_int_time(c):
    old_code = """    extremums = []
    for p in peaks:
        extremums.append({'time': int(p['time']), 'type': 'peak', 'val': p['peak']})
    for t in troughs:
        extremums.append({'time': int(t['time']), 'type': 'trough', 'val': t['trough']})"""
        
    new_code = """    extremums = []
    for p in peaks:
        t_val = p['time']
        if hasattr(t_val, 'timestamp'): t_val = t_val.timestamp()
        extremums.append({'time': int(t_val), 'type': 'peak', 'val': p['peak']})
    for t in troughs:
        t_val = t['time']
        if hasattr(t_val, 'timestamp'): t_val = t_val.timestamp()
        extremums.append({'time': int(t_val), 'type': 'trough', 'val': t['trough']})"""
        
    return c.replace(old_code, new_code)

new_content = patch_int_time(content)
if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Patched pattern_detector.py successfully.")
else:
    print("Could not find the block to patch.")
