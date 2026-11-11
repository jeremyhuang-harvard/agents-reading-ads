"""Figures for the exploratory studies (A: regions, B: StockX archive, C: looks, D: re-cueing)."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "explore" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def f(v):
    return float(v) if v not in (None, "") else None


def fit_line(ax, x, y, color):
    b, a = np.polyfit(x, y, 1)
    xs = np.linspace(min(x), max(x), 50)
    ax.plot(xs, a + b * xs, color=color, lw=2)


def fig_a():
    rows = list(csv.DictReader(open(ROOT / "output/explore/study_a/region_panel.csv")))
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
    # Panel 1: within-brand concentration (NB550 vs New Balance), weeks 2-3, vs exposure
    for ax, window, title in [(axes[0], "d_late", "Oct 1–14 (weeks 2–3 after the game)"),
                              (axes[1], "d_placebo", "Placebo: Aug 27–Sep 2 vs Jul 30–Aug 26")]:
        pts = [(f(r["Taylor Swift|d_post"]), f(r.get(f"New Balance 550|{window}")) - f(r.get(f"New Balance|{window}")), r["region"])
               for r in rows if None not in (f(r.get("Taylor Swift|d_post")), f(r.get(f"New Balance 550|{window}")), f(r.get(f"New Balance|{window}")))]
        x, y = [p[0] for p in pts], [p[1] for p in pts]
        ax.scatter(x, y, s=22, color="#B91C1C" if window == "d_late" else "#9CA3AF", alpha=0.8)
        fit_line(ax, x, y, "#111827")
        for p in pts:
            if p[2] in ("Kansas City MO", "Chicago IL", "New York NY", "Los Angeles CA", "St. Joseph MO", "Denver CO"):
                ax.annotate(p[2].rsplit(" ", 1)[0], (p[0], p[1]), fontsize=7, xytext=(3, 3), textcoords="offset points")
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(title, loc="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("Exposure: change in Taylor Swift search share, Sep 24–30 (log)")
        ax.set_ylabel("Change in log(NB 550 / New Balance) search")
    # Panel 3: Nike Dunk weeks 2-3 by exposure, split by prior Dunk familiarity
    pts = [(f(r["Taylor Swift|d_post"]), f(r.get("Nike Dunk|d_late")), f(r.get("Nike Dunk|lr_placebo_pre"))) for r in rows]
    pts = [p for p in pts if None not in p]
    fam = np.array([p[2] for p in pts])
    cut = np.median(fam)
    ax = axes[2]
    for sel, color, label in [(fam > cut, "#111827", "Dunk more familiar (above median)"), (fam <= cut, "#9CA3AF", "Dunk less familiar")]:
        x = np.array([p[0] for p in pts])[sel]
        y = np.array([p[1] for p in pts])[sel]
        ax.scatter(x, y, s=18, color=color, alpha=0.7, label=label)
        fit_line(ax, x, y, color)
    ax.axhline(0, color="black", lw=0.6)
    ax.legend(fontsize=8, frameon=False)
    ax.set_title("Rival: Nike Dunk, Oct 1–14", loc="left", fontsize=10, fontweight="bold")
    ax.set_xlabel("Exposure (as left)")
    ax.set_ylabel("Change in log(Nike Dunk / Converse) search")
    fig.suptitle("Study A — US metro areas (Google Trends DMAs): more local exposure to Taylor's appearance → more search concentrated on the "
                 "exact model; rival Dunk search falls where Dunks were habitual", fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "study_a_regions.png", dpi=170)
    plt.close(fig)


def fig_b():
    rows = list(csv.DictReader(open(ROOT / "output/explore/study_b/stockx_snapshots.csv")))
    sel = {"new-balance-550-white-red": ("Worn: 550 White/Red", "#B91C1C"),
           "new-balance-550-white-green": ("Sibling: 550 White/Green", "#1D4ED8"),
           "new-balance-550-white-black": ("Sibling: 550 White/Black", "#60A5FA"),
           "new-balance-550-white-blue": ("Sibling: 550 White/Blue", "#93C5FD")}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for key, (label, color) in sel.items():
        pts = sorted((int(r["relative_day"]), f(r["salesLast72Hours"])) for r in rows
                     if r["product"] == key and f(r.get("salesLast72Hours")) is not None)
        if pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", color=color, lw=2 if "Worn" in label else 1.2, label=label)
            for d, v in pts:
                ax.annotate(f"{int(v)}", (d, v), fontsize=8, xytext=(4, 4), textcoords="offset points", color=color)
    ax.axvline(0, color="black", ls="--", lw=1)
    ax.set_xlim(-8, 16)
    ax.set_xlabel("Days since Taylor's appearance (Sep 24, 2023)")
    ax.set_ylabel("StockX: completed sales in prior 72 hours")
    ax.set_title("Study B — archived StockX pages: the worn colorway's resale burst vs sibling 550s", loc="left", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "study_b_stockx.png", dpi=170)
    plt.close(fig)


def fig_c():
    path = ROOT / "output/explore/study_c/looks_items.csv"
    if not path.exists():
        return
    rows = [r for r in csv.DictReader(open(path)) if f(r.get("trends_log_lift")) is not None]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    colors = {"indie": "#B91C1C", "mainstream": "#1D4ED8", "luxury": "#111827"}
    ax = axes[0]
    rng = np.random.default_rng(1)
    for t, c in colors.items():
        sub = [r for r in rows if r["tier"] == t]
        x = [int(r["n_items"]) + rng.uniform(-0.18, 0.18) for r in sub]
        y = [math.exp(f(r["trends_log_lift"])) for r in sub]
        ax.scatter(x, y, color=c, s=30, alpha=0.8, label=t)
    x = [int(r["n_items"]) for r in rows]
    y = [f(r["trends_log_lift"]) for r in rows]
    b, a = np.polyfit(np.log(x), y, 1)
    xs = np.linspace(1, 9, 50)
    ax.plot(xs, np.exp(a + b * np.log(xs)), color="#6B7280", lw=2, ls="--", label="fit (all)")
    ax.set_yscale("log")
    ax.set_xlabel("Number of identified brands in the look")
    ax.set_ylabel("Search lift, days 0–3 vs prior 4 weeks (×, log scale)")
    ax.set_title("Each item's lift vs how many items compete in the look", loc="left", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.2)
    ax = axes[1]
    # Within-look contrast: each item's lift minus its look's mean lift, headline item vs the rest.
    looks = {}
    for r in rows:
        looks.setdefault(r["date"], []).append(r)
    head, rest = [], []
    for items in looks.values():
        if len(items) < 2:
            continue
        m = np.mean([f(r["trends_log_lift"]) for r in items])
        for r in items:
            (head if r["first"] == "True" else rest).append((f(r["trends_log_lift"]) - m, r))
    for i, (grp, lab) in enumerate([(head, "Headline item\n(first named in coverage)"), (rest, "Other items\nin the same look")]):
        xs = i + rng.uniform(-0.12, 0.12, len(grp))
        ax.scatter(xs, [g[0] for g in grp], color=[colors[g[1]["tier"]] for g in grp], s=28, alpha=0.8)
        ax.plot([i - 0.25, i + 0.25], [np.mean([g[0] for g in grp])] * 2, color="black", lw=2.5)
        ax.annotate(f"mean {np.mean([g[0] for g in grp]):+.2f}\n(n={len(grp)})", (i + 0.27, np.mean([g[0] for g in grp])), fontsize=8, va="center")
    ax.axhline(0, color="#6B7280", lw=0.6)
    ax.set_xticks([0, 1], ["Headline item\n(first named in coverage)", "Other items\nin the same look"])
    ax.set_xlim(-0.5, 1.7)
    ax.set_ylabel("log lift minus the look's average")
    ax.set_title("Within the same look, the headline item takes the attention", loc="left", fontsize=10, fontweight="bold")
    ax.grid(alpha=0.2, axis="y")
    fig.suptitle("Study C — 73 brand mentions across 20 Taylor Swift game-day looks (Google Trends, US; 61 with measurable search)", fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "study_c_looks.png", dpi=170)
    plt.close(fig)


def fig_d():
    path = ROOT / "output/explore/study_d/recue_daily.csv"
    if not path.exists():
        return
    rows = list(csv.DictReader(open(path)))
    from datetime import date
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.5), sharex=True)
    games = {"2023-09-24": "NB 550", "2023-10-01": "Jets", "2023-10-12": "", "2023-10-22": "Nike AF1",
             "2023-12-03": "", "2023-12-10": "", "2023-12-17": ""}
    for ax, payload, terms in [(axes[0], "link", ["Taylor Swift New Balance", "Taylor Swift Nike", "Taylor Swift shoes"]),
                               (axes[1], "products", ["New Balance 550", "Nike Air Force 1", "Nike Dunk", "Adidas Samba"])]:
        for t, c in zip(terms, ["#B91C1C", "#111827", "#9CA3AF", "#D97706"]):
            pts = sorted((date.fromisoformat(r["date"]), int(r["value"])) for r in rows if r["payload"] == payload and r["term"] == t)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, lw=1.4, label=t)
        for g, lab in games.items():
            ax.axvline(date.fromisoformat(g), color="#7C3AED", lw=0.8, ls=":")
            if lab and ax is axes[0]:
                ax.annotate(lab, (date.fromisoformat(g), ax.get_ylim()[1] if ax.get_ylim()[1] > 1 else 100), fontsize=7, color="#6D28D9",
                            xytext=(2, -10), textcoords="offset points")
        ax.legend(fontsize=8, frameon=False, loc="upper right")
        ax.grid(alpha=0.2)
        ax.set_ylabel("Google Trends (US)")
    axes[0].set_title("Study D — game days (purple) and search for Taylor's first identified shoe vs the Nike she wore later",
                      loc="left", fontsize=10, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "study_d_recue.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    fig_a()
    fig_b()
    fig_c()
    fig_d()
    print(sorted(p.name for p in OUT.iterdir()))
