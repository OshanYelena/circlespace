# Operations runbook

## Local container stack

Start PostgreSQL, the API, the web app, and Nginx:

```bash
docker compose up --build
```

The application is available through Nginx at `http://localhost:8080`. Copy
`.env.compose.example` to `.env` before startup to override credentials, the
published port, pool settings, or browser-facing API URL.

Migrations run automatically before the API starts. Seed optional demo data after the API is healthy:

```bash
docker compose exec api python -m app.seed
```

Sign in as `ada` or `grace` with password `demo-password`. Stop the stack with `docker compose down`. Add `--volumes` only when you intentionally want to delete the local database.

## Health and diagnostics

- Nginx health: `GET http://localhost:8080/nginx-health`
- API health: `GET http://localhost:8080/health`
- API documentation: `http://localhost:8080/docs`
- Web application: `http://localhost:8080`
- Service status: `docker compose ps`
- Service logs: `docker compose logs api`, `docker compose logs web`, or
  `docker compose logs nginx`

Only Nginx is published to the host. PostgreSQL, FastAPI, and Next.js remain on
the private Compose network. Stop the stack without deleting data using
`docker compose down`. To deliberately remove the PostgreSQL volume too, use
`docker compose down --volumes`.

## Database migrations

Create a migration after changing SQLAlchemy models:

```bash
cd apps/api
../../.venv/bin/alembic revision --autogenerate -m "describe change"
../../.venv/bin/alembic upgrade head
```

Review generated migrations for destructive changes and always implement `downgrade()`.

## Production checklist

- Use a managed PostgreSQL instance with encrypted backups.
- Set a randomly generated `SECRET_KEY` of at least 32 bytes in the secret manager.
- Restrict `BACKEND_CORS_ORIGINS` to the deployed web origin.
- Terminate TLS at the load balancer or ingress and redirect HTTP to HTTPS.
- Run `alembic upgrade head` as a release job before rolling out the API.
- Run containers as non-root and send structured logs to centralized storage.
- Monitor API error rate, latency, database connections, and health-check failures.
- Configure the GitHub `main` ruleset described in `docs/CODE_REVIEW.md`.

## Rollback

Roll back application containers to the previous immutable image. Roll back a migration only after confirming the previous application version is compatible and the migration downgrade is non-destructive. Restore the database from backup for destructive data changes.
