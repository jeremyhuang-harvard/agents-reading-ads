"""Study C analysis: does an item's attention lift fall with the number of competing items in the look?"""
import csv
import math

import numpy as np

rows = list(csv.DictReader(open("output/explore/study_c/looks_items.csv")))


def f(v):
    return float(v) if v not in (None, "") else None


def ols(y, cols, names):
    X = np.column_stack([np.ones(len(y))] + cols)
    y = np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    inv = np.linalg.inv(X.T @ X)
    cov = inv @ ((X * resid[:, None] ** 2).T @ X) @ inv * n / (n - k)
    se = np.sqrt(np.diag(cov))
    for nm, b, s in zip(["const"] + names, beta, se):
        print(f"    {nm:30s} {b:+.3f} (t {b / s:+.2f})")
    print(f"    n={n}")
    return beta


usable = [r for r in rows if f(r.get("trends_log_lift")) is not None]
print("items with Trends:", len(usable), "of", len(rows))
tiers = {"indie": 0, "mainstream": 1, "luxury": 2}
y = [f(r["trends_log_lift"]) for r in usable]
logn = [math.log(int(r["n_items"])) for r in usable]
first = [1.0 if r["first"] == "True" else 0.0 for r in usable]
aff = [1.0 if r["affordable"] == "True" else 0.0 for r in usable]
mainstream = [1.0 if r["tier"] == "mainstream" else 0.0 for r in usable]
luxury = [1.0 if r["tier"] == "luxury" else 0.0 for r in usable]
repeat = [1.0 if int(r["prior_looks_with_brand"]) > 0 else 0.0 for r in usable]
pre = [math.log(1 + f(r["trends_pre_mean"])) for r in usable]

print("\n(1) log lift ~ log(# items in look) + tier")
ols(y, [logn, mainstream, luxury], ["log n_items", "mainstream", "luxury"])
print("\n(2) + headline item, affordable, repeat brand")
ols(y, [logn, mainstream, luxury, first, aff, repeat], ["log n_items", "mainstream", "luxury", "first-named", "affordable", "repeat brand"])

print("\nMean log lift by look size")
for lo, hi in [(1, 1), (2, 3), (4, 6), (7, 9)]:
    sub = [f(r["trends_log_lift"]) for r in usable if lo <= int(r["n_items"]) <= hi]
    print(f"   {lo}-{hi} items: {np.mean(sub):+.2f}  (n={len(sub)})  ~ {math.exp(np.mean(sub)):.1f}x")
print("\nMean log lift by tier")
for t in tiers:
    sub = [f(r["trends_log_lift"]) for r in usable if r["tier"] == t]
    print(f"   {t:10s}: {np.mean(sub):+.2f}  (n={len(sub)})")

print("\nLouis Vuitton across looks (same brand, different look sizes)")
for r in rows:
    if r["brand"] in ("Louis Vuitton", "Versace", "Chanel", "Effy", "Retrouvai", "Cartier", "Giuseppe Zanotti", "Westside Storey", "Wear by Erin Andrews", "Stephanie Gottlieb"):
        print(f"   {r['brand']:20s} {r['date']}  n_items={r['n_items']}  first={r['first']:5s}  lift={r.get('trends_log_lift')}  wiki_excess={r.get('wiki_excess_sum_0_3')}")

wk = [r for r in rows if f(r.get("wiki_excess_sum_0_3")) is not None and f(r.get("wiki_pre_mean"))]
if len(wk) > 8:
    print("\nWikipedia (absolute views): log(1+excess share) ~ log n_items + log baseline")
    yy = [math.copysign(math.log1p(abs(f(r["wiki_excess_sum_0_3"]) / (4 * f(r["wiki_pre_mean"])))), f(r["wiki_excess_sum_0_3"])) for r in wk]
    ols(yy, [[math.log(int(r["n_items"])) for r in wk], [math.log(f(r["wiki_pre_mean"])) for r in wk]], ["log n_items", "log baseline views"])

# Within-look comparison: look fixed effects (demeaned within look), so overall attention to the
# appearance (novelty, opponent, date) is held fixed. Identifies headline and tier effects only.
print("\nWithin-look (look fixed effects): log lift ~ first-named + tier + affordable")
looks = {}
for r in usable:
    looks.setdefault(r["date"], []).append(r)
Y, Xf, Xm, Xl, Xa = [], [], [], [], []
for d, items in looks.items():
    if len(items) < 2:
        continue
    def dm(vals):
        m = sum(vals) / len(vals)
        return [v - m for v in vals]
    Y += dm([f(r["trends_log_lift"]) for r in items])
    Xf += dm([1.0 if r["first"] == "True" else 0.0 for r in items])
    Xm += dm([1.0 if r["tier"] == "mainstream" else 0.0 for r in items])
    Xl += dm([1.0 if r["tier"] == "luxury" else 0.0 for r in items])
    Xa += dm([1.0 if r["affordable"] == "True" else 0.0 for r in items])
ols(Y, [Xf, Xm, Xl, Xa], ["first-named", "mainstream", "luxury", "affordable"])
print("\nFirst-named vs other items, mean log lift, looks with 2+ items")
fn = [f(r["trends_log_lift"]) for d, it in looks.items() if len(it) > 1 for r in it if r["first"] == "True"]
ot = [f(r["trends_log_lift"]) for d, it in looks.items() if len(it) > 1 for r in it if r["first"] != "True"]
print(f"   first-named {np.mean(fn):+.2f} (n={len(fn)})   others {np.mean(ot):+.2f} (n={len(ot)})")

# Sensitivity: 12 items returned no Google Trends data at all (below the reporting threshold).
# Treat them as zero lift (no measurable search) instead of dropping them.
print("\nSensitivity: items with no Trends data coded as zero lift")
allr = rows
lift0 = [f(r.get("trends_log_lift")) if f(r.get("trends_log_lift")) is not None else 0.0 for r in allr]
print("   no-data items that were first-named:", sum(1 for r in allr if f(r.get("trends_log_lift")) is None and r["first"] == "True"))
looks2 = {}
for r, v in zip(allr, lift0):
    looks2.setdefault(r["date"], []).append((r, v))
Y, Xf, Xm, Xl = [], [], [], []
for d, items in looks2.items():
    if len(items) < 2:
        continue
    dm = lambda vals: [v - sum(vals) / len(vals) for v in vals]  # noqa: E731
    Y += dm([v for _, v in items])
    Xf += dm([1.0 if r["first"] == "True" else 0.0 for r, _ in items])
    Xm += dm([1.0 if r["tier"] == "mainstream" else 0.0 for r, _ in items])
    Xl += dm([1.0 if r["tier"] == "luxury" else 0.0 for r, _ in items])
ols(Y, [Xf, Xm, Xl], ["first-named", "mainstream", "luxury"])
print("\n   pooled: log lift ~ log n_items + tier + first-named (zeros included)")
ols(lift0, [[math.log(int(r["n_items"])) for r in allr], [1.0 if r["tier"] == "mainstream" else 0.0 for r in allr],
            [1.0 if r["tier"] == "luxury" else 0.0 for r in allr], [1.0 if r["first"] == "True" else 0.0 for r in allr]],
    ["log n_items", "mainstream", "luxury", "first-named"])
print("\n   mean lift by look size (zeros included)")
for lo, hi in [(1, 1), (2, 3), (4, 6), (7, 9)]:
    sub = [v for r, v in zip(allr, lift0) if lo <= int(r["n_items"]) <= hi]
    sub_ind = [v for r, v in zip(allr, lift0) if lo <= int(r["n_items"]) <= hi and r["tier"] == "indie"]
    print(f"   {lo}-{hi} items: all {np.mean(sub):+.2f} (n={len(sub)})   indie only {np.mean(sub_ind) if sub_ind else float('nan'):+.2f} (n={len(sub_ind)})")
