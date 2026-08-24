import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Current CSS
old_body = r"#command-center-root \.body\{display:flex !important;flex-direction:row !important;flex-wrap:nowrap !important;min-height:0;height:100%;\}"
old_rightcol = r"#command-center-root \.rightcol \{ flex: 0 0 auto !important; width: 326px; resize: horizontal; direction: rtl; overflow-y: auto; overflow-x: hidden; min-width: 250px; max-width: 600px; padding-left: 8px !important; margin-left: auto !important; \}"
old_center = r"#command-center-root \.center \{ flex: 1 1 0% !important; min-width: 0 !important; overflow: hidden !important; \}"

# New CSS based on what the user originally liked, but with height constraints to prevent footer push-down
new_body = "#command-center-root .body{display:flex !important;flex-direction:row !important;flex-wrap:nowrap !important;min-height:0;height:100%;}"
new_rightcol = "#command-center-root .rightcol { flex: 1 1 0% !important; min-width: 250px; overflow-y: auto !important; height: 100% !important; min-height: 0 !important; padding: 8px !important; }"
new_center = "#command-center-root .center { resize: horizontal !important; overflow: hidden !important; width: 75% !important; min-width: 400px !important; max-width: 95% !important; flex: 0 0 auto !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; }"

html = re.sub(old_body, new_body, html)
html = re.sub(old_rightcol, new_rightcol, html)
html = re.sub(old_center, new_center, html)

# Also remove the #command-center-root .rightcol > * { direction: ltr; }
html = re.sub(r'#command-center-root \.rightcol > \* \{ direction: ltr; \}\s*', '', html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Restored resize on CCTV, locked layout, fixed footer overflow.")
