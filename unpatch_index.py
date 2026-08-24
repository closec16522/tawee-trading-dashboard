import codecs

# Read the patched content
with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Try finding it and removing it manually
idx = content.find('<!-- Data Backtest Tab -->')
if idx != -1:
    end_idx = content.find('</script>', idx)
    if end_idx != -1:
        end_idx = content.find('</div>', end_idx) + 6
        if end_idx > 6:
            content = content[:idx] + content[end_idx:]
            print('Removed tab_pane via manual search.')

# Try finding it and removing it manually
idx = content.find('<button class="menu-item" data-tab="backtest">')
if idx != -1:
    end_idx = content.find('</button>', idx) + 9
    content = content[:idx] + content[end_idx:]
    print('Removed menu_item via manual search.')

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)
print('Done unpatching.')
