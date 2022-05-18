#!/bin/sh
set -e

echo "Starting FastAPI server..."
uvicorn main:app --app-dir .
