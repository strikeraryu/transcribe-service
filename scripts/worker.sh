#!/bin/bash

export PATH="$PATH:$HOME/.local/bin"
poetry run celery -A service.celery worker --loglevel=INFO --pool threads 
