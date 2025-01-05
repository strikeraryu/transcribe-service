#!/bin/bash

source ./scripts/setup.sh
gunicorn --config gunicorn_config.py service:app
