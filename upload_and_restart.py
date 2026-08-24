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
        if not os.path.exists(local_path):
            print(f"LOCAL FILE DOES NOT EXIST: {local_path}")
            continue
        sftp.put(local_path, remote_path)
        print("Done.")
        
    sftp.close()
    
    # Restart the container
    print("Restarting mt5_gateway_api container...")
    channel = transport.open_session()
    # Need to pass password via stdin for sudo
    channel.exec_command("echo 'NUTza067668141' | sudo -S /usr/local/bin/docker restart mt5_gateway_api")
    
    # Wait for completion
    exit_status = channel.recv_exit_status()
    print(f"Restart finished with exit code {exit_status}")
    
    out = channel.recv(1024).decode('utf8', 'ignore')
    err = channel.recv_stderr(1024).decode('utf8', 'ignore')
    print("Out:", out)
    print("Err:", err)
    
    channel.close()
    transport.close()
    print("All files uploaded and container restarted successfully.")
except Exception as e:
    print(f"Error: {e}")
