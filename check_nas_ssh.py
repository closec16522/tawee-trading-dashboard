import paramiko

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password)
    
    stdin, stdout, stderr = client.exec_command('ls -l /volume1/docker/tawee_trading_intelligence/')
    print("content:", stdout.read().decode())
    
    client.close()
except Exception as e:
    print(f"Error: {e}")
