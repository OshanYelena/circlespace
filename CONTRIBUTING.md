# Contributing

## Workflow

1. Create a branch from `main` using `feat/`, `fix/`, or `chore/`.
2. Keep commits focused and use Conventional Commit messages.
3. Add or update tests for behavior changes.
4. Run `make check` before opening a pull request.
5. Complete the pull request checklist and request at least one review.

The required checks and reviewer expectations are documented in [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md).

## Architecture rules

- Backend modules may use shared infrastructure from `app.core` and `app.db`.
- A module must call another module through its public service/API contract, never through private internals.
- Route handlers validate transport data and delegate business logic to services.
- Services own business rules; repositories own persistence queries.
- Frontend server/client components access the API through `src/lib/api`, not ad-hoc `fetch` calls.
- New UI primitives belong in `src/components`; route-specific composition belongs in `src/app`.

## Review checklist

- Module boundaries and dependency direction are preserved.
- Authorization is enforced server-side for every mutation.
- API schemas do not leak database entities.
- Database changes include a migration.
- Loading, empty, and error states are handled in the UI.
- Tests cover the happy path and meaningful failure paths.
- No secrets, credentials, or personal data are committed.
