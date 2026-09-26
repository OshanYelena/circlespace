# Architecture

## Style

The backend is a modular monolith: one FastAPI process and one database, split into cohesive business modules. It keeps deployment simple while retaining boundaries that can later become service seams if scale demands it.

```text
HTTP /api/v1
     |
FastAPI routers (transport)
     |
module services (business rules)
     |
SQLAlchemy repositories/models (persistence)
     |
single relational database
```

## Backend modules

| Module | Responsibility |
| --- | --- |
| `auth` | Registration, login, token creation, current-user dependency |
| `users` | Profiles and user discovery |
| `friendships` | Requests, acceptance/rejection, friendship lifecycle |
| `posts` | Posts, comments, likes, shares, feed queries |
| `core` | Configuration, security, errors, cross-cutting concerns |
| `db` | Session, declarative base, shared persistence setup |

Each feature module exposes schemas, a router, and service functions. SQLAlchemy entities are never returned directly from route handlers.

## Frontend

Next.js App Router owns page composition. A typed API client centralizes authentication, serialization, and error handling. Reusable UI and feature components remain independent of transport details.

## Key decisions

- JWT bearer authentication keeps the API stateless.
- SQLite is the zero-setup development default; the SQLAlchemy layer supports PostgreSQL through `DATABASE_URL`.
- Feed pagination uses a stable `created_at`/identifier ordering.
- Likes and friendships use unique database constraints to preserve invariants under concurrency.
- CI treats formatting, lint, type checks, and tests as merge gates.

