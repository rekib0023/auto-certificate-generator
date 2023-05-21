#!/bin/bash

# Load environment variables from .env file
set -a
source .env
set +a

# Run the command
gunicorn app:app --bind 0.0.0.0:5000
