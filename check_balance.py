import codecs
with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

backticks = content.count('`')
print('Backticks:', backticks)
if backticks % 2 != 0:
    print('WARNING: Odd number of backticks in file!')
else:
    print('Backticks are balanced.')
print('<script>:', content.count('<script>'))
print('</script>:', content.count('</script>'))
