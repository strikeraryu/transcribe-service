#!/bin/bash

# Create a temporary directory and give it access to all users
sudo mkdir -p ./tmp
sudo chmod 777 ./tmp

# Run the Flask application with database upgrade
flask --app service.py db upgrade
