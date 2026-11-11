"""Study A: metro-area (DMA) exposure x familiarity around Taylor Swift x NB 550 (Sep 24, 2023).

For each DMA, pull two daily Google Trends payloads (Aug 1 - Oct 15, 2023):
  sneakers: New Balance 550, Nike Dunk, Adidas Samba, Nike Air Force 1, New Balance 9060
  exposure: Taylor Swift, Travis Kelce
and compute standardized abnormal attention (weekday baseline, days -28..-1) for each term,
plus pre-period familiarity shares among the sneaker terms.

Run: uv run --extra demo python scripts/explore/study_a_dma.py [max_dmas]
Writes output/explore/study_a/dma_panel.csv
"""

from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from implicit_ads.explore import trends as T

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "explore" / "study_a"
EVENT = date(2023, 9, 24)
START, END = "2023-08-01", "2023-10-15"
SNEAKERS = ["New Balance 550", "Nike Dunk", "Adidas Samba", "Nike Air Force 1", "New Balance 9060"]
EXPOSURE = ["Taylor Swift", "Travis Kelce"]


def z_stats(series):
    pre = [(d, v) for d, v in series if -28 <= (d - EVENT).days <= -1]
    if len(pre) < 20:
        return {}
    by_dow = defaultdict(list)
    for d, v in pre:
        by_dow[d.weekday()].append(v)
    base = {k: statistics.fmean(v) for k, v in by_dow.items()}
    resid = [v - base[d.weekday()] for d, v in pre]
    sd = max(statistics.pstdev(resid), 1.0)
    pre_mean = statistics.fmean(v for _, v in pre)
    out = {"pre_mean": pre_mean, "zero_share": sum(v == 0 for _, v in pre) / len(pre)}
    for name, lo, hi in [("z03", 0, 3), ("z07", 0, 7), ("z814", 8, 14)]:
        post = [v - base[d.weekday()] for d, v in series if lo <= (d - EVENT).days <= hi]
        out[name] = statistics.fmean(post) / sd if post else None
    return out


def dma_list(limit: int):
    rows = T.by_region(["New Balance 550", "Nike Dunk", "Adidas Samba"], "2023-08-27", "2023-09-23")
    keep = []
    for r in rows:
        if r["New Balance 550"] > 0 and r["Nike Dunk"] > 0:
            state = r["region"].split()[-1]
            if len(state) == 2 and state.isupper():
                keep.append((r["region"], f"US-{state}-{r['geo_code']}"))
    # Large markets first: those with all three terms non-zero have the most search volume.
    full = {r["region"] for r in rows if min(r["New Balance 550"], r["Nike Dunk"], r["Adidas Samba"]) > 0}
    keep.sort(key=lambda x: (x[0] not in full, x[0]))
    priority = ["Kansas City MO", "Chicago IL", "New York NY", "Los Angeles CA", "St. Louis MO", "Wichita-Hutchinson KS",
                "Topeka KS", "Omaha NE", "Des Moines-Ames IA", "Springfield MO", "Joplin MO-Pittsburg KS"]
    keep.sort(key=lambda x: (x[0] not in priority, x[0] not in full, x[0]))
    return keep[:limit]


def main(limit: int = 60):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for region, geo in dma_list(limit):
        try:
            s = T.over_time(SNEAKERS, START, END, geo=geo)
            e = T.over_time(EXPOSURE, START, END, geo=geo)
        except Exception as exc:
            print("FAILED", region, exc, flush=True)
            continue
        row = {"region": region, "geo": geo}
        pre_tot = defaultdict(float)
        for payload, terms in [(s, SNEAKERS), (e, EXPOSURE)]:
            for t in terms:
                ser = [(date.fromisoformat(x["date"]), x["value"]) for x in payload if x["term"] == t]
                for k, v in z_stats(ser).items():
                    row[f"{t}|{k}"] = v
                if terms is SNEAKERS:
                    pre_tot[t] = sum(v for d, v in ser if -28 <= (d - EVENT).days <= -1)
        tot = sum(pre_tot.values()) or 1
        for t in SNEAKERS:
            row[f"{t}|pre_share"] = pre_tot[t] / tot
        rows.append(row)
        print(region, round(row.get("New Balance 550|z03") or 0, 2), round(row.get("Taylor Swift|z03") or 0, 2), flush=True)
        with (OUT / "dma_panel.csv").open("w", newline="") as h:
            fields = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("region", "geo"), k))
            w = csv.DictWriter(h, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    print("done", len(rows))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
