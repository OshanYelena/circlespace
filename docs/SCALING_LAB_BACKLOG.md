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
| P0-002 | IN PROGRESS | Establish a native PostgreSQL development database without Docker. | Version, configuration, migration, connectivity, and health evidence. |
| P0-003 | BACKLOG | Adapt the monolith to the lab article API and domain. | Articles, views, search, comments, likes, and notifications API tests. |
| P0-004 | BACKLOG | Add request, process, database-pool, and SQL timing metrics. | Prometheus endpoint and automated instrumentation tests. |
| P0-005 | BACKLOG | Add structured logs and request correlation IDs. | Request ID behavior and JSON log verification. |
| P0-006 | BACKLOG | Build a deterministic, parameterized dataset generator. | Repeatable PostgreSQL dataset manifest and count verification. |
| P0-007 | BACKLOG | Add repeatable Locust workload profiles. | Read-heavy, write-heavy, mixed, hotspot, and sustained profiles. |
| P0-008 | BACKLOG | Add experiment templates, comparison table, and results tooling. | Versioned experiment records and machine-readable result output. |
| P0-009 | BACKLOG | Verify Phase 0 observability and correctness end to end. | Phase 0 exit report answering every required observability question. |

## Phase 1 — Baseline monolith

| ID | Status | Task | Exit evidence |
| --- | --- | --- | --- |
| P1-001 | BACKLOG | Record exact baseline machine, application, worker, DB, and pool configuration. | Baseline architecture record. |
| P1-002 | BACKLOG | Run controlled read-heavy load progression. | Raw results, request metrics, resource metrics, correctness checks. |
| P1-003 | BACKLOG | Run controlled write-heavy load progression. | Raw results, contention/error observations, correctness checks. |
| P1-004 | BACKLOG | Run controlled mixed load progression. | Raw results and saturation behavior. |
| P1-005 | BACKLOG | Run sustained load at a safe representative level. | Stability, leak, connection, and drift observations. |
| P1-006 | BACKLOG | Determine sustainable throughput and identify the first bottleneck. | Completed `EXP-001` report and updated comparison table. |

## Later phases

Phases 2–17 remain `BACKLOG`. They will be expanded only when Phase 1 identifies the first measured bottleneck. No caching, queues, replicas, partitioning, sharding, service extraction, autoscaling, or multi-region work is authorized by this backlog yet.

## Decision log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-09-29 | Use native PostgreSQL for Phase 0/1. | The user requested operation without Docker and PostgreSQL 17 is installed locally. |
| 2026-09-29 | Use Locust for load generation. | It integrates with the existing Python toolchain and supports reproducible workload profiles and CSV output. |
| 2026-09-29 | Preserve the existing social UI while measuring a small article API. | This minimizes unrelated product work and keeps the experimental surface controlled. |

