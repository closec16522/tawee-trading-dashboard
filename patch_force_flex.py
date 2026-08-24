import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the grid CSS with forced Flexbox CSS
old_css = r"#command-center-root \.body\{display:grid;grid-template-columns:1fr max-content;min-height:0;height:100%;\}"
new_css = "#command-center-root .body{display:flex !important;flex-direction:row !important;flex-wrap:nowrap !important;min-height:0;height:100%;}"

html = re.sub(old_css, new_css, html)

# Replace rightcol CSS to work with Flexbox
old_rightcol = r"#command-center-root \.rightcol \{ width: 326px; resize: horizontal; direction: rtl; overflow: auto; min-width: 250px; max-width: 600px; padding-left: 8px !important; \}"
new_rightcol = "#command-center-root .rightcol { flex: 0 0 auto !important; width: 326px; resize: horizontal; direction: rtl; overflow-y: auto; overflow-x: hidden; min-width: 250px; max-width: 600px; padding-left: 8px !important; margin-left: auto !important; }"

html = re.sub(old_rightcol, new_rightcol, html)

# Force .center to shrink and not push rightcol away
old_center_re = r"#command-center-root \.center \{"
# Wait, .center might not have a base CSS rule. Let's add it right after .rightcol
center_css = "\n#command-center-root .center { flex: 1 1 0% !important; min-width: 0 !important; overflow: hidden !important; }\n"
if "#command-center-root .center { flex:" not in html:
    html = html.replace(new_rightcol, new_rightcol + center_css)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Forced Flexbox nowrap layout to prevent wrapping.")
