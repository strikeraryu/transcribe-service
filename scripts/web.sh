#!/bin/bash

export PATH="$PATH:$HOME/.local/bin"
poetry run gunicorn --config gunicorn_config.py service:app
