from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(args: list[str], cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=False, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def capture_git_provenance(cwd: Path) -> dict[str, Any]:
    status = git_value(["status", "--porcelain"], cwd)
    return {
        "git_commit": git_value(["rev-parse", "HEAD"], cwd),
        "git_dirty": None if status is None else bool(status),
    }


def build_manifest(
    repo_root: Path,
    run_id: str,
    config_path: Path,
    outputs: list[Path],
    inputs: list[Path],
    counts: dict[str, int],
    runtime_seconds: float,
    git_provenance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        **git_provenance,
        "python": sys.version,
        "platform": platform.platform(),
        "config_path": str(config_path.relative_to(repo_root)),
        "config_sha256": sha256_file(config_path),
        "runtime_seconds": runtime_seconds,
        "counts": counts,
        "input_sha256": {
            str(path.relative_to(repo_root)): sha256_file(path) for path in inputs
        },
        "output_sha256": {
            path.name: sha256_file(path) for path in outputs
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
