echo NUTza067668141 | sudo -S cp /tmp/index.html /volume1/docker/tawee_trading_intelligence/index.html
echo NUTza067668141 | sudo -S chown 1000:1000 /volume1/docker/tawee_trading_intelligence/index.html
echo NUTza067668141 | sudo -S cp /tmp/mt5_gateway.py /tmp/agent_orchestrator.py /volume1/docker/tawee_trading_intelligence/mt5_backend/
echo NUTza067668141 | sudo -S chown 1000:1000 /volume1/docker/tawee_trading_intelligence/mt5_backend/mt5_gateway.py /volume1/docker/tawee_trading_intelligence/mt5_backend/agent_orchestrator.py
cd /volume1/docker/tawee_trading_intelligence && echo NUTza067668141 | sudo -S /usr/local/bin/docker-compose down
cd /volume1/docker/tawee_trading_intelligence && echo NUTza067668141 | sudo -S /usr/local/bin/docker-compose up -d
