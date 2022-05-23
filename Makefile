run:
	uvicorn main:app --app-dir src
up:
	docker compose up --build
down:
	docker compose down -v