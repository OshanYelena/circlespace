import json
import os
import random
from pathlib import Path

from locust import HttpUser, between, events, task

PROFILE = os.getenv("LAB_PROFILE", "mixed")
ARTICLE_MIN = int(os.getenv("LAB_ARTICLE_MIN", "1"))
ARTICLE_MAX = int(os.getenv("LAB_ARTICLE_MAX", "1000"))
USERNAME = os.getenv("LAB_USERNAME", "lab_user_0000000")
PASSWORD = os.getenv("LAB_PASSWORD", "lab-password")
SUMMARY_PATH = os.getenv("LAB_SUMMARY_PATH")

PROFILE_MIX = {
    "read-heavy": (95, 3, 2),
    "write-heavy": (40, 35, 25),
    "mixed": (70, 20, 10),
    "hotspot": (95, 3, 2),
    "sustained": (70, 20, 10),
}


@events.quitting.add_listener
def write_final_summary(environment, **_kwargs) -> None:
    if not SUMMARY_PATH:
        return
    stats = environment.stats.total
    summary = {
        "requests": stats.num_requests,
        "failures": stats.num_failures,
        "failure_ratio": stats.fail_ratio,
        "average_ms": stats.avg_response_time,
        "median_ms": stats.median_response_time,
        "p95_ms": stats.get_response_time_percentile(0.95),
        "p99_ms": stats.get_response_time_percentile(0.99),
        "requests_per_second": stats.total_rps,
    }
    Path(SUMMARY_PATH).write_text(json.dumps(summary, indent=2) + "\n")


class LabUser(HttpUser):
    wait_time = between(0.01, 0.1)
    token: str | None = None

    def on_start(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"login": USERNAME, "password": PASSWORD},
            name="POST /auth/login [setup]",
        )
        if response.ok:
            self.token = response.json()["access_token"]

    def article_id(self) -> int:
        if PROFILE == "hotspot":
            hot_max = max(ARTICLE_MIN, ARTICLE_MIN + (ARTICLE_MAX - ARTICLE_MIN) // 100)
            return random.randint(ARTICLE_MIN, hot_max)
        return random.randint(ARTICLE_MIN, ARTICLE_MAX)

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task
    def workload(self) -> None:
        read_weight, interaction_weight, creation_weight = PROFILE_MIX[PROFILE]
        draw = random.randrange(100)
        article_id = self.article_id()
        if draw < read_weight:
            if random.random() < 0.8:
                self.client.get(
                    f"/api/v1/articles/{article_id}", name="GET /articles/{id}"
                )
            else:
                self.client.get("/api/v1/feed?limit=20", name="GET /feed")
        elif draw < read_weight + interaction_weight:
            if random.random() < 0.7:
                self.client.post(
                    f"/api/v1/articles/{article_id}/view",
                    name="POST /articles/{id}/view",
                )
            else:
                self.client.post(
                    f"/api/v1/articles/{article_id}/like",
                    headers=self.headers,
                    name="POST /articles/{id}/like",
                )
        elif creation_weight:
            self.client.post(
                f"/api/v1/articles/{article_id}/comments",
                headers=self.headers,
                json={"content": "Deterministic load-test comment."},
                name="POST /articles/{id}/comments",
            )
