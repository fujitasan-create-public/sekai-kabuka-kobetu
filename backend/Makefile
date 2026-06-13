.PHONY: install fmt lint gen dev migrate-create migrate-up

install:
	uv sync --dev

fmt:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .
	uv run mypy app scripts

gen:
	uv run python scripts/export_openapi.py

dev:
	uv run uvicorn app.main:app --reload --host localhost --port 8000

migrate-create:
	uv run alembic revision --autogenerate -m "$(name)"

migrate-up:
	uv run alembic upgrade head
