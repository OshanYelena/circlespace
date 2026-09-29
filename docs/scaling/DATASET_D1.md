# Dataset D1 — Deterministic Benchmark Data

Dataset D1 is development and benchmark tooling. It resets application data in
the configured PostgreSQL database while preserving the schema and Alembic
metadata. Never run it against production.

## Shape

| Table | Rows |
| --- | ---: |
| Users | 1,000 |
| Profiles | 1,000 |
| Posts | 10,000 |
| Comments | 30,000 |
| Likes | 50,000 |
| Friendships | 5,000 |
| Notifications | 10,000 |
| Friend requests | 0 |
| Shares | 0 |

The generator uses random seed `42` and fixed timestamps. Activity, authorship,
friendships, post engagement, and notifications use deterministic skew so most
records receive low or moderate activity while a small ranked subset becomes
hot. Password hashes use the application's real Argon2-based helper; their salt
can differ across resets, while credentials and dataset relationships remain
the same.

## Reset and seed

Start the Compose stack, then run:

```bash
docker compose up --build --detach
docker compose exec api python -m app.benchmark_seed --confirm-reset-d1
```

The equivalent shortcut is:

```bash
make benchmark-seed-d1
```

The explicit confirmation flag is mandatory. The script also refuses SQLite,
remote database hosts, and database names or hosts containing `prod`,
`production`, or `live`.

## Verify without resetting

```bash
docker compose exec api python -m app.benchmark_seed --verify-only
```

or:

```bash
make benchmark-verify-d1
```

Verification prints expected and actual counts for every application table,
PostgreSQL database size, elapsed time, and credential verification. Any
mismatch exits non-zero.

The validation run on 2026-09-29 generated D1 in 2.532 seconds. Every target
count and the password verification passed; PostgreSQL reported a 21 MB
database. These values describe the local Compose environment and are not
application-capacity results.

A second reset/reseed also passed every target. The observed distributions
confirm useful skew: posts per user had median 7 and maximum 341; likes per
post had median 4, p99 29, and maximum 504; comments per post had median 2,
p99 16, and maximum 293.

## Benchmark credentials

- Username: `benchmark_user_0001`
- Password: `benchmark-password-d1`

These credentials are intentionally public and suitable only for local
development and load testing. The account authenticates through the normal API
because its password is generated with the application's real password-hashing
logic.

The existing Locust profiles can use D1 without code changes:

```bash
LAB_USERNAME=benchmark_user_0001 \
LAB_PASSWORD=benchmark-password-d1 \
LAB_ARTICLE_MAX=10000 \
.venv/bin/locust -f performance/locustfile.py --host http://localhost:8080
```

## Recreate before another experiment

Run `make benchmark-seed-d1` before each experiment that requires the exact D1
starting shape. The reset uses PostgreSQL `TRUNCATE ... RESTART IDENTITY
CASCADE`, so IDs and relationships are regenerated consistently without
dropping the database or changing migrations.
