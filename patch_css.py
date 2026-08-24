import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

old_css = """      aside#left-sidebar.collapsed ~ #floating-hamburger {
        display: flex !important;
      }"""

new_css = """      aside#left-sidebar.collapsed ~ #floating-hamburger {
        display: flex !important;
      }
      @media (max-width: 900px) {
        aside#left-sidebar:not(.mobile-open) ~ #floating-hamburger {
          display: flex !important;
        }
      }"""

if old_css in html and new_css not in html:
    html = html.replace(old_css, new_css)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated CSS for floating hamburger on mobile.")
else:
    print("CSS already updated or old_css not found.")
