import os

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure tv_chart has a min-height
old_div = '<div id="tv_chart" style="flex:1; width:100%; position:relative;"></div>'
new_div = '<div id="tv_chart" style="flex:1; width:100%; position:relative; min-height:400px;"></div>'
if old_div in content:
    content = content.replace(old_div, new_div)

# Add a ResizeObserver to ensure the chart resizes when the container size is resolved
old_resize = """          const handleResize = () => {
            if (tvContainer && tvWidget) {
              tvWidget.resize(tvContainer.clientWidth, tvContainer.clientHeight);
            }
          };
          window.addEventListener('resize', handleResize);"""
new_resize = """          const handleResize = () => {
            if (tvContainer && tvWidget && tvContainer.clientWidth > 0 && tvContainer.clientHeight > 0) {
              tvWidget.resize(tvContainer.clientWidth, tvContainer.clientHeight);
            }
          };
          window.addEventListener('resize', handleResize);
          const ro = new ResizeObserver(entries => {
            for (let entry of entries) {
              if (tvWidget && entry.contentRect.width > 0 && entry.contentRect.height > 0) {
                 tvWidget.resize(entry.contentRect.width, entry.contentRect.height);
              }
            }
          });
          ro.observe(tvContainer);"""

if old_resize in content:
    content = content.replace(old_resize, new_resize)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched index.html for chart visibility.")
