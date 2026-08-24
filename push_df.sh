cat << 'EOF' | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/Dockerfile > /dev/null
# Use lightweight Nginx alpine image
FROM nginx:alpine

# Copy web app static files into Nginx serve directory
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

EOF
echo DF_OK