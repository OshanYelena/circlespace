# Operations runbook

## Local container stack

Start PostgreSQL, the API, and the web app:

```bash
docker compose up --build
```

Migrations run automatically before the API starts. Seed optional demo data after the API is healthy:

```bash
docker compose exec api python -m app.seed
```

Sign in as `ada` or `grace` with password `demo-password`. Stop the stack with `docker compose down`. Add `--volumes` only when you intentionally want to delete the local database.

## Health and diagnostics

- API health: `GET http://localhost:8000/health`
- API documentation: `http://localhost:8000/docs`
- Web application: `http://localhost:3000`
- Service status: `docker compose ps`
- Service logs: `docker compose logs api` or `docker compose logs web`

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

