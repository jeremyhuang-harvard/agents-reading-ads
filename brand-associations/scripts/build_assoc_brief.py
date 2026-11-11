"""Build the lightweight directed-association brief (output/assoc/assoc_brief.html).

Reads only derived files (no network):
  data/raw/assoc/ccnews/*/*.jsonl.gz           CC-NEWS articles (about-entity + body mentions)
  data/derived/assoc/clickstream_flows_monthly.csv
  data/derived/assoc/event_sweeney_novig_*.csv  + output/assoc/event_sweeney_novig.png
  data/derived/assoc/freeassoc_qwen3-8b-4bit_top.csv, directed_freeassoc_qwen3-8b-4bit.csv
  data/derived/assoc/trajectories_*.csv         (if present)

Run: uv run --extra assoc python scripts/build_assoc_brief.py
"""

from __future__ import annotations

import base64
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from implicit_ads.assoc import config  # noqa: E402
from implicit_ads.assoc.sources import ccnews  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "derived" / "assoc"
O = ROOT / "output" / "assoc"
O.mkdir(parents=True, exist_ok=True)
frame = config.load()
NAME = {e.id: e.name for e in frame.entities}
KIND = {e.id: e.kind for e in frame.entities}
PAIRS = {(p.celebrity, p.brand) for p in frame.pairs}
HUBS = ["adidas", "nike", "calvin_klein", "dior", "chanel", "louis_vuitton", "puma"]


# ------------------------------------------------------------------ CC-NEWS composition
def ccnews_composition():
    about_n = Counter()
    mention = Counter()  # (a, x): articles about a whose text names x
    seen = set()
    n_files = len(list((ROOT / "data/raw/assoc/ccnews").glob("*/*.done")))
    for month, art in ccnews.iter_articles():
        key = (art.get("title") or art["url"]).casefold()
        if key in seen:
            continue
        seen.add(key)
        for a in art.get("about", []):
            about_n[a] += 1
            for x in art["hits"]:
                if x != a:
                    mention[(a, x)] += 1
    return about_n, mention, len(seen), n_files


def share(mention, about_n, a, x):
    return mention[(a, x)] / about_n[a] if about_n[a] else float("nan")


def fig_hubs(about_n, mention, out="brief_hubs.png", source="full-text news articles (Common Crawl News sample)",
             unit="articles", min_c=5, min_b=20):
    hubs = [h for h in HUBS if about_n[h] >= min_b]
    fig, axes = plt.subplots(1, len(hubs), figsize=(3.3 * len(hubs), 5.4), sharey=False)
    axes = np.atleast_1d(axes)
    for ax, h in zip(axes, hubs):
        amb = sorted([c for c, b in PAIRS if b == h and about_n[c] >= min_c], key=lambda c: -share(mention, about_n, c, h))
        y = np.arange(len(amb))
        f = [100 * share(mention, about_n, c, h) for c in amb]   # brand in celebrity
        g = [100 * share(mention, about_n, h, c) for c in amb]   # celebrity in brand
        for yi, a, b in zip(y, f, g):
            ax.plot([a, b], [yi, yi], color="#D1D5DB", lw=2, zorder=1)
        ax.scatter(f, y, color="#1D4ED8", s=36, zorder=2, label=f"{NAME[h]} in celebrity's coverage")
        ax.scatter(g, y, color="#B91C1C", s=36, zorder=2, label=f"celebrity in {NAME[h]}'s coverage")
        ax.set_yticks(y, [NAME[c] for c in amb], fontsize=8)
        ax.invert_yaxis()
        ax.set_xscale("symlog", linthresh=0.5)
        ax.set_xlim(-0.05, 100)
        ax.set_title(f"{NAME[h]}\n({about_n[h]:,} {unit}; {len(amb)} ambassadors)", fontsize=9, fontweight="bold", loc="left")
        ax.set_xlabel(f"% of {unit}", fontsize=8)
        ax.grid(alpha=0.2, axis="x")
    handles = [plt.Line2D([], [], marker="o", ls="", color="#1D4ED8", label="brand's share of the celebrity (celebrity → brand)"),
               plt.Line2D([], [], marker="o", ls="", color="#B91C1C", label="celebrity's share of the brand (brand → celebrity)")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.suptitle(f"Multi-ambassador brands, {source}", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.07, 1, 0.92))
    fig.savefig(O / out, dpi=150)
    plt.close(fig)
    return hubs


def fig_pairs(about_n, mention, out="brief_pairs.png", source="Ambassador pairs in full-text news (Common Crawl News sample)",
              unit="articles", min_n=5):
    rows = []
    for c, b in PAIRS:
        if about_n[c] < min_n or about_n[b] < min_n:
            continue
        f, g = share(mention, about_n, c, b), share(mention, about_n, b, c)
        n_amb = sum(1 for cc, bb in PAIRS if bb == b)
        rows.append((c, b, f, g, about_n[c], about_n[b], n_amb))
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    ax = axes[0]
    eps = 0.002
    for c, b, f, g, nc, nb, k in rows:
        col = plt.cm.viridis(min(k, 11) / 11)
        ax.scatter(max(g, eps), max(f, eps), s=40, color=col, edgecolor="black", lw=0.3)
        ax.annotate(f"{NAME[c]}–{NAME[b]}", (max(g, eps), max(f, eps)), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    ax.plot([eps, 1], [eps, 1], ls="--", color="black", lw=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(eps * 0.8, 1.1)
    ax.set_ylim(eps * 0.8, 1.1)
    ax.set_xlabel(f"celebrity's share of the brand ({unit})")
    ax.set_ylabel(f"brand's share of the celebrity ({unit})")
    ax.set_title("Above the line: the brand is part of the celebrity more than the reverse\n(zero shares plotted at 0.2%)",
                 loc="left", fontsize=9.5)
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(1, 11))
    fig.colorbar(sm, ax=ax, label="number of ambassadors the brand has in the frame")
    ax = axes[1]
    pts = [(math.log(nb / nc), math.log(max(f, eps) / max(g, eps)), c, b, k) for c, b, f, g, nc, nb, k in rows if f > 0 or g > 0]
    if pts:
        x = np.array([p[0] for p in pts])
        y = np.array([p[1] for p in pts])
        ax.scatter(x, y, c=[plt.cm.viridis(min(p[4], 11) / 11) for p in pts], s=40, edgecolor="black", lw=0.3)
        for p in pts:
            ax.annotate(NAME[p[2]], (p[0], p[1]), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
        if len(pts) > 3:
            b1, b0 = np.polyfit(x, y, 1)
            xs = np.linspace(x.min(), x.max(), 10)
            ax.plot(xs, b0 + b1 * xs, color="black", lw=1, label=f"slope {b1:.2f}")
            ax.legend(frameon=False, fontsize=8)
    ax.axhline(0, color="#9CA3AF", lw=0.6)
    ax.axvline(0, color="#9CA3AF", lw=0.6)
    ax.set_xlabel(f"log( brand {unit} / celebrity {unit} )   — brand bigger →")
    ax.set_ylabel("log( brand-in-celebrity / celebrity-in-brand )")
    ax.set_title("The bigger side is the smaller component", loc="left", fontsize=9.5)
    fig.suptitle(source, x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(O / out, dpi=150)
    plt.close(fig)
    return rows


def fig_dumbbell(about_n, mention, min_n=10, out="brief_dumbbell.png"):
    rows = []
    for c, b in PAIRS:
        if about_n[c] >= min_n and about_n[b] >= min_n:
            f, g = share(mention, about_n, c, b), share(mention, about_n, b, c)
            if f > 0 or g > 0:
                rows.append((c, b, f, g))
    rows.sort(key=lambda r: (r[2] - r[3]))
    fig, ax = plt.subplots(figsize=(10, 0.36 * len(rows) + 1.6))
    y = np.arange(len(rows))
    for yi, (c, b, f, g) in zip(y, rows):
        ax.plot([100 * g, 100 * f], [yi, yi], color="#D1D5DB", lw=3, zorder=1)
    ax.scatter([100 * r[2] for r in rows], y, color="#1D4ED8", s=55, zorder=2, label="brand's share of the celebrity\n(% of articles about the celebrity naming the brand)")
    ax.scatter([100 * r[3] for r in rows], y, color="#B91C1C", s=55, zorder=2, label="celebrity's share of the brand\n(% of articles about the brand naming the celebrity)")
    ax.set_yticks(y, [f"{NAME[c]} – {NAME[b]}  ({about_n[c]} / {about_n[b]})" for c, b, _, _ in rows], fontsize=9)
    ax.set_xlabel("% of articles")
    ax.grid(alpha=0.2, axis="x")
    ax.legend(loc="center right", frameon=True, framealpha=0.95, edgecolor="#E5E7EB", fontsize=8.5)
    ax.set_title("Each ambassador pair in full-text news. Blue right of red: the brand is part of the celebrity more than the reverse.\n"
                 "Numbers in brackets: articles about the celebrity / about the brand.", loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(O / out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return rows


# ------------------------------------------------------------------ Wikipedia clickstream composition
def clickstream_counts():
    """Return (outflow totals, flows) in the same shape as the CC-NEWS (about_n, mention) counters."""
    path = D / "clickstream_flows_monthly.csv"
    outf, flows = Counter(), Counter()
    if not path.exists():
        return outf, flows, []
    seen, months = set(), set()
    for r in csv.DictReader(path.open()):
        flows[(r["from"], r["to"])] += int(r["n"])
        months.add(r["month"])
        if (r["month"], r["from"]) not in seen:
            seen.add((r["month"], r["from"]))
            outf[r["from"]] += int(r["outflow_from"])
    comp = D / "clickstream_outflow_monthly.csv"
    if comp.exists():  # entities with no frame-to-frame link still have an outflow total
        tot = defaultdict(dict)
        for r in csv.DictReader(comp.open()):
            n, sh = int(r["n"]), float(r["share_of_outflow"])
            if sh > 0:
                tot[r["entity"]][r["month"]] = n / sh
        for e, d in tot.items():
            outf[e] = int(sum(d.values()))
    return outf, flows, sorted(months)


def clickstream_pairs():
    path = D / "clickstream_flows_monthly.csv"
    if not path.exists():
        return [], []
    flows = defaultdict(int)
    out = {}
    months = set()
    for r in csv.DictReader(path.open()):
        flows[(r["from"], r["to"])] += int(r["n"])
        out[(r["month"], r["from"])] = int(r["outflow_from"])
        months.add(r["month"])
    tot = defaultdict(int)
    for (m, a), n in out.items():
        tot[a] += n
    rows = []
    for c, b in sorted(PAIRS):
        f = flows[(c, b)] / tot[c] if tot[c] else None
        g = flows[(b, c)] / tot[b] if tot[b] else None
        if f is not None and g is not None and (flows[(c, b)] or flows[(b, c)]):
            rows.append((c, b, flows[(c, b)], tot[c], flows[(b, c)], tot[b]))
    return rows, sorted(months)


def img(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def pct(x, d=1):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.{d}f}%"


def main():
    about_n, mention, n_articles, n_files = ccnews_composition()
    db_rows = fig_dumbbell(about_n, mention)
    n_brand_side = sum(1 for _, _, f, g in db_rows if f > g)
    outf, flows, cs_months = clickstream_counts()
    ev = {r["key"]: r for r in csv.DictReader((D / "event_sweeney_novig_periods.csv").open())}
    rel = {(r["period"], r["cue"]): r for r in csv.DictReader((D / "event_sweeney_novig_related.csv").open())}
    fa_top = defaultdict(list)
    for r in csv.DictReader((D / "freeassoc_qwen3-8b-4bit_top.csv").open()):
        fa_top[r["cue"]].append((r["response"], float(r["share_of_samples"])))
    traj_png = sorted(O.glob("trajectories_*_post.png"))
    traj_csv = D / "trajectories_st-baai-bge-base-en-v1-5.csv"
    traj_rows = list(csv.DictReader(traj_csv.open())) if traj_csv.exists() else []
    traj_m = D / "trajectories_st-baai-bge-base-en-v1-5_masked.csv"
    traj_mrows = {r["event"]: r for r in csv.DictReader(traj_m.open())} if traj_m.exists() else {}

    # Sweeney x Novig clickstream (October)
    nov = {}
    cpath = D / "clickstream_flows_monthly.csv"
    if cpath.exists():
        for r in csv.DictReader(cpath.open()):
            if {r["from"], r["to"]} == {"sydney_sweeney", "novig"}:
                nov[(r["month"], r["from"])] = (int(r["n"]), int(r["outflow_from"]))

    def fa(cue, k=6):
        items = [(w, v) for w, v in fa_top.get(cue, []) if w.casefold() != NAME[cue].casefold()]
        return ", ".join(f"{w} ({v:.0%})" for w, v in items[:k])

    nov_rows = ""
    for m in sorted({k[0] for k in nov}):
        a = nov.get((m, "sydney_sweeney"))
        b = nov.get((m, "novig"))
        nov_rows += (f"<tr><td>Wikipedia clicks, {m}</td><td class=num>{pct(a[0] / a[1], 2) if a else '–'}"
                     f"<br><span class=meta>{a[0]:,} of {a[1]:,}</span></td><td class=num>{pct(b[0] / b[1]) if b else '–'}"
                     f"<br><span class=meta>{b[0]:,} of {b[1]:,}</span></td></tr>" if a or b else "")
    post, pre = ev["post"], ev["pre"]

    traj_html = ""
    if traj_rows:
        trs = ""
        for r in traj_rows:
            mr = traj_mrows.get(r["event"], {})
            trs += (f"<tr><td>{NAME[r['celebrity']]} × {NAME[r['brand']]}<br><span class=meta>{r['type']}, {r['date']}</span></td>"
                    f"<td class=num>{float(r['did_c_to_b_post']):+.3f}<br><span class=meta>[{float(r['did_c_to_b_post_lo']):+.3f}, {float(r['did_c_to_b_post_hi']):+.3f}]</span></td>"
                    f"<td class=num>{float(r['did_b_to_c_post']):+.3f}<br><span class=meta>[{float(r['did_b_to_c_post_lo']):+.3f}, {float(r['did_b_to_c_post_hi']):+.3f}]</span></td>"
                    f"<td class=num>{float(mr['did_c_to_b_post']):+.3f} / {float(mr['did_b_to_c_post']):+.3f}</td></tr>" if mr else "")
        traj_html = f"""
<h2 id="vectors">4. Vectors: who moved toward whom (Sweeney × Novig so far)</h2>
<p>Each entity's vector is the average sentence embedding (BAAI bge-base) of its English news headlines in a window (GDELT). For each event I compare the 90 days before (days −90 to −8) with the 30 days after. <b>Celebrity → brand</b> is how much closer the celebrity's vector moved to the brand's <i>pre-event</i> position; <b>brand → celebrity</b> is the reverse. Both subtract the same movement toward three placebo targets (rival brands; comparable celebrities), so general drift cancels. Units are changes in cosine similarity; brackets are 90% bootstrap intervals over headlines.</p>
<table><tr><th>event</th><th class=num>celebrity moved toward brand</th><th class=num>brand moved toward celebrity</th><th class=num>names masked<br>(c→b / b→c)</th></tr>{trs}</table>
<p class=meta>“Names masked” replaces every celebrity and brand name with [NAME] before embedding, so movement reflects what the coverage is about rather than the literal co-mention.</p>
""" + "".join(f'<figure><img src="{img(pth)}" alt="event map"><figcaption>Entity vectors projected on their first two principal components. Grey points are placebo entities before the event. Left: names kept, so headlines naming Sweeney pull Novig toward her. Right: every name replaced by [NAME]; Novig still leaves the betting cluster, and both sides converge on the ad story.</figcaption></figure>' for pth in sorted(O.glob("event_map_*.png"))) + "".join(f'<figure><img src="{img(pth)}" alt="trajectory scatter"><figcaption>Each point is one event. Above the dashed line the celebrity absorbed the brand; below it the brand absorbed the celebrity.</figcaption></figure>' for pth in traj_png[:1])

    wiki_hubs = ""
    if flows:
        # month-matched: only months in which both articles have recorded outflow
        mo = defaultdict(dict)
        for r in csv.DictReader((D / "clickstream_outflow_monthly.csv").open()):
            if float(r["share_of_outflow"]) > 0:
                mo[r["entity"]][r["month"]] = int(r["n"]) / float(r["share_of_outflow"])
        mf = defaultdict(int)
        for r in csv.DictReader((D / "clickstream_flows_monthly.csv").open()):
            mf[(r["month"], r["from"], r["to"])] += int(r["n"])
        trs = ""
        stats = []
        for c, b in PAIRS:
            months = sorted(set(mo[c]) & set(mo[b]))
            oc, ob = sum(mo[c][m] for m in months), sum(mo[b][m] for m in months)
            fc = sum(mf[(m, c, b)] for m in months)
            fb = sum(mf[(m, b, c)] for m in months)
            if fb > 0 and oc and ob:
                stats.append((c, b, fc / oc, fb / ob, oc, ob, len(months)))
        for c, b, x, y_, oc, ob, k in sorted(stats, key=lambda r: -r[3]):
            trs += (f"<tr><td>{NAME[c]} – {NAME[b]}</td><td class=num>{pct(x, 2)}</td>"
                    f"<td class=num>{pct(y_, 2)}</td><td class=num>{int(oc):,} / {int(ob):,}<br><span class=meta>{k} month{'s' if k > 1 else ''}</span></td></tr>")
        wiki_hubs = f"""<h3>Wikipedia navigation ({cs_months[0]} to {cs_months[-1]})</h3>
<p>Share of all clicks leaving one article that go to the other. Wikipedia only publishes transitions seen at least 10 times a month, so most brand → ambassador links are zero; these are the pairs where readers do click from the brand to the person. They are the cases where the person is large relative to the brand page: Novig, Roger Federer at On, Sweeney at American Eagle, Jacob Elordi at Bottega Veneta. For a brand with many ambassadors, readers go to at most one or two of them (Messi at Adidas, LeBron at Nike, Jung Kook at Calvin Klein).</p>
<table><tr><th>pair</th><th class=num>celebrity page → brand</th><th class=num>brand page → celebrity</th><th class=num>clicks out (celebrity / brand)</th></tr>{trs}</table>"""

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Directed celebrity–brand associations — first look</title><style>{CSS}</style></head><body><div class="wrap">
<nav><p>Contents</p><a href="#idea">1. The idea</a><a href="#novig">2. Sweeney × Novig</a><a href="#hubs">3. Brands with many ambassadors</a>{'<a href="#vectors">4. Vectors</a>' if traj_html else ''}<a href="#llm">5. A language model's associations</a><a href="#next">6. Scale-up plan</a></nav>
<main>
<div class="kicker">Implicit Ads · first look · November 10, 2026</div>
<h1>Who is part of whom? Directed associations between celebrities and brands</h1>
<p class="meta">Jeremy Huang · exploratory, public data only · every number below is observed in the named source unless marked</p>
<p class="lede">Similarity says Tate McRae and Adidas are “close.” It cannot say whether thinking of Tate calls up Adidas more than thinking of Adidas calls up Tate. We measure each direction separately, as the share of one entity's representation that is made of the other.</p>
<div class="bottom-line"><h3>Bottom line</h3><ol>
<li><b>Associations are directional, and the bigger side is usually the smaller component.</b> A brand is a visible part of its ambassador's coverage and navigation; the ambassador is a sliver of the brand's.</li>
<li><b>A young brand can flip it.</b> After the September 9 campaign, Sydney Sweeney is {pct(float(post['bwd_celebrity_in_brand']), 0)} of Novig's news coverage, while Novig is {pct(float(post['fwd_brand_in_celebrity']), 0)} of hers; on Wikipedia, about a quarter of readers leaving Novig's page go to Sweeney's.</li>
<li><b>Interference shows up on the brand side.</b> A brand with many ambassadors points to one or two of them. Nike's coverage names LeBron in 9% of articles and each of its other ambassadors in under half a percent. The others are part of Nike's story without Nike being part of theirs (the “fan effect” in memory research).</li>
<li><b>This is a sketch.</b> Light samples (a few thousand articles, four months of Wikipedia clicks); the pipeline is built to scale once we choose what to measure.</li></ol></div>

<h2 id="idea">1. The idea: composition, not similarity</h2>
<p>An entity's representation is what is written and searched about it. Sarkar (“Economic Representations”) builds a firm's vector as the average embedding of its news coverage. Averaging makes the vector <i>decompose</i>: the share of Tate's vector that comes from Tate coverage mentioning Adidas is a well-defined number, and it is different from the share of Adidas's vector that comes from Adidas coverage mentioning Tate. Psychologists call the two directions forward and backward associative strength; <i>Ads as Cues</i> needs exactly this object, because a cue retrieves goods according to how strongly the cue points to them, and the goods it retrieves compete.</p>
<table><tr><th>question</th><th>similarity (symmetric)</th><th>association (directed)</th></tr>
<tr><td>McDonald's vs Burger King</td><td>very similar</td><td>neither need be part of the other</td></tr>
<tr><td>Tate McRae vs Adidas</td><td>one number</td><td>Adidas in Tate ≫ Tate in Adidas (expected)</td></tr>
<tr><td>Sweeney vs Novig</td><td>one number</td><td>Sweeney in Novig ≫ Novig in Sweeney (observed)</td></tr></table>
<p>Measures used here, all directed: share of A's news articles that name B (GDELT, Common Crawl News); share of clicks leaving A's Wikipedia article that go to B's; share of A's related Google searches naming B; and how far A's embedding moves toward B after an event.</p>

<h2 id="novig">2. Sweeney × Novig: the brand absorbs the celebrity</h2>
<p>Novig, a sports prediction-market startup, launched nationally in August 2026 and released its first national campaign starring Sydney Sweeney (also an equity holder) on September 9 <a href="https://news.northeastern.edu/2026/09/14/sydney-sweeney-ad-novig">[Northeastern]</a> <a href="https://fortune.com/2026/09/18/sydney-sweeney-novig-viral-ads">[Fortune]</a>.</p>
<table><tr><th>measure</th><th class=num>Novig's share of Sweeney</th><th class=num>Sweeney's share of Novig</th></tr>
<tr><td>English news articles (GDELT), May 1 – Sep 8</td><td class=num>{pct(float(pre['fwd_brand_in_celebrity']))}<br><span class=meta>{pre['n_joint']} of {int(pre['n_celebrity']):,}</span></td><td class=num>{pct(float(pre['bwd_celebrity_in_brand']))}<br><span class=meta>{pre['n_joint']} of {pre['n_brand']}</span></td></tr>
<tr><td>English news articles (GDELT), Sep 9 – Nov 8</td><td class=num>{pct(float(post['fwd_brand_in_celebrity']))}<br><span class=meta>{post['n_joint']} of {post['n_celebrity']}</span></td><td class=num>{pct(float(post['bwd_celebrity_in_brand']))}<br><span class=meta>{post['n_joint']} of {post['n_brand']}</span></td></tr>
<tr><td>Google related searches (US), after Sep 9</td><td class=num>{pct(float(rel[('post','sydney_sweeney')]['share_of_related_weight']))}</td><td class=num>{pct(float(rel[('post','novig')]['share_of_related_weight']))}</td></tr>
{nov_rows}</table>
<div class="note"><strong>What Novig's searches were before and after</strong>Before: {rel[('pre','novig')]['top_related'][:160]}…<br>After: {rel[('post','novig')]['top_related'][:160]}…</div>
<figure><img src="{img(O / 'event_sweeney_novig.png')}" alt="Sweeney Novig event"><figcaption>Top: weekly share of each side's news coverage that names the other. Middle: weekly article counts for Novig and rivals (rival counts were partly rate-limited by GDELT). Bottom: Google Trends interest.</figcaption></figure>
<p>On Wikipedia in October, readers leaving Novig's article went next to Sweeney (≈26%), then to the athletes who criticized the ad (Gracie Kramer, Ariarne Titmus, Amy Hunt), then to “Prediction market” and “Shock advertising.” Within weeks the cue “Novig” retrieves the spokesperson and the controversy ahead of the product category: a clean case of a celebrity cue crowding out what the brand does.</p>

<h2 id="hubs">3. Brands with many ambassadors</h2>
<p>The frame has 43 celebrities, 36 brands and 53 sourced relationships, built around hub brands: Adidas (11 ambassadors), Calvin Klein, Nike and Dior (5 each), Chanel (4), Louis Vuitton and Puma (3).</p>
<h3>Full-text news</h3>
<p>{n_articles:,} English news articles whose headline or description names a frame entity, from a light sample of {n_files} Common Crawl News files. For each pair with at least 10 articles about each side, the chart compares how often articles about the celebrity name the brand with how often articles about the brand name the celebrity. In {n_brand_side} of {len(db_rows)} pairs the brand is the larger share of the celebrity. The reversals are the superstars: Rihanna is in a fifth of the Puma articles, LeBron in a tenth of the Nike articles, and Sweeney in a third of the American Eagle articles. Rising or niche ambassadors (A'ja Wilson, Anya Taylor-Joy, Kristen Stewart, Angel Reese, Anthony Edwards) carry the brand without being part of it. Nike's coverage names its biggest star (LeBron, 9%) and almost none of its other ambassadors (≤0.4% each): with many ambassadors, the brand side points to one.</p>
<figure><img src="{img(O / 'brief_dumbbell.png')}" alt="pairs dumbbell"><figcaption>Light sample: shares based on 10–660 articles per entity; zeros are often small-sample zeros.</figcaption></figure>
{wiki_hubs}

{traj_html}

<h2 id="llm">5. A language model's associations</h2>
<p>Local Qwen3-8B, 30 independent free-association samples per name (“write the first 10 things that come to mind”), no candidate list. Its knowledge stops in early 2025, so it predates Novig and recent deals; treat it as a model of the pre-period culture (<span class="tag rep">model</span>).</p>
<table><tr><th>cue</th><th>most frequent associations (share of samples)</th></tr>
<tr><td>Adidas</td><td>{fa('adidas')}</td></tr><tr><td>Chanel</td><td>{fa('chanel')}</td></tr><tr><td>Calvin Klein</td><td>{fa('calvin_klein')}</td></tr>
<tr><td>Kendall Jenner</td><td>{fa('kendall_jenner')}</td></tr><tr><td>LeBron James</td><td>{fa('lebron_james')}</td></tr><tr><td>Rihanna</td><td>{fa('rihanna')}</td></tr><tr><td>Sydney Sweeney</td><td>{fa('sydney_sweeney')}</td></tr><tr><td>Tate McRae</td><td>{fa('tate_mcrae')}</td></tr></table>
<p>Brands retrieve attributes (country, logo, product, founder), almost never people. Celebrities sometimes retrieve their brand: LeBron James → Nike in 57% of samples, Kendall Jenner → Calvin Klein 53%, Charlize Theron → Dior 30%, Rihanna → Puma 23%. In 2,370 samples, no brand cue ever produced one of its ambassadors. This is the purest form of the asymmetry: the link runs only from person to brand.</p>

<h2 id="next">6. What is light now, and how it scales</h2>
<ul class="steps">
<li><b>Full-text news at scale.</b> Common Crawl News streams ~400 files (1 GB each) per month; we read ~2 per month here. Nothing is stored except matched articles (a few MB). Scaling to ~10 files per month gives ~5× the articles. <span class="why">Decision: which months and how many files.</span></li>
<li><b>Monthly Wikipedia clickstream back to 2024.</b> Complete, directed, free; 0.5 GB streamed per month, a few MB kept. <span class="why">Gives a monthly panel of who-points-to-whom for every entity.</span></li>
<li><b>Vectors for all 18 dated events.</b> Wear events (Taylor Swift's New Balance 550s, Nike AF1s, Kristin Juszczyk jacket; Meghan's Outland jeans) vs ambassador deals. <span class="why">The binding constraint is GDELT's rate limit (about one request a minute today), so this runs overnight.</span></li>
<li><b>Human benchmark.</b> Small World of Words free-association norms (registration required) to anchor the model-based measures.</li></ul>
<div class="note"><strong>Caveats</strong>Pairs were assembled by hand to span size ratios and hub brands, not sampled. Shares depend on how names are matched (ambiguous names such as Puma or Jennie require context words). Wikipedia only publishes transitions seen at least 10 times a month. No result here is causal.</div>
</main></div>
<div class="zoom" id="zoom"><img alt=""></div>
<script>document.querySelectorAll('figure img').forEach(i=>i.addEventListener('click',()=>{{const z=document.getElementById('zoom');z.querySelector('img').src=i.src;z.classList.add('on');}}));document.getElementById('zoom').addEventListener('click',e=>e.currentTarget.classList.remove('on'));</script>
</body></html>"""
    (O / "assoc_brief.html").write_text(html)
    print("wrote", O / "assoc_brief.html", f"{(O / 'assoc_brief.html').stat().st_size / 1e6:.1f} MB; articles", n_articles,
          "files", n_files, "clickstream months", cs_months, "trajectories", len(traj_rows))


CSS = (ROOT / "docs/report-template/demo_findings.html").read_text().split("<style>")[1].split("</style>")[0]


if __name__ == "__main__":
    main()
