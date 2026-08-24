import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Make viewtabs not dictate the width of .center
old_viewtabs = r"#command-center-root \.viewtabs\{display:flex;align-items:center;gap:6px;flex-shrink:0;\}"
new_viewtabs = "#command-center-root .viewtabs{display:flex;align-items:center;gap:6px;flex-shrink:0;width:0 !important;min-width:100% !important;}"
html = re.sub(old_viewtabs, new_viewtabs, html)

# Just to be extra safe, ensure .viewtabs has flex-wrap in CSS too
if "flex-wrap:wrap" not in new_viewtabs:
    html = html.replace(new_viewtabs, new_viewtabs.replace("display:flex;", "display:flex;flex-wrap:wrap !important;"))

# Let's also ensure .center has no min-width that prevents shrinking too much
old_center = r"#command-center-root \.center \{ width: auto !important; flex: 0 0 auto !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; \}"
# Make sure it's intact

# Let's ensure .rightcol panels break text or wrap cleanly if they get very small
panel_css_patch = "\n#command-center-root .panel { min-width: 0 !important; overflow: hidden !important; }\n#command-center-root .ai-meeting-log { min-width: 0 !important; word-wrap: break-word !important; white-space: normal !important; }\n#command-center-root .wl { flex-wrap: wrap !important; }\n#command-center-root .trade { flex-wrap: wrap !important; min-width: 0 !important; }\n"
if "word-wrap: break-word !important;" not in html:
    html = html.replace(new_viewtabs, new_viewtabs + panel_css_patch)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Applied responsive width constraints to viewtabs and panels.")
