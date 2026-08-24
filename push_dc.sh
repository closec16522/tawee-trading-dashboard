cat << 'EOF' | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/docker-compose.yml > /dev/null
version: '3.8'

services:
  tawee-trading-app:
    build: .
    container_name: tawee_trading_intelligence
    restart: always
    ports:
      - "3002:80"
    volumes:
      - .:/usr/share/nginx/html
    environment:
      - NODE_ENV=production

EOF
echo DC_OK