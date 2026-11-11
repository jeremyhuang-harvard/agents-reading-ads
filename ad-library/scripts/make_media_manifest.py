#!/usr/bin/env python3
"""Write data/media_manifest.csv: one row per (ad, media file) we downloaded.

Added for the public release. The ad creatives themselves are not redistributed, so this
manifest records, for every file the collectors stored, where it came from (the public
ad-library URL returned at collection time), its SHA-256 and the path the original code
expects it at. `scripts/fetch_media.py` uses it to re-download and verify the files.

Standard library only:  python scripts/make_media_manifest.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "media_manifest.csv"
FIELDS = ["source", "run", "ad_id", "advertiser_query", "role", "snap_index", "media_type",
          "sha256", "bytes", "url", "detail_url", "local_path"]


def rel(run_dir: Path, local: str) -> str:
    """Path of a media file relative to the ad-library root."""
    if local.startswith("data/raw/"):
        return local
    return (run_dir / local).resolve().relative_to(ROOT.resolve()).as_posix()


def snap_rows() -> list[dict]:
    rows = []
    for run_dir in sorted(RAW.glob("snap_*/run_id=*")):
        records = run_dir / "records.jsonl"
        if not records.exists():
            continue
        story_urls: dict[tuple[str, int], str] = {}
        for line in records.open():
            r = json.loads(line)
            snaps = ((r["ad"].get("composite_preview") or {}).get("ad_snaps") or [])
            for i, s in enumerate(snaps):
                if s.get("top_snap_media_download_link"):
                    story_urls[(r["ad_id"], i)] = s["top_snap_media_download_link"]
            m = r.get("media")
            if not m or not m.get("sha256"):
                continue
            rows.append({"source": "snap", "run": run_dir.relative_to(RAW).as_posix(), "ad_id": r["ad_id"],
                         "advertiser_query": r.get("query_advertiser", ""), "role": m.get("role", ""),
                         "snap_index": "", "media_type": m.get("media_type", ""), "sha256": m["sha256"],
                         "bytes": m.get("byte_length", ""), "url": m.get("url", ""),
                         "detail_url": f"https://adsapi.snapchat.com/v1/ads_library/ads/{r['ad_id']}",
                         "local_path": rel(run_dir, m["local_path"])})
        backfill = run_dir.parent / f"story_backfill_{run_dir.name}"
        if (backfill / "records.jsonl").exists():
            for line in (backfill / "records.jsonl").open():
                b = json.loads(line)
                if not b.get("sha256"):
                    continue
                rows.append({"source": "snap", "run": backfill.relative_to(RAW).as_posix(), "ad_id": b["ad_id"],
                             "advertiser_query": b.get("query_advertiser", ""), "role": "story_snap",
                             "snap_index": b["snap_index"], "media_type": b.get("media_type", ""),
                             "sha256": b["sha256"], "bytes": b.get("byte_length", ""),
                             "url": story_urls.get((b["ad_id"], b["snap_index"]), ""),
                             "detail_url": f"https://adsapi.snapchat.com/v1/ads_library/ads/{b['ad_id']}",
                             "local_path": rel(backfill, b["local_path"])})
    return rows


def bing_rows() -> list[dict]:
    rows = []
    for man in sorted(RAW.glob("bing_poc/run_id=*/manifest.json")):
        m = json.loads(man.read_text())
        for ad in m["ads"]:
            rm = ad.get("representative_media") or {}
            if rm.get("sha256"):
                rows.append({"source": "bing", "run": man.parent.relative_to(RAW).as_posix(), "ad_id": ad["ad_id"],
                             "advertiser_query": ad.get("advertiser_name", ""), "role": "representative_media",
                             "snap_index": "", "media_type": rm.get("asset_type", ""), "sha256": rm["sha256"],
                             "bytes": rm.get("byte_length", ""), "url": rm.get("asset_url", ""), "detail_url": "",
                             "local_path": rm["local_path"]})
    return rows


def tiktok_rows() -> list[dict]:
    rows = []
    for man in sorted(RAW.glob("tiktok_sin_poc/run_id=*/manifest.json")):
        m = json.loads(man.read_text())
        for ad in m["ads"]:
            vm = ad.get("video_media") or {}
            if vm.get("sha256"):
                rows.append({"source": "tiktok", "run": man.parent.relative_to(RAW).as_posix(), "ad_id": ad["ad_id"],
                             "advertiser_query": ad.get("advertiser_name", ""), "role": "video",
                             "snap_index": "", "media_type": vm.get("content_type", ""), "sha256": vm["sha256"],
                             "bytes": vm.get("byte_length", ""), "url": vm.get("source_url", ""),
                             "detail_url": ad.get("detail_url", ""), "local_path": vm["local_path"]})
    return rows


def main() -> None:
    rows = snap_rows() + bing_rows() + tiktok_rows()
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    unique = len({r["sha256"] for r in rows})
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} rows, {unique} unique files")


if __name__ == "__main__":
    main()
