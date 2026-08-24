FROM nginx:alpine

# Copy the entire afu_company project into the Nginx html folder
# This includes the main dashboard (index.html) and the RoseAI subfolder (roseai/)
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
