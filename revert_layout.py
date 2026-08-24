import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Revert .body and .center layout changes
bad_body_css = """#command-center-root .body{display:flex;flex-direction:row;min-height:0;height:100%;}
#command-center-root .center { resize: horizontal; overflow: hidden; width: 75%; min-width: 400px; max-width: 95%; flex-shrink: 0; display: flex; flex-direction: column; }
#command-center-root .rightcol { flex: 1; min-width: 250px; overflow-y: auto; }
"""
original_body_css = "#command-center-root .body{display:grid;grid-template-columns:1fr 326px;min-height:0;height:100%;}"

html = html.replace(bad_body_css, original_body_css)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Reverted .body layout to original grid.")
