#!/usr/bin/env python3
"""Collect a tiny, auditable sample from Microsoft's public Bing Ad Library API."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_URL = "https://adlibrary.api.bingads.microsoft.com/api/v1/Ads"
USER_AGENT = "betting-ads-research/0.1 (academic research proof of concept)"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_assets(raw: str | None) -> list[dict[str, Any]]:
    if not raw:
        return []
    values = json.loads(raw)
    if not isinstance(values, list):
        raise ValueError("AssetJson must decode to a list")
    assets: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict) or not value.get("AssetUrl"):
            continue
        assets.append(
            {
                "width": int(value.get("Width") or 0),
                "height": int(value.get("Height") or 0),
                "asset_type": str(value.get("AssetType") or "Unknown"),
                "asset_url": str(value["AssetUrl"]),
            }
        )
    return assets


def choose_representative_asset(assets: list[dict[str, Any]]) -> dict[str, Any] | None:
    images = [asset for asset in assets if asset.get("asset_type", "").lower() == "image"]
    if not images:
        return None

    def score(asset: dict[str, Any]) -> tuple[int, int]:
        width = int(asset.get("width") or 0)
        height = int(asset.get("height") or 0)
        landscape = int(width > height and width / max(height, 1) >= 1.4)
        return landscape, width * height

    return max(images, key=score)


def safe_extension(url: str, content_type: str) -> str:
    media_type = content_type.split(";", 1)[0].strip().lower()
    extension = (
        mimetypes.guess_extension(media_type)
        if media_type and media_type != "application/octet-stream"
        else None
    )
    if extension:
        return ".jpg" if extension == ".jpe" else extension
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4"}:
        return suffix
    return ".bin"


def fetch(url: str) -> tuple[bytes, int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), response.status, response.headers.get("content-type", "")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect(limit: int, output_root: Path) -> dict[str, Any]:
    if not 1 <= limit <= 24:
        raise ValueError("limit must be between 1 and 24")

    query_url = f"{API_URL}?{urllib.parse.urlencode({'$top': limit, '$skip': 0})}"
    raw, status, content_type = fetch(query_url)
    payload = json.loads(raw)
    rows = payload.get("value", [])
    if not isinstance(rows, list):
        raise ValueError("Bing response did not contain a value list")

    captured_at = utc_now()
    run_id = captured_at.replace(":", "").replace("+00:00", "Z")
    run_dir = output_root / f"run_id={run_id}"
    raw_dir = run_dir / "raw"
    media_dir = run_dir / "media"
    raw_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{sha256(raw)}.json"
    raw_path.write_bytes(raw)

    ads: list[dict[str, Any]] = []
    for row in rows[:limit]:
        assets = parse_assets(row.get("AssetJson"))
        representative = choose_representative_asset(assets)
        media_record: dict[str, Any] | None = None
        if representative:
            media_raw, media_status, media_type = fetch(representative["asset_url"])
            digest = sha256(media_raw)
            extension = safe_extension(representative["asset_url"], media_type)
            media_path = media_dir / f"{digest}{extension}"
            media_path.write_bytes(media_raw)
            media_record = {
                **representative,
                "http_status": media_status,
                "content_type": media_type,
                "byte_length": len(media_raw),
                "sha256": digest,
                "local_path": str(media_path.resolve()),
            }
        ads.append(
            {
                "ad_id": str(row.get("AdId")),
                "advertiser_id": str(row.get("AdvertiserId")),
                "advertiser_name": row.get("AdvertiserName"),
                "title": row.get("Title"),
                "description": row.get("Description"),
                "display_url": row.get("DisplayUrl"),
                "destination_url": row.get("DestinationUrl"),
                "asset_count": len(assets),
                "assets": assets,
                "representative_media": media_record,
            }
        )

    manifest = {
        "source": "Microsoft/Bing EU Ad Library API",
        "endpoint": API_URL,
        "request_url": query_url,
        "captured_at_utc": captured_at,
        "http_status": status,
        "content_type": content_type,
        "raw_sha256": sha256(raw),
        "raw_path": str(raw_path.resolve()),
        "reported_count": payload.get("@odata.count"),
        "ad_count": len(ads),
        "ads": ads,
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return {"run_dir": str(run_dir.resolve()), "manifest": str(manifest_path.resolve()), "ads": ads}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output-root", type=Path, default=Path("data/raw/bing_poc"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = collect(args.limit, args.output_root.resolve())
    print(json.dumps({"run_dir": result["run_dir"], "manifest": result["manifest"], "ad_count": len(result["ads"])}, indent=2))


if __name__ == "__main__":
    main()
