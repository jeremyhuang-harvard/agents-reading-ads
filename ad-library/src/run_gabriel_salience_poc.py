#!/usr/bin/env python3
"""Use GABRIEL with a Hermes OAuth transport to explore ad-salience features."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import gabriel
import pandas as pd


def build_feature_prompt(advertiser: str, title: str, description: str) -> str:
    return f"""
You are conducting exploratory social-science measurement of one advertisement.
Inspect only the supplied image and the source metadata below.

Advertiser: {advertiser or 'unknown'}
Title: {title or 'unknown'}
Description: {description or 'unknown'}

Identify observable features that could shape visual attention, memory retrieval,
emotion, perceived relevance, or behavioral salience. Do not infer actual user
exposure or causal effects. Return JSON with this schema:
{{
  "summary": "one sentence",
  "features": [
    {{
      "name": "short reusable construct name",
      "family": "visual|textual|affective|identity|reward|urgency|social|risk|other",
      "evidence": "specific visible evidence",
      "hypothesized_salience_pathway": "why this could attract attention or cue memory"
    }}
  ]
}}
Return 5 to 8 nonredundant features. Use only observable evidence. Return JSON only.
""".strip()


def build_analysis_frame(manifest_path: Path) -> pd.DataFrame:
    manifest = json.loads(manifest_path.read_text())
    rows: list[dict[str, str]] = []
    for ad in manifest.get("ads", []):
        media = ad.get("representative_media") or {}
        local_path = media.get("local_path")
        if not local_path or not Path(local_path).exists():
            continue
        rows.append(
            {
                "ad_id": str(ad.get("ad_id")),
                "advertiser_name": str(ad.get("advertiser_name") or ""),
                "title": str(ad.get("title") or ""),
                "description": str(ad.get("description") or ""),
                "sin_category": str(ad.get("sin_category") or ""),
                "image_path": str(Path(local_path).resolve()),
                "prompt": build_feature_prompt(
                    str(ad.get("advertiser_name") or ""),
                    str(ad.get("title") or ""),
                    str(ad.get("description") or ""),
                ),
            }
        )
    if not rows:
        raise ValueError("manifest has no ads with downloaded representative media")
    return pd.DataFrame(rows)


def strip_hermes_metadata(text: str) -> str:
    lines = [line for line in text.splitlines() if not line.startswith("session_id:")]
    return "\n".join(lines).strip()


def make_hermes_response_fn(provider: str, model: str):
    async def hermes_response(
        prompt: str,
        *,
        images: list[str] | None = None,
        n: int = 1,
        **_kwargs: Any,
    ) -> list[str]:
        if n != 1:
            raise ValueError("Hermes transport currently supports n=1")

        prompt_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, dir=os.environ.get("TMPDIR")
        )
        prompt_file.write(prompt)
        prompt_file.close()
        image_path: str | None = None
        try:
            command = [
                "hermes",
                "chat",
                "-Q",
                "--source",
                "tool",
                "--provider",
                provider,
                "-m",
                model,
                "--max-turns",
                "3",
                "--query-file",
                prompt_file.name,
            ]
            if images:
                image_file = tempfile.NamedTemporaryFile(
                    mode="wb", suffix=".jpg", delete=False, dir=os.environ.get("TMPDIR")
                )
                image_file.write(base64.b64decode(images[0]))
                image_file.close()
                image_path = image_file.name
                command.extend(["--image", image_path])

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise RuntimeError(
                    f"Hermes transport failed ({process.returncode}): "
                    f"{stderr.decode(errors='replace').strip()}"
                )
            return [strip_hermes_metadata(stdout.decode(errors="replace"))]
        finally:
            Path(prompt_file.name).unlink(missing_ok=True)
            if image_path:
                Path(image_path).unlink(missing_ok=True)

    return hermes_response


def response_jsons(frame: pd.DataFrame) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for value in frame.get("Response JSON", []):
        if isinstance(value, dict):
            values.append(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            values.append(value[0])
    return values


def build_synthesis_prompt(per_ad: pd.DataFrame) -> str:
    records = []
    for _, row in per_ad.iterrows():
        parsed = row.get("Response JSON")
        records.append(
            {
                "ad_id": row.get("ad_id"),
                "advertiser_name": row.get("advertiser_name"),
                "title": row.get("title"),
                "sin_category": row.get("sin_category"),
                "analysis": parsed,
            }
        )
    return f"""
You are consolidating an exploratory five-ad proof of concept. The evidence below
comes from GABRIEL multimodal calls. Produce a candidate measurement taxonomy,
not causal conclusions.

AD ANALYSES:
{json.dumps(records, ensure_ascii=False, indent=2)}

Return JSON with:
{{
  "candidate_features": [
    {{
      "name": "reusable feature name",
      "definition": "observable operational definition",
      "why_it_may_be_salient": "attention, memory, emotion, identity, reward, urgency, or risk pathway",
      "example_ad_ids": ["IDs"],
      "recommended_measurement": "boolean, category, count, or 0-100 rating"
    }}
  ],
  "sample_limitations": ["limitations"],
  "next_validation_steps": ["steps"]
}}
Return 10 to 15 candidate features. Return JSON only.
""".strip()


def write_report(
    report_path: Path,
    manifest_path: Path,
    per_ad: pd.DataFrame,
    synthesis: dict[str, Any],
    model: str,
    report_title: str = "Bing → GABRIEL salience-feature proof of concept",
) -> None:
    lines = [
        f"# {report_title}",
        "",
        f"**Source manifest:** `{manifest_path}`",
        f"**Ads analyzed:** {len(per_ad)}",
        f"**Transport model:** `{model}` via Hermes OAuth",
        "**Status:** Exploratory feature discovery; not a validated codebook or causal result.",
        "",
        "## Candidate features",
        "",
    ]
    for feature in synthesis.get("candidate_features", []):
        lines.extend(
            [
                f"### {feature.get('name', 'Unnamed feature')}",
                "",
                f"- **Definition:** {feature.get('definition', '')}",
                f"- **Potential pathway:** {feature.get('why_it_may_be_salient', '')}",
                f"- **Example ads:** {', '.join(map(str, feature.get('example_ad_ids', [])))}",
                f"- **Suggested measure:** {feature.get('recommended_measurement', '')}",
                "",
            ]
        )
    lines.extend(["## Sample limitations", ""])
    lines.extend(f"- {item}" for item in synthesis.get("sample_limitations", []))
    lines.extend(["", "## Next validation steps", ""])
    lines.extend(f"- {item}" for item in synthesis.get("next_validation_steps", []))
    lines.extend(["", "## Per-ad exploratory outputs", ""])
    for _, row in per_ad.iterrows():
        parsed = row.get("Response JSON") or {}
        lines.extend(
            [
                f"### {row.get('ad_id')} — {row.get('title')}",
                "",
                f"**Advertiser:** {row.get('advertiser_name')}",
                f"**Category:** {row.get('sin_category') or 'unspecified'}",
                f"**Summary:** {parsed.get('summary', '') if isinstance(parsed, dict) else ''}",
                "",
            ]
        )
        if isinstance(parsed, dict):
            for feature in parsed.get("features", []):
                lines.append(
                    f"- **{feature.get('name', '')}:** {feature.get('evidence', '')} "
                    f"— {feature.get('hypothesized_salience_pathway', '')}"
                )
        lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n")


async def run(args: argparse.Namespace) -> None:
    frame = build_analysis_frame(args.manifest)
    response_fn = make_hermes_response_fn(args.provider, args.model)
    per_ad = await gabriel.whatever(
        df=frame,
        column_name="prompt",
        identifier_column="ad_id",
        image_column="image_path",
        save_dir=str(args.output_dir / "per_ad"),
        file_name="salience_features.csv",
        model=args.model,
        json_mode=True,
        n_parallels=1,
        reset_files=args.reset,
        response_fn=response_fn,
        return_original_columns=True,
        image_detail="high",
    )
    if not response_jsons(per_ad):
        raise RuntimeError("GABRIEL returned no parsed per-ad JSON responses")

    synthesis_prompt = build_synthesis_prompt(per_ad)
    synthesis_frame = await gabriel.whatever(
        prompts=[synthesis_prompt],
        identifiers=["five-ad-taxonomy"],
        save_dir=str(args.output_dir / "synthesis"),
        file_name="candidate_taxonomy.csv",
        model=args.model,
        json_mode=True,
        n_parallels=1,
        reset_files=args.reset,
        response_fn=response_fn,
    )
    syntheses = response_jsons(synthesis_frame)
    if not syntheses:
        raise RuntimeError("GABRIEL returned no parsed synthesis JSON response")
    write_report(
        args.report,
        args.manifest,
        per_ad,
        syntheses[0],
        args.model,
        report_title=args.report_title,
    )
    print(json.dumps({"ads_analyzed": len(per_ad), "report": str(args.report.resolve())}, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/bing_gabriel_poc"))
    parser.add_argument("--report", type=Path, default=Path("docs/bing_gabriel_poc_results.md"))
    parser.add_argument("--provider", default="openai-codex")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument(
        "--report-title",
        default="Bing → GABRIEL salience-feature proof of concept",
    )
    parser.add_argument("--reset", action="store_true")
    return parser.parse_args()


def main() -> None:
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
