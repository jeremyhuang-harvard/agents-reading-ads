"""Brief: multi-source entity vectors and directed association profiles (output/assoc/profile_brief.html).

Reads data/derived/assoc/profile_pairs.csv, profile_shares.csv, profile_vectors_<backend>.npz.
Run: uv run --extra assoc python scripts/build_profile_brief.py
Lookup any pair: uv run --extra assoc python scripts/build_profile_brief.py --lookup "Tate McRae" "Adidas"
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assoc_brief as B  # noqa: E402

from implicit_ads.assoc import config  # noqa: E402
from implicit_ads.assoc.profile import MIN_UNITS, SOURCES  # noqa: E402

D, O = B.D, B.O
FRAME = config.load()
NAME = {e.id: e.name for e in FRAME.entities}
KIND = {e.id: e.kind for e in FRAME.entities}
BYNAME = {e.name.casefold(): e.id for e in FRAME.entities}
SHORT = {"wiki_text": "Wikipedia text", "news": "News articles", "wiki_clicks": "Wikipedia clicks", "search": "Google searches",
         "llm": "LLM free association"}
VEC = D / "profile_vectors_st-baai-bge-base-en-v1-5.npz"
CASES = [("tate_mcrae", "adidas"), ("sydney_sweeney", "novig"), ("lebron_james", "nike"),
         ("george_clooney", "nespresso"), ("johnny_depp", "dior"), ("johnny_depp", "sauvage"),
         ("shaquille_oneal", "icy_hot"), ("shaquille_oneal", "the_general"), ("roger_federer", "rolex")]


def load_pairs():
    P = {}
    for r in csv.DictReader((D / "profile_pairs.csv").open()):
        P[(r["a"], r["b"])] = r
    return P


def directed(P, a, b, src="combined"):
    """Strength a -> b (share of a's representation that is b) for one source or combined. None if a lacks data."""
    if (a, b) in P:
        v = P[(a, b)][f"{src}_a_to_b"]
    else:
        v = P[(b, a)][f"{src}_b_to_a"]
    return float(v) if v != "" else None


def asym(P, a, b):
    """Mean log10 ratio (a -> b over b -> a) across sources with both directions."""
    if (a, b) in P:
        v = P[(a, b)]["asym_log10_a_over_b"]
        return float(v) if v else None
    v = P[(b, a)]["asym_log10_a_over_b"]
    return -float(v) if v else None


def vectors():
    z = np.load(VEC, allow_pickle=True)
    ids = list(z["ids"])
    return ids, z


def centered(M):
    M = M - np.nanmean(M, axis=0, keepdims=True)
    return M / np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-12)


def lookup(a_name, b_name):
    P = load_pairs()
    a, b = BYNAME[a_name.casefold()], BYNAME[b_name.casefold()]
    ids, z = vectors()
    C = centered(z["combined_named"])
    Cm = centered(z["combined_masked"])
    i, j = ids.index(a), ids.index(b)
    print(f"{NAME[a]} → {NAME[b]} = share of {NAME[a]}'s representation that is {NAME[b]}; reverse likewise")
    for s in SOURCES:
        x, y = directed(P, a, b, s), directed(P, b, a, s)
        f = lambda v: "   n/a" if v is None else f"{100 * v:6.2f}%"  # noqa: E731
        print(f"  {SHORT[s]:22s} {f(x)} → | ← {f(y)}")
    print(f"  {'strength index (0-1)':22s} {directed(P, a, b) or 0:7.2f} → | ← {directed(P, b, a) or 0:.2f}")
    asy = asym(P, a, b)
    print(f"  asymmetry: {NAME[a]} → {NAME[b]} is {10 ** asy:.3g}x the reverse (mean over sources)" if asy is not None else "  asymmetry: n/a")
    print(f"  similarity (cosine of centered vectors): names kept {C[i] @ C[j]:+.3f}, names masked {Cm[i] @ Cm[j]:+.3f}")


def fig_cases(P):
    fig, axes = plt.subplots(3, 3, figsize=(15, 11), sharex=True)
    for ax, (c, b) in zip(axes.flat, CASES):
        ys = np.arange(len(SOURCES))
        fw = [directed(P, c, b, s) for s in SOURCES]
        bw = [directed(P, b, c, s) for s in SOURCES]
        floor = 1e-4
        for k, (x, y) in enumerate(zip(fw, bw)):
            if x is not None:
                ax.barh(k + 0.2, max(x, floor), height=0.38, color="#1D4ED8")
            if y is not None:
                ax.barh(k - 0.2, max(y, floor), height=0.38, color="#B91C1C")
            for v, dy, col in ((x, 0.2, "#1D4ED8"), (y, -0.2, "#B91C1C")):
                lab = "no data" if v is None else ("0" if v == 0 else (f"{100 * v:.2g}%"))
                ax.text(max(v or floor, floor) * 1.25, k + dy, lab, va="center", fontsize=7.5, color=col)
        ax.set_yticks(ys, [SHORT[s] for s in SOURCES], fontsize=8.5)
        ax.invert_yaxis()
        ax.set_xscale("log")
        ax.set_xlim(floor, 3)
        a_ = asym(P, c, b)
        tag = ("no link in any source" if not any((v or 0) > 0 for v in fw + bw) else
               (f"forward ×{10 ** a_:.2g}" if a_ > 0.05 else f"backward ×{10 ** -a_:.2g}" if a_ < -0.05 else "balanced"))
        ax.set_title(f"{NAME[c]} × {NAME[b]}: {tag}", loc="left", fontsize=10.5, fontweight="bold")
    axes.flat[0].barh([], [], color="#1D4ED8", label="brand's share of the celebrity  (celebrity → brand)")
    axes.flat[0].barh([], [], color="#B91C1C", label="celebrity's share of the brand  (brand → celebrity)")
    fig.legend(loc="upper center", ncol=2, fontsize=9.5, frameon=False, bbox_to_anchor=(0.5, 1.0))
    for ax in axes[-1]:
        ax.set_xlabel("share (log scale; 0 drawn at the floor)", fontsize=8.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(O / "profile_cases.png", dpi=150)
    plt.close(fig)


def fig_map(P, ids, z):
    C = centered(z["combined_named"])
    ok = ~np.isnan(C).any(1)
    X = C[ok]
    U, S, Vt = np.linalg.svd(X - X.mean(0), full_matrices=False)
    xy = np.full((len(ids), 2), np.nan)
    xy[ok] = U[:, :2] * S[:2]
    fig, ax = plt.subplots(figsize=(12.5, 9.5))
    edges = []
    for (a, b), r in P.items():
        for s_, t_, key in ((a, b, "combined_a_to_b"), (b, a, "combined_b_to_a")):
            if r[key] and float(r[key]) >= 0.6:
                edges.append((s_, t_, float(r[key])))
    for s_, t_, v in sorted(edges, key=lambda e: e[2]):
        i, j = ids.index(s_), ids.index(t_)
        if np.isnan(xy[i]).any() or np.isnan(xy[j]).any():
            continue
        ax.annotate("", xy=xy[j], xytext=xy[i], arrowprops=dict(arrowstyle="-|>", color="#6B7280", lw=0.4 + 3 * (v - 0.55) / 0.45,
                    alpha=0.6, shrinkA=6, shrinkB=6, connectionstyle="arc3,rad=0.12", mutation_scale=10 + 8 * v))
    for k, e in enumerate(ids):
        if np.isnan(xy[k]).any():
            continue
        col = "#1D4ED8" if KIND[e] == "celebrity" else "#B91C1C"
        ax.scatter(*xy[k], s=30, color=col, zorder=3)
        ax.annotate(NAME[e], xy[k], fontsize=7.5, color=col, xytext=(3, 3), textcoords="offset points", zorder=4)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Position = multi-source vector (similarity: what kind of thing it is). Arrow A → B = B is a strong component of A\n"
                 "(strength index ≥ 0.6: on average B ranks in the top 40% of observed associations across sources). Blue = celebrities, red = brands.",
                 loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(O / "profile_map.png", dpi=150)
    plt.close(fig)


def fig_sim_vs_assoc(P, ids, z):
    C = centered(z["combined_masked"])
    pairs = {(p.celebrity, p.brand) for p in FRAME.pairs}
    xs, ys, cols, labs = [], [], [], []
    for (a, b), r in P.items():
        if {KIND[a], KIND[b]} != {"celebrity", "brand"}:
            continue
        i, j = ids.index(a), ids.index(b)
        if np.isnan(C[i]).any() or np.isnan(C[j]).any():
            continue
        f, g = directed(P, a, b), directed(P, b, a)
        if f is None or g is None:
            continue
        c, br = (a, b) if KIND[a] == "celebrity" else (b, a)
        xs.append(C[i] @ C[j])
        ys.append(max(f, g))
        cols.append("#B91C1C" if (c, br) in pairs else "#D1D5DB")
        labs.append((c, br) if (c, br) in pairs and max(f, g) > 0.6 else None)
    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    order = np.argsort([c == "#B91C1C" for c in cols])
    for k in order:
        ax.scatter(xs[k], ys[k], s=14 if cols[k] != "#B91C1C" else 30, color=cols[k], zorder=2 + (cols[k] == "#B91C1C"))
        if labs[k]:
            ax.annotate(f"{NAME[labs[k][0]]}–{NAME[labs[k][1]]}", (xs[k], ys[k]), fontsize=7, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel("similarity: cosine of multi-source vectors (names masked)")
    ax.set_ylabel("association: strength index, stronger direction (0–1)")
    ax.set_title("Similarity and association are different quantities.\nRed = actual ambassador pairs; grey = all other celebrity–brand combinations",
                 loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(O / "profile_sim_vs_assoc.png", dpi=150)
    plt.close(fig)
    r = np.corrcoef(xs, ys)[0, 1]
    return r


def fig_size(P):
    """Direction of each ambassador pair vs the relative size of the two public memories (Wikipedia pageviews)."""
    pv = {r["entity"]: int(r["pageviews"] or 0) for r in csv.DictReader((D / "wiki_entities.csv").open())}
    pts = []
    for p in FRAME.pairs:
        c, b = p.celebrity, p.brand
        a_ = asym(P, c, b)
        row = P.get((c, b)) or P.get((b, c))
        if a_ is None or not pv.get(c) or not pv.get(b) or int(row["sources_a_gt_b"]) + int(row["sources_b_gt_a"]) == 0:
            continue
        pts.append((np.log10(pv[c] / pv[b]), a_, c, b))
    x = np.array([q[0] for q in pts])
    y = np.array([q[1] for q in pts])
    r = float(np.corrcoef(x, y)[0, 1])
    rng = np.random.default_rng(20261110)
    perm = np.mean([np.corrcoef(x, rng.permutation(y))[0, 1] <= r for _ in range(10000)])
    slope, icpt = np.polyfit(x, y, 1)
    fig, ax = plt.subplots(figsize=(9, 6.4))
    ax.axhline(0, color="black", lw=0.7)
    ax.axvline(0, color="#9CA3AF", lw=0.6, ls=":")
    ax.scatter(x, y, s=34, color=["#1D4ED8" if v > 0 else "#B91C1C" for v in y], zorder=3)
    xx = np.linspace(x.min(), x.max(), 10)
    ax.plot(xx, icpt + slope * xx, color="#374151", lw=1.2, ls="--")
    for xi, yi, c, b in pts:
        if abs(yi) > 0.6 or abs(xi) > 1.8 or (c, b) in (("tate_mcrae", "adidas"), ("lebron_james", "nike"), ("george_clooney", "nespresso"),
                                                     ("shaquille_oneal", "icy_hot"), ("jennifer_aniston", "smartwater")):
            ax.annotate(f"{NAME[c]}–{NAME[b]}", (xi, yi), fontsize=7.5, xytext=(4, 3), textcoords="offset points")
    ax.set_xlabel("log10( celebrity's Wikipedia pageviews / brand's pageviews ),  Nov 2025–Oct 2026")
    ax.set_ylabel("asymmetry: log10( brand-in-celebrity / celebrity-in-brand )\nabove 0 = forward, below 0 = backward")
    ax.set_title(f"The bigger public memory absorbs the link: r = {r:.2f}, slope {slope:.2f}, permutation p = {perm:.4f} (n = {len(pts)} ambassador pairs)",
                 loc="left", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(O / "profile_size.png", dpi=150)
    plt.close(fig)
    return r, slope, float(perm), len(pts)


def coverage():
    out = defaultdict(dict)
    for r in csv.DictReader((D / "profile_shares.csv").open()):
        out[r["source"]][r["from"]] = int(float(r["units_from"]))
    return out


def main():
    P = load_pairs()
    ids, z = vectors()
    fig_cases(P)
    fig_map(P, ids, z)
    r = fig_sim_vs_assoc(P, ids, z)
    r_size, slope_size, p_size, n_size = fig_size(P)
    asy_all = [asym(P, p.celebrity, p.brand) for p in FRAME.pairs]
    asy_all = [a_ for a_ in asy_all if a_ is not None]
    n_fwd, n_bwd = sum(a_ > 0.05 for a_ in asy_all), sum(a_ < -0.05 for a_ in asy_all)
    n_flat = len(asy_all) - n_fwd - n_bwd
    cov = coverage()
    C = centered(z["combined_masked"])

    def nn(e, k=5):
        i = ids.index(e)
        sims = [(C[i] @ C[j], ids[j]) for j in range(len(ids)) if j != i and not np.isnan(C[j]).any()]
        return ", ".join(NAME[x] for _, x in sorted(sims, reverse=True)[:k])

    def top_assoc(e, k=5):
        vals = []
        for o in ids:
            if o != e:
                v = directed(P, e, o)
                if v:
                    vals.append((v, o))
        return ", ".join(f"{NAME[o]} ({v:.2f})" for v, o in sorted(vals, reverse=True)[:k]) or "none above zero"

    def pct(v):
        return "n/a" if v is None else f"{100 * v:.2f}%"

    case_rows = ""
    for c, b in [(p.celebrity, p.brand) for p in FRAME.pairs]:
        f, g = directed(P, c, b), directed(P, b, c)
        both = [s for s in SOURCES if directed(P, c, b, s) is not None and directed(P, b, c, s) is not None]
        gt = sum(directed(P, c, b, s) > directed(P, b, c, s) for s in both)
        lt = sum(directed(P, c, b, s) < directed(P, b, c, s) for s in both)
        a_ = asym(P, c, b)
        case_rows += (f"<tr><td>{NAME[c]} × {NAME[b]}</td><td class=num>{f or 0:.2f}</td><td class=num>{g or 0:.2f}</td>"
                      f"<td class=num>{'—' if a_ is None or (gt + lt) == 0 else (f'×{10 ** a_:.2g} forward' if a_ > 0 else f'×{10 ** -a_:.2g} backward')}</td>"
                      f"<td class=num>{gt} / {lt} / {len(both) - gt - lt}</td></tr>")
    nn_rows = "".join(f"<tr><td>{NAME[e]}</td><td>{nn(e)}</td><td>{top_assoc(e)}</td></tr>" for e in
                      ("tate_mcrae", "adidas", "sydney_sweeney", "novig", "lebron_james", "nike"))
    cov_rows = "".join(f"<tr><td>{SOURCES[s]}</td><td class=num>{sum(v >= MIN_UNITS[s] for v in cov[s].values())} / {len(ids)}</td>"
                       f"<td class=num>{int(np.median([v for v in cov[s].values() if v >= MIN_UNITS[s]])) if cov[s] else 0:,}</td></tr>"
                       for s in SOURCES)
    figs = {k: B.img(O / f) for k, f in [("cases", "profile_cases.png"), ("map", "profile_map.png"), ("sva", "profile_sim_vs_assoc.png"), ("size", "profile_size.png")]}

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Multi-source entity vectors</title><style>{B.CSS}</style></head><body><div class="wrap"><main>
<div class="kicker">Implicit Ads · representations · November 10, 2026</div>
<h1>One vector per celebrity and brand, built from five public sources</h1>
<p class="meta">{len(ids)} entities · Wikipedia text and reader clicks · news full text · Google related searches · local LLM free association · exploratory</p>
<p class="lede">Each entity gets two objects built from the same five sources. A <b>vector</b> places it in a semantic space: what kind of thing it is. An <b>association profile</b> says what it is made of: of everything written, read, searched or recalled about Tate, what share involves Adidas. The first is symmetric. The second is directional, and that is what Ads as Cues needs.</p>
<div class="bottom-line"><h3>Bottom line</h3><ol>
<li><b>Most ambassador links run forward.</b> Of {len(asy_all)} ambassador pairs, {n_fwd} are forward (the brand is a bigger part of the celebrity than the reverse), {n_bwd} backward, and {n_flat} flat, mostly because neither side shows up in the other at all, as with Tate × Adidas.</li>
<li><b>The bigger public memory absorbs the link.</b> Direction tracks relative size: the more Wikipedia views the celebrity has relative to the brand, the more the link runs backward (r = {r_size:.2f}, permutation p = {p_size:.4f}, n = {n_size}). Sweeney × Novig (×14 backward), Federer × On, Elordi × Bottega Veneta and Jung Kook × Calvin Klein are the backward cases; athletes and actresses at Nike and Dior are the forward ones.</li>
<li><b>Similarity and association come apart</b> (correlation {r:.2f} across celebrity–brand combinations). Ambassador pairs are not unusually similar; they stand out on association.</li>
<li><b>Sources can disagree, and that is informative.</b> LeBron × Nike is forward in the LLM (LeBron brings up Nike in 57% of samples) but backward in news, Wikipedia text and clicks, where LeBron is 9% of Nike's coverage. What a model "knows" about a person and what the public reads about a brand differ.</li></ol></div>

<h2>1. Why two objects</h2>
<p>A cosine between two vectors is the same in both directions, so it cannot say that Tate calls up Adidas more than Adidas calls up Tate. It measures resemblance: Tate is close to other pop singers, Adidas to Nike and Puma. Association is a different quantity: P(B | A), the share of A's public memory in which B appears. That is what the memory literature calls forward associative strength, and it is what enters the numerator of the Ads as Cues retrieval rule.</p>
<table><tr><th>source</th><th>A's units</th><th>A → B is the share of A's units that…</th></tr>
<tr><td>Wikipedia text</td><td>sentences of A's article</td><td>name B</td></tr>
<tr><td>News</td><td>Common Crawl News articles about A (title or description)</td><td>name B anywhere in the text</td></tr>
<tr><td>Wikipedia clicks</td><td>clicks leaving A's page, Jul–Oct 2026</td><td>go to B's page</td></tr>
<tr><td>Google searches</td><td>top related queries for A (US, Nov 2025–Oct 2026)</td><td>name B (weighted by Google's index)</td></tr>
<tr><td>LLM</td><td>30 free-association lists from Qwen3-8B</td><td>name B</td></tr></table>
<p>The vector is the weighted mean embedding (bge-base) of the same units, computed per source, normalized and averaged across sources. A masked version replaces every frame name with [NAME], so similarity cannot come from the names themselves.</p>

<h2>2. Direction follows size</h2>
<figure><img src="{figs['size']}" alt=""><figcaption>Each point is an ambassador pair with a link in at least one source. In co-occurrence sources part of this is arithmetic: the same joint mentions are divided by each side's total. That is the Ads as Cues mechanism (a crowded cue spreads retrieval over more associates), but it means the informative parts are the size of the link and the pairs off the line.</figcaption></figure>
<h2>3. The map</h2>
<figure><img src="{figs['map']}" alt=""><figcaption>Positions are the first two principal components of the multi-source vectors. Arrows run from A to B when B is a strong component of A (strength index ≥ 0.6). Click to enlarge.</figcaption></figure>
<figure><img src="{figs['sva']}" alt=""><figcaption>Each point is a celebrity–brand combination. Ambassador pairs are not unusually similar; they stand out on association.</figcaption></figure>

<h2>4. Zoom-ins</h2>
<figure><img src="{figs['cases']}" alt=""><figcaption>Blue: the brand's share of the celebrity. Red: the celebrity's share of the brand. Five sources plus the combined mean.</figcaption></figure>
<table><tr><th>pair</th><th class=num>strength: brand in celebrity</th><th class=num>strength: celebrity in brand</th><th class=num>asymmetry</th><th class=num>sources: forward / backward / tied</th></tr>{case_rows}</table>
<p class=meta>Strength is the mean, across sources, of where the share ranks among all non-zero associations observed in that source (0 = absent, 1 = the strongest). Asymmetry is the geometric mean, across sources with both directions, of the ratio of the two shares (each padded by a tenth of the source's median non-zero share).</p>
<h3>Similar to vs made of</h3>
<table><tr><th>entity</th><th>most similar (vector, names masked)</th><th>largest components (combined association)</th></tr>{nn_rows}</table>

<h2>5. Coverage and caveats</h2>
<table><tr><th>source</th><th class=num>entities with enough data</th><th class=num>median units</th></tr>{cov_rows}</table>
<ul>
<li>Raw shares live on different scales (LLM lists around 50%, clicks around 0.1%), so the combined strength uses within-source ranks and the asymmetry uses ratios. Per-source shares are always shown next to them.</li>
<li>The news sample is light (a few thousand articles), so zeros there can mean small samples.</li>
<li>The LLM's knowledge stops in early 2025, so it misses recent deals, including Novig. Its numbers are model_predicted.</li>
<li>TikTok, YouTube and Reddit would add the sources ordinary people engage with most; they need official API access (see the earlier note).</li>
<li>Pairs were hand-picked from recent announcements, not sampled.</li></ul>
</main></div><div class="zoom" id="zoom"><img alt=""></div>
<script>document.querySelectorAll('figure img').forEach(i=>i.addEventListener('click',()=>{{const z=document.getElementById('zoom');z.querySelector('img').src=i.src;z.classList.add('on');}}));document.getElementById('zoom').addEventListener('click',e=>e.currentTarget.classList.remove('on'));</script>
</body></html>"""
    (O / "profile_brief.html").write_text(html)
    print("wrote", O / "profile_brief.html", f"{(O / 'profile_brief.html').stat().st_size / 1e6:.1f} MB; sim-assoc r = {r:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lookup", nargs=2, metavar=("A", "B"))
    a = ap.parse_args()
    if a.lookup:
        lookup(*a.lookup)
    else:
        main()
