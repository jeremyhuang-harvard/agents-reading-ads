"""Polite, cached HTTP access for the demo collectors.

Design rules:
- every response body is cached on disk under ``data/raw/demo/http_cache`` so a
  rerun never re-hits a source (raw data are immutable once written);
- each host has a minimum interval between requests;
- 429/5xx responses are retried with bounded exponential backoff, honoring
  ``Retry-After`` but clamped to ``MAX_BACKOFF``;
- failures are returned as ``Response(ok=False)`` rather than silently dropped.
"""

from __future__ import annotations

import hashlib
import http.client as httpclient
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "data" / "raw" / "demo" / "http_cache"
USER_AGENT = "implicit-ads-research/0.2 (academic research; contact YOUR-EMAIL@example.org)"  # public release: put your own contact here
MAX_BACKOFF = 120.0
MAX_ATTEMPTS = 5

# Minimum seconds between requests to the same host.
HOST_INTERVALS = {
    "web.archive.org": 1.5,
    "archive.org": 1.5,
    "api.gdeltproject.org": 10.0,  # GDELT asks for at most one request per 5 seconds; 6 s still drew 429s in Nov 2026
    "wikimedia.org": 0.2,
}
DEFAULT_INTERVAL = 3.0

_last_request: dict[str, float] = {}


@dataclass
class Response:
    url: str
    ok: bool
    status: int
    body: bytes
    fetched_at: str
    from_cache: bool
    error: str = ""

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", "replace")

    def json(self):
        return json.loads(self.body or b"null")


def _cache_paths(url: str) -> tuple[Path, Path]:
    host = urlparse(url).netloc.replace(":", "_") or "unknown"
    key = hashlib.sha256(url.encode()).hexdigest()
    folder = CACHE_DIR / host
    return folder / f"{key}.body", folder / f"{key}.json"


def _throttle(host: str) -> None:
    interval = DEFAULT_INTERVAL
    for suffix, value in HOST_INTERVALS.items():
        if host == suffix or host.endswith("." + suffix):
            interval = value
            break
    wait = _last_request.get(host, 0.0) + interval - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request[host] = time.monotonic()


def _retry_after(value: str | None, attempt: int) -> float:
    base = min(MAX_BACKOFF, 5.0 * (2**attempt))
    if not value:
        return base
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError):
            return base
    return max(0.0, min(MAX_BACKOFF, seconds))


def get(url: str, *, use_cache: bool = True, cache_errors: bool = False, timeout: int = 60) -> Response:
    body_path, meta_path = _cache_paths(url)
    if use_cache and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        body = body_path.read_bytes() if body_path.exists() else b""
        return Response(url, meta["ok"], meta["status"], body, meta["fetched_at"], True, meta.get("error", ""))

    host = urlparse(url).netloc
    status, body, error = 0, b"", ""
    for attempt in range(MAX_ATTEMPTS):
        _throttle(host)
        try:
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout) as resp:
                status, body, error = resp.status, resp.read(), ""
                break
        except HTTPError as exc:
            status, error = exc.code, f"HTTP {exc.code}"
            body = exc.read() or b""
            if exc.code == 429 or exc.code >= 500:
                time.sleep(_retry_after(exc.headers.get("Retry-After"), attempt))
                continue
            break
        except (URLError, TimeoutError, ConnectionError, httpclient.HTTPException, OSError) as exc:
            status, error = 0, f"{type(exc).__name__}: {exc}"
            time.sleep(min(MAX_BACKOFF, 5.0 * (2**attempt)))
            continue

    ok = 200 <= status < 300
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if ok or cache_errors:
        body_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = body_path.with_suffix(".tmp")
        tmp.write_bytes(body)
        tmp.replace(body_path)
        meta_path.write_text(
            json.dumps(
                {
                    "url": url,
                    "ok": ok,
                    "status": status,
                    "fetched_at": fetched_at,
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "bytes": len(body),
                    "error": error,
                },
                indent=2,
            )
        )
    return Response(url, ok, status, body, fetched_at, False, error)
