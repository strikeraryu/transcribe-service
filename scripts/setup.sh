#!/bin/bash

# Create a temporary directory and give it access to all users
sudo mkdir -p ./tmp
sudo chmod 777 ./tmp

# Install dependencies using poetry
poetry install

# Run the Flask application with database upgrade
poetry run flask --app service.py db upgrade
