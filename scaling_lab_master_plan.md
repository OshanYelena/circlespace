# Software System Scaling Lab - Master Plan

**Version:** 1.0  
**Status:** Fixed execution plan  
**Primary stack:** FastAPI, PostgreSQL, Docker  
**Lab application:** Mini content/feed platform  
**Primary goal:** Learn scaling by measurement, controlled failure, bottleneck diagnosis, and evidence-based architectural evolution.

---

## 0. Instructions for Agents - Operating Contract

Any agent working on this project must follow these rules unless the user explicitly changes them.

1. **Follow the phase order.** Do not skip ahead merely because a later technology is familiar or fashionable. A phase may be reordered only when measured evidence from the current system gives a concrete technical reason.
2. **Do not introduce technology without a measured problem.** Redis, RabbitMQ, replicas, sharding, microservices, Kubernetes, CDN, search engines, and multi-region deployment must each solve an observed bottleneck or explicitly defined experiment objective.
3. **Measure before recommending architecture changes.** Recommendations must cite current metrics such as throughput, p95/p99 latency, error rate, CPU, memory, DB utilization, DB connections, query latency, cache hit ratio, queue depth, or storage/network behavior.
4. **Change one major variable per experiment whenever practical.** Keep the workload and dataset fixed when comparing before/after results.
5. **Record every experiment.** Each experiment must include architecture, hypothesis, workload, dataset, measurements, bottleneck, change, result, conclusion, and next action.
6. **Do not optimize an unobserved bottleneck.** If the bottleneck is unclear, improve observability first.
7. **Prefer the simplest sufficient solution.** Optimize code and queries before introducing distributed complexity.
8. **Do not call a phase complete because a tool is installed.** A phase is complete only after the relevant hypothesis is tested and the result is documented.
9. **Preserve correctness while scaling.** Higher throughput is not success if requests are lost, duplicated incorrectly, reordered in a way that violates requirements, or data becomes inconsistent beyond the accepted model.
10. **Keep the baseline application intentionally small.** The project exists to study scaling, not product feature development.

### Agent decision loop

```text
Observe
  -> Measure
  -> Identify bottleneck
  -> Form hypothesis
  -> Make one justified change
  -> Repeat the same test
  -> Compare results
  -> Record conclusion
  -> Identify next bottleneck
```

### Core rule

> **Scale the bottleneck, not the architecture diagram.**

---

# 1. Purpose

This lab is a practical system-design learning project. We will begin with a deliberately simple hosted monolithic application, increase traffic and data volume until the system degrades, identify the actual limiting resource, apply one scaling technique, and repeat.

The goal is not to build the most complicated architecture. The goal is to understand **why each scaling technique exists, when it becomes justified, what it improves, and what new tradeoffs it introduces**.

At first principles:

```text
Demand increases
      -> some resource approaches saturation
      -> queueing increases
      -> latency rises
      -> timeouts/errors appear
      -> throughput stops growing
```

A system rarely becomes "slow" as one undifferentiated object. A specific resource or dependency becomes limiting first.

Typical limiting resources include:

- Application CPU
- Application memory
- Worker/thread/process capacity
- Network bandwidth or connection limits
- Database CPU
- Database memory
- Database connection pool
- Query execution time
- Locks and transaction contention
- Disk I/O
- Cache capacity
- Queue consumer capacity
- Object-storage throughput
- External services

---

# 2. Learning Outcomes

By the end of the lab, we should be able to:

- Determine whether a bottleneck is in traffic handling, compute, database, cache, queue, storage, network, or an external dependency.
- Distinguish vertical scaling from horizontal scaling and explain when each is appropriate.
- Explain why stateless application servers make horizontal scaling easier.
- Use caching to remove repeated work and reason about TTL, invalidation, hot keys, evictions, and cache stampedes.
- Scale relational databases progressively through query optimization, indexing, pooling, vertical scaling, replicas, partitioning, and sharding.
- Recognize concurrency bugs and contention introduced by higher parallelism.
- Move non-critical work to asynchronous queues and scale workers independently.
- Separate binary/file storage from application compute and use a CDN appropriately.
- Understand read replicas and observe eventual consistency / replication lag.
- Understand when dedicated search infrastructure becomes justified.
- Understand why partitioning and sharding add major operational and application complexity.
- Decompose services only when independent scale, deployment, failure isolation, ownership, or data requirements justify it.
- Perform failure experiments, rate limiting, backpressure, autoscaling, and optional multi-region exercises.
- Translate performance measurements into capacity and cost estimates.
- Explain system-design scaling decisions in an interview using evidence and tradeoffs rather than product names.

---

# 3. Main Scaling Areas

## 3.1 Traffic and Edge

**What can saturate:** incoming connections, request-routing capacity, bandwidth, origin traffic.

**Techniques:**

- Reverse proxy
- Load balancer
- Health checks
- TLS termination
- Rate limiting
- CDN
- Geographic routing
- DDoS protection where relevant

## 3.2 Application Compute

**What can saturate:** CPU, memory, process/worker capacity, open connections.

**Techniques:**

- Code optimization
- Worker/process tuning
- Vertical scaling
- Horizontal scaling
- Stateless application design
- Autoscaling

## 3.3 Cache

**What can saturate:** repeated computation or repeated database access.

**Techniques:**

- In-process cache
- Distributed cache
- Redis
- Cache-aside
- TTL
- Invalidation
- Hot-key mitigation
- Stampede protection

## 3.4 Database

**What can saturate:** CPU, memory, connections, locks, disk I/O, query execution, data volume.

**Techniques:**

- Query optimization
- Indexing
- Connection pooling
- Transaction tuning
- Vertical scaling
- Read replicas
- Partitioning
- Sharding

## 3.5 Asynchronous Work

**What can saturate:** synchronous request time, background-task capacity, downstream dependencies.

**Techniques:**

- Message queue
- Worker pools
- RabbitMQ
- Retries
- Dead-letter queues
- Idempotency
- Backpressure

## 3.6 Storage and Content Delivery

**What can saturate:** local disk, file-serving bandwidth, large binary storage.

**Techniques:**

- Object storage
- S3-compatible storage
- CDN
- Lifecycle policies

## 3.7 Distributed Architecture

**What can saturate:** independently growing workloads or tightly coupled failure/deployment domains.

**Techniques:**

- Service decomposition
- Independent scaling
- Independent deployment
- Failure isolation
- Distributed data
- Multi-region architecture

## 3.8 Observability - Cross-Cutting

Observability does not increase capacity directly, but it is required to know what should be scaled.

Track:

- Metrics
- Logs
- Traces
- Health checks
- Alerts

---

# 4. Laboratory Application

We will build a **mini content/feed platform**, conceptually similar to a very small Medium/Reddit/news-feed system.

It is intentionally chosen because a small feature set can generate many different scaling behaviors.

## 4.1 Core features

- User creation
- Article creation
- Article retrieval
- Feed browsing
- Likes
- Comments
- View counting
- Search
- Notifications
- Image/file uploads introduced later

## 4.2 Why this application is suitable

| Workload | Feature | Scaling topic |
|---|---|---|
| Repeated reads | Article retrieval | Caching |
| Read-heavy browsing | Feed | Read replicas, caching |
| Concurrent writes | Likes, views | Transactions, atomic updates, locks |
| Transactional writes | Comments, article creation | Database contention |
| Expensive queries | Search | Indexing, FTS, dedicated search |
| Background work | Notifications/indexing | Queues and workers |
| Large objects | Article images | Object storage and CDN |
| Hotspot | Viral article | Hot keys, cache stampede |
| Large data volume | Users/articles | Partitioning, sharding |
| Uneven workload growth | Search/notifications/feed | Selective service decomposition |

---

# 5. Initial Domain Model

## User

```text
User
- id
- username
- email
- created_at
```

## Article

```text
Article
- id
- author_id
- title
- content
- view_count
- created_at
- updated_at
```

## Comment

```text
Comment
- id
- article_id
- user_id
- content
- created_at
```

## Like

```text
Like
- user_id
- article_id
- created_at

UNIQUE(user_id, article_id)
```

## Notification

```text
Notification
- id
- user_id
- type
- reference_id
- created_at
- read_at
```

The domain should remain intentionally small. Do not add features unless an experiment requires them.

---

# 6. Initial API Surface

```http
POST /users
POST /articles

GET  /articles/{id}
GET  /feed

POST /articles/{id}/like
POST /articles/{id}/comments
POST /articles/{id}/view

GET  /articles/search?q={query}
GET  /notifications
```

File-upload endpoints are introduced only in the storage phase.

---

# 7. Technology Policy

## 7.1 Baseline stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker

## 7.2 Measurement stack

Use practical tooling such as:

- k6 or Locust for load generation
- Prometheus-compatible metrics
- Grafana dashboards
- OpenTelemetry traces where useful
- PostgreSQL statistics / slow-query data
- Host/container CPU, RAM, network, and disk metrics

## 7.3 Technologies introduced later only when justified

- Redis
- RabbitMQ
- Load balancer / reverse proxy
- Object storage
- CDN
- Read replicas
- Search engine
- Partitioning/sharding infrastructure
- Selective microservices
- Autoscaling platform
- Multi-region infrastructure

## 7.4 Explicit anti-goals

Do **not** begin with:

- Kubernetes
- Microservices
- Sharding
- Multi-region databases
- Event-driven architecture everywhere
- Multiple specialized databases

The lab must earn complexity experimentally.

---

# 8. Baseline Architecture

```text
Internet / Load Generator
          |
          v
   +---------------+
   | FastAPI       |
   | Monolith      |
   | 1 instance    |
   +-------+-------+
           |
           v
   +---------------+
   | PostgreSQL    |
   | 1 instance    |
   +---------------+
```

No Redis. No queue. No CDN. No microservices.

---

# 9. Experimental Method

Every significant experiment must follow the same workflow.

## 9.1 Define the architecture

Record the exact deployment under test.

Example:

```text
1 FastAPI instance
1 PostgreSQL instance
2 vCPU / 4 GB RAM application host
```

## 9.2 Define the workload

Example:

```text
80% GET /articles/{id}
15% GET /feed
5% POST /articles/{id}/like
```

Record concurrency, arrival pattern, duration, and request distribution.

## 9.3 Define the dataset

Example:

```text
100,000 users
1,000,000 articles
5,000,000 likes
```

Dataset size matters because query behavior changes with scale.

## 9.4 Run controlled increasing load

Example progression:

```text
50 RPS
100 RPS
250 RPS
500 RPS
1,000 RPS
2,000 RPS
...
```

Continue until a clear saturation/degradation point appears or a safety/cost limit is reached.

## 9.5 Measure

Collect request, application, database, and infrastructure metrics.

## 9.6 Identify the bottleneck

Examples:

- App CPU reaches sustained high utilization while DB remains healthy.
- DB CPU saturates while app CPU remains moderate.
- DB pool is fully utilized and requests wait for connections.
- Lock waits increase sharply under concurrent writes.
- Queue depth grows continuously because consumers cannot keep up.

## 9.7 Form a hypothesis

Example:

> Application CPU is limiting throughput; adding application capacity should raise sustainable RPS until another shared resource saturates.

## 9.8 Make one major change

Example: move from one app instance to three app instances behind a load balancer.

## 9.9 Repeat the same test

The workload and dataset should remain the same for a valid before/after comparison.

## 9.10 Compare and conclude

Record:

- Throughput change
- Latency change
- Error-rate change
- Resource-utilization change
- Cost change
- New bottleneck
- New operational complexity

---

# 10. Metrics Standard

## 10.1 Request metrics

- Requests per second (RPS)
- Concurrent users / virtual users
- Total requests
- p50 latency
- p95 latency
- p99 latency
- Error rate
- Timeout rate
- HTTP 5xx count
- HTTP 429 count when rate limiting exists

## 10.2 Application metrics

- CPU utilization
- Memory utilization
- Process/worker utilization
- Open connections
- Event-loop/worker saturation signals where available
- GC behavior if relevant

## 10.3 Database metrics

- DB CPU
- DB memory
- Query throughput
- Query latency
- Active connections
- Waiting connections
- Pool utilization
- Lock waits
- Slow queries
- Disk IOPS/throughput
- Cache/buffer behavior when available

## 10.4 Cache metrics

- Hit ratio
- Miss ratio
- Cache latency
- Memory usage
- Evictions
- Hot keys where observable

## 10.5 Queue metrics

- Publish rate
- Consumer rate
- Queue depth
- Oldest-message age / lag
- Worker utilization
- Retry count
- Failure count
- Dead-letter count

## 10.6 Storage/network metrics

- Storage request latency
- Bandwidth
- Transfer volume
- Origin request count after CDN introduction

---

# 11. Definition of Sustainable Throughput

Do not use "maximum RPS" without a quality threshold.

For each experiment, define sustainable throughput as the highest load maintained for the agreed test duration while meeting all selected service thresholds.

Example initial thresholds (adjust once the baseline is known):

```text
p95 latency < target
error rate < 1%
no continuously growing internal queue
no resource pinned at an unsafe level for the entire run
correctness checks pass
```

The objective is not to chase a single peak number that the system can survive for a few seconds.

---

# 12. Fixed Phase Roadmap

## Phase 0 - Instrumentation and Reproducible Test Environment

### Goal

Make performance observable before attempting to scale anything.

### Architecture

```text
Load Generator -> FastAPI -> PostgreSQL
                       |
                       +-> Metrics / Logs / Traces
```

### Required capabilities

- Repeatable deployment
- Seeded dataset generation
- Repeatable load-test profiles
- Request rate/latency/error metrics
- App CPU/RAM metrics
- DB CPU/connections/query-latency metrics
- Basic tracing or request timing for critical flows

### Exit criteria

We can answer:

- How much traffic is being sent?
- What are p50/p95/p99 latencies?
- What is the error rate?
- What is app CPU/RAM?
- What is DB utilization?
- Where is request time being spent?

**Do not start scaling experiments until this phase passes.**

---

## Phase 1 - Baseline Monolith

### Goal

Measure the capacity and failure behavior of the simplest hosted architecture.

### Architecture

```text
Users / k6 / Locust
        |
        v
  FastAPI Monolith
        |
        v
    PostgreSQL
```

### Experiments

1. Read-heavy workload
2. Write-heavy workload
3. Mixed workload
4. Sustained workload

### Questions

- What is sustainable RPS?
- At what point does p95 latency bend upward?
- Which resource saturates first?
- What happens after saturation: queueing, timeouts, errors, connection exhaustion?

### Exit criteria

A documented baseline exists for all core metrics and the first bottleneck is identified.

---

## Phase 2 - Vertical Scaling

### Goal

Measure what additional machine resources accomplish before distributing the application.

### Example progression

```text
2 vCPU / 4 GB
-> 4 vCPU / 8 GB
-> 8 vCPU / 16 GB
```

### Hypothesis

If application compute is limiting throughput, a larger instance should increase sustainable load.

### Measure

- RPS
- p95/p99
- CPU/RAM
- DB impact
- Cost
- Throughput per unit cost

### Learning target

Vertical scaling is simple but finite and may have diminishing cost efficiency.

### Exit criteria

We can quantify the improvement and explain why vertical scaling eventually stops being the preferred next move.

---

## Phase 3 - Horizontal Application Scaling

### Goal

Scale application compute independently using multiple stateless instances.

### Architecture

```text
                 Load Balancer
                /      |      \
             App 1   App 2   App 3
                \      |      /
                   PostgreSQL
```

### Required investigation

Identify state that prevents safe horizontal scaling:

- In-memory sessions
- In-memory mutable application state
- Local uploaded files
- Local task state

### Experiments

Compare one, two, three, and more application instances using the same workload.

### Questions

- How close is scaling to linear?
- When does adding instances stop helping?
- Does a shared dependency become the new bottleneck?
- How do DB connections change as app instance count grows?

### Exit criteria

Horizontal scaling behavior is measured and the next shared bottleneck is identified.

---

## Phase 4 - Caching

### Goal

Reduce repeated downstream work for read-heavy traffic.

### Initial target

`GET /articles/{id}` for popular articles.

### Pattern

Cache-aside:

```text
Request -> Redis
           | HIT  -> Return
           | MISS -> PostgreSQL -> Redis -> Return
```

### Experiments

- Cold cache
- Warm cache
- Different TTL values
- Increasing hit ratio
- Hot article workload

### Measure

- Cache hit/miss ratio
- DB QPS reduction
- DB CPU reduction
- Request latency
- Cache latency

### Advanced experiments

- Invalidation after article update
- Hot key
- Cache stampede after expiry
- Eviction pressure

### Exit criteria

We can show whether caching reduced DB work, quantify the improvement, and describe the consistency/operational tradeoffs it introduced.

---

## Phase 5 - Database Optimization

### Goal

Push a single relational database further before distributing it.

### Experiments

- Query plans with `EXPLAIN` / `EXPLAIN ANALYZE`
- Missing vs appropriate indexes
- Composite indexes where justified
- Pagination behavior
- Connection-pool sizing
- Slow-query identification
- Vertical DB scaling if justified

### Key principle

Do not assume more DB connections are always better. Too many concurrent DB sessions can increase contention and decrease total throughput.

### Exit criteria

The important query paths are understood, indexed appropriately, and the optimized single-primary baseline is documented.

---

## Phase 6 - Concurrency and Contention

### Goal

Study correctness and database contention under high parallelism.

### Primary workload

Many clients concurrently like or view the same article.

### Failure example

```text
likes = 100
A reads 100
B reads 100
A writes 101
B writes 101
Expected 102, actual 101
```

### Techniques to test

- Atomic SQL updates
- Unique constraints
- Transactions
- Row-level locking
- Optimistic concurrency where appropriate
- Idempotency

### Measure

- Correct final counts
- Lock-wait time
- Transaction latency
- Deadlocks/retries
- Throughput under contention

### Exit criteria

The system remains correct under the tested concurrency model and the cost of chosen consistency mechanisms is measured.

---

## Phase 7 - Asynchronous Processing

### Goal

Remove non-critical work from synchronous request paths and scale background processing independently.

### Candidate tasks

- Notifications
- Analytics events
- Search indexing
- Preview generation

### Architecture

```text
Client -> API -> DB -> RabbitMQ -> Response
                          |
                          +-> Worker pool
```

### Experiments

- Synchronous baseline vs queued version
- 1, 2, 5, 10 workers
- Burst traffic that exceeds worker capacity
- Worker failure and retry

### Measure

- API response latency
- Queue depth
- Queue lag
- Publish rate
- Consumer throughput
- Retry/failure counts

### Concepts

- Backpressure
- At-least-once delivery
- Idempotent consumers
- Retry policy
- Dead-letter queues

### Exit criteria

We can show that asynchronous processing improved the request path where appropriate and can explain failure/delivery semantics.

---

## Phase 8 - Object Storage and CDN

### Goal

Separate large/static file storage and delivery from application compute.

### Deliberate bad baseline

Store article images on a local app instance and observe what breaks when multiple app instances are used.

### Target architecture

```text
Application -> Object Storage
Users       -> CDN -> Object Storage
```

### Measure

- App-host bandwidth/load before and after
- File-serving latency
- Origin request reduction with CDN
- Storage/CDN transfer behavior

### Exit criteria

Uploads are no longer coupled to one app server and static delivery is measurably separated from core API compute.

---

## Phase 9 - Database Read Replicas

### Goal

Scale read-heavy workloads and study replication consistency.

### Architecture

```text
              Primary DB
                 |
            replication
             /       \
        Replica 1   Replica 2
```

Writes go to the primary. Selected reads go to replicas.

### Experiments

- Single DB vs primary + replicas
- Increasing read load
- Immediate read after write against a replica

### Study

- Replication lag
- Eventual consistency
- Read-after-write consistency
- Failover considerations

### Exit criteria

Read capacity change is measured and the application has an explicit strategy for reads that require fresh data.

---

## Phase 10 - Search Scaling

### Goal

Observe how search performance changes with dataset size and determine when a dedicated search system is justified.

### Dataset progression

```text
10K articles
100K
1M
10M where practical/simulated
```

### Progression

1. Naive SQL text search
2. Appropriate DB indexes
3. PostgreSQL full-text search
4. Dedicated search engine if evidence justifies it

### Target architecture when justified

```text
Application -> PostgreSQL
           \-> Search Engine
```

### Exit criteria

We can explain which search approach is appropriate at each observed scale and the indexing/update consistency tradeoff.

---

## Phase 11 - Partitioning

### Goal

Study dividing large tables while keeping a logically single database system.

### Candidate keys

- `created_at` for range partitioning
- `user_id` for hash partitioning

### Questions

- Which queries benefit from partition pruning?
- Which queries become harder?
- What happens when partitions become uneven?
- How does operational management change?

### Exit criteria

Partitioning has been tested against a defined data/query problem and its value is measured.

---

## Phase 12 - Database Sharding

### Goal

Study horizontal data distribution only after simpler DB scaling techniques are understood.

### Example scheme

```text
shard = hash(user_id) % N
```

### Architecture

```text
Application -> Shard Router -> Shard A
                           -> Shard B
                           -> Shard C
```

### Required topics

- Shard-key selection
- Hot shards
- Cross-shard queries
- Cross-shard transactions
- Rebalancing
- ID generation
- Joins
- Shard discovery/routing

### Exit criteria

The lab documents both the scaling benefit and the substantial complexity cost. Sharding must not be treated as a default production recommendation.

---

## Phase 13 - Selective Service Decomposition

### Goal

Split only workloads that now have a demonstrated reason to scale/deploy/fail independently.

### Candidate services

- Search
- Notifications
- Feed generation

### Example

```text
                API Gateway
             /      |       \
        Content   Search   Notification
          |          |
        Main DB   Search Store
```

### Valid reasons to split

- Different scaling requirements
- Different failure characteristics
- Different data requirements
- Independent deployment need
- Independent team ownership

### Invalid reason

> "Microservices scale better."

### Exit criteria

Each extracted service has a documented reason and measurable or operational benefit that outweighs added distributed-system complexity.

---

## Phase 14 - Failure Engineering

### Goal

Observe system behavior when dependencies fail instead of evaluating only the happy path.

### Failure drills

- Kill one app instance
- Stop Redis
- Stop a worker
- Restart RabbitMQ
- Slow PostgreSQL
- Make an external dependency timeout
- Remove a DB replica

### Observe

- User-visible failure
- Recovery time
- Message loss/duplication
- Retry storms
- Cascading failure
- Graceful degradation

### Techniques

- Timeouts
- Retries with bounds/backoff
- Circuit breakers where useful
- Health checks
- Failure isolation
- Graceful degradation

### Exit criteria

The system's behavior under selected failures is documented and recovery mechanisms are tested rather than assumed.

---

## Phase 15 - Rate Limiting and Backpressure

### Goal

Protect the system when accepting more work would reduce availability for everyone.

### Techniques

- Per-client/global rate limits
- Request quotas
- Queue bounds
- Admission control
- HTTP 429
- Backpressure from downstream capacity

### Exit criteria

The system rejects or delays excess demand in a controlled, measurable way instead of collapsing unpredictably.

---

## Phase 16 - Autoscaling

### Goal

Automate scaling only after manual scaling characteristics are understood.

### Candidate signals

- CPU utilization
- Request rate
- p95 latency
- Queue depth / oldest-message age

### Study

- Scale-up delay
- Scale-down delay
- Cold starts
- Oscillation/flapping
- Minimum/maximum capacity
- Cost impact

### Exit criteria

Autoscaling policy is based on a metric that actually correlates with capacity pressure and behaves acceptably under spikes and cooldown.

---

## Phase 17 - Multi-Region Architecture (Advanced / Optional)

### Goal

Study global latency and resilience only after single-region scaling is well understood.

### Architecture concept

```text
Global Users
     |
Global Routing
   /      \
Region A  Region B
  |         |
Apps      Apps
  |         |
Data <-> Cross-region replication
```

### Topics

- Global latency
- Cross-region replication
- Consistency
- Failover
- Disaster recovery
- Data residency

### Exit criteria

A clear reason exists for multi-region deployment and consistency/failover behavior is explicitly documented.

---

# 13. Standard Workload Profiles

## A. Read-heavy

```text
95% reads
5% writes
```

Useful for caching, replicas, and CDN experiments.

## B. Write-heavy

```text
40% reads
60% writes
```

Useful for database contention and transaction experiments.

## C. Mixed

Example:

```text
70% reads
20% interactions
10% content creation
```

Useful as a realistic general profile.

## D. Hotspot

```text
80% of article traffic hits 1% of articles
```

Useful for hot-key and cache-stampede experiments.

## E. Traffic spike

```text
500 RPS -> 5,000 RPS over a short ramp
```

Useful for autoscaling, queue behavior, and protective controls.

## F. Sustained load

Hold traffic for an extended period to detect:

- Memory leaks
- Connection leaks
- Queue accumulation
- Resource exhaustion
- Performance drift

---

# 14. Bottleneck Diagnosis Procedure

When performance degrades, follow this order instead of guessing.

## Step 1 - Confirm symptoms

Check:

- Throughput
- p50/p95/p99 latency
- Error rate
- Timeout rate

## Step 2 - Check application compute

- CPU
- RAM
- Worker/process saturation
- Open connections

## Step 3 - Check database

- DB CPU
- Connections/pool utilization
- Query latency
- Locks
- Disk I/O
- Slow queries

## Step 4 - Check cache

If present:

- Hit ratio
- Cache latency
- Evictions
- Memory pressure

## Step 5 - Check asynchronous infrastructure

If present:

- Queue depth
- Queue lag
- Worker utilization
- Retry/failure counts

## Step 6 - Check storage/network/dependencies

- Network bandwidth
- Object storage latency
- CDN/origin behavior
- External API latency/errors
- Search backend

### Primary diagnostic question

> **What prevents this system from handling the next 2x traffic?**

Example A:

```text
App CPU: 32%
App RAM: 45%
DB CPU: 98%
```

Do not solve this by adding more app instances.

Example B:

```text
App CPU: 100%
DB CPU: 25%
```

Do not solve this by sharding the database.

---

# 15. Experiment Record Template

Every experiment must create a record with this structure.

```markdown
# EXP-XXX - <short name>

## Objective
What are we trying to learn?

## Current Architecture
Exact app, DB, cache, queue, worker, storage, and machine configuration.

## Hypothesis
A falsifiable expectation.

## Workload
- Request mix:
- Target RPS / VUs:
- Ramp pattern:
- Duration:

## Dataset
- Users:
- Articles:
- Likes:
- Comments:
- Other relevant size:

## Metrics Before
- Sustainable RPS:
- p50:
- p95:
- p99:
- Error rate:
- App CPU/RAM:
- DB CPU/connections/query latency:
- Cache hit rate if applicable:
- Queue depth/lag if applicable:

## Change
Exactly one major architectural/configuration change where practical.

## Metrics After
Same metrics as before.

## Correctness Checks
Confirm no lost/incorrect/duplicated data beyond accepted semantics.

## Observation
What actually happened?

## Bottleneck
What resource or dependency is limiting progress now?

## Conclusion
Was the hypothesis supported?

## Tradeoffs Introduced
Cost, complexity, consistency, operations, failure modes.

## Next Experiment
What should be tested next and why?
```

---

# 16. Master Comparison Table

Maintain this throughout the project.

| Stage | Architecture | Sustainable RPS | p95 | p99 | Error Rate | Primary Bottleneck | Monthly/Hourly Cost | Notes |
|---|---|---:|---:|---:|---:|---|---:|---|
| V1 | 1 app + 1 DB | TBD | TBD | TBD | TBD | TBD | TBD | Baseline |
| V2 | Vertically scaled app | TBD | TBD | TBD | TBD | TBD | TBD | |
| V3 | Multi-app + LB | TBD | TBD | TBD | TBD | TBD | TBD | |
| V4 | + Redis | TBD | TBD | TBD | TBD | TBD | TBD | |
| V5 | DB optimized | TBD | TBD | TBD | TBD | TBD | TBD | |
| V6 | + queue/workers | TBD | TBD | TBD | TBD | TBD | TBD | |
| V7 | + read replicas | TBD | TBD | TBD | TBD | TBD | TBD | |
| V8+ | Later phases | TBD | TBD | TBD | TBD | TBD | TBD | |

---

# 17. Cost and Capacity Planning

Scaling is not only about maximum throughput. Track efficiency.

Useful measures:

```text
cost per 1,000 requests
sustainable RPS per dollar
DB cost per workload level
cache cost vs DB work avoided
worker cost per job throughput
```

If one app instance sustains 800 RPS and expected peak is 5,000 RPS:

```text
5000 / 800 = 6.25
```

Do not provision exactly seven instances and assume the job is done. Account for:

- Headroom
- One or more failed instances
- Traffic variance
- Deployment overlap
- Autoscaling delay

Capacity planning should be based on measured sustainable capacity, not theoretical machine specifications.

---

# 18. Scaling Hierarchy - Prefer Simpler Fixes First

This is a heuristic, not an immutable sequence:

```text
1. Fix bad code
2. Fix bad queries
3. Add appropriate indexes
4. Remove unnecessary work
5. Cache repeated work
6. Tune/scale the machine
7. Scale application instances horizontally
8. Move suitable work asynchronous
9. Add database replicas
10. Partition data
11. Shard data
12. Decompose selected services
13. Add multi-region distribution
```

The guiding principle is to introduce distributed complexity only when simpler approaches are insufficient for the measured problem.

---

# 19. Phase Completion Rule

A phase is **not** complete because a technology is running.

For example, "Redis is installed" does not complete the caching phase.

A phase is complete only when we can answer:

1. What problem existed?
2. What measurement proved it?
3. Why was this technique chosen?
4. What exact change was made?
5. What changed in throughput, latency, errors, resource usage, and cost?
6. Did correctness remain acceptable?
7. What new tradeoffs appeared?
8. What is the new bottleneck?

---

# 20. Final Mental Model

```text
                           USERS
                             |
                             v
                    +----------------+
                    | TRAFFIC / EDGE |
                    | CDN / LB / RL  |
                    +--------+-------+
                             |
                             v
                    +----------------+
                    | APP COMPUTE    |
                    | App Instances  |
                    +--------+-------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
            CACHE           QUEUE          STORAGE
              |              |              |
              |              v              v
              |           WORKERS       OBJECT STORE
              |
              v
           DATABASE
              |
        +-----+------+
        v            v
     REPLICA       REPLICA
              |
              v
         PARTITIONING
              |
              v
            SHARDS
```

Surrounding everything:

```text
Observability = Metrics + Logs + Traces + Health + Alerts
```

Five core scaling questions:

```text
Compute -> Can application instances handle the work?
Reads   -> Are we repeating expensive work unnecessarily?
Data    -> Can the data layer handle size and access rate?
Work    -> Does all work need to happen synchronously?
Traffic -> Can demand be distributed and controlled?
```

---

# 21. Final Deliverables

The completed Scaling Lab should contain:

- Application source code
- Infrastructure/deployment configuration
- Dataset generator
- Load-test scripts
- Monitoring dashboards
- Architecture diagrams
- Experiment records
- Master comparison table
- Performance graphs
- Failure-test results
- Cost/capacity comparisons
- Architecture evolution notes from V1 to final stage

Every architectural transition must answer:

> **Why did the architecture need to change?**

---

# 22. Fixed Execution Order

Unless measured evidence gives a strong reason to alter it, agents must follow:

```text
0. Instrumentation + reproducible test environment
1. Baseline monolith
2. Vertical scaling
3. Horizontal application scaling
4. Caching
5. Database optimization
6. Concurrency and contention
7. Asynchronous processing
8. Object storage + CDN
9. Database read replicas
10. Search scaling
11. Partitioning
12. Sharding
13. Selective service decomposition
14. Failure engineering
15. Rate limiting + backpressure
16. Autoscaling
17. Multi-region - advanced / optional
```

---

# 23. Final Principle

The project exists to learn the reasoning behind scaling decisions.

For every change, ask:

```text
What changed?
What did we measure?
What saturated?
Why did it saturate?
What is the simplest appropriate solution?
What tradeoff does that solution introduce?
Where did the bottleneck move next?
```

Do not memorize Redis, RabbitMQ, Kafka, Kubernetes, sharding, or microservices as answers.

Understand the problem that makes each one useful.

> **Scale the bottleneck, not the architecture diagram.**
