"""Assemble directed measures into a pair panel and test the size / interference predictions.

Inputs: every data/derived/assoc/directed_<measure>.csv (columns celebrity, brand, fwd, bwd, ...),
plus gdelt_counts.csv, clickstream_flows.csv and wiki_entities.csv when present.

Outputs:
  data/derived/assoc/cells.csv       every celebrity x brand cell x measure (fwd, bwd, asymmetry)
  data/derived/assoc/pair_panel.csv  configured pairs only, wide by measure, with size covariates
  output/assoc/asymmetry_<measure>.png and output/assoc/summary.md
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict

import numpy as np

from . import measures
from .config import DERIVED, OUTPUT, Frame


def _f(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def derive_count_measures(frame: Frame, log=print) -> None:
    """Turn raw GDELT and clickstream counts into directed_*.csv files."""
    cs, bs = frame.celebrities, frame.brands
    ci, bi = frame.index("celebrity"), frame.index("brand")
    path = DERIVED / "gdelt_counts.csv"
    if path.exists():
        rows = list(csv.DictReader(path.open()))
        n_c, n_b = np.full(len(cs), np.nan), np.full(len(bs), np.nan)
        n_cb = np.full((len(cs), len(bs)), np.nan)
        for r in rows:
            n = _f(r["n"])
            if n is None:
                continue
            if r["celebrity"] and r["brand"]:
                n_cb[ci[r["celebrity"]], bi[r["brand"]]] = n
            elif r["celebrity"]:
                n_c[ci[r["celebrity"]]] = n
            elif r["brand"]:
                n_b[bi[r["brand"]]] = n
        fwd_m, bwd_m = measures.conditional_from_marginals(np.nan_to_num(n_c), np.nan_to_num(n_b), np.nan_to_num(n_cb))
        full = not np.isnan(n_cb).any()
        if full:
            fwd_s, bwd_s = measures.count_shares(n_cb)
        _write_directed("gdelt_conditional", cs, bs, fwd_m, bwd_m, mask=~np.isnan(n_cb), extra={"n_cb": n_cb})
        if full:
            _write_directed("gdelt_share", cs, bs, fwd_s, bwd_s, extra={"n_cb": n_cb})
        log(f"[analyze] GDELT: {int((~np.isnan(n_cb)).sum())} cells; full matrix={full}")
    path = DERIVED / "clickstream_flows.csv"
    if path.exists():
        rows = list(csv.DictReader(path.open()))
        fwd, bwd = np.zeros((len(cs), len(bs))), np.zeros((len(cs), len(bs)))
        flows_cb, flows_bc = np.zeros_like(fwd), np.zeros_like(fwd)
        for r in rows:
            i, j = ci[r["celebrity"]], bi[r["brand"]]
            flows_cb[i, j], flows_bc[i, j] = float(r["n_c_to_b"]), float(r["n_b_to_c"])
            fwd[i, j] = flows_cb[i, j] / float(r["outflow_c"]) if float(r["outflow_c"]) else 0.0
            bwd[i, j] = flows_bc[i, j] / float(r["outflow_b"]) if float(r["outflow_b"]) else 0.0
        _write_directed("clickstream_conditional", cs, bs, fwd, bwd, extra={"n_c_to_b": flows_cb, "n_b_to_c": flows_bc})


def _write_directed(name, cs, bs, fwd, bwd, mask=None, extra=None):
    with (DERIVED / f"directed_{name}.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["celebrity", "brand", "fwd", "bwd", *(extra or {})])
        for i, c in enumerate(cs):
            for j, b in enumerate(bs):
                if mask is not None and not mask[i, j]:
                    continue
                w.writerow([c.id, b.id, f"{fwd[i, j]:.6g}", f"{bwd[i, j]:.6g}", *(f"{v[i, j]:.6g}" for v in (extra or {}).values())])


def size_covariates(frame: Frame) -> dict[str, dict[str, float]]:
    out = defaultdict(dict)
    path = DERIVED / "wiki_entities.csv"
    if path.exists():
        for r in csv.DictReader(path.open()):
            v = _f(r["pageviews"])
            if v:
                out[r["entity"]]["log_pageviews"] = math.log(v)
    path = DERIVED / "gdelt_counts.csv"
    if path.exists():
        for r in csv.DictReader(path.open()):
            v = _f(r["n"])
            ent = r["celebrity"] or r["brand"]
            if v and bool(r["celebrity"]) != bool(r["brand"]):
                out[ent]["log_coverage"] = math.log(v)
    return out


def ols(y, X):
    X = np.column_stack([np.ones(len(y))] + list(X))
    y = np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    inv = np.linalg.pinv(X.T @ X)
    cov = inv @ ((X * resid[:, None] ** 2).T @ X) @ inv * n / max(n - k, 1)
    return beta, np.sqrt(np.diag(cov))


def run(frame: Frame, log=print) -> None:
    derive_count_measures(frame, log)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pairs = {(p.celebrity, p.brand) for p in frame.pairs}
    size = size_covariates(frame)
    cells, panel = [], defaultdict(dict)
    measures_found = sorted(p.stem.removeprefix("directed_") for p in DERIVED.glob("directed_*.csv"))
    for m in measures_found:
        for r in csv.DictReader((DERIVED / f"directed_{m}.csv").open()):
            fwd, bwd = _f(r["fwd"]), _f(r["bwd"])
            a = math.log(fwd) - math.log(bwd) if fwd and bwd and fwd > 0 and bwd > 0 else None
            row = {"measure": m, "celebrity": r["celebrity"], "brand": r["brand"], "is_pair": (r["celebrity"], r["brand"]) in pairs,
                   "fwd": fwd, "bwd": bwd, "asym": a}
            for key in ("log_pageviews", "log_coverage"):
                sc, sb = size[r["celebrity"]].get(key), size[r["brand"]].get(key)
                row[f"size_ratio_{key}"] = sb - sc if sc is not None and sb is not None else None
            cells.append(row)
            if row["is_pair"]:
                p = panel[(r["celebrity"], r["brand"])]
                p.update({"celebrity": r["celebrity"], "brand": r["brand"],
                          "size_ratio_log_pageviews": row["size_ratio_log_pageviews"], "size_ratio_log_coverage": row["size_ratio_log_coverage"]})
                p[f"{m}|fwd"], p[f"{m}|bwd"], p[f"{m}|asym"] = fwd, bwd, a
    _dump(DERIVED / "cells.csv", cells)
    _dump(DERIVED / "pair_panel.csv", list(panel.values()))

    lines = [f"# Directed association: pilot summary (frame {frame.version}, window {frame.start} to {frame.end})", "",
             "Asymmetry = log P(brand | celebrity cue) - log P(celebrity | brand cue). Positive = the celebrity "
             "retrieves the brand more strongly than the brand retrieves the celebrity.", "",
             "| measure | pairs with both directions > 0 | share asym > 0 | median asym (pairs) | slope on size ratio: news coverage | slope: Wikipedia pageviews | n cells |",
             "|---|---|---|---|---|---|---|"]
    for m in measures_found:
        rows = [c for c in cells if c["measure"] == m]
        prs = [c["asym"] for c in rows if c["is_pair"] and c["asym"] is not None]
        slopes, n_xy = [], 0
        for key in ("size_ratio_log_coverage", "size_ratio_log_pageviews"):
            xy = [(c[key], c["asym"]) for c in rows if c["asym"] is not None and c[key] is not None]
            n_xy = max(n_xy, len(xy))
            if len(xy) > 10:
                beta, se = ols([y for _, y in xy], [[x for x, _ in xy]])
                slopes.append(f"{beta[1]:+.2f} (se {se[1]:.2f})")
            else:
                slopes.append("")
        share = f"{np.mean([a > 0 for a in prs]):.0%}" if prs else ""
        med = f"{np.median(prs):+.2f}" if prs else ""
        lines.append(f"| {m} | {len(prs)}/{len(frame.pairs)} | {share} | {med} | {slopes[0]} | {slopes[1]} | {n_xy} |")
        _figure(m, rows, frame)
    lines += ["", "Size ratio = log(brand) - log(celebrity) of English-language GDELT article counts (news coverage) or "
              "Wikipedia pageviews over the window. Pageviews understate brands (people visit brand sites, not brand "
              "Wikipedia pages), so coverage is the primary size measure.",
              "For `gdelt_conditional` the asymmetry equals log N(brand) - log N(celebrity) by construction (a pure size effect); "
              "competition-normalized measures (`gdelt_share`, `trends_related`, `embed_*`, `llm_*`) instead reflect crowding at each cue."]
    (OUTPUT / "summary.md").write_text("\n".join(lines) + "\n")
    log("\n".join(lines))


def _dump(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _figure(m, rows, frame):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = {e.id: e.name for e in frame.entities}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    ax = axes[0]
    bg = [c for c in rows if not c["is_pair"] and c["fwd"] and c["bwd"]]
    pr = [c for c in rows if c["is_pair"] and c["fwd"] and c["bwd"]]
    ax.scatter([c["bwd"] for c in bg], [c["fwd"] for c in bg], s=6, color="#D1D5DB", label="other celebrity x brand cells")
    ax.scatter([c["bwd"] for c in pr], [c["fwd"] for c in pr], s=30, color="#B91C1C", label="ambassador pairs")
    for c in pr:
        ax.annotate(f"{names[c['celebrity']]}–{names[c['brand']]}", (c["bwd"], c["fwd"]), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    vals = [v for c in bg + pr for v in (c["fwd"], c["bwd"]) if v and v > 0]
    if vals:
        lo, hi = min(vals), max(vals)
        ax.plot([lo, hi], [lo, hi], color="black", lw=0.8, ls="--")
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel("P(celebrity | brand cue)   — brand → celebrity")
    ax.set_ylabel("P(brand | celebrity cue)   — celebrity → brand")
    ax.set_title("Above the dashed line: the celebrity calls up the brand more\nthan the brand calls up the celebrity", loc="left", fontsize=9.5)
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    ax = axes[1]
    key = "size_ratio_log_coverage" if any(c.get("size_ratio_log_coverage") is not None for c in rows) else "size_ratio_log_pageviews"
    pts_bg = [(c[key], c["asym"]) for c in bg if c["asym"] is not None and c[key] is not None]
    pts_pr = [(c[key], c["asym"], c) for c in pr if c["asym"] is not None and c[key] is not None]
    ax.scatter([x for x, _ in pts_bg], [y for _, y in pts_bg], s=6, color="#D1D5DB")
    ax.scatter([x for x, _, _ in pts_pr], [y for _, y, _ in pts_pr], s=30, color="#B91C1C")
    for x, y, c in pts_pr:
        ax.annotate(names[c["celebrity"]], (x, y), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    allpts = pts_bg + [(x, y) for x, y, _ in pts_pr]
    if len(allpts) > 10:
        b, a = np.polyfit([x for x, _ in allpts], [y for _, y in allpts], 1)
        xs = np.linspace(min(x for x, _ in allpts), max(x for x, _ in allpts), 20)
        ax.plot(xs, a + b * xs, color="black", lw=1.2, label=f"fit, all cells: slope {b:+.2f}")
        ax.legend(fontsize=8, frameon=False)
    ax.axhline(0, color="#6B7280", lw=0.6)
    ax.axvline(0, color="#6B7280", lw=0.6)
    ax.set_xlabel(("log(brand / celebrity news coverage)" if key.endswith("coverage") else "log(brand / celebrity Wikipedia pageviews)")
                  + "   — brand bigger →")
    ax.set_ylabel("asymmetry: log P(b|c) − log P(c|b)")
    ax.set_title("Does the bigger side get retrieved more?", loc="left", fontsize=9.5)
    fig.suptitle(f"Directed association — measure: {m}", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUTPUT / f"asymmetry_{m}.png", dpi=160)
    plt.close(fig)
