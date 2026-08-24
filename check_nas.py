import paramiko

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    print(sftp.listdir('/volume1/docker/'))
    print(sftp.listdir('/volume1/docker/afu_company/'))
    
    sftp.close()
    transport.close()
except Exception as e:
    print(f"Error: {e}")
