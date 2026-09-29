import json
import logging

from fastapi.testclient import TestClient

from app.core.logging import JsonFormatter, request_id_context


def test_request_id_is_propagated(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "exp-test-request"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "exp-test-request"


def test_metrics_include_http_process_database_and_pool_signals(client: TestClient) -> None:
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "circlespace_http_requests_total" in body
    assert "circlespace_http_request_duration_seconds" in body
    assert "circlespace_db_query_duration_seconds" in body
    assert "circlespace_db_pool_checked_out" in body
    assert "circlespace_db_active_connections" in body
    assert "circlespace_db_waiting_connections" in body
    assert "circlespace_process_cpu_seconds" in body
    assert "circlespace_process_resident_memory_bytes" in body
    assert "circlespace_process_threads" in body


def test_readiness_checks_database(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "reachable"}


def test_json_formatter_includes_request_context() -> None:
    token = request_id_context.set("request-123")
    try:
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "complete", (), None)
        record.status_code = 200
        payload = json.loads(JsonFormatter().format(record))
    finally:
        request_id_context.reset(token)
    assert payload["request_id"] == "request-123"
    assert payload["status_code"] == 200
