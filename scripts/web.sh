#!/bin/bash

export PATH="/home/ec2-user/.local/bin:$PATH"

poetry run gunicorn --config gunicorn_config.py service:app;
