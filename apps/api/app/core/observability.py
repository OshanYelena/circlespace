import logging
import time
import uuid
from collections.abc import Awaitable, Callable

import psutil
from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import Engine, event, text

from app.core.logging import request_id_context

logger = logging.getLogger("circlespace.request")

HTTP_REQUESTS = Counter(
    "circlespace_http_requests_total",
    "Completed HTTP requests.",
    ("method", "route", "status_code"),
)
HTTP_DURATION = Histogram(
    "circlespace_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
HTTP_IN_PROGRESS = Gauge(
    "circlespace_http_requests_in_progress",
    "HTTP requests currently being processed.",
    ("method",),
)
DB_QUERY_DURATION = Histogram(
    "circlespace_db_query_duration_seconds",
    "SQL execution duration in seconds.",
    ("operation",),
    buckets=(0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 5),
)
DB_QUERY_ERRORS = Counter(
    "circlespace_db_query_errors_total", "SQL execution errors.", ("operation",)
)
DB_POOL_SIZE = Gauge("circlespace_db_pool_size", "Configured SQLAlchemy pool size.")
DB_POOL_CHECKED_OUT = Gauge(
    "circlespace_db_pool_checked_out", "SQLAlchemy connections currently checked out."
)
DB_POOL_OVERFLOW = Gauge("circlespace_db_pool_overflow", "SQLAlchemy pool overflow count.")
DB_ACTIVE_CONNECTIONS = Gauge(
    "circlespace_db_active_connections", "Active connections for the current PostgreSQL database."
)
DB_WAITING_CONNECTIONS = Gauge(
    "circlespace_db_waiting_connections", "Active PostgreSQL sessions waiting on an event."
)
DB_UNGRANTED_LOCKS = Gauge(
    "circlespace_db_ungranted_locks", "PostgreSQL locks currently waiting to be granted."
)
PROCESS_CPU_SECONDS = Gauge(
    "circlespace_process_cpu_seconds", "Process user and system CPU time in seconds."
)
PROCESS_MEMORY_BYTES = Gauge(
    "circlespace_process_resident_memory_bytes", "Process resident memory in bytes."
)
PROCESS_THREADS = Gauge("circlespace_process_threads", "Process thread count.")


def _operation(statement: str) -> str:
    return statement.lstrip().split(maxsplit=1)[0].upper() if statement.strip() else "UNKNOWN"


def instrument_engine(engine: Engine) -> None:
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, _cursor, statement, _parameters, _context, _many) -> None:
        conn.info.setdefault("query_start_time", []).append(time.perf_counter())
        conn.info["query_operation"] = _operation(statement)

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, _cursor, _statement, _parameters, _context, _many) -> None:
        started = conn.info.get("query_start_time", []).pop()
        DB_QUERY_DURATION.labels(conn.info.get("query_operation", "UNKNOWN")).observe(
            time.perf_counter() - started
        )

    @event.listens_for(engine, "handle_error")
    def handle_error(exception_context) -> None:
        operation = exception_context.connection.info.get("query_operation", "UNKNOWN")
        DB_QUERY_ERRORS.labels(operation).inc()


async def observe_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_context.set(request_id)
    method = request.method
    started = time.perf_counter()
    status_code = 500
    HTTP_IN_PROGRESS.labels(method).inc()
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration = time.perf_counter() - started
        route = getattr(request.scope.get("route"), "path", "unmatched")
        HTTP_IN_PROGRESS.labels(method).dec()
        HTTP_REQUESTS.labels(method, route, str(status_code)).inc()
        HTTP_DURATION.labels(method, route).observe(duration)
        logger.info(
            "request_completed",
            extra={
                "method": method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round(duration * 1_000, 3),
            },
        )
        request_id_context.reset(token)


def metrics_response(engine: Engine) -> Response:
    pool = engine.pool
    if hasattr(pool, "size"):
        DB_POOL_SIZE.set(pool.size())
    if hasattr(pool, "checkedout"):
        DB_POOL_CHECKED_OUT.set(pool.checkedout())
    if hasattr(pool, "overflow"):
        DB_POOL_OVERFLOW.set(max(0, pool.overflow()))
    process = psutil.Process()
    cpu_times = process.cpu_times()
    PROCESS_CPU_SECONDS.set(cpu_times.user + cpu_times.system)
    PROCESS_MEMORY_BYTES.set(process.memory_info().rss)
    PROCESS_THREADS.set(process.num_threads())
    if engine.dialect.name == "postgresql":
        with engine.connect() as connection:
            DB_ACTIVE_CONNECTIONS.set(
                connection.scalar(
                    text(
                        "SELECT count(*) FROM pg_stat_activity "
                        "WHERE datname = current_database() AND state = 'active'"
                    )
                )
                or 0
            )
            DB_WAITING_CONNECTIONS.set(
                connection.scalar(
                    text(
                        "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() "
                        "AND state = 'active' AND wait_event IS NOT NULL"
                    )
                )
                or 0
            )
            DB_UNGRANTED_LOCKS.set(
                connection.scalar(text("SELECT count(*) FROM pg_locks WHERE NOT granted")) or 0
            )
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
