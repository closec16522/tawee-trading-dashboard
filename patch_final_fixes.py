import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Fix .center and .rightcol for proper CCTV squeezing
old_center = r"#command-center-root \.center \{ width: auto !important; flex: 0 0 auto !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; \}"
new_center = "#command-center-root .center { width: auto !important; flex: 0 1 auto !important; min-width: 0 !important; display: flex !important; flex-direction: column !important; height: 100% !important; min-height: 0 !important; padding-right: 0 !important; }"

old_stage = r"#command-center-root \.stage \{ resize: horizontal !important; overflow: hidden !important; width: 70vw !important; min-width: 400px !important; max-width: 90vw !important; \}"
new_stage = "#command-center-root .stage { resize: horizontal !important; overflow: hidden !important; width: 65vw !important; min-width: 300px !important; max-width: 100% !important; }"

old_rightcol = r"#command-center-root \.rightcol \{ flex: 1 1 0% !important; min-width: 250px; overflow-y: auto !important; height: 100% !important; min-height: 0 !important; padding: 8px !important; \}"
new_rightcol = "#command-center-root .rightcol { flex: 1 0 0% !important; min-width: 326px !important; overflow-y: auto !important; height: 100% !important; min-height: 0 !important; padding: 8px !important; }"

html = re.sub(old_center, new_center, html)
html = re.sub(old_stage, new_stage, html)
html = re.sub(old_rightcol, new_rightcol, html)

# 2. Fix .agent-cards-row for proper horizontal scrolling
old_agent_row = r"#command-center-root \.agent-cards-row\{display:flex !important;flex-direction:row !important;gap:10px !important;flex:1 !important;overflow-x:auto !important;padding:4px 2px !important;align-items:center !important;\}"
new_agent_row = "#command-center-root .agent-cards-row{display:flex !important;flex-direction:row !important;gap:10px !important;flex:1 1 0% !important;min-width:0 !important;overflow-x:auto !important;padding:4px 2px 8px 2px !important;align-items:center !important;}"

old_scrollbar = r"#command-center-root \.agent-cards-row::-webkit-scrollbar\{height:4px;\}"
new_scrollbar = "#command-center-root .agent-cards-row::-webkit-scrollbar{height:8px !important;}"

html = re.sub(old_agent_row, new_agent_row, html)
html = re.sub(old_scrollbar, new_scrollbar, html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Patched layout for CCTV squeezing and agent row scrolling.")
