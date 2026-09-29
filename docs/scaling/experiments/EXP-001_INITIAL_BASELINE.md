# EXP-001 — Initial Baseline (Provisional)

## Objective

Initiate Phase 1 by exercising the unchanged single-worker modular monolith
with representative read-heavy, write-heavy, mixed, and sustained workloads.

## Configuration

- Architecture: one Uvicorn/FastAPI worker on port 8000, SQLAlchemy pool size
  10 plus 20 overflow connections, and local PostgreSQL 17.9.
- Dataset before each profile: seed `20260929`; 100 users, 1,000 articles,
  5,000 likes, and 2,000 comments.
- Load: 10 virtual users, spawn rate 10/s.
- Duration: 15 seconds for read-heavy, write-heavy, and mixed; 30 seconds for
  the initial sustained check.
- Acceptance guardrails: error rate below 1%, p95 below 250 ms, and all
  post-run integrity checks passing.

## Hypothesis

Ten virtual users should remain below saturation and validate all workload
paths. Therefore this run should establish a safe lower bound, but should not
identify sustainable throughput or the first bottleneck.

## Results

| Profile | Requests | RPS | Avg | p95 | p99 | Errors | API CPU avg | API RSS max | DB active/waiting max | Correctness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Read-heavy | 2,192 | 147.91 | 8.92 ms | 18 ms | 45 ms | 0% | 60.36% | 398.5 MiB | 2 / 0 | Pass |
| Write-heavy | 2,219 | 150.21 | 8.95 ms | 17 ms | 58 ms | 0% | 59.35% | 398.5 MiB | 2 / 1 | Pass |
| Mixed | 2,249 | 151.66 | 8.27 ms | 18 ms | 38 ms | 0% | 55.82% | 398.4 MiB | 2 / 1 | Pass |
| Sustained mixed | 4,451 | 149.32 | 10.55 ms | 27 ms | 63 ms | 0% | 58.79% | 398.3 MiB | 2 / 1 | Pass |

No run observed an ungranted database lock. The API used 56–60% average CPU,
while database activity peaked at two connections. PostgreSQL CPU sampling was
added during Phase 0 validation and is required for the next Phase 1 series;
these four earlier profile runs contain PostgreSQL RSS but not CPU samples.

## Interpretation

The hypothesis is supported. All guardrails passed, and the similar throughput
across profiles reflects the fixed 10-user arrival behavior rather than a
capacity ceiling. The data does not justify naming CPU, PostgreSQL, the pool,
or any endpoint as the first bottleneck.

The only defensible baseline statement is that this environment sustained at
least 149 RPS for 30 seconds at 10 virtual users with p95 27 ms, zero request
failures, and passing integrity checks. This is not a sustainable-throughput
claim because the run neither reached saturation nor held steady long enough.

## Remaining Phase 1 work

1. Reset to the fixed dataset before each run.
2. Progress each profile through 25, 50, and 100 virtual users for at least 60
   seconds per level, stopping if p95 exceeds 250 ms, errors exceed 1%, or a
   correctness check fails.
3. At the highest safe level, run a longer steady-state experiment and inspect
   latency drift, RSS growth, pool pressure, PostgreSQL CPU, waits, and locks.
4. Identify the first saturated resource or endpoint from correlated evidence,
   then—and only then—authorize the relevant Phase 2 experiment.

Machine-readable evidence is under the four `EXP-001-*-10vu` directories in
[`results`](../results).
