from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import shutil
import tempfile
import time
import uuid
from pathlib import Path

from .analysis import summarize
from .design import build_cells, build_contexts, build_personas, load_config
from .provenance import build_manifest, capture_git_provenance, write_json, write_jsonl
from .simulation import run_cells
from .validation import validate_records

APPROVED_OUTPUT_ROOTS = ("runs", "tmp", "artifacts", "data/interim", "data/processed")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def confined_path(root: Path, relative: str, label: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"{label} must be relative to the repository")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes the repository") from exc
    return resolved


def approved_output_path(root: Path, relative: str) -> Path:
    resolved = confined_path(root, relative, "outputs.root")
    approved = [confined_path(root, path, "approved output root") for path in APPROVED_OUTPUT_ROOTS]
    if not any(resolved == base or resolved.is_relative_to(base) for base in approved):
        raise ValueError(f"outputs.root must be under one of {APPROVED_OUTPUT_ROOTS}")
    return resolved


def research_inputs(root: Path, config: dict, config_path: Path) -> list[Path]:
    inputs = [
        config_path,
        root / "data/raw/manifest.json",
        root / "prompts/persona_compiler_v1.txt",
        root / "schemas/persona.schema.json",
        root / "schemas/response.schema.json",
    ]
    for prompt_variant in config["design"]["prompt_variants"]:
        inputs.append(root / "prompts" / f"{prompt_variant}.txt")
    missing = [path for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing research inputs: {[str(path) for path in missing]}")
    return inputs


def reproduce(config_arg: str) -> Path:
    root = repo_root().resolve()
    started = time.perf_counter()
    config_path = confined_path(root, config_arg, "config path")
    config = load_config(config_path)
    output_root = approved_output_path(root, config["outputs"]["root"])
    inputs = research_inputs(root, config, config_path)
    git_provenance = capture_git_provenance(root)
    personas = build_personas(config)
    contexts = build_contexts(config)
    cells = build_cells(config, personas, contexts)
    responses = run_cells(
        config["runner"]["engine"], cells, personas, config["study"]["seed"]
    )
    validate_records(personas, root / "schemas/persona.schema.json")
    validate_records(responses, root / "schemas/response.schema.json")
    summary = summarize(cells, responses)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()[:10]
    run_id = f"{config['study']['id']}-{config_hash}-{stamp}-{uuid.uuid4().hex[:8]}"
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = output_root / run_id
    temporary_dir = Path(tempfile.mkdtemp(prefix=".incomplete-", dir=output_root))

    paths = {
        "personas": temporary_dir / "personas.jsonl",
        "contexts": temporary_dir / "contexts.jsonl",
        "cells": temporary_dir / "cells.jsonl",
        "responses": temporary_dir / "responses.jsonl",
        "summary": temporary_dir / "summary.json",
    }
    try:
        write_jsonl(paths["personas"], personas)
        write_jsonl(paths["contexts"], contexts)
        write_jsonl(paths["cells"], cells)
        write_jsonl(paths["responses"], responses)
        write_json(paths["summary"], summary)

        manifest = build_manifest(
            root,
            run_id,
            config_path,
            list(paths.values()),
            inputs,
            {"personas": len(personas), "contexts": len(contexts), "cells": len(cells)},
            round(time.perf_counter() - started, 6),
            git_provenance,
        )
        write_json(temporary_dir / "manifest.json", manifest)
        temporary_dir.rename(run_dir)
    except Exception:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise
    return run_dir


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="agentic_ads")
    subparsers = result.add_subparsers(dest="command", required=True)
    reproduce_parser = subparsers.add_parser("reproduce")
    reproduce_parser.add_argument("--config", required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "reproduce":
        run_dir = reproduce(args.config)
        print(run_dir)
        return 0
    raise AssertionError("unreachable")
