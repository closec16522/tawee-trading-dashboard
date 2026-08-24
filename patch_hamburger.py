import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update the CSS for collapsed sidebar
css_patch = """      aside#left-sidebar.collapsed {
        width: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        border: none !important;
      }
      aside#left-sidebar.collapsed ~ #floating-hamburger {
        display: flex !important;
      }"""
      
# Find where the old `.collapsed` CSS is.
old_collapsed_css = """      aside#left-sidebar.collapsed {
        width: 70px !important;
      }"""
      
html = html.replace(old_collapsed_css, css_patch)

# 2. Add floating hamburger button after </aside> (the first one)
old_aside_close = """        </aside>
        
        <!-- MAIN VIEWPORT (Renders dynamically) -->"""
        
new_aside_close = """        </aside>
        
        <!-- FLOATING HAMBURGER -->
        <button id="floating-hamburger" class="hamburger-btn" style="display:none; position:fixed; top:15px; left:15px; z-index:9999; background:rgba(15,23,42,0.6)!important; backdrop-filter:blur(4px); border:1px solid rgba(255,255,255,0.1);" onclick="window.toggleSidebar(event)">?</button>
        
        <!-- MAIN VIEWPORT (Renders dynamically) -->"""

html = html.replace(old_aside_close, new_aside_close)


# 3. Remove the right hamburger button in AI Office
old_burger = """              <div class="burger" onclick="alert('\uD83D\uDEE1\uFE0F Agent-Pixels Office - \u0E23\u0E30\u0E1A\u0E1A\u0E08\u0E30\u0E21\u0E35\u0E01\u0E32\u0E23\u0E2D\u0E31\u0E1B\u0E40\u0E14\u0E15\u0E40\u0E23\u0E47\u0E27\u0E46\u0E19\u0E35\u0E49')">\u2630</div>"""
# Sometimes unicode encoding might fail the replace string matching. I'll use regex.
html = re.sub(r'<div class="burger".*?>\s*\u2630\s*</div>', '', html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Hamburger patch applied.")
