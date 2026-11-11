#!/usr/bin/env python3
"""Run blinded GABRIEL coding on the image arm of the Snap validation sample."""

from __future__ import annotations

import argparse
import asyncio
import base64
import csv
import hashlib
import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import gabriel
import pandas as pd

from run_gabriel_salience_poc import make_hermes_response_fn


def load_run_snapshots(
    packet_manifest: Path, codebook: Path
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    """Read and parse runner inputs from one immutable byte snapshot each."""
    manifest_bytes = packet_manifest.read_bytes()
    codebook_bytes = codebook.read_bytes()
    return (
        json.loads(manifest_bytes),
        json.loads(codebook_bytes),
        manifest_bytes,
        codebook_bytes,
    )


def build_coding_prompt(fields: list[dict[str, Any]]) -> str:
    _validate_codebook_fields(fields)
    field_text = []
    for field in fields:
        definition = {
            "field": field["name"],
            "type": field["type"],
            "definition": field["definition"],
        }
        if field.get("anchors"):
            definition["anchors"] = field["anchors"]
        field_text.append(definition)
    return f"""
You are coding one advertisement for a blinded measurement-validation study.
Use only the supplied creative. Do not infer delivery, audience, geography,
brand reputation, campaign goals, or causal effects.

VALUE RULES:
- Boolean values must be true, false, or null.
- Ratings must be integers from 0 through 100 or null.
- Zero means observable absence, not missingness.
- Use null only when the field cannot be observed; then provide unknown_reason.
- Positive booleans and ratings at or above 80 require concise visual evidence.
- For gambling-specific ratings in a non-gambling creative, use zero when absence
  is observable rather than null.

FIELDS:
{json.dumps(field_text, ensure_ascii=False, indent=2)}

Return JSON only with exactly this structure:
{{
  "annotations": [
    {{
      "field": "one exact field name above",
      "value": true,
      "evidence": "concise visible evidence or empty string",
      "unknown_reason": null
    }}
  ],
  "overall_notes": "brief ambiguity or quality note"
}}
Return exactly one annotation for every field, in the supplied order. Do not add fields.
""".strip()


def build_analysis_frame(
    manifest_path: Path,
    prompt: str,
    *,
    expected_count: int = 30,
    manifest: dict[str, Any] | None = None,
) -> pd.DataFrame:
    manifest_data = (
        json.loads(manifest_path.read_bytes()) if manifest is None else manifest
    )
    rows: list[dict[str, str]] = []
    coding_ids: set[str] = set()
    media_hashes: set[str] = set()
    try:
        packet_fd = os.open(
            manifest_path.parent,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
    except OSError as exc:
        raise FileNotFoundError(f"packet directory is unavailable: {manifest_path.parent}") from exc
    try:
        for item in manifest_data.get("media", []):
            media_file = str(item.get("media_file") or "")
            relative_path = Path(media_file)
            if (
                not media_file
                or relative_path.is_absolute()
                or ".." in relative_path.parts
            ):
                raise ValueError(f"packet media_file must be relative: {media_file!r}")
            if relative_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            coding_id = str(item.get("coding_id") or "")
            if not coding_id:
                raise ValueError("image creative is missing coding_id")
            if coding_id in coding_ids:
                raise ValueError(f"duplicate coding_id: {coding_id}")
            media_bytes = _read_regular_file_at(packet_fd, relative_path)
            actual_sha256 = hashlib.sha256(media_bytes).hexdigest()
            expected_sha256 = str(item.get("media_sha256") or "").lower()
            if actual_sha256 != expected_sha256:
                raise ValueError(f"checksum mismatch for {coding_id}")
            if actual_sha256 in media_hashes:
                raise ValueError(f"duplicate media hash: {actual_sha256}")
            coding_ids.add(coding_id)
            media_hashes.add(actual_sha256)
            rows.append(
                {
                    "coding_id": coding_id,
                    "image_data": base64.b64encode(media_bytes).decode("ascii"),
                    "media_sha256": actual_sha256,
                    "prompt": prompt,
                }
            )
    finally:
        os.close(packet_fd)
    if len(rows) != expected_count:
        raise ValueError(f"expected {expected_count} image creatives, found {len(rows)}")
    return pd.DataFrame(rows).sort_values("coding_id").reset_index(drop=True)


def validate_and_flatten(
    per_ad: pd.DataFrame,
    fields: list[dict[str, Any]],
    expected_coding_ids: list[str],
) -> list[dict[str, Any]]:
    _validate_codebook_fields(fields)
    _validate_result_identity(per_ad, expected_coding_ids)
    expected_names = [field["name"] for field in fields]
    field_types = {field["name"]: field["type"] for field in fields}
    rows: list[dict[str, Any]] = []
    for _, source_row in per_ad.iterrows():
        parsed = source_row.get("Response JSON")
        if isinstance(parsed, list):
            if len(parsed) != 1 or not isinstance(parsed[0], dict):
                raise ValueError(
                    f"expected single-object response wrapper for {source_row['coding_id']}"
                )
            parsed = parsed[0]
        if not isinstance(parsed, dict):
            raise ValueError(f"unparsed GABRIEL response for {source_row['coding_id']}")
        expected_response_keys = {"annotations", "overall_notes"}
        if set(parsed) != expected_response_keys:
            raise ValueError(
                f"response keys for {source_row['coding_id']} must be exactly "
                f"{sorted(expected_response_keys)}"
            )
        overall_notes = parsed["overall_notes"]
        if not isinstance(overall_notes, str):
            raise ValueError(
                f"overall_notes must be a string for {source_row['coding_id']}"
            )
        annotations = parsed.get("annotations")
        if not isinstance(annotations, list):
            raise ValueError(f"missing annotations for {source_row['coding_id']}")
        if len(annotations) != len(expected_names) or not all(
            isinstance(item, dict) for item in annotations
        ):
            raise ValueError(
                f"expected exactly one annotation per field for {source_row['coding_id']}"
            )
        found_names = [str(item.get("field")) for item in annotations]
        if found_names != expected_names:
            raise ValueError(
                f"field mismatch for {source_row['coding_id']}: "
                f"expected {expected_names}, found {found_names}"
            )
        row: dict[str, Any] = {"coding_id": source_row["coding_id"]}
        for name, annotation in zip(expected_names, annotations, strict=True):
            unexpected_annotation_keys = sorted(
                set(annotation) - {"field", "value", "evidence", "unknown_reason"}
            )
            if unexpected_annotation_keys:
                raise ValueError(
                    f"unexpected annotation keys for {name}: "
                    f"{unexpected_annotation_keys}"
                )
            for required_key in ("value", "evidence", "unknown_reason"):
                if required_key not in annotation:
                    raise ValueError(f"{name} is missing required {required_key} key")
            value = annotation.get("value")
            _validate_value(name, field_types[name], value)
            evidence = annotation["evidence"]
            unknown_reason = annotation["unknown_reason"]
            if not isinstance(evidence, str):
                raise ValueError(f"{name} evidence must be a string")
            if unknown_reason is not None and not isinstance(unknown_reason, str):
                raise ValueError(f"{name} unknown_reason must be a string or null")
            evidence_text = evidence.strip()
            unknown_text = (unknown_reason or "").strip()
            requires_evidence = (field_types[name] == "boolean" and value is True) or (
                field_types[name] == "rating_0_100"
                and isinstance(value, int)
                and not isinstance(value, bool)
                and value >= 80
            )
            if requires_evidence and not evidence_text:
                raise ValueError(f"{name} requires nonempty evidence")
            if value is None and not unknown_text:
                raise ValueError(f"{name} requires nonempty unknown_reason")
            if value is not None and unknown_text:
                raise ValueError(f"{name} unknown_reason must be empty for non-null value")
            row[name] = value
            row[f"{name}__evidence"] = evidence
            row[f"{name}__unknown_reason"] = unknown_reason
        row["overall_notes"] = overall_notes
        rows.append(row)
    return rows


def _validate_codebook_fields(fields: list[dict[str, Any]]) -> None:
    supported_types = {"boolean", "rating_0_100"}
    reserved_columns = {
        "coding_id",
        "media_file",
        "media_type",
        "coder_id",
        "observable",
        "coder_notes",
        "completed_at_utc",
        "overall_notes",
    }
    names: set[str] = set()
    expanded_columns: set[str] = set()
    for field in fields:
        name = field.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("codebook field name must be a nonempty string")
        if name in names:
            raise ValueError(f"duplicate codebook field name: {name!r}")
        names.add(name)
        field_columns = {name, f"{name}__evidence", f"{name}__unknown_reason"}
        reserved_collision = sorted(field_columns & reserved_columns)
        if reserved_collision:
            raise ValueError(
                f"codebook field collides with reserved output column: {reserved_collision[0]!r}"
            )
        generated_collision = sorted(field_columns & expanded_columns)
        if generated_collision:
            raise ValueError(
                f"codebook output column collision: {generated_collision[0]!r}"
            )
        expanded_columns.update(field_columns)
        field_type = str(field.get("type") or "")
        if field_type not in supported_types:
            raise ValueError(f"unsupported codebook field type: {field_type!r}")


def _validate_result_identity(
    per_ad: pd.DataFrame, expected_coding_ids: list[str]
) -> None:
    if any(not isinstance(coding_id, str) or not coding_id.strip() for coding_id in expected_coding_ids):
        raise ValueError("expected coding_id values must be nonempty strings")
    expected_set = set(expected_coding_ids)
    if len(expected_set) != len(expected_coding_ids):
        raise ValueError("expected coding_id values must be unique")
    if "coding_id" not in per_ad.columns:
        raise ValueError("GABRIEL results are missing coding_id")

    returned_ids = per_ad["coding_id"].tolist()
    if any(not isinstance(coding_id, str) or not coding_id.strip() for coding_id in returned_ids):
        raise ValueError("returned coding_id values must be nonempty strings")
    returned_set = set(returned_ids)
    if len(returned_set) != len(returned_ids):
        raise ValueError("duplicate coding_id in GABRIEL results")
    if len(returned_ids) != len(expected_coding_ids):
        raise ValueError(
            "GABRIEL result row count does not match analysis frame: "
            f"expected {len(expected_coding_ids)}, found {len(returned_ids)}"
        )
    if returned_set != expected_set:
        missing = sorted(expected_set - returned_set)
        unexpected = sorted(returned_set - expected_set)
        raise ValueError(
            f"GABRIEL result coding_id mismatch: missing {missing}, unexpected {unexpected}"
        )


def _validate_value(name: str, field_type: str, value: Any) -> None:
    if value is None:
        return
    if field_type == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{name} must be boolean or null")
    if field_type == "rating_0_100":
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise ValueError(f"{name} must be an integer from 0 through 100 or null")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("no model coding rows to write")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _read_regular_file_at(root_fd: int, relative_path: Path) -> bytes:
    opened_fds: list[int] = []
    try:
        parent_fd = root_fd
        for component in relative_path.parts[:-1]:
            parent_fd = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent_fd,
            )
            opened_fds.append(parent_fd)
        file_fd = os.open(
            relative_path.name,
            os.O_RDONLY | os.O_NOFOLLOW,
            dir_fd=parent_fd,
        )
        with os.fdopen(file_fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise FileNotFoundError(f"packet media is not a regular file: {relative_path}")
            return handle.read()
    except OSError as exc:
        raise FileNotFoundError(f"missing packet media: {relative_path}") from exc
    finally:
        for descriptor in reversed(opened_fds):
            os.close(descriptor)


def build_run_fingerprint(
    *,
    packet_manifest: Path,
    codebook: Path,
    prompt: str,
    provider: str,
    model: str,
    media_hashes: list[tuple[str, str]],
    packet_manifest_bytes: bytes | None = None,
    codebook_bytes: bytes | None = None,
) -> dict[str, Any]:
    if packet_manifest_bytes is None:
        packet_manifest_bytes = packet_manifest.read_bytes()
    if codebook_bytes is None:
        codebook_bytes = codebook.read_bytes()
    components: dict[str, Any] = {
        "packet_manifest_sha256": hashlib.sha256(packet_manifest_bytes).hexdigest(),
        "actual_media_sha256": [
            {"coding_id": coding_id, "sha256": sha256}
            for coding_id, sha256 in sorted(media_hashes)
        ],
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "codebook_sha256": hashlib.sha256(codebook_bytes).hexdigest(),
        "provider": provider,
        "model": model,
    }
    canonical = json.dumps(
        components, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {"fingerprint": hashlib.sha256(canonical).hexdigest(), **components}


def prepare_output_directory(
    output_dir: Path,
    pre_run_manifest: dict[str, Any],
    *,
    reset: bool,
) -> Path:
    if reset and output_dir.exists():
        shutil.rmtree(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"output directory is nonempty; use --reset: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "pre_run_manifest.json"
    manifest_path.write_text(
        json.dumps(pre_run_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    run_dir = output_dir / str(pre_run_manifest["fingerprint"])
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


async def run(args: argparse.Namespace) -> None:
    manifest, codebook, manifest_bytes, codebook_bytes = load_run_snapshots(
        args.packet_manifest, args.codebook
    )
    fields = codebook["fields"]
    prompt = build_coding_prompt(fields)
    frame = build_analysis_frame(
        args.packet_manifest,
        prompt,
        expected_count=args.expected_count,
        manifest=manifest,
    )
    pre_run_manifest = build_run_fingerprint(
        packet_manifest=args.packet_manifest,
        codebook=args.codebook,
        prompt=prompt,
        provider=args.provider,
        model=args.model,
        media_hashes=list(zip(frame["coding_id"], frame["media_sha256"], strict=True)),
        packet_manifest_bytes=manifest_bytes,
        codebook_bytes=codebook_bytes,
    )
    run_dir = prepare_output_directory(
        args.output_dir, pre_run_manifest, reset=args.reset
    )
    response_fn = make_hermes_response_fn(args.provider, args.model)
    per_ad = await gabriel.whatever(
        df=frame,
        column_name="prompt",
        identifier_column="coding_id",
        image_column="image_data",
        save_dir=str(run_dir / "raw"),
        file_name="image_arm_responses.csv",
        model=args.model,
        json_mode=True,
        n_parallels=args.parallelism,
        reset_files=True,
        response_fn=response_fn,
        return_original_columns=True,
        image_detail="high",
    )
    rows = validate_and_flatten(per_ad, fields, frame["coding_id"].tolist())
    _write_csv(run_dir / "model_codes.csv", rows)
    run_manifest = {
        **pre_run_manifest,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "arm": "image_only",
        "ads_coded": len(rows),
        "provider": args.provider,
        "model": args.model,
        "parallelism": args.parallelism,
        "limitations": [
            "This run includes still-image creatives only.",
            "Agreement with humans is not yet computed.",
            "Model outputs are measurements, not exposure or causal effects.",
        ],
    }
    (run_dir / "run_manifest.json").write_text(
        json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(run_manifest, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-manifest", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--provider", default="openai-codex")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--parallelism", type=int, default=2)
    parser.add_argument("--expected-count", type=int, default=30)
    parser.add_argument("--reset", action="store_true")
    return parser.parse_args()


def main() -> None:
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
