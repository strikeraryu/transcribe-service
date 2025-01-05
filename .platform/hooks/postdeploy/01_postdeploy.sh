#!/bin/bash


echo "Starting Hooks postbuild script..."

cp -rf /var/app/current/nginx/nginx.conf /etc/nginx/
if [ $? -eq 0 ]; then
    echo "File copied successfully."
else
    echo "Failed to copy file."
fi

sudo systemctl restart nginx
echo "postbuild script finished."

exit 0
