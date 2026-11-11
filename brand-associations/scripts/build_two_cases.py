"""Two-case theory brief: Tate McRae x Adidas vs Sydney Sweeney x Novig (output/assoc/two_cases.html).

Run: uv run --extra assoc --extra assoc-news python scripts/build_two_cases.py
"""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assoc_brief as B  # noqa: E402

D, O, NAME = B.D, B.O, B.NAME
CASES = [("tate_mcrae", "adidas", "tate_adidas_2026", "2026-07-22"), ("sydney_sweeney", "novig", "sweeney_novig", "2026-09-09")]
PRETTY = {"Nike,_Inc.": "Nike", "Puma_(brand)": "Puma", "The_Housemaid_(2025_film)": "The Housemaid (film)",
          "Euphoria_(American_TV_series)": "Euphoria (TV)", "Shock_advertising": "Shock advertising"}


def label(page):
    return PRETTY.get(page, page.replace("_", " "))


def outflow_composition():
    rows = list(csv.DictReader((D / "clickstream_outflow_monthly.csv").open()))
    out = {}
    for ent in ("tate_mcrae", "adidas", "sydney_sweeney", "novig"):
        agg, tot = Counter(), {}
        for r in rows:
            if r["entity"] == ent:
                agg[r["next_page"]] += int(r["n"])
                tot[r["month"]] = int(r["n"]) / float(r["share_of_outflow"])
        T = sum(tot.values())
        out[ent] = ([(p, n / T) for p, n in agg.most_common(10)], T, sorted(tot))
    return out


def partner_shares():
    """Month-matched share of an entity page's outgoing clicks that go to the partner page."""
    mo = defaultdict(dict)
    for r in csv.DictReader((D / "clickstream_outflow_monthly.csv").open()):
        if float(r["share_of_outflow"]) > 0:
            mo[r["entity"]][r["month"]] = int(r["n"]) / float(r["share_of_outflow"])
    mf = Counter()
    for r in csv.DictReader((D / "clickstream_flows_monthly.csv").open()):
        mf[(r["month"], r["from"], r["to"])] += int(r["n"])
    out = {}
    for a, b in (("tate_mcrae", "adidas"), ("adidas", "tate_mcrae"), ("sydney_sweeney", "novig"), ("novig", "sydney_sweeney")):
        months = sorted(set(mo[a]) & set(mo[b]))
        tot = sum(mo[a][m] for m in months)
        n = sum(mf[(m, a, b)] for m in months)
        out[a] = (n, tot, months)
    return out


def fig_made_of(comp, ps):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.6))
    for ax, ent in zip(axes.flat, ("tate_mcrae", "adidas", "sydney_sweeney", "novig")):
        items, T, months = comp[ent]
        partner = {"tate_mcrae": "Adidas", "adidas": "Tate_McRae", "sydney_sweeney": "Novig", "novig": "Sydney_Sweeney"}[ent]
        names = [label(p) for p, _ in items][::-1]
        vals = [100 * v for _, v in items][::-1]
        cols = ["#B91C1C" if p == partner else ("#F59E0B" if p in ("Nike,_Inc.", "Puma_(brand)", "Reebok", "Kalshi", "PredictIt", "Prediction_market") else "#9CA3AF")
                for p, _ in items][::-1]
        ax.barh(names, vals, color=cols)
        ax.set_title(f"{NAME[ent]}'s page: where readers click next\n{int(T):,} outgoing clicks, {months[0]} to {months[-1]}",
                     loc="left", fontsize=10, fontweight="bold")
        ax.tick_params(axis="y", labelsize=8)
        ax.set_xlabel("% of outgoing clicks", fontsize=8)
        share = next((v for p, v in items if p == partner), None)
        if share is None:
            n, tot, ms = ps[ent]
            txt = (f"{partner.replace('_', ' ')}: {100 * n / tot:.2f}% ({n:,} clicks, {', '.join(ms)})" if n
                   else f"{partner.replace('_', ' ')}: below Wikipedia's\n10-clicks-a-month floor (≈0%)")
            ax.text(0.98, 0.04, txt, transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="#B91C1C",
                    bbox=dict(facecolor="white", edgecolor="#FCA5A5"))
    fig.suptitle("What each public memory is made of. Red = the partner; amber = rivals or the product category", x=0.01, ha="left",
                 fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(O / "two_cases_made_of.png", dpi=150)
    plt.close(fig)


def fig_regimes(about_n, mention, ev, ps):
    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    eps = 0.003
    for c, b in B.PAIRS:
        if about_n[c] >= 10 and about_n[b] >= 10:
            f, g = B.share(mention, about_n, c, b), B.share(mention, about_n, b, c)
            ax.scatter(max(g, eps), max(f, eps), s=22, color="#D1D5DB", zorder=1)
    for (c, b, eid, _), col in zip(CASES, ("#1D4ED8", "#B91C1C")):
        if eid in ev:
            p = ev[eid]["post"]
            f, g = float(p["fwd_brand_in_celebrity"] or 0), float(p["bwd_celebrity_in_brand"] or 0)
            eps = 4e-4  # case points are measured shares, not small-sample zeros
            ax.scatter(max(g, eps), max(f, eps), s=140, color=col, edgecolor="black", zorder=3)
            right = g < 0.05
            ax.annotate(f"{NAME[c]} × {NAME[b]}\nnews, after campaign", (max(g, eps), max(f, eps)), fontsize=9, color=col,
                        fontweight="bold", xytext=(10, 6) if right else (-10, 10), textcoords="offset points", ha="left" if right else "right")
        n1, t1, _ = ps[c]
        n2, t2, _ = ps[b]
        if n1 and n2:
            f, g = n1 / t1, n2 / t2
            ax.scatter(g, f, s=140, facecolor="white", edgecolor=col, lw=2.2, zorder=3)
            ax.annotate(f"{NAME[c]} × {NAME[b]}\nWikipedia clicks", (g, f), fontsize=9, color=col, fontweight="bold",
                        xytext=(-12, 8), textcoords="offset points", ha="right")
    ax.plot([3e-4, 1], [3e-4, 1], ls="--", color="black", lw=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(3e-4, 1.2)
    ax.set_ylim(3e-4, 1.2)
    ax.set_xlabel("celebrity's share of the brand's memory  (brand → celebrity)")
    ax.set_ylabel("brand's share of the celebrity's memory  (celebrity → brand)")
    kw = dict(transform=ax.transAxes, fontsize=9.5, color="#374151")
    ax.text(0.03, 0.97, "ABOVE THE LINE: forward regime\nthe celebrity is a cue for the brand;\nthe brand's memory barely changes", va="top", **kw)
    ax.text(0.03, 0.03, "WEAK LINK", **kw)
    ax.text(0.97, 0.40, "BELOW THE LINE: backward regime\nthe celebrity redefines the brand\n(transfer, overshadowing, borrowed risk)", ha="right", **kw)
    ax.set_title("Grey: other ambassador pairs in full-text news (light sample; zero shares drawn at 0.3%)", loc="left", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(O / "two_cases_regimes.png", dpi=150)
    plt.close(fig)


def trends_summary(eid, d0):
    path = D / f"event_{eid}_trends.csv"
    if not path.exists():
        return []
    rows = list(csv.DictReader(path.open()))
    d0 = date.fromisoformat(d0)
    out = []
    for t in dict.fromkeys(r["term"] for r in rows):
        s = {date.fromisoformat(r["date"]): int(r["value"]) for r in rows if r["term"] == t}
        pre = [v for d, v in s.items() if -56 <= (d - d0).days <= -1]
        post = [v for d, v in s.items() if 0 <= (d - d0).days <= 13]
        late = [v for d, v in s.items() if 14 <= (d - d0).days <= 45]
        if pre and post:
            out.append((t, np.mean(pre), np.mean(post), np.mean(late) if late else float("nan")))
    return out


def main():
    about_n, mention, n_articles, n_files = B.ccnews_composition()
    comp = outflow_composition()
    ps = partner_shares()
    fig_made_of(comp, ps)
    ev = {}
    for c, b, eid, _ in CASES:
        p = D / f"event_{eid}_periods.csv"
        if p.exists():
            ev[eid] = {r["key"]: r for r in csv.DictReader(p.open())}
    fig_regimes(about_n, mention, ev, ps)
    rel = {}
    for c, b, eid, _ in CASES:
        p = D / f"event_{eid}_related.csv"
        if p.exists():
            for r in csv.DictReader(p.open()):
                rel[(eid, r["period"], r["cue"])] = r
    traj = {r["event"]: r for r in csv.DictReader((D / "trajectories_st-baai-bge-base-en-v1-5.csv").open())} \
        if (D / "trajectories_st-baai-bge-base-en-v1-5.csv").exists() else {}
    trajm = {r["event"]: r for r in csv.DictReader((D / "trajectories_st-baai-bge-base-en-v1-5_masked.csv").open())} \
        if (D / "trajectories_st-baai-bge-base-en-v1-5_masked.csv").exists() else {}
    pct = B.pct

    def ev_row(eid, period):
        r = ev.get(eid, {}).get(period)
        if not r:
            return "<td class=num>pending</td><td class=num>pending</td>"
        f = float(r["fwd_brand_in_celebrity"]) if r["fwd_brand_in_celebrity"] else None
        g = float(r["bwd_celebrity_in_brand"]) if r["bwd_celebrity_in_brand"] else None
        d = lambda v: 2 if v is not None and v < 0.01 else 1  # noqa: E731
        return (f"<td class=num>{pct(f, d(f))}<br><span class=meta>{r['n_joint']} of {int(r['n_celebrity']):,}</span></td>"
                f"<td class=num>{pct(g, d(g))}<br><span class=meta>{r['n_joint']} of {int(r['n_brand']):,}</span></td>")

    def rel_row(eid, period, c, b):
        a, z = rel.get((eid, period, c)), rel.get((eid, period, b))
        if not a or not z:
            return "<td class=num>pending</td><td class=num>pending</td>"
        return f"<td class=num>{pct(float(a['share_of_related_weight']))}</td><td class=num>{pct(float(z['share_of_related_weight']))}</td>"

    def traj_row(eid):
        r, m = traj.get(eid), trajm.get(eid)
        if not r:
            return "<td class=num>pending</td><td class=num>pending</td>"
        return (f"<td class=num>{float(r['did_c_to_b_post']):+.3f}<br><span class=meta>[{float(r['did_c_to_b_post_lo']):+.3f}, {float(r['did_c_to_b_post_hi']):+.3f}]"
                f"{'; masked ' + format(float(m['did_c_to_b_post']), '+.3f') if m else ''}</span></td>"
                f"<td class=num>{float(r['did_b_to_c_post']):+.3f}<br><span class=meta>[{float(r['did_b_to_c_post_lo']):+.3f}, {float(r['did_b_to_c_post_hi']):+.3f}]"
                f"{'; masked ' + format(float(m['did_b_to_c_post']), '+.3f') if m else ''}</span></td>")

    def wiki_share(ent, partner_page):
        n, tot, ms = ps[ent]
        if not n:
            return "≈0<br><span class=meta>below the 10-clicks-a-month floor</span>"
        return f"{pct(n / tot, 2)}<br><span class=meta>{n:,} of {int(tot):,}; {', '.join(ms) if len(ms) < 3 else ms[0] + '–' + ms[-1]}</span>"

    tr_nov = trends_summary("sweeney_novig", "2026-09-09")
    tr_tate = trends_summary("tate_adidas_2026", "2026-07-22")

    def tr_table(rows):
        if not rows:
            return "<p class=meta>pending</p>"
        return "<table><tr><th>Google Trends term (US)</th><th class=num>8 weeks before</th><th class=num>days 0–13</th><th class=num>days 14–45</th></tr>" + "".join(
            f"<tr><td>{t}</td><td class=num>{a:.1f}</td><td class=num>{b:.1f}</td><td class=num>{c:.1f}</td></tr>" for t, a, b, c in rows) + "</table>"

    figs = {k: (B.img(O / f) if (O / f).exists() else "") for k, f in
            [("regimes", "two_cases_regimes.png"), ("madeof", "two_cases_made_of.png"), ("nov", "event_sweeney_novig.png"),
             ("tate", "event_tate_adidas_2026.png"), ("map_nov", "event_map_sweeney_novig.png"), ("map_tate", "event_map_tate_adidas_2026.png")]}

    def fig(key, cap):
        return f'<figure><img src="{figs[key]}" alt=""><figcaption>{cap}</figcaption></figure>' if figs[key] else ""

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Two directed associations: Tate McRae × Adidas and Sydney Sweeney × Novig</title><style>{B.CSS}
.eq {{ font-family: var(--serif); font-size: 19px; background:#fff; border:1px solid var(--rule); padding:12px 16px; margin:14px 0; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }} @media (max-width:700px) {{ .two {{ grid-template-columns:1fr; }} }}
.two > div {{ background:#fff; border:1px solid var(--rule); padding:14px 16px; }}</style></head><body><div class="wrap">
<nav><p>Contents</p><a href="#claim">1. The claim</a><a href="#theory">2. What theory says</a><a href="#cases">3. The two cases in data</a><a href="#predictions">4. Predictions</a><a href="#tests">5. Tests we can run</a><a href="#refs">References</a></nav>
<main>
<div class="kicker">Implicit Ads · theory note · November 10, 2026</div>
<h1>Who is part of whom, and why it governs interference</h1>
<p class="meta">Tate McRae × Adidas and Sydney Sweeney × Novig as opposite cases · public data · exploratory</p>
<p class="lede">An ambassador deal creates two links, not one. One runs from the celebrity to the brand: whenever people think of Tate, does Adidas come along? The other runs from the brand to the celebrity: whenever people think of Adidas, does Tate come along? How big each link is depends on how much else is already stored under each name, and that determines both what the celebrity can do for the brand and how much interference the celebrity creates.</p>
<div class="bottom-line"><h3>Bottom line</h3><ol>
<li><b>Tate × Adidas is a weak link, tilted slightly forward.</b> After the July 22 campaign, Adidas appears in {pct(float(ev['tate_adidas_2026']['post']['fwd_brand_in_celebrity']), 2) if 'tate_adidas_2026' in ev else '–'} of Tate's English news coverage and Tate in {pct(float(ev['tate_adidas_2026']['post']['bwd_celebrity_in_brand']), 2) if 'tate_adidas_2026' in ev else '–'} of Adidas's. Neither shows up in the other's Wikipedia clicks or related searches. Both memories are crowded: Tate's with her songs and relationships, Adidas's with its founders, its rivals and eleven ambassadors. Theory says crowding at both cues caps what the deal can do.</li>
<li><b>Sweeney × Novig is the backward regime.</b> Novig had almost no public memory, so the campaign wrote it. Sweeney became {pct(float(ev['sweeney_novig']['post']['bwd_celebrity_in_brand']), 0) if 'sweeney_novig' in ev else '–'} of Novig's news coverage and 26% of the clicks leaving its Wikipedia page, while Novig is a sliver of hers.</li>
<li><b>Theory predicts opposite risks.</b> Tate's forward link is limited by interference at her name, from her songs, tours and relationships. Sweeney's backward link creates interference inside the brand: the celebrity and the controversy crowd out the category (“sports prediction market”) that should bring Novig to mind when a bettor decides where to bet.</li></ol></div>

<h2 id="claim">1. The claim</h2>
<p>Write the public memory of an entity as everything that is written, searched and read about it. Its representation, in Sarkar's sense, is the average of those documents. Then:</p>
<div class="two"><div><b>Forward strength</b> a(c→b)<br>share of the celebrity's memory that is the brand<br><span class=meta>“When I think of Tate, does Adidas come to mind?”</span></div>
<div><b>Backward strength</b> β(b→c)<br>share of the brand's memory that is the celebrity<br><span class=meta>“When I think of Novig, does Sweeney come to mind?”</span></div></div>
<p>Our claim is that these two numbers, together with how large and crowded each memory already is, determine how a celebrity link affects interference: whether the celebrity's appearances bring the brand to mind over its rivals, and whether the celebrity takes over the brand's own cue.</p>

<h2 id="theory">2. What theory says</h2>
<h3>2.1 Ads as Cues: asymmetry is interference</h3>
<p>In Bordalo, Burro, Gennaioli, Nacamulli & Shleifer (2025), a cue <i>c</i> brings to mind experience <i>x</i> with probability</p>
<div class="eq">r<sub>x</sub>(c) = S(c, x) · f<sub>x</sub> / Σ<sub>x′</sub> S(c, x′) · f<sub>x′</sub>&nbsp;&nbsp;&nbsp;(their eq. 1)</div>
<p>Similarity S is symmetric. The numerator is association times frequency; the denominator is interference: everything else the cue also calls up, including the “fog” of unbranded experiences. Apply it to both directions of one pair with the same S(Tate, Adidas):</p>
<div class="eq">log r<sub>Adidas</sub>(Tate) − log r<sub>Tate</sub>(Adidas) = log Σ<sub>x′</sub>S(Adidas,x′)f<sub>x′</sub> − log Σ<sub>x′</sub>S(Tate,x′)f<sub>x′</sub> + log f<sub>Adidas</sub>/f<sub>Tate</sub></div>
<p>So the asymmetry has two sources: <b>how crowded each cue is</b> (the denominators) and <b>how familiar each target is</b> (the frequencies). Adidas is both crowded and familiar, which makes Adidas → Tate weak. Tate → Adidas is limited instead by how crowded Tate's own memory is: her songs, tour and relationships all compete with Adidas when Tate is the cue. Novig is neither crowded nor familiar, so the backward link becomes enormous. Their Proposition 2 adds the rival channel: a cue that mostly retrieves the <i>category</i> raises demand for the rival the consumer already uses, more so for habitual users. Brand-specific cues avoid this.</p>
<h3>2.2 The fan effect: one cue, many associates</h3>
<p>Memory research finds that the more facts are attached to a concept, the more weakly each one is retrieved from it (Anderson 1974; Anderson & Reder 1999). In ACT-R the strength from cue <i>j</i> to item <i>i</i> is S<sub>ji</sub> = S − ln(fan<sub>j</sub>). In the rational-analysis version it is the log of P(i | j)/P(i). Anderson & Schooler (1991) estimated these quantities from New York Times headlines, which is what we do with GDELT and Common Crawl. Both versions are directional by construction. A brand with eleven ambassadors has a large fan, so each ambassador is weakly retrieved from it. A celebrity with one sportswear deal has a small fan in that category.</p>
<h3>2.3 Cue competition in learning: overshadowing</h3>
<p>When two cues are paired with an outcome, the more salient one takes most of the learned association: overshadowing and blocking in Rescorla–Wagner learning (Kamin 1969; Rescorla & Wagner 1972). In consumer learning, brand names can block learning of attribute–quality links (van Osselaer & Alba 2000; van Osselaer & Janiszewski 2001). Pairing an unknown brand with a superstar therefore makes the brand memorable, but the superstar overshadows what the brand <i>does</i>. Advertising research calls the endorser version the <b>vampire effect</b>: celebrities can reduce recall of the brand they endorse (Evans 1988; Erfgen, Zenker & Sattler 2015).</p>
<h3>2.4 Familiar brands resist interference; endorsers can be diluted</h3>
<p>Ads for familiar brands are less vulnerable to competitive interference than ads for unfamiliar ones (Burke & Srull 1988; Kent & Allen 1994). An endorser with many deals is a weaker cue for each (Tripp, Jensen & Carlson 1994). Meaning transfer runs from the celebrity to the product (McCracken 1989). Similarity judgments are themselves asymmetric, with the less prominent object judged more like the prominent one (Tversky 1977). In brand-equity terms, Keller (1993), these are directed links in an associative network.</p>
<div class="note"><strong>Where we add</strong>Ads as Cues treats similarity as symmetric and measures it from ad text. Celebrity links are directional, and their strengths can be measured from public memory, from both sides, over time. The two cases are the extremes of that variation.</div>

<h2 id="cases">3. The two cases in data</h2>
{fig('regimes', 'Each axis is a measured share. Blue and red: GDELT English news, from campaign day to Nov 8. Grey: other ambassador pairs in the Common Crawl News sample. Above the dashed line, the brand is a bigger part of the celebrity than the reverse.')}
<table><tr><th>measure</th><th class=num>Adidas's share of Tate</th><th class=num>Tate's share of Adidas</th><th class=num>Novig's share of Sweeney</th><th class=num>Sweeney's share of Novig</th></tr>
<tr><td>News articles (GDELT), before the campaign</td>{ev_row('tate_adidas_2026', 'pre')}{ev_row('sweeney_novig', 'pre')}</tr>
<tr><td>News articles (GDELT), from the campaign to Nov 8</td>{ev_row('tate_adidas_2026', 'post')}{ev_row('sweeney_novig', 'post')}</tr>
<tr><td>Google related searches (US), after the campaign</td>{rel_row('tate_adidas_2026', 'post', 'tate_mcrae', 'adidas')}{rel_row('sweeney_novig', 'post', 'sydney_sweeney', 'novig')}</tr>
<tr><td>Wikipedia: share of clicks leaving the page that go to the partner (months when both pages exist)</td><td class=num>{wiki_share('tate_mcrae', 'Adidas')}</td><td class=num>{wiki_share('adidas', 'Tate_McRae')}</td><td class=num>{wiki_share('sydney_sweeney', 'Novig')}</td><td class=num>{wiki_share('novig', 'Sydney_Sweeney')}</td></tr>
<tr><td>Embedding moved toward partner (Δ cosine vs placebos, days 0–30)</td>{traj_row('tate_adidas_2026')}{traj_row('sweeney_novig')}</tr></table>
<p class="meta">Campaign dates: Adidas Originals Sport with Tate McRae, July 22, 2026 (Tate has worked with Adidas since its Z.N.E. campaign of August 29, 2024); Novig's “Just Sports” campaign, September 9, 2026. Embedding brackets are 90% bootstrap intervals; “masked” replaces every name with [NAME].</p>
{fig('madeof', 'Top ten next pages for readers leaving each article, pooled over July–October 2026. Adidas is made of its founders and its rivals: 19% of readers go on to Nike or Puma, and none of its ambassadors is in the top ten. Novig is made of Sweeney, the athletes who criticized the ad (42% combined), “Shock advertising,” and only then the category.')}
<h3>Tate McRae × Adidas</h3>
<p>The July 22 campaign barely registers in public memory. GDELT finds 2 English articles naming both, against 1,126 about Tate and 1,660 about Adidas after the campaign. Tate's Wikipedia readers go to The Kid LAROI, Cole Sillinger and her albums; Adidas's go to Adolf Dassler, Nike and Puma. A deal of this kind gives Adidas one more forward cue among many, which is the fan-effect prediction for a brand with many ambassadors.</p>
<div class="note"><strong>Clearer forward-regime examples in our data</strong>Light Common Crawl News sample: Nike is named in 14% of articles about A'ja Wilson, and she is named in none about Nike. Dior is in 9% of Anya Taylor-Joy's articles; she is in none of Dior's. In Qwen free association, LeBron James brings up Nike in 57% of samples and Kendall Jenner brings up Calvin Klein in 53%, while neither brand ever brings up the person. Any of these would make a stronger forward case alongside Sweeney × Novig.</div>
{fig('tate', 'Weekly composition of English news coverage, coverage volumes, and Google Trends interest around the Originals Sport campaign (July 22, 2026). Each spike in the top panel is a single article naming both; there are four such articles from March to November.')}
{tr_table(tr_tate)}
<h3>Sydney Sweeney × Novig</h3>
{fig('nov', 'Weekly composition of English news coverage around the campaign (September 9, 2026).')}
{fig('map_nov', 'Headline-embedding vectors before and after, projected on two principal components; grey are placebo entities. With names kept, Novig leaves the betting cluster and lands next to Sweeney. With names masked, both move toward the ad story.')}
{tr_table(tr_nov)}
<div class="note"><strong>Rival spillover, with a confound</strong>Search for Kalshi, Polymarket and PrizePicks also rose after September 9, as Proposition 2 predicts for an unfamiliar brand's category-heavy ad. But the NFL season opened the next day, so this is not separable from football betting season without a comparison year or region.</div>

<h2 id="predictions">4. Predictions</h2>
<ul class="steps">
<li><b>Implicit-ad value scales with forward strength.</b> When the celebrity is in the news for unrelated reasons (a tour, a film, a breakup), the brand should get a lift proportional to a(c→b). <span class="why">Tate: positive but bounded by her crowded memory (songs, The Kid LAROI, tour). Sweeney: near zero for Novig outside the ad itself.</span></li>
<li><b>Contagion scales with backward strength.</b> Shocks to the celebrity should move the brand in proportion to β(b→c). <span class="why">Sweeney news should move Novig search; Tate news should not move Adidas.</span></li>
<li><b>Fan effect on the brand side.</b> Each additional ambassador should be a smaller share of the brand's memory, while each still adds a forward channel. <span class="why">Big brands buy a portfolio of forward cues; they do not let any one person redefine them.</span></li>
<li><b>Overshadowing of the category for young brands.</b> With high β, the link from the category to the brand (“sports prediction market” → Novig) should grow more slowly than attention to the brand. <span class="why">That category → brand link is the cue that matters when a bettor decides where to bet.</span></li>
<li><b>Rival spillover depends on familiarity and specificity.</b> Category-heavy ads for unfamiliar brands help familiar rivals among habitual users (Ads as Cues, Prop. 2). A celebrity with strong forward strength to one brand is a brand-specific cue, which limits that spillover.</li></ul>

<h2 id="tests">5. Tests we can run with public data</h2>
<table><tr><th>prediction</th><th>test</th><th>data</th></tr>
<tr><td>forward → implicit ads</td><td>brand search and stock response on days when the celebrity trends for non-brand reasons, by measured a(c→b)</td><td>Trends daily, GDELT, Wikipedia pageviews; archived product pages</td></tr>
<tr><td>backward → contagion</td><td>co-movement of brand attention with celebrity news shocks, by β(b→c)</td><td>GDELT daily counts, Trends, Wikipedia</td></tr>
<tr><td>fan effect</td><td>β per ambassador against the number and size of a brand's ambassadors, across hub brands</td><td>Common Crawl News, Wikipedia clickstream</td></tr>
<tr><td>overshadowing</td><td>month-by-month share of the brand's memory that is the category vs the celebrity (Novig: “prediction market” vs Sweeney)</td><td>clickstream outflows, Trends related queries, news text</td></tr>
<tr><td>rival spillover</td><td>rival search around campaigns of unfamiliar vs familiar brands, with a placebo year or region for sport seasonality</td><td>Trends by metro area and year</td></tr></table>

<h2 id="refs">References</h2>
<p class="meta">Bordalo, Burro, Gennaioli, Nacamulli & Shleifer (2025), “Ads as Cues,” NBER WP 34387. Sarkar (2026), “Economic Representations.” Anderson (1974), Cognitive Psychology. Anderson & Schooler (1991), “Reflections of the environment in memory,” Psychological Science. Anderson & Reder (1999), “The fan effect: new results and new theories,” JEP: General. Kamin (1969). Rescorla & Wagner (1972). van Osselaer & Alba (2000), JCR. van Osselaer & Janiszewski (2001), JCR. Evans (1988), the “vampire effect.” Erfgen, Zenker & Sattler (2015), IJRM. Burke & Srull (1988), JCR. Kent & Allen (1994), Journal of Marketing. Tripp, Jensen & Carlson (1994), JCR. McCracken (1989), JCR. Tversky (1977), Psychological Review. Keller (1993), Journal of Marketing. Nelson, McEvoy & Schreiber (2004), USF free-association norms. Literature references outside Ads as Cues and Sarkar are cited from memory and should be checked before circulation.</p>
</main></div><div class="zoom" id="zoom"><img alt=""></div>
<script>document.querySelectorAll('figure img').forEach(i=>i.addEventListener('click',()=>{{const z=document.getElementById('zoom');z.querySelector('img').src=i.src;z.classList.add('on');}}));document.getElementById('zoom').addEventListener('click',e=>e.currentTarget.classList.remove('on'));</script>
</body></html>"""
    (O / "two_cases.html").write_text(html)
    print("wrote", O / "two_cases.html", f"{(O / 'two_cases.html').stat().st_size / 1e6:.1f} MB", "events", sorted(ev), "traj", sorted(traj))


if __name__ == "__main__":
    main()
