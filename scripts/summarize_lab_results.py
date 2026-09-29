"""Summarize one raw scaling-lab experiment directory."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def metric_value(text: str, name: str) -> float | None:
    match = re.search(rf"^{re.escape(name)}\s+(-?[0-9.eE+]+)$", text, re.MULTILINE)
    return float(match.group(1)) if match else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    samples = [
        json.loads(line)
        for line in (args.directory / "metrics.jsonl").read_text().splitlines()
    ]
    start = datetime.fromisoformat(samples[0]["timestamp"])
    end = datetime.fromisoformat(samples[-1]["timestamp"])
    duration = max((end - start).total_seconds(), 0.001)

    prometheus = [sample.get("prometheus", "") for sample in samples]
    cpu_values = [
        value
        for text_value in prometheus
        if (value := metric_value(text_value, "circlespace_process_cpu_seconds"))
        is not None
    ]
    memory_values = [
        value
        for text_value in prometheus
        if (
            value := metric_value(
                text_value, "circlespace_process_resident_memory_bytes"
            )
        )
        is not None
    ]

    def maximum(name: str) -> float:
        values = [
            value
            for text_value in prometheus
            if (value := metric_value(text_value, name)) is not None
        ]
        return max(values, default=0)

    locust_path = args.directory / "locust_summary.json"
    summary: dict[str, object] = {
        "provisional": True,
        "sample_count": len(samples),
        "sample_duration_seconds": duration,
        "host_cpu_average_percent": sum(
            sample["host_cpu_percent"] for sample in samples
        )
        / len(samples),
        "host_cpu_max_percent": max(sample["host_cpu_percent"] for sample in samples),
        "api_cpu_average_percent": (
            (cpu_values[-1] - cpu_values[0]) / duration * 100
            if len(cpu_values) > 1
            else 0
        ),
        "api_rss_max_bytes": max(memory_values, default=0),
        "postgres_rss_max_bytes": max(
            sample["postgres_rss_bytes"] for sample in samples
        ),
        "postgres_cpu_average_percent": sum(
            sample.get("postgres_cpu_percent", 0) for sample in samples
        )
        / len(samples),
        "postgres_cpu_max_percent": max(
            sample.get("postgres_cpu_percent", 0) for sample in samples
        ),
        "db_active_connections_max": maximum("circlespace_db_active_connections"),
        "db_waiting_connections_max": maximum("circlespace_db_waiting_connections"),
        "db_ungranted_locks_max": maximum("circlespace_db_ungranted_locks"),
    }
    if locust_path.exists():
        summary["locust"] = json.loads(locust_path.read_text())
    correctness_path = args.directory / "correctness.json"
    if correctness_path.exists():
        summary["correctness"] = json.loads(correctness_path.read_text())
    (args.directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
