run:
	export REDIS_HOST=localhost; \
	export ELASTIC_HOST=localhost; \
	uvicorn main:app --app-dir src --reload
up:
	docker compose -f dev-docker-compose.yml up -d
