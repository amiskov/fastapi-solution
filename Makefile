run:
	export REDIS_HOST=localhost; \
	export ELASTIC_HOST=localhost; \
	uvicorn main:app --app-dir src --reload
up:
	docker compose -f dev-docker-compose.yml up -d
down:
	docker compose down -v
test:
	export SERVICE_URL='http://127.0.0.1:8000';\
	export PERSONS_ES_INDEX='persons_test';\
	export GENRES_ES_INDEX='genres_test';\
	export MOVIES_INDEX='movies_test';\
	export REDIS_HOST='127.0.0.1';\
	export REDIS_PORT='6379';\
	export REDIS_URL='http://127.0.0.1:6379';\
	export ELASTIC_HOST='http://127.0.0.1:9200';\
	pytest tests/functional/src -s
pinges:
	export PYTHONPATH='.';\
	python tests/functional/utils/wait_for_es.py
pingredis:
	export PYTHONPATH='.';\
	python tests/functional/utils/wait_for_redis.py
