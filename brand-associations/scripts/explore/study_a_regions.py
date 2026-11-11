"""Study A (v2): metro-area exposure x familiarity around Taylor Swift x NB 550 (Sep 24, 2023).

Daily DMA series are too sparse outside the largest markets, so this uses Google Trends
"interest by region" over windows. With a two-term payload [term, anchor], each DMA's values
are the two terms' shares of their combined search in that DMA, which are comparable across
windows. For each term t and DMA r:

    lr(t, r, window) = log(share_t / share_anchor)
    response(t, r)   = lr(post) - lr(pre)          (change relative to the anchor)
    familiarity(t,r) = lr(pre)                       (pre-period popularity relative to anchor)

Exposure to the event: change in log(Taylor Swift / weather) and log(Travis Kelce / weather)
between the same windows. A placebo pair of windows with no event checks noise.

Run: uv run --extra demo python scripts/explore/study_a_regions.py
Writes output/explore/study_a/region_panel.csv
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from implicit_ads.explore import trends as T

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "explore" / "study_a"

WINDOWS = {
    "pre": ("2023-08-27", "2023-09-23"),
    "post": ("2023-09-24", "2023-09-30"),
    "placebo_pre": ("2023-07-30", "2023-08-26"),
    "placebo_post": ("2023-08-27", "2023-09-02"),
    "late": ("2023-10-01", "2023-10-14"),
}
ANCHOR = "Converse"
TERMS = {
    "New Balance 550": "focal",
    "New Balance": "focal_brand",
    "Nike Dunk": "rival",
    "Adidas Samba": "rival",
    "Nike Air Force 1": "rival",
    "Vans": "rival",
}
EXPOSURE = {"Taylor Swift": "weather", "Travis Kelce": "weather"}


def lr(rows, term, anchor):
    out = {}
    for r in rows:
        a, b = r.get(term, 0), r.get(anchor, 0)
        if a > 0 and b > 0:
            out[r["region"]] = math.log(a / b)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    panel: dict[str, dict] = {}
    for term, anchor in [*((t, ANCHOR) for t in TERMS), *EXPOSURE.items()]:
        vals = {}
        for w, (s, e) in WINDOWS.items():
            rows = T.by_region([term, anchor], s, e)
            vals[w] = lr(rows, term, anchor)
            print(term, w, len(vals[w]), flush=True)
        for region in vals["pre"]:
            row = panel.setdefault(region, {"region": region})
            row[f"{term}|lr_pre"] = vals["pre"][region]
            for w in ("placebo_pre", "post", "late"):
                if region in vals[w]:
                    row[f"{term}|lr_{w}"] = vals[w][region]
            for w in ("post", "late"):
                if region in vals[w]:
                    row[f"{term}|d_{w}"] = vals[w][region] - vals["pre"][region]
            if region in vals["placebo_pre"] and region in vals["placebo_post"]:
                row[f"{term}|d_placebo"] = vals["placebo_post"][region] - vals["placebo_pre"][region]
    rows = list(panel.values())
    fields = sorted({k for r in rows for k in r}, key=lambda k: (k != "region", k))
    with (OUT / "region_panel.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("regions", len(rows))


if __name__ == "__main__":
    main()
