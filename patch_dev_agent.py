import re

path = 'developer_agent.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        app.run_polling()'''

replacement = '''        while True:
            try:
                app.run_polling(read_timeout=30, connect_timeout=30, pool_timeout=30)
            except Exception as e:
                import time
                print(f"Network error in polling: {e}. Retrying in 10 seconds...")
                time.sleep(10)'''

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched developer_agent.py")
else:
    print("Target not found.")
