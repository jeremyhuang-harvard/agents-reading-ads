"""Prolific ambassador vs single-brand faces: Shaq (three brands) vs Samuel L. Jackson x Capital One vs Johnny Depp x Dior Sauvage.

Top row: what each celebrity's public memory is made of (where Wikipedia readers click next, Jul-Oct 2026), with the
share going to their brand(s). Bottom row: what the brand's memory is made of, with the celebrity's share.
Output: output/presentation/ambassador_contrast.png. Run: uv run --extra assoc python scripts/plot_ambassador_contrast.py
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "derived" / "assoc"
OUT = ROOT / "output" / "presentation" / "ambassador_contrast.png"
RED, AMBER, GREY, BLUE = "#B91C1C", "#F59E0B", "#D1D5DB", "#1D4ED8"
ROWS = list(csv.DictReader((D / "clickstream_outflow_monthly.csv").open()))
FLOWS = list(csv.DictReader((D / "clickstream_flows_monthly.csv").open()))


def outflow(ent):
    agg, tot = Counter(), {}
    for r in ROWS:
        if r["entity"] == ent:
            agg[r["next_page"]] += int(r["n"])
            tot[r["month"]] = int(r["n"]) / float(r["share_of_outflow"])
    return agg, sum(tot.values()), sorted(tot)


def share(a, b):
    """Share of a's outgoing clicks that go to b, over months in which a has outflow."""
    agg, T, months = outflow(a)
    n = sum(int(r["n"]) for r in FLOWS if r["from"] == a and r["to"] == b and r["month"] in months)
    return (n / T if T else None), n


def label(p):
    t = re.sub(r" \(.*\)$", "", p.replace("_", " "))
    if t.startswith("List of awards"):
        return "Awards list"
    if t.startswith("List of") and t.endswith("performances") or t.endswith("filmography"):
        return "Filmography"
    if t == "List of highest-grossing actors":
        return "Highest-grossing actors"
    if t == "List of largest banks in the United States":
        return "Largest US banks"
    return t if len(t) <= 24 else t[:23] + "…"


def bars(ax, ent, title, highlight=(), amber=(), k=8, note=None):
    agg, T, _ = outflow(ent)
    items = agg.most_common(k)[::-1]
    cols = [RED if p in highlight else AMBER if p in amber else GREY for p, _ in items]
    ax.barh([label(p) for p, _ in items], [100 * n / T for _, n in items], color=cols)
    for y, (_, n) in enumerate(items):
        ax.text(100 * n / T + 0.4, y, f"{100 * n / T:.0f}%", va="center", fontsize=8.5)
    ax.set_title(f"{title}\n{int(T):,} outgoing clicks", loc="left", fontsize=10.5, fontweight="bold")
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlabel("% of clicks leaving the page", fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(100 * n / T for _, n in items) * 1.18)
    if note:
        ax.text(0.0, -0.30, note, transform=ax.transAxes, ha="left", va="top", fontsize=9.5, color=RED, fontweight="bold")


def pct(v):
    return "no page" if v is None else ("0%" if v == 0 else f"{100 * v:.2g}%")


def main():
    fig, axes = plt.subplots(2, 3, figsize=(17, 10.5))

    # Shaq: one face, many brands
    s_gen, _ = share("shaquille_oneal", "the_general")
    s_gold, _ = share("shaquille_oneal", "gold_bond")
    bars(axes[0, 0], "shaquille_oneal", "Shaquille O'Neal's page → next click",
         note=f"His brands: The General {pct(s_gen)}, Gold Bond {pct(s_gold)}, Icy Hot (no page)")
    ax = axes[1, 0]
    brands = [("The General", "the_general"), ("Gold Bond", "gold_bond"), ("Icy Hot", "icy_hot")]
    vals = []
    for name, b in brands:
        v, _ = share(b, "shaquille_oneal") if outflow(b)[1] else (None, 0)
        vals.append(v)
    ax.bar([n for n, _ in brands], [100 * (v or 0) for v in vals], color=[RED if v else GREY for v in vals])
    for x, v in enumerate(vals):
        ax.text(x, 100 * (v or 0) + 0.3, "no Wikipedia page;\nQwen: 'pain relief',\nnever Shaq" if v is None else pct(v), ha="center", fontsize=9)
    ax.text(0.0, -0.30, "One of his three brands carries him; none is part of him", transform=ax.transAxes, ha="left", va="top",
            fontsize=9.5, color=RED, fontweight="bold")
    ax.set_ylim(0, 14)
    ax.set_ylabel("Shaq's share of the brand's clicks (%)", fontsize=9)
    ax.set_title("Shaq's share of each brand's memory", loc="left", fontsize=10.5, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    # Samuel L. Jackson x Capital One (shared with Jennifer Garner)
    sj, _ = share("samuel_l_jackson", "capital_one")
    bars(axes[0, 1], "samuel_l_jackson", "Samuel L. Jackson's page → next click", note=f"Capital One: {pct(sj)}")
    cj, _ = share("capital_one", "samuel_l_jackson")
    cg, _ = share("capital_one", "jennifer_garner")
    bars(axes[1, 1], "capital_one", "Capital One's page → next click",
         note=f"Samuel L. Jackson: {pct(cj)}   Jennifer Garner: {pct(cg)}")

    # Johnny Depp x Dior Sauvage
    ds, _ = share("johnny_depp", "sauvage")
    dd, _ = share("johnny_depp", "dior")
    bars(axes[0, 2], "johnny_depp", "Johnny Depp's page → next click", amber={"Amber_Heard", "Depp_v._Heard"},
         note=f"Dior: {pct(dd)}   Sauvage: {pct(ds)}")
    sd, n_sd = share("sauvage", "johnny_depp")
    xd, _ = share("dior", "johnny_depp")
    bars(axes[1, 2], "sauvage", "Dior Sauvage's page → next click", highlight={"Johnny_Depp"},
         note=f"Depp: {pct(sd)} of Sauvage ({n_sd} clicks), {pct(xd)} of Dior")

    for ax, t in zip(axes[0], ("ONE FACE, MANY BRANDS", "ONE BRAND, TWO FACES", "A PRODUCT'S FACE")):
        ax.text(0, 1.30, t, transform=ax.transAxes, fontsize=12.5, fontweight="bold", color="#374151")
    fig.suptitle("Celebrity side (top) vs brand side (bottom): who is part of whom", x=0.01, ha="left", fontsize=14, fontweight="bold")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (RED, AMBER, GREY)]
    fig.legend(handles, ["the partner", "scandal", "other"], loc="lower center", ncol=3, frameon=False, fontsize=10,
               bbox_to_anchor=(0.5, -0.005))
    fig.subplots_adjust(left=0.1, right=0.98, top=0.83, bottom=0.12, hspace=0.85, wspace=0.6)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    print("wrote", OUT, dict(shaq_general=s_gen, shaq_gold=s_gold, brands_to_shaq=vals, sj_c1=sj, c1_sj=cj, c1_garner=cg,
                             depp_sauvage=ds, depp_dior=dd, sauvage_depp=sd, dior_depp=xd))


if __name__ == "__main__":
    main()
