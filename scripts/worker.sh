#!/bin/bash

export PATH="/home/ec2-user/.local/bin:$PATH"

poetry run celery -A service.celery worker --loglevel=INFO --pool threads 
