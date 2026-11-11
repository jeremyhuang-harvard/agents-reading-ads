"""Load and validate the demo case configuration."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "config" / "demo_cases.json"
DERIVED_DIR = ROOT / "data" / "derived" / "demo"
OUTPUT_DIR = ROOT / "output" / "demo"

REQUIRED_CASE_KEYS = {"case_id", "label", "event_date", "role", "relationship", "identification", "focal"}
ROLES = {"primary", "benchmark"}


def load_cases(path: Path = CONFIG_PATH, only: list[str] | None = None) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data["cases"]
    seen: set[str] = set()
    for case in cases:
        missing = REQUIRED_CASE_KEYS - case.keys()
        if missing:
            raise ValueError(f"{case.get('case_id')}: missing keys {sorted(missing)}")
        if case["case_id"] in seen:
            raise ValueError(f"duplicate case_id {case['case_id']}")
        if case["role"] not in ROLES:
            raise ValueError(f"{case['case_id']}: role must be one of {sorted(ROLES)}")
        seen.add(case["case_id"])
        for level, patterns in case["identification"].items():
            for pattern in patterns:
                re.compile(pattern)
    if only:
        unknown = set(only) - seen
        if unknown:
            raise ValueError(f"unknown case ids: {sorted(unknown)}")
        cases = [case for case in cases if case["case_id"] in only]
    return cases


def ensure_dirs() -> None:
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
