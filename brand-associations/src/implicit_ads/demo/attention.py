"""Search-attention series: Google Trends and Wikipedia pageviews.

Google Trends is accessed with the unofficial ``pytrends`` client. Values are
normalized 0–100 *within each payload*, so terms are only comparable inside
the same payload group. Zeros can mean "below reporting threshold". Results
are cached to ``data/raw/demo/trends`` so reruns do not re-query Google.

Wikipedia pageviews (Wikimedia REST API) start in July 2015.
"""

from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import date

from . import http
from .config import DERIVED_DIR, ROOT

TRENDS_CACHE = ROOT / "data" / "raw" / "demo" / "trends"
TRENDS_PAUSE = 12.0  # seconds between uncached Google Trends payloads


def _trends_payload(terms: list[str], geo: str, start: str, end: str, log) -> list[dict]:
    key = hashlib.sha256(json.dumps([terms, geo, start, end]).encode()).hexdigest()[:16]
    path = TRENDS_CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    from pytrends.request import TrendReq  # imported lazily; optional dependency

    client = TrendReq(hl="en-US", tz=300, retries=3, backoff_factor=1.0)
    client.build_payload(terms, timeframe=f"{start} {end}", geo=geo)
    frame = client.interest_over_time()
    rows = []
    if not frame.empty:
        partial = frame.get("isPartial")
        for ts, values in frame.drop(columns=["isPartial"], errors="ignore").iterrows():
            for term in terms:
                rows.append({
                    "date": ts.date().isoformat(), "term": term, "value": int(values[term]),
                    "is_partial": bool(partial.loc[ts]) if partial is not None else False,
                })
    TRENDS_CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows))
    time.sleep(TRENDS_PAUSE)
    return rows


def collect_trends(cases: list[dict], log=print) -> None:
    out = []
    for case in cases:
        event = date.fromisoformat(case["event_date"])
        for group in case.get("trends") or []:
            try:
                rows = _trends_payload(group["terms"], group["geo"], group["from"], group["to"], log)
            except Exception as exc:  # pytrends raises a variety of errors on 429
                log(f"[trends] {case['case_id']}/{group['name']}: FAILED {type(exc).__name__}: {exc}")
                continue
            for row in rows:
                out.append({
                    "case_id": case["case_id"], "group": group["name"], "geo": group["geo"],
                    **row, "relative_day": (date.fromisoformat(row["date"]) - event).days,
                })
            log(f"[trends] {case['case_id']}/{group['name']}: {len(rows)} rows")
    _write(DERIVED_DIR / "trends_daily.csv", out)


def collect_pageviews(cases: list[dict], log=print) -> None:
    out = []
    for case in cases:
        spec = case.get("pageviews")
        if not spec:
            continue
        event = date.fromisoformat(case["event_date"])
        start, end = spec["from"].replace("-", ""), spec["to"].replace("-", "")
        for article in spec["articles"]:
            url = (
                "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
                f"en.wikipedia/all-access/user/{article}/daily/{start}00/{end}00"
            )
            resp = http.get(url)
            if not resp.ok:
                log(f"[pageviews] {case['case_id']}/{article}: {resp.error}")
                continue
            for item in resp.json().get("items", []):
                day = date(int(item["timestamp"][:4]), int(item["timestamp"][4:6]), int(item["timestamp"][6:8]))
                out.append({
                    "case_id": case["case_id"], "article": article, "date": day.isoformat(),
                    "views": item["views"], "relative_day": (day - event).days,
                })
            log(f"[pageviews] {case['case_id']}/{article}: ok")
    _write(DERIVED_DIR / "pageviews_daily.csv", out)


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
