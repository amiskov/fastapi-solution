#!/bin/sh
set -e

echo "Starting FastAPI server..."
uvicorn main:app --port 8000 --host 0.0.0.0 --app-dir .
