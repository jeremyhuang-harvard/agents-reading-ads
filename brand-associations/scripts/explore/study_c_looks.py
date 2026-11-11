"""Study C: within-look competition for attention across Taylor Swift's game-day outfits.

For every identified brand in every look (config/explore/taylor_gameday_looks.json):
  * Google Trends (US, daily, single-term payload over day -35..+10): weekday-adjusted lift on
    days 0..3 relative to days -28..-1, excluding days within 2 of any other game-day look.
  * Wikipedia pageviews (absolute daily views) for brands with an article: same baseline;
    absolute excess views over days 0..3.

Run: uv run --extra demo python scripts/explore/study_c_looks.py
Writes output/explore/study_c/looks_items.csv
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

from implicit_ads.demo import http
from implicit_ads.explore import trends as T

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config" / "explore" / "taylor_gameday_looks.json"
OUT = ROOT / "output" / "explore" / "study_c"


def metrics(series: dict[date, float], d0: date, other_days: set[date]) -> dict:
    pre = {d: v for d, v in series.items() if -28 <= (d - d0).days <= -1
           and not any(abs((d - o).days) <= 2 for o in other_days)}
    if len(pre) < 10:
        return {}
    by_dow = defaultdict(list)
    for d, v in pre.items():
        by_dow[d.weekday()].append(v)
    mean_pre = statistics.fmean(pre.values())
    base = {k: statistics.fmean(v) for k, v in by_dow.items()}
    exp = lambda d: base.get(d.weekday(), mean_pre)  # noqa: E731
    resid = [v - exp(d) for d, v in pre.items()]
    sd = max(statistics.pstdev(resid), 1.0)
    post = [(d, v) for d, v in series.items() if 0 <= (d - d0).days <= 3]
    if not post:
        return {}
    excess = [v - exp(d) for d, v in post]
    post_mean = statistics.fmean(v for _, v in post)
    return {
        "pre_mean": round(mean_pre, 3),
        "post_mean": round(post_mean, 3),
        "zero_share_pre": round(sum(v == 0 for v in pre.values()) / len(pre), 3),
        "excess_0_3": round(statistics.fmean(excess), 3),
        "excess_sum_0_3": round(sum(excess), 1),
        "z_0_3": round(statistics.fmean(excess) / sd, 3),
        "log_lift": round(math.log((post_mean + 1) / (mean_pre + 1)), 4),
        "peak_day": max(post, key=lambda x: x[1])[0].isoformat(),
    }


def wiki_series(article: str, start: date, end: date) -> dict[date, float]:
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
           f"{quote(article, safe='')}/daily/{start:%Y%m%d}00/{end:%Y%m%d}00")
    resp = http.get(url)
    if not resp.ok:
        return {}
    out = {}
    for item in json.loads(resp.text).get("items", []):
        ts = item["timestamp"]
        out[date(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))] = float(item["views"])
    return out


def main():
    cfg = json.loads(CFG.read_text())
    looks = cfg["appearances"]
    all_days = {date.fromisoformat(a["date"]) for a in looks}
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    seen_brand = defaultdict(int)
    for look in looks:
        d0 = date.fromisoformat(look["date"])
        n_items = len(look["items"])
        others = all_days - {d0}
        start, end = d0 - timedelta(days=35), d0 + timedelta(days=10)
        for pos, item in enumerate(look["items"]):
            seen_brand[item["brand"]] += 1
            row = {"date": look["date"], "brand": item["brand"], "query": item["query"], "tier": item["tier"],
                   "n_items": n_items, "position": pos + 1, "first": bool(item.get("first")),
                   "affordable": bool(item.get("affordable")), "prior_looks_with_brand": seen_brand[item["brand"]] - 1}
            try:
                ts = T.over_time([item["query"]], start.isoformat(), end.isoformat(), geo="US")
                series = {date.fromisoformat(x["date"]): float(x["value"]) for x in ts}
                row.update({f"trends_{k}": v for k, v in metrics(series, d0, others).items()})
            except Exception as exc:
                row["trends_error"] = str(exc)[:120]
            if item.get("wiki"):
                ws = wiki_series(item["wiki"], start, end)
                row.update({f"wiki_{k}": v for k, v in metrics(ws, d0, others).items()})
            rows.append(row)
            print(look["date"], item["brand"], row.get("trends_log_lift"), row.get("wiki_excess_sum_0_3"), flush=True)
            fields = sorted({k for r in rows for k in r}, key=lambda k: (not k[0].islower() or "_" in k, k))
            with (OUT / "looks_items.csv").open("w", newline="") as h:
                w = csv.DictWriter(h, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
    print("done", len(rows))


if __name__ == "__main__":
    main()
