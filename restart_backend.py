import paramiko

host = '192.168.0.11'
username = 'superuser'
password = 'NUTza067668141'

try:
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    
    # Try to restart the docker container for tawee_trading_intelligence or python process
    # Assuming it's docker container or docker-compose
    # Let's check what containers are running
    stdin, stdout, stderr = client.exec_command("docker ps | grep tawee")
    output = stdout.read().decode()
    if output:
        # get container id
        container_id = output.split()[0]
        print(f"Restarting container {container_id}...")
        stdin, stdout, stderr = client.exec_command(f"docker restart {container_id}")
        print(stdout.read().decode())
        print("Restarted.")
    else:
        print("No docker container found with 'tawee' in name. Trying to restart docker-compose if exists in /docker/tawee_trading_intelligence")
        stdin, stdout, stderr = client.exec_command("cd /docker/tawee_trading_intelligence && docker-compose restart")
        print(stdout.read().decode())
        print("Restarted via docker-compose.")

    client.close()
    transport.close()
except Exception as e:
    print(f"Error: {e}")
