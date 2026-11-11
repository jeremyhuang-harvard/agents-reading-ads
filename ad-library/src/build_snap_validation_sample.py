#!/usr/bin/env python3
"""Build a blinded, stratified validation sample from a Snap corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import shutil
import stat
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return _parse_jsonl(path.read_bytes())


def load_input_snapshots(
    records_path: Path,
    spec_path: Path,
    codebook_path: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, str],
]:
    """Read, hash, and parse every builder input from one byte snapshot each."""
    records_bytes = records_path.read_bytes()
    spec_bytes = spec_path.read_bytes()
    codebook_bytes = codebook_path.read_bytes()
    return (
        _parse_jsonl(records_bytes),
        json.loads(spec_bytes),
        json.loads(codebook_bytes),
        {
            "source_records_sha256": hashlib.sha256(records_bytes).hexdigest(),
            "sampling_spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
            "codebook_sha256": hashlib.sha256(codebook_bytes).hexdigest(),
        },
    )


def _parse_jsonl(payload: bytes) -> list[dict[str, Any]]:
    return [json.loads(line) for line in payload.splitlines() if line.strip()]


def build_creatives(
    records: Iterable[dict[str, Any]], run_dir: Path
) -> list[dict[str, Any]]:
    """Collapse campaign records to unique creative hashes."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_paths: dict[int, str] = {}
    for record in records:
        media = record.get("media") or {}
        sha256 = str(media.get("sha256") or "").strip()
        local_path = str(media.get("local_path") or "").strip()
        content_type = str(media.get("content_type") or "").lower()
        if not sha256 or not local_path or not (
            content_type.startswith("image/") or content_type.startswith("video/")
        ):
            continue
        source_paths[id(record)] = _validate_relative_media_path(local_path).as_posix()
        grouped[sha256].append(record)

    creatives: list[dict[str, Any]] = []
    for sha256, members in sorted(grouped.items()):
        cell_exposure: dict[tuple[str, str, str], int] = defaultdict(int)
        for member in members:
            media = member.get("media") or {}
            media_kind = _media_kind(str(media.get("content_type") or ""))
            key = (
                str(member.get("category") or "unknown"),
                str(member.get("query_country") or "unknown").lower(),
                media_kind,
            )
            cell_exposure[key] += _impressions(member)
        assigned_cell = min(
            cell_exposure,
            key=lambda key: (-cell_exposure[key], key),
        )
        eligible = [
            member
            for member in members
            if (
                str(member.get("category") or "unknown"),
                str(member.get("query_country") or "unknown").lower(),
                _media_kind(str((member.get("media") or {}).get("content_type") or "")),
            )
            == assigned_cell
        ]
        representative = min(
            eligible,
            key=lambda member: (-_impressions(member), str(member.get("ad_id") or "")),
        )
        media = representative.get("media") or {}
        ad = representative.get("ad") or {}
        languages = sorted(
            {
                str(language)
                for member in eligible
                for language in ((member.get("ad") or {}).get("languages") or [])
                if language
            }
        )
        creatives.append(
            {
                "media_sha256": sha256,
                "source_media_path": source_paths[id(representative)],
                "content_type": str(media.get("content_type") or ""),
                "media_kind": assigned_cell[2],
                "category": assigned_cell[0],
                "country": assigned_cell[1],
                "representative_ad_id": str(representative.get("ad_id") or ""),
                "advertiser": str(representative.get("query_advertiser") or ""),
                "headline": str(ad.get("headline") or ""),
                "languages": languages,
                "start_date": str(ad.get("start_date") or ""),
                "status": str(ad.get("status") or ""),
                "total_impressions": sum(_impressions(member) for member in eligible),
                "reuse_count": len(members),
            }
        )
    return creatives


def select_creatives(
    creatives: list[dict[str, Any]],
    cells: list[dict[str, Any]],
    *,
    seed: int,
) -> list[dict[str, Any]]:
    """Select one creative from each exposure bin inside every quota cell."""
    randomizer = random.Random(seed)
    selected: list[dict[str, Any]] = []
    used_hashes: set[str] = set()

    for cell in cells:
        quota = int(cell["quota"])
        candidates = [
            creative
            for creative in creatives
            if creative["category"] == cell["category"]
            and creative["country"] == cell["country"]
            and creative["media_kind"] == cell["media_kind"]
            and creative["media_sha256"] not in used_hashes
        ]
        candidates.sort(
            key=lambda creative: (
                int(creative["total_impressions"]),
                creative["media_sha256"],
            )
        )
        if len(candidates) < quota:
            raise ValueError(
                "insufficient creatives for cell "
                f"{cell['category']}/{cell['country']}/{cell['media_kind']}: "
                f"need {quota}, found {len(candidates)}"
            )

        for bin_index in range(quota):
            start = bin_index * len(candidates) // quota
            end = (bin_index + 1) * len(candidates) // quota
            bucket = candidates[start:end]
            chosen = dict(randomizer.choice(bucket))
            chosen["exposure_bin"] = bin_index + 1
            chosen["cell_quota"] = quota
            selected.append(chosen)
            used_hashes.add(chosen["media_sha256"])

    return selected


def validate_source_run_id(records_path: Path, spec: dict[str, Any]) -> str:
    parent_name = records_path.parent.name
    if not parent_name.startswith("run_id="):
        raise ValueError(f"records parent must be named run_id=<id>: {records_path.parent}")
    records_run_id = parent_name.removeprefix("run_id=")
    spec_run_id = str(spec.get("source_run_id") or "")
    if not spec_run_id or spec_run_id != records_run_id:
        raise ValueError(
            f"spec source_run_id {spec_run_id!r} does not match records parent run_id "
            f"{records_run_id!r}"
        )
    return records_run_id


def write_coding_packet(
    selected: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    output_dir: Path,
    *,
    source_run_dir: Path,
    seed: int,
    provenance: dict[str, Any],
) -> None:
    """Atomically write blinded coding materials plus a separate linkage key."""
    _validate_blinded_fields(fields)
    _validate_provenance(provenance, coding_order_seed=seed)
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_dir = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent)
    )
    try:
        _write_coding_packet_contents(
            selected,
            fields,
            temporary_dir,
            source_run_dir=source_run_dir,
            seed=seed,
            provenance=provenance,
        )
        temporary_dir.rename(output_dir)
    except BaseException:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise


def _write_coding_packet_contents(
    selected: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    output_dir: Path,
    *,
    source_run_dir: Path,
    seed: int,
    provenance: dict[str, Any],
) -> None:
    media_dir = output_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    ordered = [dict(item) for item in selected]
    random.Random(seed).shuffle(ordered)
    coding_rows: list[dict[str, Any]] = []
    linkage_rows: list[dict[str, Any]] = []

    root_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        source_run_fd = os.open(source_run_dir, root_flags)
    except OSError as exc:
        raise FileNotFoundError(f"source run directory is unavailable: {source_run_dir}") from exc
    try:
        for index, creative in enumerate(ordered, start=1):
            coding_id = f"SCV-{index:03d}"
            source = _validate_relative_media_path(str(creative["source_media_path"]))
            suffix = source.suffix.lower() or _suffix_for_content_type(creative["content_type"])
            relative_media = Path("media") / f"{coding_id}{suffix}"
            destination = output_dir / relative_media
            _copy_verified_media(
                source_run_fd,
                source,
                destination,
                expected_sha256=creative["media_sha256"],
                coding_id=coding_id,
            )

            coding_row: dict[str, Any] = {
                "coding_id": coding_id,
                "media_file": relative_media.as_posix(),
                "media_type": creative["media_kind"],
                "coder_id": "",
                "observable": "",
            }
            for field in fields:
                coding_row[field["name"]] = ""
                coding_row[f"{field['name']}__evidence"] = ""
                coding_row[f"{field['name']}__unknown_reason"] = ""
            coding_row["coder_notes"] = ""
            coding_row["completed_at_utc"] = ""
            coding_rows.append(coding_row)

            linkage_rows.append(
                {
                    "coding_id": coding_id,
                    "representative_ad_id": creative["representative_ad_id"],
                    "media_sha256": creative["media_sha256"],
                    "category": creative["category"],
                    "country": creative["country"],
                    "advertiser": creative["advertiser"],
                    "headline": creative["headline"],
                    "languages": "|".join(creative["languages"]),
                    "content_type": creative["content_type"],
                    "total_impressions": creative["total_impressions"],
                    "reuse_count": creative["reuse_count"],
                    "exposure_bin": creative["exposure_bin"],
                    "start_date": creative["start_date"],
                    "status": creative["status"],
                }
            )
    finally:
        os.close(source_run_fd)

    _write_csv(output_dir / "coding_sheet.csv", coding_rows)
    _write_csv(output_dir / "linkage_key.csv", linkage_rows)
    (output_dir / "coding_instructions.md").write_text(
        _coding_instructions(fields), encoding="utf-8"
    )
    manifest = {
        "sample_size": len(ordered),
        "seed": seed,
        "unique_media_hashes": len({item["media_sha256"] for item in ordered}),
        "fields": fields,
        "provenance": {
            **provenance,
            "selected_media_sha256": [
                {"coding_id": row["coding_id"], "sha256": row["media_sha256"]}
                for row in linkage_rows
            ],
        },
        "files": {
            "blinded_coding_sheet": "coding_sheet.csv",
            "restricted_linkage_key": "linkage_key.csv",
            "instructions": "coding_instructions.md",
            "media_directory": "media",
        },
        "media": [
            {
                "coding_id": row["coding_id"],
                "media_file": coding_rows[index]["media_file"],
                "media_sha256": row["media_sha256"],
            }
            for index, row in enumerate(linkage_rows)
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _validate_blinded_fields(fields: list[dict[str, Any]]) -> None:
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
    denylist = (
        "category",
        "advertiser",
        "country",
        "headline",
        "language",
        "hash",
        "sha",
        "exposure",
        "impression",
        "source_id",
        "source_run",
        "representative_ad_id",
        "ad_id",
    )
    names: set[str] = set()
    expanded_columns: set[str] = set()
    for field in fields:
        raw_name = field.get("name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ValueError("codebook field name must be a nonempty string")
        if raw_name in names:
            raise ValueError(f"duplicate codebook field name: {raw_name!r}")
        names.add(raw_name)
        field_columns = {
            raw_name,
            f"{raw_name}__evidence",
            f"{raw_name}__unknown_reason",
        }
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
        name = raw_name.lower()
        if any(token in name for token in denylist):
            raise ValueError(f"sensitive field forbidden in blinded coding sheet: {name!r}")


def _validate_provenance(
    provenance: dict[str, Any], *, coding_order_seed: int
) -> None:
    required = {
        "source_records_sha256",
        "source_run_id",
        "sampling_spec_sha256",
        "sampling_spec_version",
        "codebook_sha256",
        "codebook_version",
        "selection_seed",
        "coding_order_seed",
    }
    missing = sorted(required - provenance.keys())
    if missing:
        raise ValueError(f"missing packet provenance fields: {missing}")
    empty = sorted(
        key for key in required if provenance[key] is None or provenance[key] == ""
    )
    if empty:
        raise ValueError(f"empty packet provenance fields: {empty}")
    if provenance["coding_order_seed"] != coding_order_seed:
        raise ValueError("provenance coding_order_seed does not match packet seed")


def _coding_instructions(fields: list[dict[str, Any]]) -> str:
    lines = [
        "# Blinded Snapchat validation coding instructions",
        "",
        "Code only what is observable in the supplied creative. Do not use the filename to infer category, advertiser, exposure, country, or campaign metadata.",
        "",
        "- Boolean values: `1` present, `0` observably absent, blank only when genuinely unobservable.",
        "- Ratings: integer 0–100 using the field anchors. Zero means observable absence, not missingness.",
        "- For blanks, complete the corresponding `__unknown_reason` field.",
        "- Positive booleans and ratings of 80 or above require concise visible/audible evidence.",
        "- Watch complete videos with sound when available. Do not code from thumbnails alone.",
        "- Code each creative independently before consulting another coder.",
        "",
        "## Fields",
        "",
    ]
    for field in fields:
        lines.extend(
            [
                f"### `{field['name']}` — {field['type']}",
                "",
                str(field["definition"]),
                "",
            ]
        )
        anchors = field.get("anchors") or {}
        for value, label in anchors.items():
            lines.append(f"- **{value}:** {label}")
        if anchors:
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _media_kind(content_type: str) -> str:
    lowered = content_type.lower()
    if lowered.startswith("image/"):
        return "image"
    if lowered.startswith("video/"):
        return "video"
    return "other"


def _impressions(record: dict[str, Any]) -> int:
    value = (record.get("ad") or {}).get("impressions_total")
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _suffix_for_content_type(content_type: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "video/mp4": ".mp4",
    }.get(content_type.lower(), ".bin")


def _validate_relative_media_path(local_path: str) -> Path:
    relative_path = Path(local_path)
    if not local_path or relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(
            f"media local_path must be relative without parent traversal: {local_path!r}"
        )
    return relative_path



def _copy_verified_media(
    source_run_fd: int,
    source: Path,
    destination: Path,
    *,
    expected_sha256: str,
    coding_id: str,
) -> None:
    digest = hashlib.sha256()
    opened_fds: list[int] = []
    try:
        parent_fd = source_run_fd
        for component in source.parts[:-1]:
            parent_fd = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent_fd,
            )
            opened_fds.append(parent_fd)
        source_fd = os.open(
            source.name,
            os.O_RDONLY | os.O_NOFOLLOW,
            dir_fd=parent_fd,
        )
        with os.fdopen(source_fd, "rb") as source_handle:
            if not stat.S_ISREG(os.fstat(source_handle.fileno()).st_mode):
                raise FileNotFoundError(f"selected media is not a regular file: {source}")
            with destination.open("xb") as destination_handle:
                for chunk in iter(lambda: source_handle.read(1024 * 1024), b""):
                    digest.update(chunk)
                    destination_handle.write(chunk)
    except OSError as exc:
        raise FileNotFoundError(f"selected media is missing: {source}") from exc
    finally:
        for descriptor in reversed(opened_fds):
            os.close(descriptor)
    if digest.hexdigest() != expected_sha256:
        raise ValueError(f"checksum mismatch for {coding_id}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records, spec, codebook, snapshot_hashes = load_input_snapshots(
        args.records, args.spec, args.codebook
    )
    source_run_id = validate_source_run_id(args.records, spec)
    creatives = build_creatives(records, args.records.parent)
    selected = select_creatives(creatives, spec["cells"], seed=int(spec["selection_seed"]))
    write_coding_packet(
        selected,
        codebook["fields"],
        args.output_dir,
        source_run_dir=args.records.parent,
        seed=int(spec["coding_order_seed"]),
        provenance={
            **snapshot_hashes,
            "source_run_id": source_run_id,
            "sampling_spec_version": str(spec["spec_version"]),
            "codebook_version": str(codebook["spec_version"]),
            "selection_seed": int(spec["selection_seed"]),
            "coding_order_seed": int(spec["coding_order_seed"]),
        },
    )
    print(
        json.dumps(
            {
                "sample_size": len(selected),
                "unique_creatives_available": len(creatives),
                "output_dir": str(args.output_dir.resolve()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
