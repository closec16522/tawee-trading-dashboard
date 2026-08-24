import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace const speechBubbles = { with window.speechBubbles = {
content = re.sub(r'const speechBubbles = \{', 'window.speechBubbles = {', content)

# Replace speechBubbles[ with window.speechBubbles[
content = re.sub(r'(?<!window\.)speechBubbles\[', 'window.speechBubbles[', content)

# Replace typeof speechBubbles with typeof window.speechBubbles
content = re.sub(r"typeof speechBubbles", "typeof window.speechBubbles", content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched speechBubbles logic.')
