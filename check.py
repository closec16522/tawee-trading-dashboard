import re
with open('index_from_nas.html', 'r', encoding='utf-8') as f:
    content = f.read()
match = re.search(r'async function initAnalyticsLogic\(\) \{.*?\}\s*catch \(e\) \{.*?\}\s*\}', content, re.DOTALL)
if match:
    print("FOUND:")
    print(match.group(0)[:100])
else:
    print("NOT FOUND")
