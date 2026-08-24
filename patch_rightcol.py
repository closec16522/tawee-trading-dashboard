import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Change .body layout from Grid to Flex to support CSS resize on .center
old_body_css = "#command-center-root .body{display:grid;grid-template-columns:1fr 326px;min-height:0;height:100%;}"
new_body_css = """#command-center-root .body{display:flex;flex-direction:row;min-height:0;height:100%;}
#command-center-root .center { resize: horizontal; overflow: hidden; width: 75%; min-width: 400px; max-width: 95%; flex-shrink: 0; display: flex; flex-direction: column; }
#command-center-root .rightcol { flex: 1; min-width: 250px; overflow-y: auto; }
"""
html = html.replace(old_body_css, new_body_css)


# 2. Extract AI Meeting Room HTML
# We know it starts with `<!-- AI Meeting Room Chat Log -->`
ai_room_regex = r'(\s*<!-- AI Meeting Room Chat Log -->\s*<div class="ai-meeting-room" id="ai-meeting-room">.*?</div>\s*</div>)'
# Actually, the user wants it as a Panel. Let's rewrite the HTML for the panel completely and just search for id="ai-meeting-room" block to delete it.

ai_room_search = re.search(r'\s*<!-- AI Meeting Room Chat Log -->.*?id="ai-meeting-log".*?</div>\s*</div>', html, re.DOTALL)
if ai_room_search:
    html = html.replace(ai_room_search.group(0), "")
else:
    print("Warning: Could not extract AI meeting room!")

# 3. Inject AI Meeting Panel into rightcol
# The rightcol starts at: `<aside class="rightcol scroll">`
rightcol_marker = '<aside class="rightcol scroll">'
new_panel_html = """<aside class="rightcol scroll">
                <div class="panel" style="border-color:#38bdf8; box-shadow: 0 0 10px rgba(56,189,248,0.2);">
                  <div class="rh"><h3 style="color:#38bdf8; display:flex; align-items:center; gap:6px;">?? AI Team Meeting Room</h3><span class="tag" style="background:rgba(56,189,248,0.2); color:#38bdf8;">LIVE</span></div>
                  <div class="ai-meeting-log" id="ai-meeting-log" style="height:250px; overflow-y:auto; font-family:monospace; font-size:11px; padding:4px; display:flex; flex-direction:column; gap:4px; background:rgba(0,0,0,0.2); border-radius:6px; border:1px solid #1e293b;">
                    <div class="ai-msg system-msg" style="color:#64748b; margin-bottom:4px;">[SYSTEM] Connecting to Multi-Agent Protocol...</div>
                    <div class="ai-msg system-msg" style="color:#64748b; margin-bottom:4px;">[SYSTEM] Connection Established. Listening to Agents.</div>
                  </div>
                </div>"""
html = html.replace(rightcol_marker, new_panel_html)

# 4. Remove the old .ai-meeting-room absolute positioning CSS so it doesn't break the new panel layout if the class is reused.
# Actually, I renamed the id and removed the wrapper class `ai-meeting-room`. The new panel just uses native `.panel` class and `#ai-meeting-log`. So the old CSS won't hurt, but I can leave it.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Applied AI Meeting Panel to rightcol and enabled resizing.")
