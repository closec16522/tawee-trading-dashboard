import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Nuke everything between <!-- Data Backtest Tab --> and its ending </div> (including any nested </script>)
while True:
    idx = content.find('<!-- Data Backtest Tab -->')
    if idx == -1:
        break
    # To be safe and delete the whole block, let's find the specific unique string at the end of the block
    end_str = '</div>'
    
    # We know the block originally had </div> at the end, let's just find the next <!-- END OF TABS> or </main> and delete up to it?
    # No, that might delete too much.
    # Let's find </script> and the </div> after it
    s_idx = content.find('</script>', idx)
    if s_idx != -1:
        end_idx = content.find('</div>', s_idx) + 6
        content = content[:idx] + content[end_idx:]
        print('Deleted one occurrence with script.')
    else:
        # If there is no </script>, it's the safe patch version!
        # The safe patch version ends after 'Refresh Results</button>\n          </div>\n        </div>'
        end_idx = content.find('Refresh Results</button>', idx)
        if end_idx != -1:
            end_idx = content.find('</div>', end_idx)
            end_idx = content.find('</div>', end_idx + 6) + 6
            content = content[:idx] + content[end_idx:]
            print('Deleted one safe occurrence.')
        else:
            break

# Nuke the menu item
while True:
    idx = content.find('<button class="menu-item" data-tab="backtest">')
    if idx == -1:
        break
    end_idx = content.find('</button>', idx) + 9
    content = content[:idx] + content[end_idx:]
    print('Deleted one menu item.')

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)
print('Cleanup done.')
