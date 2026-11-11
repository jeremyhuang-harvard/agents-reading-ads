from __future__ import annotations

import hashlib
import itertools
import json
import re
import tomllib
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = {"study", "design", "runner", "outputs"}
REQUIRED_DESIGN_LISTS = {
    "preferences",
    "histories",
    "price_contexts",
    "quality_contexts",
    "prompt_variants",
    "models",
}
ALLOWED_LEVELS = {
    "preferences": {"price_first", "performance_first"},
    "histories": {"budget_pressure", "product_failure"},
    "price_contexts": {"near_benchmark", "favorable_contrast"},
    "quality_contexts": {"near_benchmark", "favorable_contrast"},
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_id(prefix: str, value: Any, length: int = 16) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"


def load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        config = tomllib.load(handle)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    missing = REQUIRED_SECTIONS - config.keys()
    if missing:
        raise ValueError(f"missing config sections: {sorted(missing)}")
    design = config["design"]
    missing_lists = REQUIRED_DESIGN_LISTS - design.keys()
    if missing_lists:
        raise ValueError(f"missing design fields: {sorted(missing_lists)}")
    for field in REQUIRED_DESIGN_LISTS:
        values = design[field]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise ValueError(f"design.{field} must be a nonempty list of unique values")
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError(f"design.{field} values must be nonempty strings")
    if not all(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value)
        for value in design["prompt_variants"]
    ):
        raise ValueError("design.prompt_variants must contain safe identifiers")
    for field, allowed in ALLOWED_LEVELS.items():
        unsupported = set(design[field]) - allowed
        if unsupported:
            raise ValueError(f"unsupported design.{field} values: {sorted(unsupported)}")
    replicates = config["study"].get("persona_replicates")
    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 1:
        raise ValueError("study.persona_replicates must be a positive integer")
    seed = config["study"].get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("study.seed must be an integer")
    study_id = config["study"].get("id")
    if not isinstance(study_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", study_id):
        raise ValueError("study.id must be a safe identifier containing only letters, numbers, '.', '_', or '-'")
    ad_id = config["study"].get("ad_id")
    if not isinstance(ad_id, str) or not ad_id.strip():
        raise ValueError("study.ad_id must be a nonempty string")
    output_root = config["outputs"].get("root")
    if not isinstance(output_root, str) or not output_root.strip():
        raise ValueError("outputs.root must be a nonempty relative path")
    if config["runner"].get("engine") not in {"mock", "unconfigured"}:
        raise ValueError("runner.engine must be mock or unconfigured")


def build_personas(config: dict[str, Any]) -> list[dict[str, Any]]:
    study = config["study"]
    design = config["design"]
    personas: list[dict[str, Any]] = []
    for preference, history, replicate in itertools.product(
        design["preferences"],
        design["histories"],
        range(1, study["persona_replicates"] + 1),
    ):
        core = {"preference": preference, "history": history, "replicate": replicate}
        personas.append(
            {
                "persona_id": stable_id("persona", core),
                **core,
                "profile_text": (
                    f"This profile prioritizes {preference.replace('_', ' ')} and has a recent "
                    f"history of {history.replace('_', ' ')}. No demographic traits are assigned."
                ),
            }
        )
    assert_unique(personas, "persona_id")
    return personas


def build_contexts(config: dict[str, Any]) -> list[dict[str, Any]]:
    design = config["design"]
    contexts: list[dict[str, Any]] = []
    for price_context, quality_context in itertools.product(
        design["price_contexts"], design["quality_contexts"]
    ):
        core = {"price_context": price_context, "quality_context": quality_context}
        contexts.append({"context_id": stable_id("context", core), **core})
    assert_unique(contexts, "context_id")
    return contexts


def build_cells(
    config: dict[str, Any],
    personas: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for persona, context, prompt_variant, model in itertools.product(
        personas,
        contexts,
        config["design"]["prompt_variants"],
        config["design"]["models"],
    ):
        core = {
            "study_id": config["study"]["id"],
            "ad_id": config["study"]["ad_id"],
            "persona_id": persona["persona_id"],
            "context_id": context["context_id"],
            "prompt_variant": prompt_variant,
            "model": model,
        }
        cells.append({"cell_id": stable_id("cell", core), **core, **context})
    assert_unique(cells, "cell_id")
    return cells


def assert_unique(records: list[dict[str, Any]], key: str) -> None:
    values = [record[key] for record in records]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {key} values")
