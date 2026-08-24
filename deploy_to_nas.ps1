Write-Host "Copying index.html via pscp..."
.\pscp.exe -scp -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -pw NUTza067668141 index.html superuser@192.168.0.11:/tmp/index.html

Write-Host "Copying mt5_gateway.py via pscp..."
.\pscp.exe -scp -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -pw NUTza067668141 mt5_backend/mt5_gateway.py superuser@192.168.0.11:/tmp/mt5_gateway.py

Write-Host "Copying agent_orchestrator.py via pscp..."
.\pscp.exe -scp -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -pw NUTza067668141 mt5_backend/agent_orchestrator.py superuser@192.168.0.11:/tmp/agent_orchestrator.py

Write-Host "Moving files on NAS..."
$sh = "echo NUTza067668141 | sudo -S cp /tmp/index.html /volume1/docker/tawee_trading_intelligence/index.html`n" +
      "echo NUTza067668141 | sudo -S chown 1000:1000 /volume1/docker/tawee_trading_intelligence/index.html`n" +
      "echo NUTza067668141 | sudo -S cp /tmp/mt5_gateway.py /tmp/agent_orchestrator.py /volume1/docker/tawee_trading_intelligence/mt5_backend/`n" +
      "echo NUTza067668141 | sudo -S chown 1000:1000 /volume1/docker/tawee_trading_intelligence/mt5_backend/mt5_gateway.py /volume1/docker/tawee_trading_intelligence/mt5_backend/agent_orchestrator.py`n" +
      "echo NUTza067668141 | sudo -S docker restart mt5_gateway_api`n"
[System.IO.File]::WriteAllText("cmd_move.sh", $sh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_move.sh superuser@192.168.0.11

Write-Host "Deployment Complete!"