#!/usr/bin/env python3
"""Collect a bounded, auditable sample from Snap's public Ads Gallery API."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import mimetypes
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, BinaryIO, Callable

SEARCH_URL = "https://adsapi.snapchat.com/v1/ads_library/ads/search"
DETAIL_URL = "https://adsapi.snapchat.com/v1/ads_library/ads/{ad_id}"
USER_AGENT = "betting-ads-research/0.1 (non-commercial academic research)"
JsonFetcher = Callable[[str, dict[str, Any] | None], tuple[bytes, int, str]]
MediaFetcher = Callable[[str, int], tuple[bytes, int, str]]


def utc_datetime_now() -> datetime:
    return datetime.now(timezone.utc)


class HttpStatusError(RuntimeError):
    def __init__(self, status: int):
        super().__init__(f"HTTP status {status}")
        self.status = status


def fetch_with_retry(
    fetch_fn: Callable[..., tuple[bytes, int, str]],
    *args: Any,
    retry_attempts: int,
    retry_base_seconds: float,
    retry_max_seconds: float,
    sleep_fn: Callable[[float], None],
    clock_fn: Callable[[], datetime] = utc_datetime_now,
) -> tuple[bytes, int, str]:
    for attempt in range(retry_attempts):
        try:
            result = fetch_fn(*args)
            status = result[1]
            if 200 <= status < 400:
                return result
            error: Exception = HttpStatusError(status)
        except urllib.error.HTTPError as exc:
            status = exc.code
            error = exc

        transient = status == 429 or 500 <= status <= 599
        if not transient or attempt + 1 >= retry_attempts:
            raise error
        delay = min(retry_max_seconds, retry_base_seconds * (2**attempt))
        headers = getattr(error, "headers", None)
        retry_after = headers.get("Retry-After") if headers is not None else None
        if retry_after is not None:
            parsed_delay: float | None = None
            try:
                numeric_delay = float(retry_after)
                if math.isfinite(numeric_delay):
                    parsed_delay = numeric_delay
            except (TypeError, ValueError):
                try:
                    retry_at = parsedate_to_datetime(str(retry_after))
                    if retry_at.tzinfo is None:
                        retry_at = retry_at.replace(tzinfo=timezone.utc)
                    now = clock_fn()
                    if now.tzinfo is None:
                        now = now.replace(tzinfo=timezone.utc)
                    parsed_delay = (retry_at - now).total_seconds()
                except (TypeError, ValueError, OverflowError):
                    parsed_delay = None
            if parsed_delay is not None:
                delay = parsed_delay
        delay = min(retry_max_seconds, max(0.0, delay))
        sleep_fn(delay)

    raise AssertionError("retry loop exited unexpectedly")


@dataclass
class StorageBudget:
    max_bytes: int
    used_bytes: int = 0

    def reserve(self, byte_count: int) -> None:
        if byte_count < 0:
            raise ValueError("byte_count must be nonnegative")
        if self.used_bytes + byte_count > self.max_bytes:
            raise RuntimeError("storage budget would be exceeded")
        self.used_bytes += byte_count


@dataclass(frozen=True)
class CollectionConfig:
    roster: list[dict[str, Any]]
    target: int
    max_storage_gb: float
    per_file_max_mb: float


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_preview_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    request_status = payload.get("request_status")
    if request_status != "SUCCESS":
        context = _status_context(
            payload,
            status_name="request_status",
            identifier_name="request_id",
        )
        raise RuntimeError(f"incomplete search page: {context}")

    records: list[dict[str, Any]] = []
    previews = payload.get("ad_previews", [])
    if not isinstance(previews, list):
        raise RuntimeError("incomplete search page: ad_previews is not a list")
    for index, item in enumerate(previews):
        if not isinstance(item, dict):
            raise RuntimeError(f"incomplete search page: invalid subrequest index={index}")
        if item.get("sub_request_status") != "SUCCESS":
            context = _status_context(
                item,
                status_name="sub_request_status",
                identifier_name="sub_request_id",
            )
            raise RuntimeError(f"incomplete search page: {context} index={index}")
        ad = item.get("ad_preview")
        if isinstance(ad, dict) and ad.get("id"):
            records.append(ad)
    return records


def _status_context(
    payload: dict[str, Any], status_name: str, identifier_name: str
) -> str:
    parts = [f"{status_name}={_safe_context_value(payload.get(status_name))}"]
    for name in (identifier_name, "error_code"):
        if payload.get(name) is not None:
            parts.append(f"{name}={_safe_context_value(payload[name])}")
    return " ".join(parts)


def _safe_context_value(value: Any) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text[:160]


def select_new_candidates(
    records: list[dict[str, Any]], seen_ids: set[str], quota: int
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for record in records:
        ad_id = str(record.get("id") or "")
        if not ad_id or ad_id in seen_ids or ad_id in selected_ids:
            continue
        selected.append(record)
        selected_ids.add(ad_id)
        if len(selected) >= quota:
            break
    return selected


def read_limited(
    stream: BinaryIO,
    budget: StorageBudget,
    per_file_max: int,
    chunk_size: int = 1024 * 1024,
) -> bytes:
    chunks: list[bytes] = []
    byte_count = 0
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        byte_count += len(chunk)
        if byte_count > per_file_max:
            raise RuntimeError("per-file media limit would be exceeded")
        chunks.append(chunk)
    budget.reserve(byte_count)
    return b"".join(chunks)


def choose_primary_media(ad: dict[str, Any]) -> dict[str, Any] | None:
    top_url = ad.get("top_snap_media_download_link")
    if top_url:
        return {
            "role": "top_snap",
            "media_type": ad.get("top_snap_media_type"),
            "url": str(top_url),
        }
    composite = ad.get("composite_preview")
    snaps = composite.get("ad_snaps") if isinstance(composite, dict) else None
    if isinstance(snaps, list):
        linked = [
            (index, snap)
            for index, snap in enumerate(snaps)
            if isinstance(snap, dict) and snap.get("top_snap_media_download_link")
        ]
        if linked:
            index, snap = linked[0]
            return {
                "role": "story_snap",
                "media_type": snap.get("top_snap_media_type"),
                "url": str(snap["top_snap_media_download_link"]),
                "snap_index": index,
                "story_snap_link_count": len(linked),
            }
    app_preview = ad.get("app_install_preview")
    if isinstance(app_preview, dict) and app_preview.get("media_download_link"):
        return {
            "role": "app_install_preview",
            "media_type": None,
            "url": str(app_preview["media_download_link"]),
        }
    return None


def safe_extension(url: str, content_type: str) -> str:
    media_type = content_type.split(";", 1)[0].strip().lower()
    extension = (
        mimetypes.guess_extension(media_type)
        if media_type and media_type != "application/octet-stream"
        else None
    )
    if extension:
        return ".jpg" if extension in {".jpe", ".jpeg"} else extension
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return ".bin"


def default_json_fetcher(
    url: str, body: dict[str, Any] | None
) -> tuple[bytes, int, str]:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"User-Agent": USER_AGENT}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.status, response.headers.get("content-type", "")


def default_media_fetcher(url: str, per_file_max: int) -> tuple[bytes, int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        local_budget = StorageBudget(max_bytes=per_file_max)
        content = read_limited(response, budget=local_budget, per_file_max=per_file_max)
        return content, response.status, response.headers.get("content-type", "")


def write_budgeted(path: Path, content: bytes, budget: StorageBudget) -> None:
    budget.reserve(len(content))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def collect_sample(
    roster: list[dict[str, Any]],
    output_root: Path,
    target: int,
    max_bytes: int,
    per_file_max: int,
    delay_seconds: float,
    detail_limit: int = 0,
    json_fetcher: JsonFetcher = default_json_fetcher,
    media_fetcher: MediaFetcher = default_media_fetcher,
    now_fn: Callable[[], str] = utc_now,
    sleep_fn: Callable[[float], None] = time.sleep,
    max_pages_per_stratum: int = 100,
    retry_attempts: int = 4,
    retry_base_seconds: float = 1.0,
    retry_max_seconds: float = 30.0,
) -> dict[str, Any]:
    if target < 1:
        raise ValueError("target must be positive")
    if max_bytes < 1 or per_file_max < 1:
        raise ValueError("storage limits must be positive")
    if retry_attempts < 1:
        raise ValueError("retry_attempts must be positive")
    if retry_base_seconds < 0 or retry_max_seconds < 0:
        raise ValueError("retry delays must be nonnegative")

    captured_at = now_fn()
    run_id = captured_at.replace(":", "").replace("+00:00", "Z")
    run_dir = output_root / f"run_id={run_id}"
    raw_search_dir = run_dir / "raw" / "search"
    raw_detail_dir = run_dir / "raw" / "detail"
    media_dir = run_dir / "media"
    records_path = run_dir / "records.jsonl"
    manifest_path = run_dir / "manifest.json"
    for directory in (raw_search_dir, raw_detail_dir, media_dir):
        directory.mkdir(parents=True, exist_ok=False)

    budget = StorageBudget(max_bytes=max_bytes)
    seen_ids: set[str] = set()
    media_paths: dict[str, str] = {}
    record_count = 0
    no_media_count = 0
    media_error_count = 0
    detail_request_count = 0
    budget_exhausted = False
    strata_results: list[dict[str, Any]] = []

    with records_path.open("w", encoding="utf-8") as records_file:
        for stratum_index, stratum in enumerate(roster):
            if record_count >= target or budget_exhausted:
                break
            category = str(stratum["category"])
            advertiser = str(stratum["advertiser"])
            country = str(stratum["country"]).lower()
            quota = min(int(stratum["quota"]), target - record_count)
            selected_in_stratum = 0
            pages_fetched = 0
            next_url: str | None = SEARCH_URL
            next_body: dict[str, Any] | None = {
                "countries": [country],
                "paying_advertiser_name": advertiser,
            }

            while (
                next_url
                and selected_in_stratum < quota
                and record_count < target
                and pages_fetched < max_pages_per_stratum
                and not budget_exhausted
            ):
                raw, status, content_type = fetch_with_retry(
                    json_fetcher,
                    next_url,
                    next_body,
                    retry_attempts=retry_attempts,
                    retry_base_seconds=retry_base_seconds,
                    retry_max_seconds=retry_max_seconds,
                    sleep_fn=sleep_fn,
                )
                search_path = raw_search_dir / f"stratum_{stratum_index:03d}_page_{pages_fetched:04d}.json"
                try:
                    write_budgeted(search_path, raw, budget)
                except RuntimeError:
                    budget_exhausted = True
                    break
                payload = json.loads(raw)
                remaining = min(quota - selected_in_stratum, target - record_count)
                candidates = select_new_candidates(
                    iter_preview_records(payload), seen_ids=seen_ids, quota=remaining
                )

                for candidate in candidates:
                    ad_id = str(candidate["id"])
                    detail_status: int | None = None
                    detail_content_type: str | None = None
                    detail_error: str | None = None
                    detail_skipped = detail_request_count >= detail_limit
                    ad = candidate
                    if not detail_skipped:
                        detail_request_count += 1
                        try:
                            detail_raw, detail_status, detail_content_type = fetch_with_retry(
                                json_fetcher,
                                DETAIL_URL.format(ad_id=urllib.parse.quote(ad_id)),
                                None,
                                retry_attempts=retry_attempts,
                                retry_base_seconds=retry_base_seconds,
                                retry_max_seconds=retry_max_seconds,
                                sleep_fn=sleep_fn,
                            )
                            write_budgeted(raw_detail_dir / f"{ad_id}.json", detail_raw, budget)
                            detail_payload = json.loads(detail_raw)
                            if isinstance(detail_payload.get("ad_preview"), dict):
                                ad = detail_payload["ad_preview"]
                        except Exception as exc:
                            detail_error = f"{type(exc).__name__}: {exc}"
                            if isinstance(exc, RuntimeError) and "storage budget" in str(exc):
                                budget_exhausted = True
                                break

                    selected_media = choose_primary_media(ad)
                    media_record: dict[str, Any] | None = None
                    media_error: str | None = None
                    if selected_media:
                        try:
                            media_raw, media_status, media_content_type = fetch_with_retry(
                                media_fetcher,
                                selected_media["url"],
                                per_file_max,
                                retry_attempts=retry_attempts,
                                retry_base_seconds=retry_base_seconds,
                                retry_max_seconds=retry_max_seconds,
                                sleep_fn=sleep_fn,
                            )
                            digest = sha256(media_raw)
                            relative_path = media_paths.get(digest)
                            if relative_path is None:
                                extension = safe_extension(
                                    selected_media["url"], media_content_type
                                )
                                media_path = media_dir / f"{digest}{extension}"
                                write_budgeted(media_path, media_raw, budget)
                                relative_path = str(media_path.relative_to(run_dir))
                                media_paths[digest] = relative_path
                            media_record = {
                                **selected_media,
                                "http_status": media_status,
                                "content_type": media_content_type,
                                "byte_length": len(media_raw),
                                "sha256": digest,
                                "local_path": relative_path,
                            }
                        except Exception as exc:
                            media_error = f"{type(exc).__name__}: {exc}"
                            media_error_count += 1
                            if isinstance(exc, RuntimeError) and "storage budget" in str(exc):
                                budget_exhausted = True
                    else:
                        no_media_count += 1

                    record = {
                        "ad_id": ad_id,
                        "category": category,
                        "query_advertiser": advertiser,
                        "query_country": country,
                        "captured_at_utc": captured_at,
                        "search_http_status": status,
                        "search_content_type": content_type,
                        "detail_http_status": detail_status,
                        "detail_content_type": detail_content_type,
                        "detail_skipped": detail_skipped,
                        "detail_error": detail_error,
                        "media_error": media_error,
                        "ad": ad,
                        "media": media_record,
                    }
                    records_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    records_file.flush()
                    seen_ids.add(ad_id)
                    record_count += 1
                    selected_in_stratum += 1
                    if record_count >= target or budget_exhausted:
                        break
                    if delay_seconds:
                        sleep_fn(delay_seconds)

                pages_fetched += 1
                paging = payload.get("paging")
                next_url = paging.get("next_link") if isinstance(paging, dict) else None
                if next_url and delay_seconds:
                    sleep_fn(delay_seconds)

            search_exhausted = False
            truncation_reason: str | None = None
            if budget_exhausted:
                truncation_reason = "storage_budget"
            elif next_url is None:
                search_exhausted = True
            elif record_count >= target:
                truncation_reason = "global_target"
            elif selected_in_stratum >= quota:
                truncation_reason = "quota"
            elif pages_fetched >= max_pages_per_stratum:
                truncation_reason = "max_pages"

            strata_results.append(
                {
                    "category": category,
                    "advertiser": advertiser,
                    "country": country,
                    "quota": quota,
                    "selected": selected_in_stratum,
                    "pages_fetched": pages_fetched,
                    "search_exhausted": search_exhausted,
                    "truncation_reason": truncation_reason,
                }
            )

    manifest = {
        "source": "Snap Ads Gallery API",
        "search_endpoint": SEARCH_URL,
        "detail_endpoint_template": DETAIL_URL,
        "captured_at_utc": captured_at,
        "target": target,
        "ad_count": record_count,
        "unique_media_count": len(media_paths),
        "no_media_count": no_media_count,
        "media_error_count": media_error_count,
        "detail_request_count": detail_request_count,
        "max_bytes": max_bytes,
        "stored_bytes": budget.used_bytes,
        "budget_exhausted": budget_exhausted,
        "per_file_max": per_file_max,
        "records_path": str(records_path.relative_to(run_dir)),
        "strata": strata_results,
        "roster": roster,
    }
    manifest_raw = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    write_budgeted(manifest_path, manifest_raw, budget)
    return {
        **manifest,
        "run_dir": str(run_dir.resolve()),
        "records_path": str(records_path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "stored_bytes": budget.used_bytes,
    }


def load_collection_config(
    path: Path,
    target_override: int | None = None,
    max_storage_gb_override: float | None = None,
    per_file_max_mb_override: float | None = None,
) -> CollectionConfig:
    payload = json.loads(path.read_text())
    roster = payload.get("strata") if isinstance(payload, dict) else payload
    if not isinstance(roster, list) or not roster:
        raise ValueError("roster must contain a non-empty list of strata")
    config_target = payload.get("target", 100) if isinstance(payload, dict) else 100
    config_storage = (
        payload.get("storage_cap_gib", 30.0) if isinstance(payload, dict) else 30.0
    )
    config_per_file = (
        payload.get("per_file_max_mib", 512.0) if isinstance(payload, dict) else 512.0
    )
    target = int(config_target if target_override is None else target_override)
    max_storage_gb = float(
        config_storage if max_storage_gb_override is None else max_storage_gb_override
    )
    per_file_max_mb = float(
        config_per_file if per_file_max_mb_override is None else per_file_max_mb_override
    )
    if target < 1:
        raise ValueError("target must be positive")
    if max_storage_gb <= 0 or per_file_max_mb <= 0:
        raise ValueError("storage limits must be positive")
    return CollectionConfig(
        roster=roster,
        target=target,
        max_storage_gb=max_storage_gb,
        per_file_max_mb=per_file_max_mb,
    )


def load_roster(path: Path) -> list[dict[str, Any]]:
    return load_collection_config(path).roster


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roster", type=Path, default=Path("config/snap_pilot_roster.json"))
    parser.add_argument("--output-root", type=Path, default=Path("data/raw/snap_ads"))
    parser.add_argument("--target", type=int)
    parser.add_argument("--max-storage-gb", type=float)
    parser.add_argument("--per-file-max-mb", type=float)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    parser.add_argument("--detail-limit", type=int, default=0)
    parser.add_argument("--max-pages-per-stratum", type=int, default=100)
    parser.add_argument("--retry-attempts", type=int, default=4)
    parser.add_argument("--retry-base-seconds", type=float, default=1.0)
    parser.add_argument("--retry-max-seconds", type=float, default=30.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_collection_config(
        args.roster.resolve(),
        target_override=args.target,
        max_storage_gb_override=args.max_storage_gb,
        per_file_max_mb_override=args.per_file_max_mb,
    )
    result = collect_sample(
        roster=config.roster,
        output_root=args.output_root.resolve(),
        target=config.target,
        max_bytes=int(config.max_storage_gb * 1024**3),
        per_file_max=int(config.per_file_max_mb * 1024**2),
        delay_seconds=args.delay_seconds,
        detail_limit=args.detail_limit,
        max_pages_per_stratum=args.max_pages_per_stratum,
        retry_attempts=args.retry_attempts,
        retry_base_seconds=args.retry_base_seconds,
        retry_max_seconds=args.retry_max_seconds,
    )
    print(
        json.dumps(
            {
                "run_dir": result["run_dir"],
                "manifest": result["manifest_path"],
                "ad_count": result["ad_count"],
                "unique_media_count": result["unique_media_count"],
                "stored_bytes": result["stored_bytes"],
                "budget_exhausted": result["budget_exhausted"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
