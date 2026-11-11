import asyncio
from argparse import Namespace
import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
import run_snap_validation_gabriel as runner

from run_snap_validation_gabriel import (
    build_analysis_frame,
    build_coding_prompt,
    build_run_fingerprint,
    load_run_snapshots,
    prepare_output_directory,
    validate_and_flatten,
)


def test_build_coding_prompt_uses_frozen_fields_without_linkage_metadata() -> None:
    fields = [
        {
            "name": "financial_inducement_present",
            "type": "boolean",
            "definition": "Observable inducement.",
        },
        {
            "name": "urgency_scarcity",
            "type": "rating_0_100",
            "definition": "Observable urgency.",
            "anchors": {"0": "none", "100": "dominant"},
        },
    ]

    prompt = build_coding_prompt(fields)

    assert "financial_inducement_present" in prompt
    assert "urgency_scarcity" in prompt
    assert '"value"' in prompt
    assert "unknown_reason" in prompt
    assert "advertiser" not in prompt.lower()
    assert "category" not in prompt.lower()


def test_build_coding_prompt_rejects_unknown_codebook_field_type() -> None:
    with pytest.raises(ValueError, match="unsupported codebook field type"):
        build_coding_prompt(
            [{"name": "field", "type": "free_text", "definition": "Field."}]
        )


@pytest.mark.parametrize("invalid_name", ["", "   ", None, 1])
def test_build_coding_prompt_rejects_empty_or_non_string_field_names(
    invalid_name: object,
) -> None:
    with pytest.raises(ValueError, match="nonempty string"):
        build_coding_prompt(
            [{"name": invalid_name, "type": "boolean", "definition": "Field."}]
        )


def test_build_coding_prompt_rejects_duplicate_field_names() -> None:
    fields = [
        {"name": "present", "type": "boolean", "definition": "First."},
        {"name": "present", "type": "rating_0_100", "definition": "Second."},
    ]

    with pytest.raises(ValueError, match="duplicate codebook field name"):
        build_coding_prompt(fields)


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
def test_build_coding_prompt_rejects_reserved_output_columns(field_name: str) -> None:
    with pytest.raises(ValueError, match="reserved output column"):
        build_coding_prompt(
            [{"name": field_name, "type": "boolean", "definition": "Field."}]
        )


@pytest.mark.parametrize(
    "field_names",
    [
        ["foo", "foo__evidence"],
        ["foo", "foo__unknown_reason"],
        ["foo__evidence", "foo"],
    ],
)
def test_build_coding_prompt_rejects_generated_output_column_collisions(
    field_names: list[str],
) -> None:
    fields = [
        {"name": name, "type": "boolean", "definition": "Field."}
        for name in field_names
    ]

    with pytest.raises(ValueError, match="output column collision"):
        build_coding_prompt(fields)


def test_build_analysis_frame_uses_only_blinded_image_media(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    media = packet / "media"
    media.mkdir(parents=True)
    (media / "SCV-001.jpg").write_bytes(b"image")
    (media / "SCV-002.mp4").write_bytes(b"video")
    manifest = {
        "media": [
            {
                "coding_id": "SCV-001",
                "media_file": "media/SCV-001.jpg",
                "media_sha256": hashlib.sha256(b"image").hexdigest(),
            },
            {
                "coding_id": "SCV-002",
                "media_file": "media/SCV-002.mp4",
                "media_sha256": hashlib.sha256(b"video").hexdigest(),
            },
        ]
    }
    (packet / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    frame = build_analysis_frame(packet / "manifest.json", "prompt", expected_count=1)

    assert frame["coding_id"].tolist() == ["SCV-001"]
    assert frame["prompt"].tolist() == ["prompt"]
    assert frame["image_data"].tolist() == [base64.b64encode(b"image").decode("ascii")]


def test_build_analysis_frame_binds_hash_and_image_to_same_open_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet = tmp_path / "packet"
    media = packet / "media"
    media.mkdir(parents=True)
    source = media / "SCV-001.jpg"
    source.write_bytes(b"original")
    manifest = {
        "media": [
            {
                "coding_id": "SCV-001",
                "media_file": "media/SCV-001.jpg",
                "media_sha256": hashlib.sha256(b"original").hexdigest(),
            }
        ]
    }
    manifest_path = packet / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    original_open = os.open
    swapped = False

    def racing_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal swapped
        descriptor = original_open(path, flags, *args, **kwargs)
        if path == "SCV-001.jpg" and kwargs.get("dir_fd") is not None and not swapped:
            swapped = True
            replacement = media / "replacement.jpg"
            replacement.write_bytes(b"replacement")
            replacement.replace(source)
        return descriptor

    monkeypatch.setattr(os, "open", racing_open)

    frame = build_analysis_frame(manifest_path, "prompt", expected_count=1)

    assert frame.loc[0, "media_sha256"] == hashlib.sha256(b"original").hexdigest()
    assert base64.b64decode(frame.loc[0, "image_data"]) == b"original"
    assert source.read_bytes() == b"replacement"


@pytest.mark.parametrize("media_file", ["/etc/passwd.jpg", "../escape.jpg", "media/../../escape.jpg"])
def test_build_analysis_frame_rejects_media_paths_outside_packet(
    tmp_path: Path, media_file: str
) -> None:
    packet = tmp_path / "packet"
    packet.mkdir()
    manifest = {
        "media": [
            {
                "coding_id": "SCV-001",
                "media_file": media_file,
                "media_sha256": hashlib.sha256(b"escape").hexdigest(),
            }
        ]
    }
    (packet / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="relative|outside packet"):
        build_analysis_frame(packet / "manifest.json", "prompt", expected_count=1)


def test_build_analysis_frame_recalculates_hash_and_enforces_unique_ids_hashes_and_count(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    media = packet / "media"
    media.mkdir(parents=True)
    (media / "one.jpg").write_bytes(b"one")
    (media / "two.jpg").write_bytes(b"two")

    def write_manifest(entries: list[dict]) -> Path:
        path = packet / "manifest.json"
        path.write_text(json.dumps({"media": entries}), encoding="utf-8")
        return path

    base = {
        "coding_id": "SCV-001",
        "media_file": "media/one.jpg",
        "media_sha256": hashlib.sha256(b"wrong").hexdigest(),
    }
    with pytest.raises(ValueError, match="checksum mismatch"):
        build_analysis_frame(write_manifest([base]), "prompt", expected_count=1)

    first = {**base, "media_sha256": hashlib.sha256(b"one").hexdigest()}
    second = {
        "coding_id": "SCV-001",
        "media_file": "media/two.jpg",
        "media_sha256": hashlib.sha256(b"two").hexdigest(),
    }
    with pytest.raises(ValueError, match="duplicate coding_id"):
        build_analysis_frame(write_manifest([first, second]), "prompt", expected_count=2)

    second["coding_id"] = "SCV-002"
    second["media_sha256"] = first["media_sha256"]
    with pytest.raises(ValueError, match="checksum mismatch|duplicate media hash"):
        build_analysis_frame(write_manifest([first, second]), "prompt", expected_count=2)

    second["media_sha256"] = hashlib.sha256(b"two").hexdigest()
    with pytest.raises(ValueError, match="expected 3 image creatives, found 2"):
        build_analysis_frame(write_manifest([first, second]), "prompt", expected_count=3)


def test_load_run_snapshots_hashes_and_parses_each_exact_byte_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = tmp_path / "manifest.json"
    codebook = tmp_path / "codebook.json"
    snapshots = {
        manifest: (b'{"media":[],"version":"first"}', b"not json"),
        codebook: (b'{"fields":[],"version":"first"}', b"not json"),
    }
    calls = {path: 0 for path in snapshots}

    def changing_read_bytes(path: Path) -> bytes:
        index = calls[path]
        calls[path] += 1
        return snapshots[path][min(index, 1)]

    monkeypatch.setattr(Path, "read_bytes", changing_read_bytes)

    loaded_manifest, loaded_codebook, manifest_bytes, codebook_bytes = load_run_snapshots(
        manifest, codebook
    )

    assert loaded_manifest == {"media": [], "version": "first"}
    assert loaded_codebook == {"fields": [], "version": "first"}
    assert manifest_bytes == snapshots[manifest][0]
    assert codebook_bytes == snapshots[codebook][0]
    assert calls == {manifest: 1, codebook: 1}


def test_validate_and_flatten_enforces_frozen_schema() -> None:
    fields = [
        {"name": "present", "type": "boolean", "definition": "Presence."},
        {"name": "rating", "type": "rating_0_100", "definition": "Rating."},
    ]
    frame = pd.DataFrame(
        [
            {
                "coding_id": "SCV-001",
                "Response JSON": {
                    "annotations": [
                        {
                            "field": "present",
                            "value": True,
                            "evidence": "visible",
                            "unknown_reason": None,
                        },
                        {
                            "field": "rating",
                            "value": 80,
                            "evidence": "prominent",
                            "unknown_reason": None,
                        },
                    ],
                    "overall_notes": "",
                },
            }
        ]
    )

    rows = validate_and_flatten(frame, fields, ["SCV-001"])

    assert rows[0]["present"] is True
    assert rows[0]["rating"] == 80
    assert rows[0]["rating__evidence"] == "prominent"


def test_validate_and_flatten_rejects_out_of_range_rating() -> None:
    fields = [{"name": "rating", "type": "rating_0_100", "definition": "Rating."}]
    frame = pd.DataFrame(
        [
            {
                "coding_id": "SCV-001",
                "Response JSON": {
                    "annotations": [
                        {
                            "field": "rating",
                            "value": 101,
                            "evidence": "",
                            "unknown_reason": None,
                        }
                    ],
                    "overall_notes": "",
                },
            }
        ]
    )

    with pytest.raises(ValueError, match="integer from 0 through 100"):
        validate_and_flatten(frame, fields, ["SCV-001"])


def _response_frame(annotations: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "coding_id": "SCV-001",
                "Response JSON": {"annotations": annotations, "overall_notes": ""},
            }
        ]
    )


def _valid_response() -> dict[str, Any]:
    return {
        "annotations": [
            {"field": "present", "value": False, "evidence": "", "unknown_reason": None}
        ],
        "overall_notes": "",
    }


@pytest.mark.parametrize(
    ("returned_ids", "expected_ids", "message"),
    [
        (["SCV-001", "SCV-001"], ["SCV-001", "SCV-002"], "duplicate coding_id"),
        (["SCV-001"], ["SCV-001", "SCV-002"], "row count|missing"),
        (["SCV-001", "SCV-003"], ["SCV-001", "SCV-002"], "unexpected|missing"),
    ],
)
def test_validate_and_flatten_rejects_non_bijective_result_identity(
    returned_ids: list[str], expected_ids: list[str], message: str
) -> None:
    frame = pd.DataFrame(
        [
            {"coding_id": coding_id, "Response JSON": _valid_response()}
            for coding_id in returned_ids
        ]
    )

    with pytest.raises(ValueError, match=message):
        validate_and_flatten(
            frame,
            [{"name": "present", "type": "boolean", "definition": "Presence."}],
            expected_ids,
        )


@pytest.mark.parametrize(
    ("annotations", "message"),
    [
        (
            [
                {"field": "present", "value": False, "evidence": "", "unknown_reason": None},
                {"field": "present", "value": False, "evidence": "", "unknown_reason": None},
                {"field": "rating", "value": 0, "evidence": "", "unknown_reason": None},
            ],
            "exactly one annotation",
        ),
        (
            [
                {"field": "rating", "value": 0, "evidence": "", "unknown_reason": None},
                {"field": "present", "value": False, "evidence": "", "unknown_reason": None},
            ],
            "field mismatch",
        ),
        (
            [
                {"field": "present", "value": False, "evidence": "", "unknown_reason": None},
                {"field": "extra", "value": 0, "evidence": "", "unknown_reason": None},
            ],
            "field mismatch",
        ),
    ],
)
def test_validate_and_flatten_rejects_duplicate_out_of_order_and_extra_annotations(
    annotations: list[dict], message: str
) -> None:
    fields = [
        {"name": "present", "type": "boolean", "definition": "Presence."},
        {"name": "rating", "type": "rating_0_100", "definition": "Rating."},
    ]

    with pytest.raises(ValueError, match=message):
        validate_and_flatten(_response_frame(annotations), fields, ["SCV-001"])


@pytest.mark.parametrize(
    "response",
    [
        {
            "annotations": [
                {
                    "field": "present",
                    "value": False,
                    "evidence": "",
                    "unknown_reason": None,
                }
            ],
            "overall_notes": "",
            "extra": "not allowed",
        },
        {
            "annotations": [
                {
                    "field": "present",
                    "value": False,
                    "evidence": "",
                    "unknown_reason": None,
                    "extra": "not allowed",
                }
            ],
            "overall_notes": "",
        },
    ],
)
def test_validate_and_flatten_rejects_unexpected_schema_keys(response: dict) -> None:
    frame = pd.DataFrame([{"coding_id": "SCV-001", "Response JSON": response}])

    with pytest.raises(ValueError, match="unexpected|exactly"):
        validate_and_flatten(
            frame,
            [{"name": "present", "type": "boolean", "definition": "Presence."}],
            ["SCV-001"],
        )


@pytest.mark.parametrize("overall_notes", [None, 1, [], {}])
def test_validate_and_flatten_requires_string_overall_notes(overall_notes: object) -> None:
    response = {
        "annotations": [
            {"field": "present", "value": False, "evidence": "", "unknown_reason": None}
        ],
        "overall_notes": overall_notes,
    }

    with pytest.raises(ValueError, match="overall_notes must be a string"):
        validate_and_flatten(
            pd.DataFrame([{"coding_id": "SCV-001", "Response JSON": response}]),
            [{"name": "present", "type": "boolean", "definition": "Presence."}],
            ["SCV-001"],
        )


def test_validate_and_flatten_requires_overall_notes_key() -> None:
    response = {
        "annotations": [
            {"field": "present", "value": False, "evidence": "", "unknown_reason": None}
        ]
    }

    with pytest.raises(ValueError, match="response keys"):
        validate_and_flatten(
            pd.DataFrame([{"coding_id": "SCV-001", "Response JSON": response}]),
            [{"name": "present", "type": "boolean", "definition": "Presence."}],
            ["SCV-001"],
        )


@pytest.mark.parametrize("wrapper", [[], [{}, {}]])
def test_validate_and_flatten_rejects_non_singleton_list_wrappers(wrapper: list[dict]) -> None:
    with pytest.raises(ValueError, match="single-object response wrapper"):
        validate_and_flatten(
            pd.DataFrame([{"coding_id": "SCV-001", "Response JSON": wrapper}]),
            [{"name": "present", "type": "boolean", "definition": "Presence."}],
            ["SCV-001"],
        )


@pytest.mark.parametrize("missing_key", ["value", "evidence", "unknown_reason"])
def test_validate_and_flatten_requires_evidence_and_unknown_reason_keys(
    missing_key: str,
) -> None:
    annotation = {
        "field": "present",
        "value": False,
        "evidence": "",
        "unknown_reason": None,
    }
    del annotation[missing_key]

    with pytest.raises(ValueError, match=missing_key):
        validate_and_flatten(
            _response_frame([annotation]),
            [{"name": "present", "type": "boolean", "definition": "Presence."}],
            ["SCV-001"],
        )


@pytest.mark.parametrize(
    ("field_type", "value", "evidence", "unknown_reason", "message"),
    [
        ("boolean", True, "", None, "requires nonempty evidence"),
        ("rating_0_100", 80, "  ", None, "requires nonempty evidence"),
        ("boolean", None, "", None, "requires nonempty unknown_reason"),
        ("boolean", False, "", "cannot see", "unknown_reason must be empty"),
    ],
)
def test_validate_and_flatten_enforces_evidence_and_unknown_semantics(
    field_type: str,
    value: object,
    evidence: str,
    unknown_reason: object,
    message: str,
) -> None:
    annotation = {
        "field": "field",
        "value": value,
        "evidence": evidence,
        "unknown_reason": unknown_reason,
    }

    with pytest.raises(ValueError, match=message):
        validate_and_flatten(
            _response_frame([annotation]),
            [{"name": "field", "type": field_type, "definition": "Field."}],
            ["SCV-001"],
        )


def test_run_fingerprint_binds_manifest_media_prompt_codebook_provider_and_model(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "manifest.json"
    codebook = tmp_path / "codebook.json"
    manifest.write_text('{"version": 1}', encoding="utf-8")
    codebook.write_text('{"version": 1}', encoding="utf-8")
    base = build_run_fingerprint(
        packet_manifest=manifest,
        codebook=codebook,
        prompt="prompt",
        provider="provider",
        model="model",
        media_hashes=[("SCV-001", "a" * 64)],
    )

    changes = [
        {"prompt": "changed"},
        {"provider": "other"},
        {"model": "other"},
        {"media_hashes": [("SCV-001", "b" * 64)]},
    ]
    for change in changes:
        kwargs = {
            "packet_manifest": manifest,
            "codebook": codebook,
            "prompt": "prompt",
            "provider": "provider",
            "model": "model",
            "media_hashes": [("SCV-001", "a" * 64)],
        }
        kwargs.update(change)
        assert build_run_fingerprint(**kwargs)["fingerprint"] != base["fingerprint"]

    manifest.write_text('{"version": 2}', encoding="utf-8")
    assert (
        build_run_fingerprint(
            packet_manifest=manifest,
            codebook=codebook,
            prompt="prompt",
            provider="provider",
            model="model",
            media_hashes=[("SCV-001", "a" * 64)],
        )["fingerprint"]
        != base["fingerprint"]
    )

    manifest_snapshot = b'{"version":"snapshotted"}'
    codebook_snapshot = b'{"fields":"snapshotted"}'
    from_snapshots = build_run_fingerprint(
        packet_manifest=tmp_path / "missing-manifest.json",
        codebook=tmp_path / "missing-codebook.json",
        prompt="prompt",
        provider="provider",
        model="model",
        media_hashes=[("SCV-001", "a" * 64)],
        packet_manifest_bytes=manifest_snapshot,
        codebook_bytes=codebook_snapshot,
    )
    assert from_snapshots["packet_manifest_sha256"] == hashlib.sha256(
        manifest_snapshot
    ).hexdigest()
    assert from_snapshots["codebook_sha256"] == hashlib.sha256(
        codebook_snapshot
    ).hexdigest()


def test_prepare_output_directory_rejects_stale_or_unbound_output_without_reset(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    first = {"fingerprint": "a" * 64, "provider": "one"}
    second = {"fingerprint": "b" * 64, "provider": "two"}

    run_dir = prepare_output_directory(output, first, reset=False)
    assert run_dir == output / first["fingerprint"]
    assert json.loads((output / "pre_run_manifest.json").read_text()) == first

    stale_file = run_dir / "raw-response.json"
    stale_file.write_text("stale", encoding="utf-8")
    with pytest.raises(ValueError, match="--reset"):
        prepare_output_directory(output, second, reset=False)
    assert stale_file.read_text(encoding="utf-8") == "stale"
    assert json.loads((output / "pre_run_manifest.json").read_text()) == first

    reset_dir = prepare_output_directory(output, second, reset=True)
    assert reset_dir == output / second["fingerprint"]
    assert not stale_file.exists()

    legacy = tmp_path / "legacy"
    legacy.mkdir()
    (legacy / "responses.csv").write_text("old", encoding="utf-8")
    with pytest.raises(ValueError, match="--reset"):
        prepare_output_directory(legacy, first, reset=False)


def test_prepare_output_directory_rejects_forged_matching_checkpoint_without_reset(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    manifest = {"fingerprint": "a" * 64, "provider": "provider"}
    run_dir = prepare_output_directory(output, manifest, reset=False)
    forged = run_dir / "raw/image_arm_responses.csv"
    forged.parent.mkdir(parents=True)
    forged.write_text("forged", encoding="utf-8")

    with pytest.raises(ValueError, match="--reset"):
        prepare_output_directory(output, manifest, reset=False)

    assert forged.read_text(encoding="utf-8") == "forged"


def test_run_always_disables_gabriel_checkpoint_reuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet = tmp_path / "packet"
    media = packet / "media"
    media.mkdir(parents=True)
    (media / "SCV-001.jpg").write_bytes(b"image")
    manifest = {
        "media": [
            {
                "coding_id": "SCV-001",
                "media_file": "media/SCV-001.jpg",
                "media_sha256": hashlib.sha256(b"image").hexdigest(),
            }
        ]
    }
    manifest_path = packet / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    codebook_path = tmp_path / "codebook.json"
    codebook_path.write_text(
        json.dumps(
            {
                "fields": [
                    {"name": "present", "type": "boolean", "definition": "Presence."}
                ]
            }
        ),
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    async def fake_whatever(**kwargs: Any) -> pd.DataFrame:
        captured.update(kwargs)
        return pd.DataFrame(
            [
                {
                    "coding_id": "SCV-001",
                    "Response JSON": {
                        "annotations": [
                            {
                                "field": "present",
                                "value": False,
                                "evidence": "",
                                "unknown_reason": None,
                            }
                        ],
                        "overall_notes": "",
                    },
                }
            ]
        )

    monkeypatch.setattr(runner.gabriel, "whatever", fake_whatever)
    monkeypatch.setattr(runner, "make_hermes_response_fn", lambda *_: object())
    args = Namespace(
        packet_manifest=manifest_path,
        codebook=codebook_path,
        output_dir=tmp_path / "output",
        provider="provider",
        model="model",
        parallelism=1,
        expected_count=1,
        reset=False,
    )

    asyncio.run(runner.run(args))

    assert captured["reset_files"] is True
    assert captured["image_column"] == "image_data"
    assert captured["df"].loc[0, "image_data"] == base64.b64encode(b"image").decode("ascii")
