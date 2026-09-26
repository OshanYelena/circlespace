"""Fail CI when code crosses an undeclared modular-monolith boundary."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "apps" / "api" / "app" / "modules"
WEB = ROOT / "apps" / "web" / "src"

ALLOWED_DEPENDENCIES = {
    "auth": {"users"},
    "users": {"auth"},
    "friendships": {"auth", "users"},
    "posts": {"auth", "friendships", "users"},
}


def imported_module(node: ast.AST) -> str | None:
    name = node.module if isinstance(node, ast.ImportFrom) else None
    if not name or not name.startswith("app.modules."):
        return None
    parts = name.split(".")
    return parts[2] if len(parts) > 2 else None


def backend_violations() -> list[str]:
    errors: list[str] = []
    for source, allowed in ALLOWED_DEPENDENCIES.items():
        for path in (MODULES / source).rglob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                target = imported_module(node)
                if target and target != source and target not in allowed:
                    relative = path.relative_to(ROOT)
                    errors.append(f"{relative}:{node.lineno}: {source} may not import {target}")
    return errors


def frontend_violations() -> list[str]:
    errors: list[str] = []
    api_client = WEB / "lib" / "api.ts"
    for path in WEB.rglob("*.ts*"):
        if path == api_client or path.name.endswith(".test.ts"):
            continue
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            if "fetch(" in line:
                relative = path.relative_to(ROOT)
                errors.append(f"{relative}:{line_number}: HTTP calls belong in src/lib/api.ts")
    return errors


def main() -> int:
    errors = backend_violations() + frontend_violations()
    if errors:
        print("Architecture boundary violations:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Architecture boundaries are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
