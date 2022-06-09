#!/bin/sh
set -e
export PYTHONPATH='.';\

echo "Wait for ElasticSearch started..."
python waiters/wait_for_es.py

echo "Wait for Redis started..."
python waiters/wait_for_redis.py

echo "Run tests..."
pytest
