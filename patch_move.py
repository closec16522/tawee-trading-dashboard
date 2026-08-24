import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Find the ai-meeting-room div
meeting_room_html = """                  <!-- AI Meeting Room Chat Log -->
                  <div class="ai-meeting-room" id="ai-meeting-room">
                    <div class="ai-meeting-header">?? AI Team Meeting Room - Live Protocol</div>
                    <div class="ai-meeting-log" id="ai-meeting-log">
                        <div class="ai-msg system-msg">[SYSTEM] Connecting to Multi-Agent Protocol...</div>
                        <div class="ai-msg system-msg">[SYSTEM] Connection Established. Listening to Agents.</div>
                    </div>
                  </div>"""

# Remove it from the current location (before </main>)
html = html.replace(meeting_room_html + "\n              </main>", "              </main>")

# Also try to remove it if it was injected with a slightly different whitespace
html = html.replace(meeting_room_html, "")

# Now inject it inside page-dashboard, right after the end of stage.
# We know the stage ends right before paperclipview's closing divs.
# Actually, the most robust way is to find `<!-- Secondary views (scraped pages templates rendered on nav clicks) -->`
# and insert it right before the `</div>` that precedes it. That `</div>` is the closing tag for `page-dashboard`.

# Let's search for the exact block:
target_block = """                </div>
                
                <!-- Secondary views (scraped pages templates rendered on nav clicks) -->"""

replacement_block = """                  <!-- AI Meeting Room Chat Log -->
                  <div class="ai-meeting-room" id="ai-meeting-room">
                    <div class="ai-meeting-header">?? AI Team Meeting Room - Live Protocol</div>
                    <div class="ai-meeting-log" id="ai-meeting-log">
                        <div class="ai-msg system-msg">[SYSTEM] Connecting to Multi-Agent Protocol...</div>
                        <div class="ai-msg system-msg">[SYSTEM] Connection Established. Listening to Agents.</div>
                    </div>
                  </div>
                </div>
                
                <!-- Secondary views (scraped pages templates rendered on nav clicks) -->"""

if target_block in html:
    html = html.replace(target_block, replacement_block)
    print("Moved AI Meeting Room inside page-dashboard.")
else:
    print("Could not find target_block.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
