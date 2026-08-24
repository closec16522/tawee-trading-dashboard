import paramiko
import os

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    channel = transport.open_session()
    
    # Run a simple bash script on the remote
    script = '''
    echo NUTza067668141 | sudo -S /usr/local/bin/docker restart $(echo NUTza067668141 | sudo -S /usr/local/bin/docker ps -q -f name=frontend)
    '''
    channel.exec_command(script)
    out = channel.recv(1024).decode()
    err = channel.recv_stderr(1024).decode()
    print('Restart Output:', out)
    print('Error:', err)
    channel.close()
    transport.close()
except Exception as e:
    print('Error:', e)
