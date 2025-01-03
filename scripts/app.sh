#!/bin/bash

poetry run gunicorn --config gunicorn_config.py service:app;
