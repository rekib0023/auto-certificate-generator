#!/bin/bash

# Run database migrations
flask db init
flask db migrate
flask db upgrade

# Start the Flask application
gunicorn --bind 0.0.0.0:5000 app:app