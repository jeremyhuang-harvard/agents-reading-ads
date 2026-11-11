import json
from pathlib import Path

import pandas as pd

from run_gabriel_salience_poc import (
    build_analysis_frame,
    build_feature_prompt,
    write_report,
)


def test_build_analysis_frame_uses_representative_media_and_ad_context(tmp_path: Path):
    image = tmp_path / "ad.jpg"
    image.write_bytes(b"fake")
    manifest = {
        "ads": [
            {
                "ad_id": "123",
                "advertiser_name": "Example Brand",
                "title": "Save today",
                "description": "A short offer",
                "sin_category": "betting",
                "representative_media": {"local_path": str(image)},
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    frame = build_analysis_frame(manifest_path)

    assert list(frame["ad_id"]) == ["123"]
    assert list(frame["image_path"]) == [str(image.resolve())]
    assert list(frame["sin_category"]) == ["betting"]
    assert "Example Brand" in frame.loc[0, "prompt"]
    assert "Save today" in frame.loc[0, "prompt"]


def test_feature_prompt_requests_observable_salience_features():
    prompt = build_feature_prompt("Brand", "Title", "Description")

    assert "observable" in prompt.lower()
    assert "salience" in prompt.lower()
    assert "json" in prompt.lower()


def test_write_report_supports_source_specific_title_and_category(tmp_path: Path):
    report = tmp_path / "report.md"
    per_ad = pd.DataFrame(
        [
            {
                "ad_id": "123",
                "advertiser_name": "Example Brand",
                "title": "Example ad",
                "sin_category": "alcohol",
                "Response JSON": {"summary": "Summary", "features": []},
            }
        ]
    )

    write_report(
        report,
        Path("manifest.json"),
        per_ad,
        {"candidate_features": [], "sample_limitations": [], "next_validation_steps": []},
        "model",
        report_title="TikTok sin-product salience proof of concept",
    )

    text = report.read_text()
    assert text.startswith("# TikTok sin-product salience proof of concept")
    assert "**Category:** alcohol" in text
