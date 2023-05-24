#!/bin/bash

# Load environment variables from .env file
set -a
source .env
export DB_HOST=192.168.0.2
export FLASK_APP='app.py'
set +a

# Run database migrations
flask db init
flask db migrate
# flask db upgrade

# Run the command
# flask run --host=0.0.0.0 --debug
