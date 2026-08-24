import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Make the grid column auto-sizing and the rightcol resizable
old_body_css = "#command-center-root .body{display:grid;grid-template-columns:1fr 326px;min-height:0;height:100%;}"
new_body_css = """#command-center-root .body{display:grid;grid-template-columns:1fr max-content;min-height:0;height:100%;}
#command-center-root .rightcol { width: 326px; resize: horizontal; direction: rtl; overflow: auto; min-width: 250px; max-width: 50vw; padding-left: 8px !important; }
#command-center-root .rightcol > * { direction: ltr; }
"""
html = html.replace(old_body_css, new_body_css)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated .body to support CSS resizing of rightcol.")
