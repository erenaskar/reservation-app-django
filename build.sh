#!/usr/bin/env bash
# exit on error
set -o errexit

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export DJANGO_SETTINGS_MODULE=eventbooker.settings

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate 