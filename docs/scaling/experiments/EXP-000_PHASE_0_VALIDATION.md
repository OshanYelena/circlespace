# EXP-000 — Phase 0 Validation

## Objective

Prove that the native, no-Docker experiment environment is reproducible and
that request, application, database, and correctness signals can be collected
before attempting to find capacity limits.

## Configuration

- Architecture: one Uvicorn/FastAPI worker, SQLAlchemy pool, PostgreSQL 17.9.
- Host: Apple M4, 10 logical CPUs, 16 GiB RAM, Darwin arm64.
- Dataset seed: `20260929`.
- Starting dataset: 100 users, 1,000 articles, 5,000 unique likes, 2,000 comments.
- Workload: mixed, 5 virtual users, spawn rate 5/s, 10 seconds.
- Generator: Locust 2.46.0 colocated with the API and database.

## Hypothesis

At this deliberately light load, the system should return no request failures,
expose every required signal, and preserve all checked data invariants. This
run validates the laboratory, not system capacity.

## Results

| Signal | Result |
| --- | ---: |
| Requests | 714 |
| Request failures | 0 (0%) |
| Throughput | 72.53 RPS |
| Average / median latency | 10.06 / 8 ms |
| p95 / p99 latency | 18 / 68 ms |
| Host CPU average / max | 27.13% / 49.0% |
| API CPU average | 39.64% |
| API RSS max | 336.0 MiB |
| PostgreSQL CPU average / max | 8.37% / 11.3% |
| PostgreSQL RSS max | 89.0 MiB |
| DB active / waiting max | 1 / 0 |
| Ungranted locks max | 0 |

The post-run integrity snapshot found 100 users, 1,000 articles, 5,043 likes,
and 2,080 comments. It found zero negative view counts, duplicate user/article
likes, or orphan comments, so the correctness check passed.

## Phase 0 exit questions

- Can a request be correlated through the service? **Yes.** Every response has
  `X-Request-ID`, and the same ID appears in the structured completion log.
- Can request rate, errors, and latency be measured? **Yes.** Prometheus
  counters and histograms plus Locust statistics capture them.
- Can application saturation be observed? **Yes.** Process CPU, RSS, threads,
  and in-progress request metrics are sampled.
- Can database pressure be observed? **Yes.** SQL duration/errors, pool state,
  active/waiting sessions, ungranted locks, PostgreSQL CPU, and RSS are sampled.
- Is the dataset repeatable? **Yes.** The explicit reset command and fixed seed
  reproduce the starting counts recorded in `dataset-manifest.json`.
- Are correctness checks automatic? **Yes.** Each completed experiment writes a
  `correctness.json`, and the runner summary includes its pass/fail state.

## Conclusion

Phase 0 is complete. The instrumentation and experiment workflow are suitable
for controlled local comparisons. The colocated load generator competes for
the same host resources, so these numbers are workflow-validation evidence and
must not be presented as production capacity.

Machine-readable evidence is under
[`results/EXP-000-phase0-validation`](../results/EXP-000-phase0-validation).
