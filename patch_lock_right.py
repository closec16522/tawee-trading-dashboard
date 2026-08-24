import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Bring back the resizing logic and grid changes
original_css = "#command-center-root .body{display:grid;grid-template-columns:1fr 326px;min-height:0;height:100%;}"
new_css = """#command-center-root .body{display:grid;grid-template-columns:1fr max-content;min-height:0;height:100%;}
#command-center-root .rightcol { width: 326px; resize: horizontal; direction: rtl; overflow: auto; min-width: 250px; max-width: 600px; padding-left: 8px !important; }
#command-center-root .rightcol > * { direction: ltr; }
"""
html = html.replace(original_css, new_css)

# 2. Remove the media query rules that break the layout and force wrapping
media_query_bad = """      @media (max-width: 1024px) {
        #command-center-root .body { flex-direction: column !important; overflow-y: auto !important; }
        #command-center-root .center { width: 100% !important; flex: none !important; min-height: 480px; }
        #command-center-root .rightcol { width: 100% !important; height: auto !important; padding: 8px !important; }"""

# We just remove those three lines.
if media_query_bad in html:
    html = html.replace(media_query_bad, "      @media (max-width: 1024px) {")
else:
    print("Warning: Could not find exact media query block to remove. Will use regex.")
    html = re.sub(r'#command-center-root \.body \{ flex-direction: column !important; overflow-y: auto !important; \}\s*', '', html)
    html = re.sub(r'#command-center-root \.center \{ width: 100% !important; flex: none !important; min-height: 480px; \}\s*', '', html)
    html = re.sub(r'#command-center-root \.rightcol \{ width: 100% !important; height: auto !important; padding: 8px !important; \}\s*', '', html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Locked layout to right side, restored resize capability, and disabled mobile wrapping.")
