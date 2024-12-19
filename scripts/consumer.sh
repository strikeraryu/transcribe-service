#!/bin/bash

celery -A service.celery worker --loglevel=INFO --pool threads 
