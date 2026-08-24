import os

file_path = 'mt5_backend/pattern_detector.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to fix the duplicate time issue in cleaned_ext
# Let's find the loop:
old_loop = """    for e in extremums:
        if not cleaned_ext:
            cleaned_ext.append(e)
        else:
            if cleaned_ext[-1]['type'] == e['type']:
                if e['type'] == 'peak':
                    if e['val'] > cleaned_ext[-1]['val']:
                        cleaned_ext[-1] = e
                else:
                    if e['val'] < cleaned_ext[-1]['val']:
                        cleaned_ext[-1] = e
            else:
                cleaned_ext.append(e)"""

new_loop = """    for e in extremums:
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
                cleaned_ext.append(e)"""

if "if cleaned_ext[-1]['time'] == e['time']:" not in content:
    content = content.replace(old_loop, new_loop)

# Also ensure to_points does not append current_time if it's equal or less than last time
old_to_points = """        if len(pts) == 0 or current_time > pts[-1]["time"]:
            pts.append({"time": current_time, "value": current_price})"""
            
new_to_points = """        if len(pts) == 0 or current_time > pts[-1]["time"]:
            pts.append({"time": current_time, "value": current_price})""" # already correct

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched pattern_detector.py to remove duplicate times.")
