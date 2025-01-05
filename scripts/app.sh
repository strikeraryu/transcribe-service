#!/bin/bash

source ./setup.sh
poetry run gunicorn --config gunicorn_config.py service:app;
