#!/bin/bash

gunicorn --config gunicorn_config.py service:app
