#!/bin/sh

echo "Waiting for database..."


# Run DB migrations
echo "Running migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI in Production..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
