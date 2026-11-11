"""Permutation p-values for the key Study A coefficients (shuffle exposure across regions)."""
import csv

import numpy as np

rows = list(csv.DictReader(open("output/explore/study_a/region_panel.csv")))
rng = np.random.default_rng(20261109)


def f(r, k):
    v = r.get(k)
    return float(v) if v not in (None, "") else None


def z(a):
    a = np.asarray(a, float)
    return (a - a.mean()) / a.std()


def coef(y, cols, idx):
    X = np.column_stack([np.ones(len(y))] + cols)
    return np.linalg.lstsq(X, y, rcond=None)[0][idx]


def perm(name, y, e, fam=None, which="exposure", n=5000):
    y = np.asarray(y, float)
    def stat(ev):
        ev = z(ev)
        if fam is None:
            return coef(y, [ev], 1)
        fz = z(fam)
        return coef(y, [ev, fz, ev * fz], 3 if which == "interaction" else 1)
    obs = stat(e)
    null = np.array([stat(rng.permutation(e)) for _ in range(n)])
    p = (np.abs(null) >= abs(obs)).mean()
    print(f"{name:55s} coef {obs:+.3f}  permutation p = {p:.4f}  (n={len(y)})")


def collect(keys):
    out = []
    for r in rows:
        vals = [f(r, k) for k in keys]
        if None not in vals:
            out.append(vals)
    return np.array(out)


d = collect(["New Balance 550|d_late", "Taylor Swift|d_post"])
perm("NB550 weeks 2-3 ~ exposure", d[:, 0], d[:, 1])
d = collect(["New Balance 550|d_late", "New Balance|d_late", "Taylor Swift|d_post"])
perm("log(NB550/New Balance brand) weeks 2-3 ~ exposure", d[:, 0] - d[:, 1], d[:, 2])
d = collect(["New Balance 550|d_late", "Nike Dunk|d_late", "Taylor Swift|d_post"])
perm("log(NB550/Nike Dunk) weeks 2-3 ~ exposure", d[:, 0] - d[:, 1], d[:, 2])
d = collect(["Nike Dunk|d_late", "Taylor Swift|d_post", "Nike Dunk|lr_placebo_pre"])
perm("Nike Dunk weeks 2-3 ~ exposure x familiarity", d[:, 0], d[:, 1], d[:, 2], "interaction")
d = collect(["Adidas Samba|d_late", "Taylor Swift|d_post", "Adidas Samba|lr_placebo_pre"])
perm("Adidas Samba weeks 2-3 ~ exposure x familiarity", d[:, 0], d[:, 1], d[:, 2], "interaction")
d = collect(["Nike Dunk|d_placebo", "Taylor Swift|d_post", "Nike Dunk|lr_placebo_pre"])
perm("PLACEBO Nike Dunk ~ exposure x familiarity", d[:, 0], d[:, 1], d[:, 2], "interaction")
d = collect(["New Balance 550|d_placebo", "Taylor Swift|d_post"])
perm("PLACEBO NB550 ~ exposure", d[:, 0], d[:, 1])
