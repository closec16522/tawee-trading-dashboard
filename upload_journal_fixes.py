import urllib.request
import json
import os

nas_url = "http://192.168.0.11:19000/update_file"

files_to_upload = [
    ("mt5_backend/agent_orchestrator.py", "/docker/tawee_trading_intelligence/mt5_backend/agent_orchestrator.py"),
    ("mt5_backend/journal.json", "/docker/tawee_trading_intelligence/mt5_backend/journal.json")
]

for local_path, remote_path in files_to_upload:
    print(f"Uploading {local_path} -> {remote_path}")
    
    if not os.path.exists(local_path):
        print(f"File {local_path} not found locally! Skipping.")
        continue
        
    with open(local_path, "rb") as f:
        file_content = f.read()
        
    import base64
    b64_content = base64.b64encode(file_content).decode('utf-8')
    
    payload = {
        "filepath": remote_path,
        "content_base64": b64_content
    }
    
    req = urllib.request.Request(nas_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print("Done.")
            else:
                print(f"Failed with status: {response.status}")
    except Exception as e:
        print(f"Error: {e}")

print("Upload complete.")
