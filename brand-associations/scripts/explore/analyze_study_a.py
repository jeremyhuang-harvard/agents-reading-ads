"""Analyze Study A region panel (OLS with robust SEs, no external stats deps beyond numpy)."""
import csv
import math
import sys

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
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = (X * resid[:, None] ** 2).T @ X
    cov = XtX_inv @ meat @ XtX_inv * n / (n - k)  # HC1
    se = np.sqrt(np.diag(cov))
    out = []
    for nm, b, s in zip(["const"] + names, beta, se):
        out.append(f"    {nm:28s} {b:+.3f}  (se {s:.3f}, t {b / s:+.2f})")
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return "\n".join(out) + f"\n    n={n}  R2={r2:.3f}"


def standardize(v):
    a = np.asarray(v, float)
    return (a - a.mean()) / a.std()


# Exposure: change in log(Taylor Swift / weather) from pre (Aug 27-Sep 23) to post week (Sep 24-30).
print("Top exposure regions:")
ex = sorted([(f(r, "Taylor Swift|d_post"), r["region"]) for r in rows if f(r, "Taylor Swift|d_post") is not None], reverse=True)
for v, reg in ex[:8]:
    print(f"   {reg:40s} {v:+.2f}")
print("   ...median", sorted(v for v, _ in ex)[len(ex) // 2])

for term in ["New Balance 550", "New Balance", "Nike Dunk", "Adidas Samba", "Nike Air Force 1", "Vans"]:
    for window in ["d_post", "d_late", "d_placebo"]:
        data = [(f(r, f"{term}|{window}"), f(r, "Taylor Swift|d_post"), f(r, f"{term}|lr_pre"), f(r, "Travis Kelce|d_post"))
                for r in rows]
        data = [d for d in data if None not in d]
        if len(data) < 15:
            print(term, window, "too few", len(data))
            continue
        y = [d[0] for d in data]
        e = standardize([d[1] for d in data])
        fam = standardize([d[2] for d in data])
        print(f"\n{term} | response={window} (change in log share vs Converse)")
        print(ols(y, [e, fam, e * fam], ["exposure(TS)", "familiarity", "exposure x familiarity"]))
