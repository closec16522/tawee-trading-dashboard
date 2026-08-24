import paramiko
import os

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'
base_remote_dir = '/docker/tawee_trading_intelligence'
local_path = 'index_from_nas.html'
remote_path = f"{base_remote_dir}/index.html"

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(remote_path, local_path)
    sftp.close()
    transport.close()
    print("Download successful")
except Exception as e:
    print(f"Error: {e}")
