#!/bin/sh

# Ensure local folders exist so volumes don't cause permission issues
mkdir -p audio reports

# Run DB migrations
echo "Running migrations..."
alembic upgrade head

# Start the application in development mode with auto-reload
echo "Starting FastAPI in Dev mode..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
