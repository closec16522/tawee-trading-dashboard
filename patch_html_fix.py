import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# First, remove the bad injection I made just in case
bad_injection = """
                  <!-- AI Meeting Room Chat Log -->
                  <div class="ai-meeting-room" id="ai-meeting-room">
                    <div class="ai-meeting-header">?? AI Team Meeting Room - Live Protocol</div>
                    <div class="ai-meeting-log" id="ai-meeting-log">
                        <div class="ai-msg system-msg">[SYSTEM] Connecting to Multi-Agent Protocol...</div>
                        <div class="ai-msg system-msg">[SYSTEM] Connection Established. Listening to Agents.</div>
                    </div>
                  </div>
              </main> <!-- Fix closing if needed, but actually let's just inject before aside -->
              <aside class="right-panel">
"""
html = html.replace(bad_injection, '<aside class="right-panel">')

# Now inject correctly just before `</main>` on line 2868
old_main_close = "              </main>"
new_main_close = """
                  <!-- AI Meeting Room Chat Log -->
                  <div class="ai-meeting-room" id="ai-meeting-room">
                    <div class="ai-meeting-header">?? AI Team Meeting Room - Live Protocol</div>
                    <div class="ai-meeting-log" id="ai-meeting-log">
                        <div class="ai-msg system-msg">[SYSTEM] Connecting to Multi-Agent Protocol...</div>
                        <div class="ai-msg system-msg">[SYSTEM] Connection Established. Listening to Agents.</div>
                    </div>
                  </div>
              </main>"""
              
if "ai-meeting-room" not in html[html.find('</main>') - 500 : html.find('</main>') + 500]:
    html = html.replace(old_main_close, new_main_close, 1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Correctly injected AI Meeting Room HTML before </main>.")
