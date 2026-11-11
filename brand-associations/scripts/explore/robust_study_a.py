"""Robustness for Study A's headline: drop the most-exposed metros; rank correlation."""
import csv

import numpy as np

rows = list(csv.DictReader(open("output/explore/study_a/region_panel.csv")))
f = lambda v: float(v) if v not in (None, "") else None  # noqa: E731


def ranks(a):
    return np.argsort(np.argsort(a)).astype(float)


for window in ["d_late", "d_post", "d_placebo"]:
    pts = [(f(r["Taylor Swift|d_post"]), f(r.get(f"New Balance 550|{window}")) - f(r.get(f"New Balance|{window}")), r["region"])
           for r in rows if None not in (f(r.get("Taylor Swift|d_post")), f(r.get(f"New Balance 550|{window}")), f(r.get(f"New Balance|{window}")))]
    pts.sort()
    for drop in (0, 3, 6):
        sub = pts[: len(pts) - drop] if drop else pts
        x = np.array([p[0] for p in sub]); y = np.array([p[1] for p in sub])
        rho = np.corrcoef(ranks(x), ranks(y))[0, 1]
        rng = np.random.default_rng(1)
        null = [np.corrcoef(ranks(rng.permutation(x)), ranks(y))[0, 1] for _ in range(4000)]
        p = np.mean(np.abs(null) >= abs(rho))
        print(f"{window:9s} drop top {drop}: n={len(sub)} Spearman {rho:+.2f} perm p={p:.3f}" + (f"  dropped {[q[2] for q in pts[-drop:]]}" if drop else ""))
