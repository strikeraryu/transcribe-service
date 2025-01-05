#!/bin/bash

# Exit on error
set -e

# Log start of script
echo "Starting predeploy setup script"

# Navigate to application directory
cd /var/app/staging

# Create tmp directory and set permissions
sudo mkdir -p ./tmp
sudo chmod 777 ./tmp

# Log completion
echo "Predeploy setup script completed"
