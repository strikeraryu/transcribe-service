#!/bin/bash

flask --app service.py db upgrade
gunicorn --config gunicorn_config.py service:app
