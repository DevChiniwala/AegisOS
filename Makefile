.PHONY: install install-all dev test test-unit test-integration lint format docker-up docker-down generate-data migrate clean

install:
	pip install -e .

install-all:
	pip install -e ".[all]"

dev:
	uvicorn apps.api.main:app --reload

test: test-unit test-integration

test-unit:
	pytest tests/unit

test-integration:
	pytest tests/integration

lint:
	ruff check .
	mypy .

format:
	ruff format .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

generate-data:
	python scripts/generate_data.py

migrate:
	alembic upgrade head

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
