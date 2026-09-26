# CircleSpace

CircleSpace is a full-stack social media application implemented as a modular monolith. The Next.js frontend and FastAPI backend are independently deployable, while backend business capabilities remain isolated behind explicit module boundaries.

## Capabilities

- Register and sign in with JWT authentication
- Create and edit a user profile
- Publish, edit, and delete posts
- Like, comment on, and share posts
- Send, accept, reject, and remove friend relationships
- Browse a personalized feed and public profiles

## Repository layout

```text
apps/
  api/                 FastAPI modular monolith
  web/                 Next.js App Router application
docs/                  Architecture and delivery documentation
.github/               Pull request templates and CI/review policy
```

## Development

Copy `.env.example` to `.env`, then run the services in separate terminals:

```bash
make api-install
make api-dev
```

```bash
make web-install
make web-dev
```

The API is available at `http://localhost:8000` (OpenAPI at `/docs`) and the web app at `http://localhost:3000`.

Run all local quality checks with:

```bash
make check
```

## Delivery workflow

Work is tracked in [docs/TASKS.md](docs/TASKS.md). Each completed task is represented by a focused Git commit. Pull requests must pass the checks defined in `.github/workflows/ci.yml` and follow the review guidance in `CONTRIBUTING.md`.

