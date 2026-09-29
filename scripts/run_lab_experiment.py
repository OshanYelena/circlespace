"""Run a headless Locust experiment while sampling application and host metrics."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import psutil
from sqlalchemy import create_engine, text


def sample_metrics(
    url: str, output: Path, stop: threading.Event, interval: float
) -> None:
    with output.open("w") as stream:
        while not stop.is_set():
            snapshot: dict[str, object] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "host_cpu_percent": psutil.cpu_percent(),
                "host_memory_percent": psutil.virtual_memory().percent,
            }
            postgres = [
                process
                for process in psutil.process_iter(["name"])
                if process.info["name"] == "postgres"
            ]
            snapshot["postgres_cpu_percent"] = sum(
                process.cpu_percent() for process in postgres if process.is_running()
            )
            snapshot["postgres_rss_bytes"] = sum(
                process.memory_info().rss
                for process in postgres
                if process.is_running()
            )
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    snapshot["prometheus"] = response.read().decode()
            except Exception as exc:  # noqa: BLE001
                snapshot["metrics_error"] = str(exc)
            stream.write(json.dumps(snapshot) + "\n")
            stream.flush()
            stop.wait(interval)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=["read-heavy", "write-heavy", "mixed", "hotspot", "sustained"],
        default="mixed",
    )
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--spawn-rate", type=float, default=2)
    parser.add_argument("--run-time", default="30s")
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    parser.add_argument("--article-min", type=int, default=1)
    parser.add_argument("--article-max", type=int, default=1_000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--database-url", default="postgresql+psycopg://localhost/circlespace_lab"
    )
    return parser.parse_args()


def correctness_snapshot(database_url: str) -> dict[str, int | bool]:
    engine = create_engine(database_url)
    with engine.connect() as connection:
        result: dict[str, int | bool] = {
            "users": connection.scalar(text("SELECT count(*) FROM users")) or 0,
            "articles": connection.scalar(text("SELECT count(*) FROM posts")) or 0,
            "likes": connection.scalar(text("SELECT count(*) FROM likes")) or 0,
            "comments": connection.scalar(text("SELECT count(*) FROM comments")) or 0,
            "negative_view_counts": connection.scalar(
                text("SELECT count(*) FROM posts WHERE view_count < 0")
            )
            or 0,
            "duplicate_likes": connection.scalar(
                text(
                    "SELECT count(*) FROM (SELECT post_id, user_id FROM likes "
                    "GROUP BY post_id, user_id HAVING count(*) > 1) duplicates"
                )
            )
            or 0,
            "orphan_comments": connection.scalar(
                text(
                    "SELECT count(*) FROM comments c LEFT JOIN posts p ON p.id = c.post_id "
                    "WHERE p.id IS NULL"
                )
            )
            or 0,
        }
    result["passed"] = all(
        result[key] == 0
        for key in ("negative_view_counts", "duplicate_likes", "orphan_comments")
    )
    return result


def main() -> int:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = vars(args).copy()
    metadata["output"] = str(args.output)
    metadata["started_at"] = datetime.now(timezone.utc).isoformat()
    (args.output / "experiment.json").write_text(
        json.dumps(metadata, indent=2, default=str) + "\n"
    )

    stop = threading.Event()
    sampler = threading.Thread(
        target=sample_metrics,
        args=(f"{args.host}/metrics", args.output / "metrics.jsonl", stop, 1.0),
        daemon=True,
    )
    sampler.start()
    environment = os.environ | {
        "LAB_PROFILE": args.profile,
        "LAB_ARTICLE_MIN": str(args.article_min),
        "LAB_ARTICLE_MAX": str(args.article_max),
        "LAB_SUMMARY_PATH": str((args.output / "locust_summary.json").resolve()),
    }
    command = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        "performance/locustfile.py",
        "--headless",
        "--host",
        args.host,
        "--users",
        str(args.users),
        "--spawn-rate",
        str(args.spawn_rate),
        "--run-time",
        args.run_time,
        "--csv",
        str(args.output / "locust"),
        "--only-summary",
    ]
    with (args.output / "locust.log").open("w") as log:
        result = subprocess.run(
            command, env=environment, stdout=log, stderr=subprocess.STDOUT, check=False
        )
    stop.set()
    sampler.join(timeout=3)
    correctness = correctness_snapshot(args.database_url)
    (args.output / "correctness.json").write_text(
        json.dumps(correctness, indent=2) + "\n"
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
