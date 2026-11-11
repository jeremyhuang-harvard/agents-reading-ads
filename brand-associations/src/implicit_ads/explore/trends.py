"""Cached Google Trends helpers for exploratory studies (interest over time, by region, related queries).

All payloads are cached under data/raw/explore/trends/<sha>.json so reruns never re-query Google.
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "raw" / "explore" / "trends"
PAUSE = 14.0

_client = None


def _get_client():
    global _client
    if _client is None:
        from pytrends.request import TrendReq

        _client = TrendReq(hl="en-US", tz=300, retries=2, backoff_factor=2.0)
    return _client


def _cached(kind: str, spec: dict, fetch):
    key = hashlib.sha256(json.dumps([kind, spec], sort_keys=True).encode()).hexdigest()[:20]
    path = CACHE / f"{kind}_{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    last = None
    for attempt in range(4):
        try:
            data = fetch()
            break
        except Exception as exc:  # pytrends raises assorted errors on 429
            last = exc
            time.sleep(60 * (attempt + 1) + random.random() * 10)
    else:
        raise RuntimeError(f"trends {kind} failed: {last}")
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"spec": spec, "data": data}))
    time.sleep(PAUSE + random.random() * 4)
    return {"spec": spec, "data": data}


def over_time(terms: list[str], start: str, end: str, geo: str = "US") -> list[dict]:
    spec = {"terms": terms, "start": start, "end": end, "geo": geo}

    def fetch():
        c = _get_client()
        c.build_payload(terms, timeframe=f"{start} {end}", geo=geo)
        df = c.interest_over_time()
        rows = []
        if not df.empty:
            for ts, vals in df.drop(columns=["isPartial"], errors="ignore").iterrows():
                for t in terms:
                    rows.append({"date": ts.date().isoformat(), "term": t, "value": int(vals[t])})
        return rows

    return _cached("time", spec, fetch)["data"]


def by_region(terms: list[str], start: str, end: str, geo: str = "US", resolution: str = "DMA") -> list[dict]:
    spec = {"terms": terms, "start": start, "end": end, "geo": geo, "resolution": resolution}

    def fetch():
        c = _get_client()
        c.build_payload(terms, timeframe=f"{start} {end}", geo=geo)
        df = c.interest_by_region(resolution=resolution, inc_low_vol=True, inc_geo_code=True)
        rows = []
        for region, vals in df.iterrows():
            row = {"region": region, "geo_code": str(vals.get("geoCode", ""))}
            for t in terms:
                row[t] = int(vals[t])
            rows.append(row)
        return rows

    return _cached("region", spec, fetch)["data"]


def related(term: str, start: str, end: str, geo: str = "US") -> dict:
    spec = {"term": term, "start": start, "end": end, "geo": geo}

    def fetch():
        c = _get_client()
        c.build_payload([term], timeframe=f"{start} {end}", geo=geo)
        out = c.related_queries().get(term, {}) or {}
        return {k: (v.to_dict("records") if v is not None else []) for k, v in out.items()}

    return _cached("related", spec, fetch)["data"]
