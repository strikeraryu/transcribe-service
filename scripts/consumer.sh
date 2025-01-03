#!/bin/bash

poetry run celery -A service.celery worker --loglevel=INFO --pool threads 
