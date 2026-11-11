"""Study A analysis v2: anchor-free contrasts and independent familiarity measures."""
import csv

import numpy as np

rows = list(csv.DictReader(open("output/explore/study_a/region_panel.csv")))


def f(r, k):
    v = r.get(k)
    return float(v) if v not in (None, "") else None


def ols(y, X, names):
    X = np.column_stack([np.ones(len(y))] + X)
    y = np.asarray(y)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    inv = np.linalg.inv(X.T @ X)
    cov = inv @ ((X * resid[:, None] ** 2).T @ X) @ inv * n / (n - k)
    se = np.sqrt(np.diag(cov))
    return [(nm, b, s) for nm, b, s in zip(["const"] + names, beta, se)], n


def show(title, res):
    coefs, n = res
    print(title, f"(n={n})")
    for nm, b, s in coefs:
        print(f"    {nm:26s} {b:+.3f} (t {b / s:+.2f})")


z = lambda a: (np.asarray(a, float) - np.mean(a)) / np.std(a)  # noqa: E731

for rival in ["Nike Dunk", "Adidas Samba", "Nike Air Force 1", "Vans", "New Balance"]:
    for window in ["d_post", "d_late", "d_placebo"]:
        data = []
        for r in rows:
            a, b, e = f(r, f"New Balance 550|{window}"), f(r, f"{rival}|{window}"), f(r, "Taylor Swift|d_post")
            if None not in (a, b, e):
                data.append((a - b, e))
        if len(data) < 15:
            continue
        y = [d[0] for d in data]
        show(f"\nlog(NB550/{rival}) change, {window}", ols(y, [z([d[1] for d in data])], ["exposure (Taylor Swift)"]))

# Exposure-quartile means (descriptive)
print("\nMean change in log(NB550 / Nike Dunk), by Taylor-exposure group")
data = [(f(r, "New Balance 550|d_post") - f(r, "Nike Dunk|d_post"), f(r, "Taylor Swift|d_post"), r["region"])
        for r in rows if None not in (f(r, "New Balance 550|d_post"), f(r, "Nike Dunk|d_post"), f(r, "Taylor Swift|d_post"))]
data.sort(key=lambda d: d[1])
k = len(data) // 3
for name, part in [("low", data[:k]), ("mid", data[k:2 * k]), ("high", data[2 * k:])]:
    print(f"   {name:5s} exposure: mean {np.mean([d[0] for d in part]):+.3f}  n={len(part)}  e.g. {[d[2] for d in part[-3:]]}")
for reg in ["Kansas City MO", "Chicago IL", "New York NY", "Los Angeles CA", "St. Louis MO", "Topeka KS", "Wichita-Hutchinson KS", "Omaha NE"]:
    r = next((x for x in rows if x["region"] == reg), None)
    if r:
        print(f"   {reg:24s} TS {f(r, 'Taylor Swift|d_post')}  NB550 {f(r, 'New Balance 550|d_post')}  Dunk {f(r, 'Nike Dunk|d_post')}  NB {f(r, 'New Balance|d_post')}")

# Familiarity measured in an independent earlier window (Jul 30 - Aug 26) to avoid mean reversion.
print("\nExposure x independent familiarity (familiarity = log(term/Converse) in Jul 30-Aug 26)")
for term in ["New Balance 550", "Nike Dunk", "Nike Air Force 1", "Adidas Samba", "Vans"]:
    for window in ["d_post", "d_late"]:
        data = []
        for r in rows:
            y = f(r, f"{term}|{window}")
            e = f(r, "Taylor Swift|d_post")
            fam = f(r, f"{term}|lr_placebo_pre")
            if None not in (y, e, fam):
                data.append((y, e, fam))
        if len(data) < 15:
            continue
        e = z([d[1] for d in data]); fam = z([d[2] for d in data])
        show(f"\n{term} {window}", ols([d[0] for d in data], [e, fam, e * fam], ["exposure", "familiarity (indep.)", "exposure x familiarity"]))
