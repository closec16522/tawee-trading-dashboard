import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add absolute max-width to .center to protect .rightcol from ever being pushed out
old_center = r"#command-center-root \.center \{ width: auto !important; flex: 0 1 auto !important; min-width: 0 !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; \}"
new_center = "#command-center-root .center { width: auto !important; flex: 0 1 auto !important; min-width: 0 !important; max-width: calc(100% - 380px) !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; }"

# 2. Add padding-right to .rightcol to give the 0.25 inch gap (approx 24px)
old_rightcol = r"#command-center-root \.rightcol \{ flex: 1 0 0% !important; min-width: 326px !important; overflow-y: auto !important; height: 100% !important; min-height: 0 !important; padding: 8px !important; \}"
new_rightcol = "#command-center-root .rightcol { flex: 1 0 0% !important; min-width: 350px !important; max-width: 500px !important; overflow-y: auto !important; height: 100% !important; min-height: 0 !important; padding: 8px 24px 8px 8px !important; box-sizing: border-box !important; }"

html = re.sub(old_center, new_center, html)
html = re.sub(old_rightcol, new_rightcol, html)

# Ensure .body itself isn't overflowing
old_body = r"#command-center-root \.body\{display:flex !important;flex-direction:row !important;flex-wrap:nowrap !important;min-height:0;height:100%;\}"
new_body = "#command-center-root .body{display:flex !important;flex-direction:row !important;flex-wrap:nowrap !important;min-height:0;height:100%;max-width:100% !important;overflow-x:hidden !important;}"
html = re.sub(old_body, new_body, html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Applied absolute max-width to center to protect rightcol, added right padding.")
