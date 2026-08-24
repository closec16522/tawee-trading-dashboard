import re
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the block that was mistakenly added around eqGrowthEl (line 8161)
pattern = r'const meetingLog = document\.getElementById\(\'ai-meeting-log\'\);\s+if \(meetingLog\) \{\s+function translateCasual\(agentId, text\).*?meetingLog\.scrollTop = meetingLog\.scrollHeight;\s+\}'
content = re.sub(pattern, '', content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
