# Scaling Lab Master Comparison

Only measured results belong in this table. Provisional runs must be labeled.

| Stage | Architecture | Dataset | Workload | Sustainable RPS | p95 | p99 | Error rate | Primary bottleneck | Cost | Evidence |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| V1 | 1 FastAPI worker + PostgreSQL 17.9 | 100 users, 1,000 articles, 5,000 likes, 2,000 comments | Initial read/write/mixed at 10 VU | Not established; >=149 RPS observed | 27 ms observed | 63 ms observed | 0% observed | Not identified; run was unsaturated | Local | [Provisional EXP-001](experiments/EXP-001_INITIAL_BASELINE.md) |
| V2 | Vertically scaled app | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Not authorized |
| V3 | Multi-app + load balancer | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Not authorized |
| V4 | Cache, only if justified | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Not authorized |
