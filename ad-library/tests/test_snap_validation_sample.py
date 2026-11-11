import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pytest

from build_snap_validation_sample import (
    build_creatives,
    load_input_snapshots,
    select_creatives,
    validate_source_run_id,
    write_coding_packet,
)


def _record(
    ad_id: str,
    category: str,
    country: str,
    content_type: str,
    sha256: str,
    impressions: int,
    local_path: str,
) -> dict:
    return {
        "ad_id": ad_id,
        "category": category,
        "query_advertiser": f"advertiser-{category}",
        "query_country": country,
        "ad": {
            "headline": f"headline-{ad_id}",
            "impressions_total": impressions,
            "languages": [country],
            "start_date": "2026-01-01T00:00:00.000Z",
            "status": "ACTIVE",
        },
        "media": {
            "content_type": content_type,
            "sha256": sha256,
            "local_path": local_path,
        },
    }


def _provenance() -> dict:
    return {
        "source_records_sha256": "1" * 64,
        "source_run_id": "run-1",
        "sampling_spec_sha256": "2" * 64,
        "sampling_spec_version": "sample-v1",
        "codebook_sha256": "3" * 64,
        "codebook_version": "codebook-v1",
        "selection_seed": 6,
        "coding_order_seed": 7,
    }


def test_build_creatives_deduplicates_and_aggregates_exposure(tmp_path: Path) -> None:
    records = [
        _record("a1", "betting", "fr", "image/jpeg", "same", 10, "media/same.jpg"),
        _record("a2", "betting", "fr", "image/jpeg", "same", 25, "media/same.jpg"),
        _record("a3", "betting", "de", "video/mp4", "other", 7, "media/other.mp4"),
        _record("missing", "betting", "fr", "image/jpeg", "", 99, ""),
    ]

    creatives = build_creatives(records, tmp_path)

    assert len(creatives) == 2
    same = next(item for item in creatives if item["media_sha256"] == "same")
    assert same["total_impressions"] == 35
    assert same["reuse_count"] == 2
    assert same["representative_ad_id"] == "a2"
    assert same["country"] == "fr"
    assert same["media_kind"] == "image"
    assert same["source_media_path"] == "media/same.jpg"


def test_build_creatives_assigns_cross_cell_hash_by_cell_exposure_and_bins_on_that_exposure(
    tmp_path: Path,
) -> None:
    records = [
        _record("a1", "betting", "fr", "image/jpeg", "same", 10, "media/same.jpg"),
        _record("a2", "control", "de", "image/jpeg", "same", 20, "media/same.jpg"),
        _record("a3", "control", "de", "image/jpeg", "same", 5, "media/same.jpg"),
    ]

    creative = build_creatives(records, tmp_path)[0]

    assert (creative["category"], creative["country"], creative["media_kind"]) == (
        "control",
        "de",
        "image",
    )
    assert creative["total_impressions"] == 25
    assert creative["reuse_count"] == 3
    assert creative["languages"] == ["de"]


@pytest.mark.parametrize(
    "local_path", ["/tmp/outside.jpg", "../outside.jpg", "media/../creative.jpg"]
)
def test_build_creatives_rejects_absolute_and_parent_traversal_media_paths(
    tmp_path: Path, local_path: str
) -> None:
    records = [
        _record("a1", "betting", "fr", "image/jpeg", "hash", 10, local_path)
    ]

    with pytest.raises(ValueError, match="outside source run|relative"):
        build_creatives(records, tmp_path / "run")


def test_build_creatives_keeps_validated_relative_media_path(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    records = [
        _record(
            "a1",
            "betting",
            "fr",
            "image/jpeg",
            hashlib.sha256(b"image").hexdigest(),
            10,
            "media/creative.jpg",
        )
    ]

    creative = build_creatives(records, run_dir)[0]

    assert creative["source_media_path"] == "media/creative.jpg"


def test_load_input_snapshots_hashes_and_parses_each_exact_byte_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = {
        tmp_path / "records.jsonl": (
            b'{"ad_id":"first"}\n',
            b'{"ad_id":"changed"}\n',
        ),
        tmp_path / "spec.json": (b'{"spec_version":"first"}', b"not json"),
        tmp_path / "codebook.json": (b'{"spec_version":"first"}', b"not json"),
    }
    calls = {path: 0 for path in paths}

    def changing_read_bytes(path: Path) -> bytes:
        index = calls[path]
        calls[path] += 1
        return paths[path][min(index, 1)]

    monkeypatch.setattr(Path, "read_bytes", changing_read_bytes)

    records, spec, codebook, hashes = load_input_snapshots(*paths)

    assert records == [{"ad_id": "first"}]
    assert spec == {"spec_version": "first"}
    assert codebook == {"spec_version": "first"}
    assert calls == {path: 1 for path in paths}
    assert hashes == {
        "source_records_sha256": hashlib.sha256(paths[tmp_path / "records.jsonl"][0]).hexdigest(),
        "sampling_spec_sha256": hashlib.sha256(paths[tmp_path / "spec.json"][0]).hexdigest(),
        "codebook_sha256": hashlib.sha256(paths[tmp_path / "codebook.json"][0]).hexdigest(),
    }


def test_select_creatives_meets_cells_and_is_deterministic(tmp_path: Path) -> None:
    records = []
    for category, country, media_kind in [
        ("betting", "fr", "image"),
        ("betting", "fr", "video"),
        ("control", "fr", "image"),
        ("control", "fr", "video"),
    ]:
        content_type = "image/jpeg" if media_kind == "image" else "video/mp4"
        suffix = "jpg" if media_kind == "image" else "mp4"
        for index in range(10):
            sha256 = f"{category}-{media_kind}-{index}"
            relative_path = f"media/{sha256}.{suffix}"
            media_path = tmp_path / relative_path
            media_path.parent.mkdir(parents=True, exist_ok=True)
            media_path.write_bytes(str(index).encode())
            records.append(
                _record(
                    f"{category}-{media_kind}-{index}",
                    category,
                    country,
                    content_type,
                    sha256,
                    index + 1,
                    relative_path,
                )
            )

    cells = [
        {"category": "betting", "country": "fr", "media_kind": "image", "quota": 3},
        {"category": "betting", "country": "fr", "media_kind": "video", "quota": 3},
        {"category": "control", "country": "fr", "media_kind": "image", "quota": 2},
        {"category": "control", "country": "fr", "media_kind": "video", "quota": 2},
    ]
    creatives = build_creatives(records, tmp_path)

    first = select_creatives(creatives, cells, seed=20261015)
    second = select_creatives(creatives, cells, seed=20261015)

    assert [item["media_sha256"] for item in first] == [
        item["media_sha256"] for item in second
    ]
    assert len(first) == 10
    assert len({item["media_sha256"] for item in first}) == 10
    actual_cells = {}
    for item in first:
        key = (item["category"], item["country"], item["media_kind"])
        actual_cells[key] = actual_cells.get(key, 0) + 1
    assert actual_cells == {
        (cell["category"], cell["country"], cell["media_kind"]): cell["quota"]
        for cell in cells
    }


def test_write_coding_packet_blinds_sheet_and_separates_linkage(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    source_media = run_dir / "media/source.jpg"
    source_media.parent.mkdir(parents=True)
    source_media.write_bytes(b"image")
    selected = [
        {
            "media_sha256": hashlib.sha256(b"image").hexdigest(),
            "source_media_path": "media/source.jpg",
            "media_kind": "image",
            "content_type": "image/jpeg",
            "category": "betting",
            "country": "fr",
            "advertiser": "Winamax",
            "headline": "Bonus",
            "representative_ad_id": "ad-1",
            "total_impressions": 100,
            "reuse_count": 2,
            "languages": ["fr"],
            "start_date": "2026-01-01T00:00:00.000Z",
            "status": "ACTIVE",
            "exposure_bin": 1,
        }
    ]
    fields = [
        {
            "name": "financial_inducement_present",
            "type": "boolean",
            "definition": "Whether an inducement is observable.",
        },
        {
            "name": "urgency_scarcity",
            "type": "rating_0_100",
            "definition": "Observable urgency.",
        },
    ]

    provenance = _provenance()
    write_coding_packet(
        selected,
        fields,
        tmp_path / "packet",
        source_run_dir=run_dir,
        seed=7,
        provenance=provenance,
    )

    with (tmp_path / "packet/coding_sheet.csv").open(newline="", encoding="utf-8") as handle:
        coding_rows = list(csv.DictReader(handle))
    with (tmp_path / "packet/linkage_key.csv").open(newline="", encoding="utf-8") as handle:
        linkage_rows = list(csv.DictReader(handle))

    assert len(coding_rows) == 1
    assert coding_rows[0]["coding_id"].startswith("SCV-")
    assert coding_rows[0]["media_file"].endswith(".jpg")
    assert "category" not in coding_rows[0]
    assert "advertiser" not in coding_rows[0]
    assert coding_rows[0]["financial_inducement_present"] == ""
    assert coding_rows[0]["urgency_scarcity"] == ""
    assert linkage_rows[0]["category"] == "betting"
    assert linkage_rows[0]["advertiser"] == "Winamax"
    manifest = json.loads((tmp_path / "packet/manifest.json").read_text())
    assert manifest["sample_size"] == 1
    assert manifest["provenance"] == {
        **provenance,
        "selected_media_sha256": [
            {
                "coding_id": coding_rows[0]["coding_id"],
                "sha256": hashlib.sha256(b"image").hexdigest(),
            }
        ],
    }
    assert (tmp_path / "packet" / coding_rows[0]["media_file"]).read_bytes() == b"image"


def test_write_coding_packet_survives_source_run_ancestor_symlink_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_run = tmp_path / "source-run"
    source = source_run / "media/source.jpg"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"verified")
    outside = tmp_path / "outside"
    (outside / "media").mkdir(parents=True)
    (outside / "media/source.jpg").write_bytes(b"replacement")
    selected = [
        {
            "media_sha256": hashlib.sha256(b"verified").hexdigest(),
            "source_media_path": "media/source.jpg",
            "media_kind": "image",
            "content_type": "image/jpeg",
            "category": "control",
            "country": "fr",
            "advertiser": "A",
            "headline": "H",
            "representative_ad_id": "ad",
            "total_impressions": 1,
            "reuse_count": 1,
            "languages": ["fr"],
            "start_date": "",
            "status": "",
            "exposure_bin": 1,
        }
    ]
    original_os_open = os.open
    swapped = False

    def racing_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal swapped
        if Path(path) == source_run and kwargs.get("dir_fd") is None and not swapped:
            descriptor = original_os_open(path, flags, *args, **kwargs)
            swapped = True
            source_run.rename(tmp_path / "original-source-run")
            source_run.symlink_to(outside, target_is_directory=True)
            return descriptor
        return original_os_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", racing_os_open)

    write_coding_packet(
        selected,
        [{"name": "rating", "type": "rating_0_100", "definition": "R"}],
        tmp_path / "packet",
        source_run_dir=source_run,
        seed=7,
        provenance=_provenance(),
    )

    assert (tmp_path / "packet/media/SCV-001.jpg").read_bytes() == b"verified"


def test_validate_source_run_id_matches_records_parent() -> None:
    records = Path("data/raw/snap_1000/run_id=run-123/records.jsonl")
    assert validate_source_run_id(records, {"source_run_id": "run-123"}) == "run-123"

    with pytest.raises(ValueError, match="source_run_id"):
        validate_source_run_id(records, {"source_run_id": "run-999"})


@pytest.mark.parametrize(
    "field_name",
    [
        "category",
        "advertiser_name",
        "campaign_country",
        "headline_text",
        "language_code",
        "media_hash",
        "exposure_bin",
        "source_id",
    ],
)
def test_write_coding_packet_rejects_sensitive_blinded_columns(
    tmp_path: Path, field_name: str
) -> None:
    selected = []
    fields = [{"name": field_name, "type": "boolean", "definition": "bad"}]

    with pytest.raises(ValueError, match="blinded coding sheet"):
        write_coding_packet(
            selected,
            fields,
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=1,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()


def test_write_coding_packet_rejects_unknown_codebook_field_type(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported codebook field type"):
        write_coding_packet(
            [],
            [{"name": "rating", "type": "free_text", "definition": "R"}],
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=7,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()


@pytest.mark.parametrize("invalid_name", ["", "   ", None, 1])
def test_write_coding_packet_rejects_empty_or_non_string_field_names(
    tmp_path: Path, invalid_name: object
) -> None:
    with pytest.raises(ValueError, match="nonempty string"):
        write_coding_packet(
            [],
            [{"name": invalid_name, "type": "boolean", "definition": "Field."}],
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=7,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()


def test_write_coding_packet_rejects_duplicate_field_names(tmp_path: Path) -> None:
    fields = [
        {"name": "present", "type": "boolean", "definition": "First."},
        {"name": "present", "type": "rating_0_100", "definition": "Second."},
    ]

    with pytest.raises(ValueError, match="duplicate codebook field name"):
        write_coding_packet(
            [],
            fields,
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=7,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()


@pytest.mark.parametrize(
    "field_name",
    [
        "coding_id",
        "media_file",
        "media_type",
        "coder_id",
        "observable",
        "coder_notes",
        "completed_at_utc",
        "overall_notes",
    ],
)
def test_write_coding_packet_rejects_reserved_output_columns(
    tmp_path: Path, field_name: str
) -> None:
    with pytest.raises(ValueError, match="reserved output column"):
        write_coding_packet(
            [],
            [{"name": field_name, "type": "boolean", "definition": "Field."}],
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=7,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()


@pytest.mark.parametrize(
    "field_names",
    [
        ["foo", "foo__evidence"],
        ["foo", "foo__unknown_reason"],
        ["foo__evidence", "foo"],
    ],
)
def test_write_coding_packet_rejects_generated_output_column_collisions(
    tmp_path: Path, field_names: list[str]
) -> None:
    fields = [
        {"name": name, "type": "boolean", "definition": "Field."}
        for name in field_names
    ]

    with pytest.raises(ValueError, match="output column collision"):
        write_coding_packet(
            [],
            fields,
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=7,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()


def test_write_coding_packet_is_atomic_on_failure(tmp_path: Path) -> None:
    source_run = tmp_path / "source-run"
    source = source_run / "media/source.jpg"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"valid")
    base = {
        "media_sha256": hashlib.sha256(b"valid").hexdigest(),
        "source_media_path": "media/source.jpg",
        "media_kind": "image",
        "content_type": "image/jpeg",
        "category": "control",
        "country": "fr",
        "advertiser": "A",
        "headline": "H",
        "representative_ad_id": "ad",
        "total_impressions": 1,
        "reuse_count": 1,
        "languages": ["fr"],
        "start_date": "",
        "status": "",
        "exposure_bin": 1,
    }
    missing = {**base, "source_media_path": "media/missing.jpg"}
    output = tmp_path / "packet"

    with pytest.raises(FileNotFoundError):
        write_coding_packet(
            [base, missing],
            [{"name": "rating", "type": "rating_0_100", "definition": "R"}],
            output,
            source_run_dir=source_run,
            seed=7,
            provenance=_provenance(),
        )

    assert not output.exists()
    assert not list(tmp_path.glob(".packet.*"))


def test_write_coding_packet_rejects_inconsistent_provenance_seed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="coding_order_seed"):
        write_coding_packet(
            [],
            [{"name": "rating", "type": "rating_0_100", "definition": "R"}],
            tmp_path / "packet",
            source_run_dir=tmp_path,
            seed=8,
            provenance=_provenance(),
        )
    assert not (tmp_path / "packet").exists()
