import os

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace window.location.hostname with 192.168.0.41 in the history fetch
old_fetch = "await fetch(`http://${window.location.hostname}:19000/api/history"
new_fetch = "await fetch(`http://192.168.0.41:19000/api/history"

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched API URL to 192.168.0.41 successfully.")
else:
    print("Could not find the fetch call.")
