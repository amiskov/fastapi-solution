#!/bin/sh
set -e

echo "Run functional tests in docker..."
docker-compose -f docker-compose-tests.yml build
docker-compose -f docker-compose-tests.yml up --abort-on-container-exit
