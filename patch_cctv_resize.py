import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Current center CSS
old_center = r"#command-center-root \.center \{ resize: horizontal !important; overflow: hidden !important; width: 75% !important; min-width: 400px !important; max-width: 95% !important; flex: 0 0 auto !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; \}"

# New center CSS: no resize, width auto
new_center = "#command-center-root .center { width: auto !important; flex: 0 0 auto !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; }"

# We need to add resize to .stage
# The existing .stage might not have a specific ID, but we can add a new CSS rule just for it
stage_resize_rule = "\n#command-center-root .stage { resize: horizontal !important; overflow: hidden !important; width: 70vw !important; min-width: 400px !important; max-width: 90vw !important; }\n"

html = re.sub(old_center, new_center + stage_resize_rule, html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Moved resize from .center to .stage for intuitive CCTV resizing.")
