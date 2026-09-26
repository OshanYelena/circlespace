.PHONY: api-install api-dev api-test api-lint api-migrate api-seed web-install web-dev web-test web-lint architecture check up

api-install:
	python3 -m venv .venv
	.venv/bin/pip install -e 'apps/api[dev]'

api-dev:
	.venv/bin/uvicorn app.main:app --reload --app-dir apps/api

api-test:
	.venv/bin/pytest apps/api/tests

api-lint:
	.venv/bin/ruff check apps/api
	.venv/bin/ruff format --check apps/api

api-migrate:
	cd apps/api && ../../.venv/bin/alembic upgrade head

api-seed:
	cd apps/api && ../../.venv/bin/python -m app.seed

web-install:
	npm --prefix apps/web install

web-dev:
	npm --prefix apps/web run dev

web-test:
	npm --prefix apps/web run test

web-lint:
	npm --prefix apps/web run lint
	npm --prefix apps/web run typecheck

architecture:
	python3 scripts/check_architecture.py

check: architecture api-lint api-test web-lint web-test

up:
	docker compose up --build
