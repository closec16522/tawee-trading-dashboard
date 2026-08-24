import re

path = 'mt5_backend/agent_orchestrator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find the block starting with `delta = df['close'].diff()`
# inside run_supervisor and delete everything until `elif confidence >= 80:`

pattern = r"(        # Calculate grade\n        if confidence >= 90:\n            grade = \"A\"\n)            delta = df\['close'\]\.diff\(\).*?(        # Calculate grade\n        if confidence >= 90:\n            grade = \"A\"\n        elif confidence >= 80:\n)"

if re.search(pattern, content, re.DOTALL):
    print("Found the corrupted block!")
    new_content = re.sub(pattern, r"\2", content, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed corrupted block in agent_orchestrator.py")
else:
    print("Did not find the corrupted block.")
