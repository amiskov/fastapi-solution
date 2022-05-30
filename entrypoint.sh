#!/bin/sh
set -e

echo "Starting FastAPI server with workers count $GUNICORN_WORKERS..."
gunicorn --workers="$GUNICORN_WORKERS" --bind="0.0.0.0:8000" --worker-class=uvicorn.workers.UvicornWorker main:app
