import paramiko
import os

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

local_path = r'C:\Users\Administrator\.gemini\antigravity\scratch\afu_company\index.html'
remote_path = '/docker/tawee_trading_intelligence/index.html'

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    print(f'Uploading to {remote_path}...')
    sftp.put(local_path, remote_path)
    print('Upload done.')
    
    # Verify size
    channel = transport.open_session()
    channel.exec_command(f'ls -l {remote_path}')
    print('Verification:', channel.recv(1024).decode())
    channel.close()
    
    sftp.close()
    transport.close()
except Exception as e:
    print('Error:', e)
