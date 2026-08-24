import os

file_path = 'mt5_backend/pattern_detector.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Rename the original function
content = content.replace("def detect_chart_pattern(df, window=5, tolerance=0.005):", "def _detect_pattern_impl(df, window=5, tolerance=0.005):")

# Add the new wrapper function
wrapper = """
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

def _detect_pattern_impl(df, window=5, tolerance=0.005):"""

content = content.replace("def _detect_pattern_impl(df, window=5, tolerance=0.005):", wrapper)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched pattern_detector.py")
