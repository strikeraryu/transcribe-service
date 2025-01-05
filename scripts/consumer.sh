#!/bin/bash

source ./setup.sh
poetry run celery -A service.celery worker --loglevel=INFO --pool threads 
