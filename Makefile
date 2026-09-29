.PHONY: api-install api-dev api-test api-lint api-migrate api-seed web-install web-dev web-test web-lint architecture check up down compose-config compose-logs compose-ps lab-migrate lab-seed lab-reset-seed lab-api lab-run nginx-prepare nginx-test nginx-start nginx-stop nginx-reload nginx-status nginx-api nginx-web

LAB_DATABASE_URL ?= postgresql+psycopg://localhost/circlespace_lab
LAB_RESULT_DIR ?= docs/scaling/results/manual-run
LAB_PROFILE ?= mixed
LAB_USERS ?= 10
LAB_SPAWN_RATE ?= 2
LAB_RUN_TIME ?= 30s
NGINX_BIN ?= /opt/homebrew/opt/nginx/bin/nginx
NGINX_PREFIX ?= $(CURDIR)
NGINX_RUNTIME ?= $(CURDIR)/.nginx-runtime
NGINX_CONFIG ?= ops/nginx/nginx.conf

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

lab-migrate:
	cd apps/api && DATABASE_URL='$(LAB_DATABASE_URL)' ../../.venv/bin/alembic upgrade head

lab-seed:
	cd apps/api && DATABASE_URL='$(LAB_DATABASE_URL)' ../../.venv/bin/python -m app.lab_seed --manifest ../../docs/scaling/results/dataset-manifest.json

lab-reset-seed:
	cd apps/api && DATABASE_URL='$(LAB_DATABASE_URL)' ../../.venv/bin/python -m app.lab_seed --reset --manifest ../../docs/scaling/results/dataset-manifest.json

lab-api:
	cd apps/api && DATABASE_URL='$(LAB_DATABASE_URL)' ../../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

lab-run:
	.venv/bin/python scripts/run_lab_experiment.py --profile '$(LAB_PROFILE)' --users '$(LAB_USERS)' --spawn-rate '$(LAB_SPAWN_RATE)' --run-time '$(LAB_RUN_TIME)' --database-url '$(LAB_DATABASE_URL)' --output '$(LAB_RESULT_DIR)'

nginx-prepare:
	mkdir -p '$(NGINX_RUNTIME)/logs' '$(NGINX_RUNTIME)/client_body_temp' '$(NGINX_RUNTIME)/proxy_temp' '$(NGINX_RUNTIME)/fastcgi_temp' '$(NGINX_RUNTIME)/uwsgi_temp' '$(NGINX_RUNTIME)/scgi_temp'

nginx-test: nginx-prepare
	'$(NGINX_BIN)' -t -p '$(NGINX_PREFIX)/' -c '$(NGINX_CONFIG)'

nginx-start: nginx-test
	'$(NGINX_BIN)' -p '$(NGINX_PREFIX)/' -c '$(NGINX_CONFIG)'

nginx-stop:
	'$(NGINX_BIN)' -p '$(NGINX_PREFIX)/' -c '$(NGINX_CONFIG)' -s quit

nginx-reload: nginx-test
	'$(NGINX_BIN)' -p '$(NGINX_PREFIX)/' -c '$(NGINX_CONFIG)' -s reload

nginx-status:
	curl --fail --silent --show-error http://127.0.0.1:8080/nginx-health

nginx-api:
	$(MAKE) lab-api

nginx-web:
	NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1 npm --prefix apps/web run dev

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

down:
	docker compose down

compose-config:
	docker compose config --quiet

compose-logs:
	docker compose logs --follow

compose-ps:
	docker compose ps
