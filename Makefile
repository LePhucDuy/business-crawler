.PHONY: install dev test lint format migrate run

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check .

format:
	black .

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(name)"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
