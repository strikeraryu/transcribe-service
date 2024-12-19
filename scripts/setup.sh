#!/bin/bash

poetry install
poetry shell
flask --app service.py db upgrade

