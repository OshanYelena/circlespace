# Scaling Lab Backlog

This is the authoritative task and status ledger for the scaling experiment. Product work remains tracked separately in `docs/TASKS.md`.

## Status legend

- `BACKLOG` — not started
- `IN PROGRESS` — active work exists but exit criteria are not met
- `BLOCKED` — requires an external dependency or decision
- `DONE` — implemented, verified, and linked to evidence

## Global experiment rules

- Follow the phase order in `scaling_lab_master_plan.md`.
- Record the architecture, workload, dataset, hypothesis, metrics, correctness, and conclusion for every experiment.
- Change one major variable at a time where practical.
- Do not introduce scaling technology without evidence from the current phase.
- Keep the baseline application and measured workload intentionally small.

## Phase 0 — Instrumentation and reproducible environment

| ID | Status | Task | Exit evidence |
| --- | --- | --- | --- |
| P0-001 | DONE | Import the master plan and establish this backlog. | Root plan plus this file. |
| P0-002 | DONE | Establish a native PostgreSQL development database without Docker. | [`PHASE_0_ENVIRONMENT.md`](scaling/PHASE_0_ENVIRONMENT.md) and successful migration/readiness checks. |
| P0-003 | DONE | Adapt the monolith to the lab article API and domain. | Article, feed, search, view, like, comment, and notification tests. |
| P0-004 | DONE | Add request, process, database-pool, and SQL timing metrics. | Prometheus endpoint plus instrumentation tests. |
| P0-005 | DONE | Add structured logs and request correlation IDs. | Request ID behavior and JSON formatter tests. |
| P0-006 | DONE | Build a deterministic, parameterized dataset generator. | [`dataset-manifest.json`](scaling/results/dataset-manifest.json) and integrity checks. |
| P0-007 | DONE | Add repeatable Locust workload profiles. | Read-heavy, write-heavy, mixed, hotspot, and sustained profiles in `performance/locustfile.py`. |
| P0-008 | DONE | Add experiment templates, comparison table, and results tooling. | Versioned experiment records and machine-readable summaries. |
| P0-009 | DONE | Verify Phase 0 observability and correctness end to end. | [`EXP-000_PHASE_0_VALIDATION.md`](scaling/experiments/EXP-000_PHASE_0_VALIDATION.md). |

## Phase 1 — Baseline monolith

| ID | Status | Task | Exit evidence |
| --- | --- | --- | --- |
| P1-001 | DONE | Record exact baseline machine, application, worker, DB, and pool configuration. | [`PHASE_0_ENVIRONMENT.md`](scaling/PHASE_0_ENVIRONMENT.md) and EXP-001 architecture record. |
| P1-002 | IN PROGRESS | Run controlled read-heavy load progression. | Initial 10-VU result exists; higher load levels and saturation remain. |
| P1-003 | IN PROGRESS | Run controlled write-heavy load progression. | Initial 10-VU result exists; higher load levels and contention boundary remain. |
| P1-004 | IN PROGRESS | Run controlled mixed load progression. | Initial 10-VU result exists; saturation progression remains. |
| P1-005 | IN PROGRESS | Run sustained load at a safe representative level. | Initial 30-second stability run exists; a longer steady-state run remains. |
| P1-006 | BACKLOG | Determine sustainable throughput and identify the first bottleneck. | Completed `EXP-001` report and updated comparison table. |

## Later phases

Phases 2–17 remain `BACKLOG`. They will be expanded only when Phase 1 identifies the first measured bottleneck. No caching, queues, replicas, partitioning, sharding, service extraction, autoscaling, or multi-region work is authorized by this backlog yet.

## Prepared infrastructure — excluded from current baseline

| ID | Status | Task | Exit evidence |
| --- | --- | --- | --- |
| PREP-001 | DONE | Install and configure native Nginx as a local reverse proxy. | Syntax check, proxy health check, API routing check, and [`NGINX_REVERSE_PROXY.md`](scaling/NGINX_REVERSE_PROXY.md). |

Prepared infrastructure is not evidence of completing a scaling phase. Phase 1
load tests continue to target FastAPI directly on port 8000 until a recorded
experiment explicitly changes that single variable.

## Decision log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-09-29 | Use native PostgreSQL for Phase 0/1. | The user requested operation without Docker and PostgreSQL 17 is installed locally. |
| 2026-09-29 | Use Locust for load generation. | It integrates with the existing Python toolchain and supports reproducible workload profiles and CSV output. |
| 2026-09-29 | Preserve the existing social UI while measuring a small article API. | This minimizes unrelated product work and keeps the experimental surface controlled. |
| 2026-09-29 | Keep Phase 1 open after the 10-VU runs. | These runs validate the harness but do not establish saturation or sustainable throughput. |
| 2026-09-29 | Prepare Nginx without adding it to the Phase 1 data path. | The user requested the proxy setup, while the master plan requires evidence before adopting later-stage scaling infrastructure. |
