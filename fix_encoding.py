import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the first accidental insertion at ~line 8164
content = re.sub(r'\s*function translateCasual.*?return r;\s*}\s*', '\n', content, count=1, flags=re.DOTALL)

# 2. Fix the corrupted function and the innerHTML
# First, remove the corrupted function
content = re.sub(r'\s*function translateCasual\(agentId, text\).*?return r;\s*}', '', content, flags=re.DOTALL)

# Remove the call to translateCasual
content = content.replace('let meetingTxt = translateCasual(data.agent_id, txt);', '')

# Replace meetingTxt with txt
content = content.replace('', '')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Cleaned up corrupted code.")
