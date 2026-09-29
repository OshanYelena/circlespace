# Phase 0 Environment

## Native services

- Host: Apple M4, 10 logical CPUs, 16 GiB RAM, Darwin arm64.
- Python: CPython 3.10.18.
- PostgreSQL: Homebrew PostgreSQL 17.9, database `circlespace_lab`, port 5432.
- PostgreSQL configuration: `max_connections=100`, `shared_buffers=128MB`,
  `work_mem=4MB`, and `effective_cache_size=4GB`.
- API: Uvicorn 0.54.0, one process and one worker on port 8000.
- SQLAlchemy pool: size 10, max overflow 20, timeout 30 seconds, pre-ping enabled.
- Web: optional Next.js development server on port 3000; excluded from API load tests.
- Load generator: Locust 2.46.0, executed from the same development host for initial local experiments.

The colocated load generator makes local measurements useful for workflow validation and relative comparisons, but not production capacity claims. Hosted experiments must record separate load-generator and application resources.

## Baseline data path

```text
Locust -> FastAPI modular monolith -> SQLAlchemy pool -> PostgreSQL 17
                       |
                       +-> /metrics + structured JSON logs
```

There is no cache, queue, replica, object store, CDN, or service decomposition.

## Reproduce

```bash
make api-install
make lab-migrate
make lab-reset-seed
make lab-api
```

In another terminal:

```bash
make lab-run
```

The dataset defaults to 100 users, 1,000 articles, 5,000 unique likes, and 2,000 comments with seed `20260929`. Change dataset size only between explicitly recorded experiments.

## Metrics

- `GET /metrics` exposes request count, latency histograms, in-progress requests, SQL latency/error histograms, pool state, PostgreSQL active/waiting sessions and locks, and API-process CPU/RSS/threads.
- Every response includes `X-Request-ID`.
- Request completion logs are JSON and include method, path, status, duration, and request ID.
- The experiment runner samples metrics and host/PostgreSQL process memory every second.
- `GET /health/ready` verifies that the API can execute a database query.

## Phase 0 verification

- Alembic migrations apply through revision `0004_scaling_lab_articles`.
- The fixed seed contains 100 users, 1,000 articles, 5,000 unique likes, and
  2,000 comments before workloads mutate it.
- The validation workload completed 714 requests with zero failures and passed
  checks for negative view counts, duplicate likes, and orphan comments.
- The full evidence and limitations are recorded in
  [`experiments/EXP-000_PHASE_0_VALIDATION.md`](experiments/EXP-000_PHASE_0_VALIDATION.md).
