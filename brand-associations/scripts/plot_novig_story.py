"""Novig before vs after the Sydney Sweeney campaign (Sept 9, 2026): output/presentation/novig_story.png.

Panels: (A) related searches for "Novig" before, (B) after, (C) news volume vs a rival, (D) share of Novig news naming
Sweeney, (E) where Novig's Wikipedia readers click next (October 2026).
Run: uv run --extra assoc python scripts/plot_novig_story.py
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "derived" / "assoc"
OUT = ROOT / "output" / "presentation"
D0 = date(2026, 9, 9)
RED, AMBER, GREY, BLUE = "#B91C1C", "#F59E0B", "#9CA3AF", "#1D4ED8"
SWEENEY = re.compile(r"sydney|sweeney|\bad\b|commercial", re.I)
CATEGORY = re.compile(r"kalshi|polymarket|fanduel|draftkings|prizepicks|betting|sportsbook|prediction|sports", re.I)


def related(period):
    for r in csv.DictReader((D / "event_sweeney_novig_related.csv").open()):
        if r["period"] == period and r["cue"] == "novig":
            out = []
            for part in r["top_related"].split(" | "):
                m = re.match(r"(.*) \((\d+)\)$", part.strip())
                if m:
                    out.append((m.group(1), int(m.group(2))))
            return out, float(r["share_of_related_weight"])
    return [], 0.0


def colour(q):
    if SWEENEY.search(q):
        return RED
    if CATEGORY.search(q):
        return AMBER
    return GREY


def bars(ax, items, title):
    items = items[:8][::-1]
    ax.barh([q for q, _ in items], [v for _, v in items], color=[colour(q) for q, _ in items])
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    ax.set_xlabel("Google's relative weight (top query = 100)", fontsize=8.5)
    ax.tick_params(axis="y", labelsize=9.5)
    ax.set_xlim(0, 112)


def main():
    pre, _ = related("pre")
    post, post_share = related("post")
    periods = {r["key"]: r for r in csv.DictReader((D / "event_sweeney_novig_periods.csv").open())}
    weekly = list(csv.DictReader((D / "event_sweeney_novig_weekly.csv").open()))
    pre_w = [r for r in weekly if (date.fromisoformat(r["key"]) - D0).days <= -7]  # weeks entirely before the campaign
    novig_pw = sum(int(r["n_brand"] or 0) for r in pre_w) / len(pre_w)
    kalshi_pw = sum(int(r["n_kalshi"] or 0) for r in pre_w) / len(pre_w)

    out_n, out_tot = Counter(), {}
    for r in csv.DictReader((D / "clickstream_outflow_monthly.csv").open()):
        if r["entity"] == "novig":
            out_n[r["next_page"]] += int(r["n"])
            out_tot[r["month"]] = int(r["n"]) / float(r["share_of_outflow"])
    T = sum(out_tot.values())

    fig = plt.figure(figsize=(15, 8.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.15, 1.15, 1], hspace=0.55, wspace=0.55)
    bars(fig.add_subplot(gs[0, 0]), pre, "A. Before: searches alongside “Novig”\n(May 1 – Sept 8)")
    bars(fig.add_subplot(gs[0, 1]), post, f"B. After: Sweeney is {post_share:.0%} of the weight\n(Sept 9 – Nov 8)")

    ax = fig.add_subplot(gs[0, 2])
    ax.bar(["Novig", "Kalshi"], [novig_pw, kalshi_pw], color=[RED, AMBER])
    for x, v in enumerate([novig_pw, kalshi_pw]):
        ax.text(x, v * 1.02, f"{v:.0f}", ha="center", fontsize=10)
    ax.set_title("C. Small player, crowded market\nnews articles per week, before", loc="left", fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    ax = fig.add_subplot(gs[1, 2])
    pr, po = periods["pre"], periods["post"]
    vals = [float(pr["bwd_celebrity_in_brand"] or 0), float(po["bwd_celebrity_in_brand"] or 0)]
    ax.bar(["before", "after"], [100 * v for v in vals], color=[GREY, RED])
    for x, (v, r) in enumerate(zip(vals, (pr, po))):
        ax.text(x, 100 * v + 2, f"{v:.0%}\n({r['n_joint']} of {r['n_brand']})", ha="center", fontsize=9.5)
    ax.set_ylim(0, 112)
    ax.set_title("D. Share of Novig news\narticles naming Sweeney", loc="left", fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    ax = fig.add_subplot(gs[1, :2])
    people = {"Sydney_Sweeney"}
    critics = {"Gracie_Kramer", "Ariarne_Titmus", "Amy_Hunt"}
    items = out_n.most_common(9)[::-1]
    names = [re.sub(r" \(.*\)$", "", p.replace("_", " ")) for p, _ in items]
    cols = [RED if p in people else ("#FCA5A5" if p in critics or p == "Shock_advertising" else AMBER if CATEGORY.search(p) else GREY)
            for p, _ in items]
    ax.barh(names, [100 * n / T for _, n in items], color=cols)
    ax.set_title(f"E. What Novig is made of now: where its Wikipedia readers click next (Oct 2026, {int(T):,} clicks)\n"
                 "The article itself was created on Oct 16, 2026, starting from text copied from Sydney Sweeney's page",
                 loc="left", fontsize=11, fontweight="bold")
    ax.set_xlabel("% of outgoing clicks", fontsize=9)
    ax.tick_params(axis="y", labelsize=9.5)
    for y, (_, n) in enumerate(items):
        ax.text(100 * n / T + 0.3, y, f"{100 * n / T:.0f}%", va="center", fontsize=9)

    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (RED, "#FCA5A5", AMBER, GREY)]
    fig.legend(handles, ["Sweeney / the ad", "the controversy (critics, shock advertising)", "category and rivals", "other"],
               loc="lower center", ncol=4, frameon=False, fontsize=10, bbox_to_anchor=(0.5, -0.005))
    fig.suptitle("Novig before and after Sydney Sweeney: from a generic betting app to “the Sweeney ad”", x=0.01, ha="left",
                 fontsize=14, fontweight="bold")
    fig.subplots_adjust(left=0.11, right=0.97, top=0.88, bottom=0.1)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "novig_story.png", dpi=160)
    print("wrote", OUT / "novig_story.png", f"novig/wk {novig_pw:.1f} kalshi/wk {kalshi_pw:.0f} weeks {len(pre_w)}")


if __name__ == "__main__":
    main()
