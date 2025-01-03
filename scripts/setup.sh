#!/bin/bash

poetry install
poetry run flask --app service.py db upgrade
