import paramiko

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    
    channel = transport.open_session()
    channel.exec_command("echo 'NUTza067668141' | sudo -S /usr/local/bin/docker ps")
    
    exit_status = channel.recv_exit_status()
    out = channel.recv(4096).decode('utf8', 'ignore')
    
    print("Out:", out)
    
    channel.close()
    transport.close()
except Exception as e:
    print(f"Error: {e}")
