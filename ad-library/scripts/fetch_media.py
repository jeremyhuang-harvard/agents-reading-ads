#!/usr/bin/env python3
"""Re-download the ad creatives listed in data/media_manifest.csv and verify their SHA-256.

Added for the public release, which does not redistribute ad creatives. Files are written to
the paths the original collectors used (data/raw/<source>/<run>/media/...), so every
downstream script (labelling, report builders, the agent-feeds stimuli) finds them unchanged.

    python scripts/fetch_media.py                       # everything (~0.7 GB, 1,480 files)
    python scripts/fetch_media.py --run snap_fr_betting_competitors   # one collection
    python scripts/fetch_media.py --sha256 922e8309...  # specific files

Standard library only. Be polite: the default pause between requests is 0.5 s.

URLs are the public ad-library links recorded at collection time. Snap's CDN links have kept
working, but they can expire; when one fails, the script asks the public Snap Ads Gallery
detail endpoint for a fresh link for the same ad (no account needed). TikTok's signed video
links expire within a day, so TikTok files usually have to be re-located by hand from the
`detail_url` page. A file is only kept if its SHA-256 matches the manifest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "media_manifest.csv"
UA = "agents-reading-ads-replication/1.0 (non-commercial academic research)"


def get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fresh_snap_urls(row: dict) -> list[str]:
    """Ask the public Snap Ads Gallery detail endpoint for current media links for this ad."""
    try:
        payload = json.loads(get(row["detail_url"], timeout=60))
    except (urllib.error.URLError, TimeoutError, ValueError):
        return []
    ad = payload.get("ad_preview") or payload
    urls = [ad.get("top_snap_media_download_link"),
            (ad.get("app_install_preview") or {}).get("media_download_link")]
    for snap in ((ad.get("composite_preview") or {}).get("ad_snaps") or []):
        urls.append(snap.get("top_snap_media_download_link"))
    return [u for u in urls if u]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", help="only rows whose run path starts with this (e.g. snap_fr_betting_competitors)")
    ap.add_argument("--source", choices=["snap", "bing", "tiktok"])
    ap.add_argument("--sha256", nargs="*", help="only these files")
    ap.add_argument("--sleep", type=float, default=0.5)
    args = ap.parse_args()

    rows = list(csv.DictReader(MANIFEST.open()))
    wanted: dict[str, list[dict]] = {}
    for r in rows:
        if args.run and not r["run"].startswith(args.run):
            continue
        if args.source and r["source"] != args.source:
            continue
        if args.sha256 and r["sha256"] not in args.sha256:
            continue
        wanted.setdefault(r["sha256"], []).append(r)

    ok = present = failed = 0
    for sha, group in wanted.items():
        targets = sorted({ROOT / r["local_path"] for r in group})
        if all(t.exists() and hashlib.sha256(t.read_bytes()).hexdigest() == sha for t in targets):
            present += 1
            continue
        data = None
        candidates = [r["url"] for r in group if r["url"]]
        for i, url in enumerate(candidates + ["<fresh>"]):
            if url == "<fresh>":
                snap = [r for r in group if r["source"] == "snap"]
                extra = fresh_snap_urls(snap[0]) if snap else []
                for u in extra:
                    try:
                        blob = get(u)
                    except (urllib.error.URLError, TimeoutError):
                        continue
                    if hashlib.sha256(blob).hexdigest() == sha:
                        data = blob
                        break
                break
            try:
                blob = get(url)
            except (urllib.error.URLError, TimeoutError):
                continue
            if hashlib.sha256(blob).hexdigest() == sha:
                data = blob
                break
        if data is None:
            failed += 1
            print(f"FAILED {sha} ({group[0]['source']} ad {group[0]['ad_id']}; see {group[0]['detail_url'] or 'manifest'})",
                  file=sys.stderr)
        else:
            for t in targets:
                t.parent.mkdir(parents=True, exist_ok=True)
                t.write_bytes(data)
            ok += 1
        time.sleep(args.sleep)
    print(f"files: {len(wanted)} requested, {present} already present, {ok} downloaded and verified, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
