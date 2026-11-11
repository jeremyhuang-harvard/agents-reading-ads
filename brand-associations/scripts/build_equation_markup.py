"""Ads-as-Cues recall rule, marked up with where our measures enter (output/presentation/equation_markup.html).

Reads derived data (clickstream composition, Trends related queries, GDELT period counts) and, if present, the GDELT
topic mix for Sydney Sweeney's coverage (~/.hermes/cache/scratch/sweeney_gdelt_mix.json, copied into data/derived/assoc).
Run: uv run --extra assoc python scripts/build_equation_markup.py
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "derived" / "assoc"
OUT = ROOT / "output" / "presentation" / "equation_markup.html"
MIX_SRC = Path.home() / ".hermes/cache/scratch/sweeney_gdelt_mix.json"
MIX = D / "sweeney_gdelt_topic_mix.json"


def outflow(ent, months=None):
    agg, tot = Counter(), {}
    for r in csv.DictReader((D / "clickstream_outflow_monthly.csv").open()):
        if r["entity"] == ent and (months is None or r["month"] in months):
            agg[r["next_page"]] += int(r["n"])
            tot[r["month"]] = int(r["n"]) / float(r["share_of_outflow"])
    T = sum(tot.values())
    return {p: n / T for p, n in agg.items()}, T


def related(cue, period):
    for r in csv.DictReader((D / "event_sweeney_novig_related.csv").open()):
        if r["cue"] == cue and r["period"] == period:
            return [m.group(1) for m in (re.match(r"(.*) \(\d+\)$", x.strip()) for x in r["top_related"].split(" | ")) if m], \
                float(r["share_of_related_weight"])
    return [], 0.0


def pct(v, d=0):
    return f"{100 * v:.{d}f}%"


def main():
    if MIX_SRC.exists():
        shutil.copy(MIX_SRC, MIX)
    mix = json.loads(MIX.read_text()) if MIX.exists() else {}
    sw, sw_T = outflow("sydney_sweeney")
    sw_oct, _ = outflow("sydney_sweeney", {"2026-10"})
    nv, nv_T = outflow("novig")
    rel_sw_pre, _ = related("sydney_sweeney", "pre")
    rel_nv_pre, _ = related("novig", "pre")
    rel_sw_post, sw_post_share = related("sydney_sweeney", "post")
    rel_nv_post, nv_post_share = related("novig", "post")
    per = {r["key"]: r for r in csv.DictReader((D / "event_sweeney_novig_periods.csv").open())}
    weekly = list(csv.DictReader((D / "event_sweeney_novig_weekly.csv").open()))
    pre_w = [r for r in weekly if (date.fromisoformat(r["key"]) - date(2026, 9, 9)).days <= -7]
    novig_pw = sum(int(r["n_brand"] or 0) for r in pre_w) / len(pre_w)
    kalshi_pw = sum(int(r["n_kalshi"] or 0) for r in pre_w) / len(pre_w)
    critics = sum(nv.get(p, 0) for p in ("Gracie_Kramer", "Ariarne_Titmus", "Amy_Hunt"))

    mix_line = ""
    if mix.get("all") and "american_eagle" in mix:
        tot = sum(mix["all"])

        def m(k):
            return sum(mix[k]) / tot

        mix_line = (f"In English news over the past year (GDELT, {tot:,} articles naming her), {pct(m('american_eagle'))} also name American Eagle "
                    f"(Euphoria {pct(m('euphoria'))}, The Housemaid {pct(m('housemaid'))}). ")
        if "politics" in mix:
            mix_line += f"{pct(m('politics'))} mention Republicans, Trump, MAGA, conservatives or “woke”."
        else:
            mix_line += ("Politics: in a smaller full-text sample (28 articles about her), 21% mention Republicans, Trump, MAGA, "
                         "conservatives or “woke”; the GDELT count was rate-limited.")
    if not mix_line:
        mix_line = ("In our Common Crawl News sample of articles about her (28 articles, Jul 2025–Oct 2026), 18% name American Eagle and 21% "
                    "mention Republicans, Trump, MAGA, conservatives or “woke”. Small sample.")

    css = """
:root{--ink:#111827;--muted:#6B7280;--rule:#E5E7EB;--num:#1D4ED8;--den:#B91C1C;--fog:#6B7280;--ours:#7C3AED}
*{box-sizing:border-box} body{margin:0;background:#F3F4F6;color:var(--ink);font:17px/1.55 -apple-system,"Helvetica Neue",Helvetica,Arial,sans-serif}
.deck{max-width:1060px;margin:0 auto;padding:28px 18px 60px}
.slide{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:32px 42px 26px;margin:0 0 26px;position:relative}
.part{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px}
h1{font-size:31px;line-height:1.15;margin:4px 0 12px} h2{font-size:25px;line-height:1.2;margin:0 0 12px}
.eq{font-family:Georgia,"Times New Roman",serif;font-size:27px;display:flex;align-items:center;justify-content:center;gap:14px;margin:20px 0 8px;flex-wrap:wrap}
.frac{display:inline-flex;flex-direction:column;align-items:center}
.frac>.top{padding:4px 10px 8px;border-bottom:2px solid var(--ink)} .frac>.bot{padding:8px 10px 4px}
.t{border-radius:6px;padding:2px 6px;position:relative;white-space:nowrap}
.t sup.c{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:12px;font-weight:700;color:#fff;border-radius:50%;padding:1px 6px;margin-left:3px;vertical-align:super}
.n{background:#DBEAFE} .n sup.c{background:var(--num)}
.d{background:#FEE2E2} .d sup.c{background:var(--den)}
.f{background:#F3F4F6} .f sup.c{background:var(--fog)}
.o{background:#EDE9FE;outline:2px dashed var(--ours)} .o sup.c{background:var(--ours)}
.plus{color:#374151;margin:0 3px}
.brace{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:12.5px;color:var(--muted);text-align:center;margin-top:-2px}
.legend{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px;margin-top:16px}
.legend div{font-size:14.5px;border-left:4px solid;padding:6px 10px;background:#FAFAFA}
.legend b{display:block;font-size:15px}
.ln{border-color:var(--num)} .ld{border-color:var(--den)} .lf{border-color:var(--fog)} .lo{border-color:var(--ours)}
.quote{font-family:Georgia,serif;font-size:15.5px;color:#374151;border-left:3px solid var(--rule);padding:4px 12px;margin:10px 0}
.say{margin-top:14px;padding:10px 14px;border-left:3px solid #9CA3AF;background:#F9FAFB;font-size:14.5px;color:#374151}
.small{font-size:13.5px;color:var(--muted)}
.lab{font-size:11px;font-weight:700;padding:1px 6px;border-radius:8px;margin-left:4px}
.obs{background:#DCFCE7;color:#166534}.rpt{background:#FEF3C7;color:#92400E}.hyp{background:#EDE9FE;color:#5B21B6}
.map{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}.map div{border:1px solid var(--rule);border-radius:8px;padding:10px 12px;font-size:14.5px}
@media(max-width:760px){.legend,.map{grid-template-columns:1fr}.eq{font-size:21px}}
"""
    OBS, RPT, HYP = '<span class="lab obs">observed</span>', '<span class="lab rpt">reported</span>', '<span class="lab hyp">our proposal</span>'
    sb, hm, eu = sw.get("Scooter_Braun", 0), sw.get("The_Housemaid_(2025_film)", 0), sw.get("Euphoria_(American_TV_series)", 0)
    pm = nv.get("Prediction_market", 0)
    shock = nv.get("Shock_advertising", 0)
    p_post = per["post"]

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Where our findings enter the recall rule</title><style>{css}</style></head><body><div class="deck">

<section class="slide"><div class="part">Ads as Cues · the recall rule</div>
<h1>Recall is a share: the target against everything else the cue brings to mind</h1>
<div class="eq">r<sub>x</sub>(c, <b>f</b>) =
<span class="frac"><span class="top"><span class="t n">S(c, x) · f<sub>x</sub><sup class="c">A</sup></span></span>
<span class="bot"><span class="t d">Σ<sub>x′ ∈ X</sub> S(c, x′) · f<sub>x′</sub><sup class="c">B</sup></span></span></span>
<span style="font-size:16px;color:#6B7280">&nbsp;(1)</span></div>
<div class="legend">
<div class="ln"><b>A · numerator</b>similarity of the cue to the target × how often the target was experienced. “The numerator captures associativity and frequency in recall.”</div>
<div class="ld"><b>B · denominator = interference</b>the same product summed over every memory, including the “fog” of neutral, non-branded experiences f<sub>n</sub>. “Experiences compete in recall… Interference captures distraction.”</div></div>
<p class="small" style="margin-top:14px">Then recall over all cues a person sees is r<sub>g</sub>(<b>e</b>, <b>f</b>) = Σ<sub>c</sub> r<sub>g</sub>(c, <b>f</b>) · η<sub>c</sub> (2), and demand is d<sub>g</sub> = q<sub>g</sub> · r<sub>g</sub> − θ · p<sub>g</sub> (3): goods that are not recalled lose the pleasure q<sub>g</sub> from the purchase decision. Bordalo, Burro, Gennaioli, Nacamulli &amp; Shleifer (2025), NBER WP 34387, eqs. (1)–(3).</p>
<div class="say"><b>The bridge to our data:</b> an entity's association profile, the share of A's public memory that involves B, is an empirical stand-in for r<sub>B</sub>(c = A) in a representative population. Forward strength is r<sub>brand</sub>(cue = celebrity); backward strength is r<sub>celebrity</sub>(cue = brand). Both are this same fraction, read in opposite directions.</div>
</section>

<section class="slide"><div class="part">Forward · the cue is a Sweeney appearance</div>
<h2>Will seeing Sweeney bring Novig to mind?</h2>
<div class="eq">r<sub>Novig</sub>(Sweeney) =
<span class="frac"><span class="top"><span class="t n">S(Sweeney, Novig)<sup class="c">1</sup></span> · <span class="t n">f<sub>Novig</sub><sup class="c">2</sup></span></span>
<span class="bot"><span class="t n">S·f<sub>Novig</sub></span><span class="plus">+</span><span class="t o">Σ<sub>her memories</sub> S·f<sup class="c">3</sup></span><span class="plus">+</span><span class="t d">Σ<sub>rivals</sub> S·f<sup class="c">4</sup></span><span class="plus">+</span><span class="t f">S·f<sub>n</sub><sup class="c">5</sup></span></span></span></div>
<div class="legend">
<div class="ln"><b>1 · association, built by the campaign</b>Novig was in none of her coverage or searches before Sept 9. After: {pct(float(p_post['fwd_brand_in_celebrity']))} of her news articles and {pct(sw_post_share)} of her related-search weight; {pct(sw_oct.get('Novig', 0), 2)} of clicks leaving her Wikipedia page (October). {OBS}</div>
<div class="ln"><b>2 · frequency of the target: tiny</b>About {novig_pw:.0f} English articles a week before the campaign, vs {kalshi_pw:.0f} for Kalshi. Its top searches were “novig promo” and “what is novig”. {OBS}</div>
<div class="lo"><b>3 · her own memory, now inside the denominator</b>Readers leaving her page go to Scooter Braun ({pct(sb)}), The Housemaid ({pct(hm)}), Euphoria ({pct(eu)}). Her past controversies are part of the same memory: the American Eagle “great jeans” ad (July 2025) and the reported Republican registration that Trump then praised (August 2025). {RPT} {mix_line}</div>
<div class="ld"><b>4 · category rivals</b>A betting ad also brings Kalshi, DraftKings and FanDuel to mind. Rival search rose after Sept 9, but so did football betting season (the NFL opened Sept 10). {OBS}</div>
<div class="lf" style="grid-column:1/-1"><b>5 · the fog</b>Everything unrelated to brands. Same as in the paper.</div></div>
<div class="say"><b>What changes relative to a product ad:</b> a celebrity is a cue with a heavy, charged denominator. Pairing can raise term 1, but Novig still competes with everything she is, including politically loaded memories. That caps the forward link (it is why Tate is ≈0% of the way to Adidas) and decides what else comes along with the brand.</div>
</section>

<section class="slide"><div class="part">Backward · the cue is Novig</div>
<h2>When a bettor sees “Novig”, what comes to mind? Crowding out</h2>
<div class="eq">r<sub>betting</sub>(Novig) =
<span class="frac"><span class="top"><span class="t n">S(Novig, sports betting) · f<sub>betting</sub><sup class="c">1</sup></span></span>
<span class="bot"><span class="t n">S·f<sub>betting</sub></span><span class="plus">+</span><span class="t o">S(Novig, Sweeney) · f<sub>Sweeney</sub><sup class="c">2</sup></span><span class="plus">+</span><span class="t o">Σ<sub>controversy</sub> S·f<sup class="c">3</sup></span><span class="plus">+</span><span class="t f">S·f<sub>n</sub></span></span></span></div>
<div class="legend">
<div class="ln"><b>1 · what the brand is for</b>The category link a bettor needs (“where do I bet on football?” → Novig). Before the campaign, Novig's top searches were “novig betting”, “novig sportsbook”, Kalshi, Polymarket. {OBS}</div>
<div class="lo"><b>2 · the celebrity enters with her full frequency</b>f<sub>Sweeney</sub> is enormous relative to anything Novig-specific, so even modest similarity makes her term dominate. Sweeney is {pct(nv_post_share)} of Novig's related-search weight and {pct(float(p_post['bwd_celebrity_in_brand']))} of its news; {pct(nv.get('Sydney_Sweeney', 0))} of clicks leaving its Wikipedia page go to her, versus {pct(pm)} to “Prediction market”. {OBS}</div>
<div class="lo"><b>3 · the controversy comes with her</b>{pct(critics)} of Novig's clicks go to the three athletes who criticized the ad, {pct(shock)} to “Shock advertising”. Anything retrieved through her (the jeans ad, her political associations) is reachable from the Novig cue as well. {HYP}</div>
<div class="lf"><b>Net effect</b>The numerator need not fall for the share to fall: the category link is diluted because the denominator has grown. That is crowding out in the model's own terms. {HYP}</div></div>
<div class="say"><b>Caveat to say out loud:</b> our numbers are shares, so we see dilution, not necessarily a fall in the category link's absolute strength. Novig's Wikipedia page did not exist before October 16, so there is no before-and-after click comparison.</div>
</section>

<section class="slide"><div class="part">What is the paper's, what is ours</div>
<h2>Three additions to the recall rule</h2>
<div class="map">
<div><b>In the paper</b><br>X = consumption experiences of goods, plus neutral events n. Similarity S is symmetric. Interference = other goods and the fog.</div>
<div><b>Our proposal</b> {HYP}<br>A celebrity cue makes a structured block of non-consumption memories similar: her roles, partners, ads and controversies. These are part of X and enter the denominator.</div>
<div><b>Direction</b><br>Because f differs enormously between a star and a small brand, the same S gives r<sub>brand</sub>(celebrity) ≪ r<sub>celebrity</sub>(brand) for small brands. Across 53 ambassador pairs, the bigger memory absorbs the link (r = −0.55; on your pre-specified list, −0.48).</div>
<div><b>Valence</b> {HYP}<br>Recall in the paper retrieves the pleasure q<sub>g</sub>. If a brand cue retrieves a controversy, that retrieved content may lower simulated utility for some consumers and raise it for others (the AE stock rose after Trump's praise). Testable with search and sales by region or political lean.</div></div>
<p class="small" style="margin-top:14px">Labels: <span class="lab obs">observed</span> computed by us from public data; <span class="lab rpt">reported</span> press accounts (BBC, Guardian, USA Today, Aug 2025); <span class="lab hyp">our proposal</span> theoretical extension, not yet tested.</p>
</section>
</div></body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print("wrote", OUT, "gdelt mix:", bool(mix), mix_line[:120])


if __name__ == "__main__":
    main()
