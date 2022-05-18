#!/bin/sh
set -e

echo "Starting FastAPI server..."
uvicorn app.main:app --app-dir src
