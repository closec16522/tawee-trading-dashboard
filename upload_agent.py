import paramiko
import os

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

base_local_dir = r'C:\Users\Administrator\.gemini\antigravity\scratch\afu_company'
base_remote_dir = '/docker/tawee_trading_intelligence'

files_to_upload = [
    ('mt5_backend/agent_orchestrator.py', 'mt5_backend/agent_orchestrator.py')
]

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    for local_rel, remote_rel in files_to_upload:
        local_path = base_local_dir + r'\\' + local_rel.replace('/', r'\\')
        remote_path = f"{base_remote_dir}/{remote_rel}"
        print(f"Uploading {local_path} -> {remote_path}")
        sftp.put(local_path, remote_path)
        print("Done.")
        
    sftp.close()
    transport.close()
    print("All files uploaded successfully.")
except Exception as e:
    print(f"Error: {e}")
