import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# I will find the exact string that ends the stage div.
# Let's search for "paperclipview" and its closing tags.
# It ends with: </div> <!-- End of Paperclip View -->
# And then the stage div is closed: </div>
# Then the page div is closed: </div>

# A reliable way is to insert before `<aside class="right-panel">` which is the RIGHT SIDEBAR.
# Or right after `<div class="page active" id="page-dashboard">` ends. But it doesn't end there, the stage ends, then the right sidebar starts. Wait, the `aside` is a sibling of `main`?
# Let's check `</main>` or `<aside class="right-panel">`.

old_str = '                <!-- DASHBOARD PAGE (Default Active) -->'
# I will use a simple regex replacement to put it just after the stage div ends.
# I'll find `<div class="stage" id="stage">` and count divs.
# To be safe, let's just insert it right before `<aside class="right-panel">` inside `<div class="body">` if it exists.
# Wait, `<aside>` is inside `<div class="body">`! Yes!

html = html.replace('<aside class="right-panel">', """
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
""")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Injected AI Meeting Room HTML.")
