"""Rebuild every results table in `results/` from the saved data in this repository.

No API key, no network, standard library only:

    python analysis/make_results.py

Three parts, three groups of tables:

* agent-feeds/        a vision-language model (Qwen3-VL-8B) rates one ad shown inside a feed of
                      other images. Outcome = the model's expected rating (probability-weighted
                      mean of the next-token distribution over "1".."5"). Effects are "same ad,
                      after primes" minus "same ad, after 5 neutral images", computed per ad and
                      then averaged over the ads in a category.
* ad-library/         five French sports-betting firms' Snapchat ads, each unique creative coded
                      by a model against a frozen codebook; firm profiles and cue similarity.
* brand-associations/ directed celebrity -> brand association measures and a look-size study.

Intervals marked * are 90% percentile bootstrap intervals that exclude zero, resampling feeds
within each ad (seeded, so the output is deterministic). Like the original notes, they ignore
that the same prime images recur across draws, so treat them as rough.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
AF = ROOT / "agent-feeds"
AL = ROOT / "ad-library"
BA = ROOT / "brand-associations"

RUN_B1 = AF / "runs" / "batch1-image-priming-61d1c48aaf-20261021T024258Z"
RUN_B1_RERUN = AF / "runs" / "batch1-rerun-normal-scale-311cfa8d08-20261021T182547Z"
RUN_B2 = AF / "runs" / "batch2-beer-priming-9a960c96e6-20261021T194553Z"
PANEL_RUN = AL / "data/raw/snap_fr_betting_competitors/run_id=2026-10-21T005219.747976+0000"
SNAP1000_RUN = AL / "data/raw/snap_1000/run_id=2026-10-14T234838.202710+0000"
SNAP1000_BACKFILL = AL / "data/raw/snap_1000/story_backfill_run_id=2026-10-14T234838.202710+0000"
ANALYSIS = AL / "data/processed/competitor_analysis_v1"
LABELS = AL / "data/processed/competitor_labels_v1"

BOOT_REPS = 1000
BOOT_SEED = 20261111

SET_LABEL = {"social_drink": "pubs, beer gardens", "drink_harm": "drink-driving, crashes",
             "look_beer": "amber look-alikes", "win": "winning", "loss": "losing, distress",
             "look_bet": "green/yellow look-alikes", "neutral": "neutral"}
CAT_LABEL = {"beer": "Beer", "betting": "Betting", "control": "Fanta/Nike"}
CAT_SETS = {"beer": ["social_drink", "drink_harm", "look_beer"],
            "betting": ["win", "loss", "look_bet"],
            "control": ["win", "loss", "social_drink"]}
Q_LABEL = {"chance_ahead": "better off", "risk": "risk", "safe": "safe", "pressure": "pushiness",
           "respectful": "free to decide", "norm": "normal", "appeal": "appeal", "try": "try it"}
Q_B1 = ["chance_ahead", "risk", "pressure", "norm", "appeal"]
Q_B2 = ["risk", "safe", "pressure", "respectful", "norm", "appeal", "try"]
AD_LABEL = {"beer_heineken_glass": "Heineken pint (regular)", "beer_heineken_fans": "Heineken Oranje fan kit (regular)",
            "beer_heineken00_drinker": "Heineken 0.0 drinker", "beer_heineken00_can": "Heineken 0.0 \"Ultimate\" can",
            "bet_pmu_100cash": "PMU (betting)", "bet_unibet_10free": "Unibet (betting)"}
FIRMS = ["Winamax", "PMU", "Unibet", "Betsson", "bet365"]
FIRM = {"Winamax": "Winamax", "PMU": "PMU", "Kindred London Ltd": "Unibet", "Betsson France SA": "Betsson",
        "bet365": "bet365"}


# --------------------------------------------------------------------------- helpers

def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_csv(name: str, rows: list[dict]) -> None:
    OUT.mkdir(exist_ok=True)
    with (OUT / name).open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows([{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()} for r in rows])


def signed(x: float, star: bool = False) -> str:
    text = f"{x:+.2f}"
    return ("+0.00" if text == "-0.00" else text) + ("*" if star else "")


def pct(x: float, digits: int = 0) -> str:
    return f"{x * 100:.{digits}f}%"


def corr(a: list[float], b: list[float]) -> float:
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return num / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def solve(A: list[list[float]], b: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting (small dense systems)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A: list[list[float]]) -> list[list[float]]:
    n = len(A)
    cols = [solve(A, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def ols_hc1(y: list[float], cols: list[list[float]]) -> tuple[list[float], list[float]]:
    """OLS with a constant and HC1 (n/(n-k)) robust standard errors, as in the original scripts."""
    X = [[1.0] + [c[i] for c in cols] for i in range(len(y))]
    k, n = len(X[0]), len(y)
    XtX = [[sum(X[r][i] * X[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(X[r][i] * y[r] for r in range(n)) for i in range(k)]
    beta = solve(XtX, Xty)
    e = [y[r] - sum(X[r][i] * beta[i] for i in range(k)) for r in range(n)]
    inv = inverse(XtX)
    meat = [[sum(X[r][i] * X[r][j] * e[r] ** 2 for r in range(n)) for j in range(k)] for i in range(k)]
    tmp = [[sum(inv[i][m] * meat[m][j] for m in range(k)) for j in range(k)] for i in range(k)]
    cov = [[sum(tmp[i][m] * inv[m][j] for m in range(k)) * n / (n - k) for j in range(k)] for i in range(k)]
    return beta, [math.sqrt(cov[i][i]) for i in range(k)]


# --------------------------------------------------------------------------- agent-feeds

def load_run(run: Path) -> tuple[dict, dict, dict]:
    """Feeds and responses keyed by feed id. Rows re-written when a crashed run was resumed are
    dropped (we check below that every such duplicate is bit-identical to its original)."""
    feeds: dict[str, dict] = {}
    for f in jsonl(run / "feeds.jsonl"):
        feeds.setdefault(f["feed_id"], f)
    resp: dict[str, dict] = defaultdict(dict)
    raw: dict[tuple, str] = {}
    dups = identical = 0
    for line in (run / "responses.jsonl").read_text().splitlines():
        r = json.loads(line)
        key = (r["feed_id"], r["question_id"])
        if key in raw:
            dups += 1
            identical += raw[key] == line
            continue
        raw[key] = line
        resp[r["feed_id"]][r["question_id"]] = r
    return feeds, resp, {"duplicate_rows": dups, "identical_duplicates": identical}


def batch1_clean() -> tuple[dict, dict]:
    """Batch 1 on the normal scale: its normal-scale feeds plus the rerun of its reversed-scale
    feeds (same seed, so same feed ids and image orders)."""
    f1, r1, _ = load_run(RUN_B1)
    fr, rr, _ = load_run(RUN_B1_RERUN)
    feeds = {k: v for k, v in f1.items() if not v["reversed_scales"]}
    resp = {k: r1[k] for k in feeds}
    for k, v in fr.items():
        assert f1[k]["reversed_scales"] and f1[k]["images"] == v["images"]
        feeds[k], resp[k] = v, rr[k]
    return feeds, resp


def cell_values(feeds: dict, resp: dict, questions: list[str]) -> dict:
    """(ad, category, prime_set, position) -> list of {question: rating mean}, one per feed."""
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for fid in sorted(feeds):
        f = feeds[fid]
        cells[(f["ad_id"], f["ad_category"], f["prime_set"], f["position"])].append(
            {q: resp[fid][q]["mean"] for q in questions})
    return cells


def ads_in(cells: dict, cat: str) -> list[str]:
    return sorted({k[0] for k in cells if k[1] == cat})


def effect(cells: dict, ad: str, cat: str, prime_set: str, positions: list[str], q: str) -> float:
    treated = [v[q] for pos in positions for v in cells[(ad, cat, prime_set, pos)]]
    base = [v[q] for v in cells[(ad, cat, "neutral", "before_k5")]]
    return st.mean(treated) - st.mean(base)


def category_effects(cells: dict, cat: str, prime_set: str, positions: list[str], questions: list[str],
                     rng: random.Random | None = None) -> tuple[dict, dict]:
    """Mean over the category's ads of the per-ad effect; optional bootstrap 'interval excludes 0'."""
    ads = ads_in(cells, cat)
    point = {q: st.mean(effect(cells, ad, cat, prime_set, positions, q) for ad in ads) for q in questions}
    if rng is None:
        return point, {}
    groups = []
    for ad in ads:
        treated = [v for pos in positions for v in cells[(ad, cat, prime_set, pos)]]
        groups.append((treated, cells[(ad, cat, "neutral", "before_k5")]))
    draws = {q: [] for q in questions}
    for _ in range(BOOT_REPS):
        per_ad = []
        for treated, base in groups:
            t = [treated[rng.randrange(len(treated))] for _ in treated]
            b = [base[rng.randrange(len(base))] for _ in base]
            per_ad.append({q: st.mean(x[q] for x in t) - st.mean(x[q] for x in b) for q in questions})
        for q in questions:
            draws[q].append(st.mean(d[q] for d in per_ad))
    star = {}
    for q in questions:
        s = sorted(draws[q])
        lo, hi = s[int(0.05 * BOOT_REPS)], s[int(0.95 * BOOT_REPS) - 1]
        star[q] = lo > 0 or hi < 0
    return point, star


def table_b1_scale_problem() -> list[dict]:
    f1, r1, _ = load_run(RUN_B1)
    rows = []
    for q in Q_B1:
        normal = [r1[k][q]["mean"] for k, f in f1.items() if not f["reversed_scales"]]
        rev = [r1[k][q]["mean"] for k, f in f1.items() if f["reversed_scales"]]
        rows.append({"question": Q_LABEL[q], "mean_normal_scale": round(st.mean(normal), 2),
                     "mean_reversed_scale_after_recoding": round(st.mean(rev), 2),
                     "n_normal": len(normal), "n_reversed": len(rev)})
    return rows


def table_b1_behaviour() -> dict:
    f1, r1, _ = load_run(RUN_B1)
    spend = [r1[k]["spend"]["p_A"] for k in f1]
    show = [r1[k]["delegate"]["p_A"] for k in f1]
    return {"feeds": len(f1), "share_p_spend_gt_0.1": round(sum(p > 0.1 for p in spend) / len(spend), 3),
            "share_p_show_gt_0.1": round(sum(p > 0.1 for p in show) / len(show), 3)}


def table_b1_effects() -> list[dict]:
    feeds, resp = batch1_clean()
    cells = cell_values(feeds, resp, Q_B1)
    rng = random.Random(BOOT_SEED)
    rows = []
    for cat, sets in CAT_SETS.items():
        for ps in sets:
            point, star = category_effects(cells, cat, ps, ["before_k1", "before_k3", "before_k5"], Q_B1, rng)
            row = {"category": cat, "prime_set": ps}
            for q in Q_B1:
                row[q] = point[q]
                row[q + "_ci90_excludes_0"] = star[q]
            rows.append(row)
    return rows


def b1_betting_risk_range() -> dict:
    """Absolute risk ratings for the betting ads in clean batch 1, per ad x prime set x position cell."""
    feeds, resp = batch1_clean()
    cells = cell_values(feeds, resp, ["risk"])
    means = [st.mean(v["risk"] for v in vals) for k, vals in cells.items() if k[1] == "betting" and k[2] != "none"]
    return {"cells": len(means), "min_cell_mean_risk": min(means), "median_cell_mean_risk": st.median(means),
            "max_cell_mean_risk": max(means)}


def table_b1_dose() -> list[dict]:
    feeds, resp = batch1_clean()
    cells = cell_values(feeds, resp, Q_B1)
    rows = []
    for ps in ["drink_harm", "social_drink"]:
        for pos in ["before_k1", "before_k3", "before_k5", "ad_first"]:
            point, _ = category_effects(cells, "beer", ps, [pos], Q_B1)
            rows.append({"prime_set": ps, "position": pos, **{q: point[q] for q in Q_B1}})
    return rows


def table_b1_baselines() -> list[dict]:
    feeds, resp = batch1_clean()
    cells = cell_values(feeds, resp, Q_B1)
    rows = []
    for ad, cat in sorted({(k[0], k[1]) for k in cells}):
        alone = cells[(ad, cat, "none", "ad_only")][0]
        neutral = cells[(ad, cat, "neutral", "before_k5")]
        rows.append({"ad_id": ad, "category": cat,
                     **{f"{q}_alone": round(alone[q], 2) for q in ("appeal", "pressure")},
                     **{f"{q}_neutral_feed": round(st.mean(v[q] for v in neutral), 2) for q in ("appeal", "pressure")}})
    return rows


def table_b2_replication() -> list[dict]:
    feeds1, resp1 = batch1_clean()
    c1 = cell_values(feeds1, resp1, Q_B1)
    f2, r2_, _ = load_run(RUN_B2)
    c2 = cell_values(f2, r2_, Q_B2 + ["chance_ahead"])
    rows = []
    for ad, cat, ps in [("beer_heineken_glass", "beer", "drink_harm"), ("beer_heineken_glass", "beer", "social_drink"),
                        ("beer_heineken00_drinker", "beer", "drink_harm"), ("beer_heineken00_drinker", "beer", "social_drink"),
                        ("bet_pmu_100cash", "betting", "win"), ("bet_unibet_10free", "betting", "loss")]:
        row = {"ad": AD_LABEL[ad], "prime_set": ps}
        for q in ("risk", "pressure", "norm", "appeal"):
            row[f"{q}_batch1"] = effect(c1, ad, cat, ps, ["before_k5"], q)
            row[f"{q}_batch2"] = effect(c2, ad, cat, ps, ["before_k5"], q)
        rows.append(row)
    return rows


def table_b2_harm_by_ad() -> list[dict]:
    f2, r2_, _ = load_run(RUN_B2)
    cells = cell_values(f2, r2_, Q_B2)
    order = ["beer_heineken_glass", "beer_heineken_fans", "beer_heineken00_drinker", "beer_heineken00_can"]
    return [{"ad": AD_LABEL[ad], "alcohol_free": "00" in ad,
             **{q: effect(cells, ad, "beer", "drink_harm", ["before_k5"], q) for q in ("risk", "safe", "norm")}}
            for ad in order]


def table_b2_pooled() -> list[dict]:
    f2, r2_, _ = load_run(RUN_B2)
    cells = cell_values(f2, r2_, Q_B2)
    rng = random.Random(BOOT_SEED + 2)
    rows = []
    for cat, sets in CAT_SETS.items():
        for ps in sets:
            point, star = category_effects(cells, cat, ps, ["before_k1", "before_k5"], Q_B2, rng)
            row = {"category": cat, "prime_set": ps}
            for q in Q_B2:
                row[q] = point[q]
                row[q + "_ci90_excludes_0"] = star[q]
            rows.append(row)
    return rows


def table_b2_position() -> list[dict]:
    f2, r2_, _ = load_run(RUN_B2)
    cells = cell_values(f2, r2_, Q_B2)
    rows = []
    for ps in ["drink_harm", "social_drink"]:
        for pos in ["before_k1", "before_k5", "ad_first"]:
            point, _ = category_effects(cells, "beer", ps, [pos], Q_B2)
            rows.append({"prime_set": ps, "position": pos, **{q: point[q] for q in Q_B2}})
    return rows


def table_b2_checks() -> list[dict]:
    f2, r2_, integrity = load_run(RUN_B2)
    rows = []
    for sub in (None, "beer", "betting", "control"):
        keys = [k for k, f in f2.items() if sub is None or f["ad_category"] == sub]
        rows.append({"feeds": "all" if sub is None else sub, "n": len(keys),
                     "corr_risk_safe": round(corr([r2_[k]["risk"]["mean"] for k in keys],
                                                  [r2_[k]["safe"]["mean"] for k in keys]), 2),
                     "corr_pushiness_free_to_decide": round(corr([r2_[k]["pressure"]["mean"] for k in keys],
                                                                 [r2_[k]["respectful"]["mean"] for k in keys]), 2)})
    return rows


def b2_integrity() -> dict:
    f2, r2_, integrity = load_run(RUN_B2)
    scored = [r for d in r2_.values() for r in d.values() if r["kind"] == "rating"]
    manifest = json.loads((RUN_B2 / "manifest.json").read_text())
    return {"design_feeds": len(f2), "manifest_n_feeds": manifest["n_feeds"],
            "scored_answers": len(scored), "answers_valid_mass_below_0.8": sum(r["valid_mass"] < 0.8 for r in scored),
            **integrity, "git_dirty": manifest["git_dirty"]}


# --------------------------------------------------------------------------- ad-library

def panel_rows() -> list[dict]:
    return jsonl(ANALYSIS / "ad_label_panel.jsonl")


def creative_labels() -> dict[str, dict]:
    out = {}
    for r in jsonl(LABELS / "results.jsonl"):
        if r["status"] == "ok":
            out[r["coding_id"]] = r["labels"]
    return out


def table_panel_composition() -> list[dict]:
    recs = jsonl(PANEL_RUN / "records.jsonl")
    manifest = json.loads((PANEL_RUN / "manifest.json").read_text())
    strata = {FIRM[s["advertiser"]]: s for s in manifest["strata"]}
    rows = []
    for firm in FIRMS:
        rs = [r for r in recs if FIRM[r["query_advertiser"].strip()] == firm]
        starts = sorted(r["ad"]["start_date"][:10] for r in rs)
        rows.append({"firm": firm, "ads": len(rs),
                     "pagination": "exhausted" if strata[firm]["search_exhausted"] else "capped at quota",
                     "unique_creatives_base_run": len({r["media"]["sha256"] for r in rs if r.get("media")}),
                     "first_start": starts[0], "last_start": starts[-1]})
    rows.append({"firm": "Total", "ads": len(recs), "pagination": "",
                 "unique_creatives_base_run": len({r["media"]["sha256"] for r in recs if r.get("media")}),
                 "first_start": "", "last_start": ""})
    return rows


def panel_facts() -> dict:
    recs = jsonl(PANEL_RUN / "records.jsonl")
    labs = creative_labels()
    calls = jsonl(LABELS / "results.jsonl")
    invalid = AL / "data/raw/snap_fr_betting_competitors/run_id=2026-10-21T003157.817999+0000/records.jsonl"
    discovery = jsonl(AL / "data/processed/competitor_discovery_v1/results.jsonl")
    return {"ad_types": dict(Counter(r["ad"]["ad_type"] for r in recs).most_common()),
            "records_without_top_level_media": sum(1 for r in recs if not r.get("media")),
            "story_records_without_top_level_media": sum(1 for r in recs if not r.get("media")
                                                         and r["ad"]["ad_type"] == "STORY"),
            "invalidated_first_run_records": len(jsonl(invalid)),
            "label_calls": len(calls),
            "label_cost_equivalent_usd": round(sum(r.get("cost_equivalent_usd") or 0 for r in calls), 2),
            "discovery_calls": len(discovery),
            "discovery_cost_equivalent_usd": round(sum(r.get("cost_equivalent_usd") or 0 for r in discovery), 2),
            "coded_creatives": len(labs),
            "creatives_with_event_cue": sum(any(c["cue_type"] == "event" for c in L["cues_linked_to_brand"])
                                            for L in labs.values()),
            "creatives_with_sport_cue": sum(any(c["cue_type"] == "sport" for c in L["cues_linked_to_brand"])
                                            for L in labs.values())}


def table_firm_profiles() -> list[dict]:
    rows = panel_rows()
    labs = creative_labels()
    recs = {r["ad_id"]: r for r in jsonl(PANEL_RUN / "records.jsonl")}
    total_imp = sum(r["impressions"] for r in rows)
    out = []
    for firm in FIRMS:
        rs = [r for r in rows if r["firm"] == firm]
        imp = sum(r["impressions"] for r in rs)
        prom = Counter()
        bp3 = 0
        creatives: dict[str, list] = {}
        for r in rs:
            prom[r["most_prominent"]] += r["impressions"]
            if labs[r["coding_id"]]["brand_prominence"] == 3:
                bp3 += r["impressions"]
            c = creatives.setdefault(r["sha256"], [0, "9999"])
            c[0] += r["impressions"]
            c[1] = min(c[1], r["start"])
        male = upper = 0
        for r in rs:
            d = (recs[r["ad_id"]]["ad"].get("targeting_v2") or {}).get("demographics") or [{}]
            male += (d[0].get("gender") or "ALL") == "MALE"
            upper += d[0].get("max_age") is not None
        out.append({
            "firm": firm,
            "share_of_panel_impressions": round(imp / total_imp, 3),
            "ads_mentioning_football": round(sum("football" in (r["sports"] or []) for r in rs) / len(rs), 3),
            "ads_match_card_template": round(sum(r["template"] == "match_card" for r in rs) / len(rs), 3),
            "imp_offer_amount_most_prominent": round(prom["offer_amount"] / imp, 3),
            "imp_headline_most_prominent": round(prom["headline"] / imp, 3),
            "imp_brand_prominence_max": round(bp3 / imp, 3),
            "impressions_per_creative_millions": round(imp / len(creatives) / 1e6, 2),
            "ads_per_creative": round(len(rs) / len(creatives), 2),
            "creatives_first_run_before_2025": sum(1 for c in creatives.values() if c[1] < "2025-01"),
            "ads_targeting_men_only": round(male / len(rs), 3),
            "ads_with_an_upper_age_limit": round(upper / len(rs), 3),
            "last_launch": max(r["start"] for r in rs),
        })
    return out


def stem_tokens(text: str) -> list[str]:
    """Exactly as ad-library/src/ads_as_cues_metrics.py: accents stripped, stop/warning/brand
    words dropped, words truncated to 6 letters."""
    import re
    import unicodedata
    stop = set("""le la les de des du un une et en à a au aux sur pour par ton ta tes ta votre vos ou ce cet cette ces est sont avec dans
pas plus que qui on il elle nous vous ils ne se sa son ses mon ma mes l d j s n c qu jusqu jusqu'à 1er 18 www fr com the of and to in""".split())
    warn = set("jeux argent hasard peuvent etre dangereux pertes conflits familiaux addiction retrouvez conseils joueurs "
               "info service appel non surtaxe gouvernement 09 74 75 13 interdit mineurs".split())
    brand = {"winamax", "pmu", "unibet", "betsson", "bet365", "bet", "365", "kindred", "play", "wina"}
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return [w[:6] for w in re.findall(r"[a-z0-9]+", t)
            if not (w in stop or w in warn or w in brand or len(w) < 3 or w.isdigit())]


def feature_vector(L: dict) -> Counter:
    f: Counter = Counter()
    for k, v in L["borrowed_meaning"].items():
        f["bm:" + k] += v["prominence"] / 3
    for s in L["sports"]:
        f["sp:" + s] += 1
    f["lvl:" + L["competition_level"]] += 1
    f["fr:" + L["primary_framing"]] += 1
    f["of:" + L["offer"]["type"]] += 1
    f["tp:" + L["template"]] += 1
    return f


def cosine(a: Counter, b: Counter) -> float:
    num = sum(a[k] * b.get(k, 0) for k in a)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0


def firm_vector(rows: list[dict], labs: dict, kind: str, weight: str) -> Counter:
    v: Counter = Counter()
    for r in rows:
        L = labs.get(r["coding_id"])
        if not L:
            continue
        w = (r["impressions"] or 1) if weight == "imp" else 1
        src = (Counter(stem_tokens(" ".join(L["visible_text_verbatim"]) + " " + (r["headline"] or "")))
               if kind == "text" else feature_vector(L))
        for k, x in src.items():
            v[k] += w * x
    return v


def table_similarity() -> list[dict]:
    rows, labs = panel_rows(), creative_labels()
    vecs = {(kind, w, f): firm_vector([r for r in rows if r["firm"] == f], labs, kind, w)
            for kind in ("text", "labels") for w in ("ads", "imp") for f in FIRMS}
    out = []
    for i, a in enumerate(FIRMS):
        for b in FIRMS[i + 1:]:
            out.append({"pair": f"{a}-{b}",
                        "text_stems_by_ads": round(cosine(vecs[("text", "ads", a)], vecs[("text", "ads", b)]), 3),
                        "coded_cues_by_ads": round(cosine(vecs[("labels", "ads", a)], vecs[("labels", "ads", b)]), 3),
                        "coded_cues_by_impressions": round(cosine(vecs[("labels", "imp", a)], vecs[("labels", "imp", b)]), 3)})
    return out


def table_monthly_similarity() -> list[dict]:
    rows, labs = panel_rows(), creative_labels()
    out = []
    for m in sorted({r["start"][:7] for r in rows if r["start"] >= "2026-01"}):
        V = {f: firm_vector([r for r in rows if r["firm"] == f and r["start"][:7] == m], labs, "labels", "ads")
             for f in FIRMS}
        V = {f: v for f, v in V.items() if v}
        if len(V) < 2:
            continue
        names = list(V)
        sims = [cosine(V[a], V[b]) for i, a in enumerate(names) for b in names[i + 1:]]
        out.append({"launch_month": m, "firms_launching": " ".join(names), "n_firms": len(names),
                    "mean_pairwise_similarity": round(st.mean(sims), 3),
                    "winamax_bet365": round(cosine(V["Winamax"], V["bet365"]), 3)
                    if "Winamax" in V and "bet365" in V else ""})
    return out


def table_distinctive() -> list[dict]:
    rows, labs = panel_rows(), creative_labels()
    allv = {f: firm_vector([r for r in rows if r["firm"] == f], labs, "labels", "imp") for f in FIRMS}
    out = []
    for f in FIRMS:
        tot = sum(allv[f].values())
        rival: Counter = Counter()
        for g in FIRMS:
            if g != f:
                rival.update(allv[g])
        rtot = sum(rival.values())
        ratios = {k: (allv[f][k] / tot) / ((rival[k] / rtot) + 1e-3) for k in allv[f] if allv[f][k] / tot > 0.02}
        for rank, (k, x) in enumerate(sorted(ratios.items(), key=lambda kv: -kv[1])[:3], 1):
            out.append({"firm": f, "rank": rank, "feature": k, "representativeness_ratio": round(x, 1)})
    return out


def table_snap1000() -> list[dict]:
    recs = jsonl(SNAP1000_RUN / "records.jsonl")
    backfill = jsonl(SNAP1000_BACKFILL / "records.jsonl")
    with_media = {r["ad_id"] for r in recs if r.get("media")}
    after = with_media | {b["ad_id"] for b in backfill if b.get("sha256")}
    rows = [{"measure": "ads", "value": len(recs)}]
    rows += [{"measure": f"category: {k}", "value": v} for k, v in sorted(Counter(r["category"] for r in recs).items())]
    rows += [{"measure": f"country: {k}", "value": v} for k, v in sorted(Counter(r["query_country"] for r in recs).items())]
    rows += [{"measure": "records with media (collector)", "value": len(with_media)},
             {"measure": "unique media files (collector)", "value": len({r["media"]["sha256"] for r in recs if r.get("media")})},
             {"measure": "media requests answered HTTP 403", "value": sum("403" in (r.get("media_error") or "") for r in recs)},
             {"measure": "records with media after Story backfill", "value": len(after)}]
    return rows


# --------------------------------------------------------------------------- brand-associations

def table_asymmetry() -> list[dict]:
    cells = list(csv.DictReader((BA / "data/derived/assoc/cells.csv").open()))
    out = []
    for m in sorted({c["measure"] for c in cells}):
        rows = [c for c in cells if c["measure"] == m]
        prs = [float(c["asym"]) for c in rows if c["is_pair"] == "True" and c["asym"]]
        xy = [(float(c["size_ratio_log_pageviews"]), float(c["asym"])) for c in rows
              if c["asym"] and c["size_ratio_log_pageviews"]]
        beta, se = ols_hc1([y for _, y in xy], [[x for x, _ in xy]])
        out.append({"measure": m, "pairs_with_both_directions": len(prs),
                    "share_pairs_celebrity_to_brand_stronger": sum(a > 0 for a in prs) / len(prs),
                    "median_pair_asymmetry": st.median(prs),
                    "slope_on_log_size_ratio_pageviews": beta[1], "slope_se": se[1],
                    "cells": len(xy)})
    return out


def profile_direction() -> dict:
    """Direction of the 73 configured ambassador pairs in the multi-source association profiles
    (as in brand-associations/scripts/build_profile_brief.py): forward if the brand is a bigger
    part of the celebrity than the reverse (mean log10 ratio > 0.05), backward if < -0.05."""
    P = {(r["a"], r["b"]): r for r in csv.DictReader((BA / "data/derived/assoc/profile_pairs.csv").open())}

    def asym(a: str, b: str) -> float | None:
        if (a, b) in P:
            v = P[(a, b)]["asym_log10_a_over_b"]
            return float(v) if v else None
        v = P[(b, a)]["asym_log10_a_over_b"]
        return -float(v) if v else None

    def share(a: str, b: str, src: str) -> float | None:
        v = P[(a, b)][f"{src}_a_to_b"] if (a, b) in P else P[(b, a)][f"{src}_b_to_a"]
        return float(v) if v != "" else None

    pairs = json.loads((BA / "config/assoc/ambassadors.json").read_text())["pairs"]
    asy = [a for a in (asym(p["celebrity"], p["brand"]) for p in pairs) if a is not None]
    pv = {r["entity"]: int(r["pageviews"] or 0) for r in csv.DictReader((BA / "data/derived/assoc/wiki_entities.csv").open())}
    pts = []
    for p in pairs:
        c, b = p["celebrity"], p["brand"]
        a = asym(c, b)
        row = P.get((c, b)) or P.get((b, c))
        if a is None or not pv.get(c) or not pv.get(b) or int(row["sources_a_gt_b"]) + int(row["sources_b_gt_a"]) == 0:
            continue
        pts.append((math.log10(pv[c] / pv[b]), a))
    return {"pairs": len(asy), "forward": sum(a > 0.05 for a in asy), "backward": sum(a < -0.05 for a in asy),
            "flat": sum(-0.05 <= a <= 0.05 for a in asy),
            "corr_direction_vs_log_pageview_ratio": corr([x for x, _ in pts], [y for _, y in pts]), "n_corr": len(pts),
            "sweeney_novig_backward_ratio": 10 ** -asym("sydney_sweeney", "novig"),
            "lebron_nike_llm_share": share("lebron_james", "nike", "llm"),
            "nike_news_share_lebron": share("nike", "lebron_james", "news"),
            "lebron_news_share_nike": share("lebron_james", "nike", "news"),
            "lebron_nike_sources_forward": int(P[("lebron_james", "nike")]["sources_a_gt_b"]),
            "lebron_nike_sources_backward": int(P[("lebron_james", "nike")]["sources_b_gt_a"])}


def study_c_rows() -> list[dict]:
    return list(csv.DictReader((BA / "output/explore/study_c/looks_items.csv").open()))


def table_study_c() -> tuple[list[dict], dict]:
    rows = study_c_rows()
    usable = [r for r in rows if r["trends_log_lift"] not in ("", None)]
    lift = [float(r["trends_log_lift"]) for r in usable]
    bins = []
    for lo, hi in [(1, 1), (2, 3), (4, 6), (7, 9)]:
        sub = [float(r["trends_log_lift"]) for r in usable if lo <= int(r["n_items"]) <= hi]
        bins.append({"brands_in_look": f"{lo}" if lo == hi else f"{lo}-{hi}", "items": len(sub),
                     "mean_log_lift": st.mean(sub), "lift_multiple": math.exp(st.mean(sub))})
    tier = lambda r, t: 1.0 if r["tier"] == t else 0.0  # noqa: E731
    beta, se = ols_hc1(lift, [[math.log(int(r["n_items"])) for r in usable],
                              [tier(r, "mainstream") for r in usable], [tier(r, "luxury") for r in usable]])
    looks: dict[str, list] = defaultdict(list)
    for r in usable:
        looks[r["date"]].append(r)
    Y, Xf, Xm, Xl, Xa, dm_first, dm_other = [], [], [], [], [], [], []

    def dm(vals):
        m = sum(vals) / len(vals)
        return [v - m for v in vals]

    for d in looks:
        items = looks[d]
        if len(items) < 2:
            continue
        yy = dm([float(r["trends_log_lift"]) for r in items])
        Y += yy
        Xf += dm([1.0 if r["first"] == "True" else 0.0 for r in items])
        Xm += dm([tier(r, "mainstream") for r in items])
        Xl += dm([tier(r, "luxury") for r in items])
        Xa += dm([1.0 if r["affordable"] == "True" else 0.0 for r in items])
        for r, v in zip(items, yy):
            (dm_first if r["first"] == "True" else dm_other).append(v)
    bfe, sfe = ols_hc1(Y, [Xf, Xm, Xl, Xa])
    facts = {"brand_mentions": len(rows), "looks": len({r["date"] for r in rows}), "with_trends_data": len(usable),
             "slope_log_n_items_with_tier_controls": beta[1], "t": beta[1] / se[1],
             "within_look_first_named": bfe[1], "t_first_named": bfe[1] / sfe[1],
             "first_named_vs_look_mean": st.mean(dm_first), "others_vs_look_mean": st.mean(dm_other)}
    return bins, facts


def table_spillover() -> list[dict]:
    path = BA / "data/derived/demo/spillover_attention.csv"
    rows = list(csv.DictReader(path.open()))
    keep = [("taylor_nb550", "google_trends", "celebrity_link", "Taylor Swift New Balance"),
            ("taylor_nb550", "google_trends", "celebrity_link", "Taylor Swift Nike"),
            ("taylor_nb550", "google_trends", "nb_siblings", "New Balance 550"),
            ("kanye_energy_boost", "google_trends", "boost_siblings", "Energy Boost"),
            ("kanye_energy_boost", "google_trends", "boost_siblings", "Ultra Boost"),
            ("bieber_crocs", "google_trends", "celebrity_link", "Justin Bieber Crocs"),
            ("bieber_crocs", "google_trends", "competitors", "Crocs"),
            ("bieber_crocs", "wikipedia_pageviews", "brand_pages", "Crocs")]
    out = []
    for case, source, group, term in keep:
        match = [r for r in rows if (r["case_id"], r["source"], r["group"], r["term"]) == (case, source, group, term)]
        assert len(match) == 1, (case, source, group, term)
        out.append({"case": case, "source": source, "term": term, "role": match[0]["role"],
                    "z_days_0_3": match[0]["z_0_3"]})
    return out


# --------------------------------------------------------------------------- figures

def svg_bars(title: str, rows: list[tuple[str, float, str]], note: str, lo: float, hi: float, fmt) -> str:
    w, left, bar_h, gap, top = 780, 300, 22, 10, 50
    h = top + len(rows) * (bar_h + gap) + 44
    span = w - left - 70
    x0 = left + span * (0 - lo) / (hi - lo)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
             f'font-family="Helvetica, Arial, sans-serif" font-size="13">',
             f'<rect width="{w}" height="{h}" fill="white"/>',
             f'<text x="20" y="28" font-size="16" font-weight="bold">{title}</text>']
    for i, (label, value, color) in enumerate(rows):
        y = top + i * (bar_h + gap)
        xv = left + span * (value - lo) / (hi - lo)
        x, width = (x0, xv - x0) if value >= 0 else (xv, x0 - xv)
        parts.append(f'<text x="{left - 10}" y="{y + 16}" text-anchor="end">{label}</text>')
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{bar_h}" fill="{color}"/>')
        tx = xv + 6 if value >= 0 else xv - 6
        anchor = "start" if value >= 0 else "end"
        parts.append(f'<text x="{tx:.1f}" y="{y + 16}" text-anchor="{anchor}">{fmt(value)}</text>')
    parts.append(f'<line x1="{x0:.1f}" y1="{top - 6}" x2="{x0:.1f}" y2="{top + len(rows) * (bar_h + gap)}" '
                 f'stroke="#333" stroke-width="1"/>')
    parts.append(f'<text x="20" y="{h - 14}" font-size="11" fill="#555">{note}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def svg_harm(rows: list[dict]) -> str:
    bars = [(r["ad"].replace('"', "&quot;"), r["safe"], "#c0392b" if not r["alcohol_free"] else "#2e86c1")
            for r in rows]
    return svg_bars("Same drink-driving images, opposite effects on how safe the beer looks",
                    bars, "Qwen3-VL-8B, batch 2: change in 'how safe' (1-5) after 5 drink-driving images vs 5 neutral "
                    "images. Red = regular beer, blue = alcohol-free.", -2.5, 1.6, lambda v: f"{v:+.2f}")


def svg_prominence(rows: list[dict]) -> str:
    bars = [(f"{r['firm']}: offer amount", r["imp_offer_amount_most_prominent"], "#c0392b") for r in rows]
    bars += [(f"{r['firm']}: headline", r["imp_headline_most_prominent"], "#2e86c1") for r in rows]
    return svg_bars("What dominates each betting firm's Snapchat ads (share of impressions)",
                    bars, "Most prominent element as coded by Sonnet from each unique creative; weighted by lifetime "
                    "impressions in the Snap Ads Gallery.", 0.0, 0.7, lambda v: f"{v * 100:.0f}%")


# --------------------------------------------------------------------------- markdown

def md_table(header: list[str], rows: list[list]) -> list[str]:
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + \
           ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]


def markdown(t: dict) -> str:
    L = ["# Results", "",
         "Generated by `python analysis/make_results.py` from the saved data in this repository. "
         "Do not edit by hand. Every table has a CSV twin in this folder.", "",
         "Agent-feed ratings are the model's expected rating on a 1-5 scale (1 = low, 5 = high). "
         "Effects are the same ad after the named images minus the same ad after 5 neutral images, "
         "computed per ad and averaged over the ads in the category. `*` = 90% bootstrap interval over "
         "feeds within ad excludes zero (seeded; rough, because shared images across draws are ignored).", "",
         "## Part 1. Agents reading ads in a feed (`agent-feeds/`)", "",
         "### 1.1 Batch 1 measurement problem: the model ignored reversed scale labels", "",
         "Means after recoding reversed answers; if the model read the labels, the two columns would match.", ""]
    L += md_table(["question", "normal scale", "reversed scale (recoded)", "feeds (normal / reversed)"],
                  [[r["question"], f"{r['mean_normal_scale']:.2f}", f"{r['mean_reversed_scale_after_recoding']:.2f}",
                    f"{r['n_normal']} / {r['n_reversed']}"] for r in t["b1_scale"]])
    b = t["b1_behaviour"]
    L += ["", f"Behaviour questions in batch 1 were dead: P(spend 10 euros) exceeded 0.1 in "
          f"{pct(b['share_p_spend_gt_0.1'], 1)} of {b['feeds']} feeds, P(show the ad) in {pct(b['share_p_show_gt_0.1'], 1)}.", "",
          "### 1.2 Batch 1, clean (normal scale, 568 feeds): effect of the images before the ad (k = 1, 3, 5 pooled)", ""]
    L += md_table(["ad", "images before"] + [Q_LABEL[q] for q in Q_B1],
                  [[CAT_LABEL[r["category"]], SET_LABEL[r["prime_set"]]] +
                   [signed(r[q], r[q + "_ci90_excludes_0"]) for q in Q_B1] for r in t["b1_effects"]])
    br = t["b1_bet_risk"]
    L += ["", f"Betting ads sit near the ceiling on risk: across {br['cells']} ad x prime set x position cells the mean "
          f"risk rating has median {br['median_cell_mean_risk']:.2f} and range {br['min_cell_mean_risk']:.2f}-"
          f"{br['max_cell_mean_risk']:.2f} on the 1-5 scale.", "",
          "### 1.3 Batch 1, dose and position (beer ads, difference vs neutral feed)", ""]
    L += md_table(["images", "position"] + [Q_LABEL[q] for q in ("risk", "pressure", "norm", "appeal")],
                  [[SET_LABEL[r["prime_set"]], r["position"]] + [signed(r[q]) for q in ("risk", "pressure", "norm", "appeal")]
                   for r in t["b1_dose"]])
    L += ["", "### 1.4 Batch 1, the ad alone vs the ad after 5 neutral images", ""]
    L += md_table(["ad", "appeal alone", "appeal, neutral feed", "pushiness alone", "pushiness, neutral feed"],
                  [[r["ad_id"], f"{r['appeal_alone']:.2f}", f"{r['appeal_neutral_feed']:.2f}",
                    f"{r['pressure_alone']:.2f}", f"{r['pressure_neutral_feed']:.2f}"] for r in t["b1_base"]])
    i2 = t["b2_integrity"]
    L += ["", "### 1.5 Batch 2 run integrity", "",
          f"{i2['design_feeds']} unique design feeds (manifest: {i2['manifest_n_feeds']}); "
          f"{i2['duplicate_rows']} answer rows re-written around crashes, {i2['identical_duplicates']} of them "
          f"bit-identical to the original; {i2['answers_valid_mass_below_0.8']} of {i2['scored_answers']} scored "
          f"answers put < 80% probability on the valid options; `git_dirty` = {str(i2['git_dirty']).lower()}.", "",
          "### 1.6 Batch 1 replicates in batch 2 (ad after 5 images; batch 1 -> batch 2)", ""]
    L += md_table(["ad", "images before", "risk", "pushiness", "normal", "appeal"],
                  [[r["ad"], SET_LABEL[r["prime_set"]]] +
                   [f"{signed(r[q + '_batch1'])} -> {signed(r[q + '_batch2'])}" for q in ("risk", "pressure", "norm", "appeal")]
                   for r in t["b2_rep"]])
    L += ["", "### 1.7 Batch 2: 5 drink-driving images, by beer ad", ""]
    L += md_table(["ad", "risk", "safe", "normal"],
                  [[r["ad"], signed(r["risk"]), signed(r["safe"]), signed(r["norm"])] for r in t["b2_harm"]])
    L += ["", "![drink-driving effect on safe, by ad](beer_harm_by_ad.svg)", "",
          "### 1.8 Batch 2, pooled effects (ad last, 1 or 5 images)", ""]
    L += md_table(["ad", "images before"] + [Q_LABEL[q] for q in Q_B2],
                  [[CAT_LABEL[r["category"]], SET_LABEL[r["prime_set"]]] +
                   [signed(r[q], r[q + "_ci90_excludes_0"]) for q in Q_B2] for r in t["b2_pooled"]])
    L += ["", "### 1.9 Batch 2, position (beer ads, difference vs neutral feed)", ""]
    L += md_table(["images", "position"] + [Q_LABEL[q] for q in ("risk", "safe", "pressure", "norm", "appeal", "try")],
                  [[SET_LABEL[r["prime_set"]], r["position"]] +
                   [signed(r[q]) for q in ("risk", "safe", "pressure", "norm", "appeal", "try")] for r in t["b2_pos"]])
    L += ["", "### 1.10 Batch 2, reverse-worded twins (correlation across feeds)", ""]
    L += md_table(["feeds", "n", "risk vs safe", "pushiness vs free to decide"],
                  [[r["feeds"], r["n"], f"{r['corr_risk_safe']:+.2f}", f"{r['corr_pushiness_free_to_decide']:+.2f}"]
                   for r in t["b2_twins"]])
    pf = t["panel_facts"]
    L += ["", "## Part 2. Five betting firms' ads on Snapchat (`ad-library/`)", "",
          "### 2.1 The panel", ""]
    L += md_table(["firm", "ads", "pagination", "unique creatives (base run)", "campaign starts"],
                  [[r["firm"], f"{r['ads']:,}", r["pagination"], r["unique_creatives_base_run"],
                    f"{r['first_start']} - {r['last_start']}" if r["first_start"] else ""] for r in t["panel"]])
    L += ["", "Ad types: " + ", ".join(f"{k} {v:,}" for k, v in pf["ad_types"].items()) + ".", "",
          f"Coded unique creatives: {pf['coded_creatives']}. Tied to an event cue: {pf['creatives_with_event_cue']} "
          f"({pct(pf['creatives_with_event_cue'] / pf['coded_creatives'])}); to a sport cue: "
          f"{pf['creatives_with_sport_cue']} ({pct(pf['creatives_with_sport_cue'] / pf['coded_creatives'])}). "
          f"Records whose media sat only inside Story snaps (missed by the first collector, recovered by the "
          f"backfill): {pf['records_without_top_level_media']:,} ({pf['story_records_without_top_level_media']:,} of "
          f"them Story ads). The invalidated first run stopped after {pf['invalidated_first_run_records']} records. "
          f"Labelling took {pf['label_calls']} calls (cost-equivalent reported by the CLI: "
          f"${pf['label_cost_equivalent_usd']:.2f}); the discovery pass {pf['discovery_calls']} calls "
          f"(${pf['discovery_cost_equivalent_usd']:.2f}).", "",
          "### 2.2 Firm profiles", "",
          "Shares of ads are unweighted; shares of impressions are weighted by lifetime impressions. "
          "Brand prominence max = coded 3 on the 0-3 scale.", ""]
    keys = [("share_of_panel_impressions", "share of panel impressions", "p"),
            ("ads_mentioning_football", "ads featuring football", "p"),
            ("ads_match_card_template", "ads using a match-card template", "p"),
            ("imp_offer_amount_most_prominent", "impressions where the offer amount dominates", "p"),
            ("imp_headline_most_prominent", "impressions where the headline dominates", "p"),
            ("imp_brand_prominence_max", "impressions with maximal brand prominence", "p1"),
            ("impressions_per_creative_millions", "impressions per creative (millions)", "n"),
            ("ads_per_creative", "ads per creative", "n"),
            ("creatives_first_run_before_2025", "creatives first run before 2025", "i"),
            ("ads_targeting_men_only", "ads targeting men only", "p"),
            ("ads_with_an_upper_age_limit", "ads with an upper age limit", "p"),
            ("last_launch", "last campaign start", "s")]
    prof = {r["firm"]: r for r in t["profiles"]}
    fmt = {"p": lambda v: pct(v), "p1": lambda v: pct(v, 1), "n": lambda v: f"{v:.2f}", "i": str, "s": str}
    L += md_table(["measure"] + FIRMS, [[label] + [fmt[k](prof[f][key]) for f in FIRMS] for key, label, k in keys])
    L += ["", "![most prominent element by firm](firm_prominence.svg)", "",
          "### 2.3 How similar are the firms' ads? (cosine similarity of firm vectors)", ""]
    L += md_table(["pair", "ad-text stems (by ads)", "coded cues (by ads)", "coded cues (by impressions)"],
                  [[r["pair"], f"{r['text_stems_by_ads']:.3f}", f"{r['coded_cues_by_ads']:.3f}",
                    f"{r['coded_cues_by_impressions']:.3f}"] for r in t["sim"]])
    L += [""]
    L += ["Summary over the ten pairs (min / mean / max): " + "; ".join(
        f"{label} {min(r[col] for r in t['sim']):.3f} / {st.mean(r[col] for r in t['sim']):.3f} / "
        f"{max(r[col] for r in t['sim']):.3f}"
        for col, label in (("text_stems_by_ads", "ad-text stems"), ("coded_cues_by_ads", "coded cues by ads"),
                           ("coded_cues_by_impressions", "coded cues by impressions"))) + "."]
    L += ["", "### 2.4 Similarity of ads launched in the same month (coded cues, 2026)", ""]
    L += md_table(["launch month", "firms launching", "mean pairwise similarity", "Winamax-bet365"],
                  [[r["launch_month"], r["firms_launching"], f"{r['mean_pairwise_similarity']:.3f}",
                    r["winamax_bet365"]] for r in t["monthly"]])
    L += ["", "### 2.5 Most representative features (firm share / rival share, impression-weighted)", ""]
    L += md_table(["firm", "rank", "feature", "ratio"],
                  [[r["firm"], r["rank"], f"`{r['feature']}`", f"{r['representativeness_ratio']:.1f}x"] for r in t["dist"]])
    L += ["", "### 2.6 The earlier 1,000-ad Snapchat corpus (betting, alcohol, controls)", ""]
    L += md_table(["measure", "value"], [[r["measure"], r["value"]] for r in t["snap1000"]])
    sc = t["study_c_facts"]
    L += ["", "## Part 3. Celebrity-brand associations (`brand-associations/`)", "",
          "### 3.1 Directed association: does the celebrity retrieve the brand more than the reverse?", "",
          "Asymmetry = log P(brand | celebrity) - log P(celebrity | brand) for the 23 pilot ambassador pairs; "
          "slope = regression of asymmetry on log(brand pageviews / celebrity pageviews) over all "
          "celebrity x brand cells (HC1 standard errors).", ""]
    L += md_table(["measure", "pairs", "share celebrity -> brand stronger", "median asymmetry", "slope on size ratio (se)", "cells"],
                  [[r["measure"], r["pairs_with_both_directions"], pct(r["share_pairs_celebrity_to_brand_stronger"]),
                    f"{r['median_pair_asymmetry']:+.2f}", f"{r['slope_on_log_size_ratio_pageviews']:+.2f} ({r['slope_se']:.2f})",
                    r["cells"]] for r in t["asym"]])
    pd = t["profile"]
    L += ["", "### 3.2 Multi-source association profiles (110-entity frame, 73 ambassador pairs)", "",
          f"Of {pd['pairs']} ambassador pairs, {pd['forward']} run forward (the brand is a bigger part of the celebrity "
          f"than the reverse), {pd['backward']} backward and {pd['flat']} flat. Correlation between direction and "
          f"log10(celebrity pageviews / brand pageviews): {pd['corr_direction_vs_log_pageview_ratio']:+.2f} "
          f"(n = {pd['n_corr']} pairs with a link in at least one source). Sydney Sweeney x Novig is backward by a factor "
          f"of {pd['sweeney_novig_backward_ratio']:.1f}. LeBron James names Nike in "
          f"{pct(pd['lebron_nike_llm_share'])} of the language model's free-association lists; in news, Nike appears in "
          f"{pct(pd['lebron_news_share_nike'], 1)} of LeBron's articles and LeBron in {pct(pd['nike_news_share_lebron'], 1)} "
          f"of Nike's; across the five sources the pair is forward in {pd['lebron_nike_sources_forward']} and backward in "
          f"{pd['lebron_nike_sources_backward']}.", "",
          "### 3.3 Study C: items in the same celebrity outfit compete for search attention", "",
          f"{sc['brand_mentions']} brand mentions in {sc['looks']} Taylor Swift game-day looks; "
          f"{sc['with_trends_data']} with measurable Google Trends search. Lift = days 0-3 vs same-weekday baseline.", ""]
    L += md_table(["brands identified in the look", "items", "mean log lift", "lift"],
                  [[r["brands_in_look"], r["items"], f"{r['mean_log_lift']:+.2f}", f"x{r['lift_multiple']:.1f}"]
                   for r in t["study_c"]])
    L += ["", f"Slope of log lift on log(number of brands), tier controls: {sc['slope_log_n_items_with_tier_controls']:+.3f} "
          f"(t {sc['t']:+.2f}). Within-look (look fixed effects), first-named item: "
          f"{sc['within_look_first_named']:+.3f} log points (t {sc['t_first_named']:+.2f}); relative to the look mean, "
          f"first-named {sc['first_named_vs_look_mean']:+.2f}, others {sc['others_vs_look_mean']:+.2f}.", "",
          "### 3.4 Demo spillover: search z-scores, days 0-3 (read from the pipeline's saved table)", ""]
    L += md_table(["case", "source", "term", "role", "z"],
                  [[r["case"], r["source"], r["term"], r["role"], r["z_days_0_3"]] for r in t["spill"]])
    return "\n".join(L) + "\n"


def build() -> dict:
    t = {"b1_scale": table_b1_scale_problem(), "b1_behaviour": table_b1_behaviour(),
         "b1_effects": table_b1_effects(), "b1_dose": table_b1_dose(), "b1_base": table_b1_baselines(),
         "b2_integrity": b2_integrity(), "b2_rep": table_b2_replication(), "b2_harm": table_b2_harm_by_ad(),
         "b2_pooled": table_b2_pooled(), "b2_pos": table_b2_position(), "b2_twins": table_b2_checks(),
         "panel": table_panel_composition(), "panel_facts": panel_facts(), "profiles": table_firm_profiles(),
         "sim": table_similarity(), "monthly": table_monthly_similarity(), "dist": table_distinctive(),
         "snap1000": table_snap1000(), "asym": table_asymmetry(), "spill": table_spillover(),
         "profile": profile_direction(), "b1_bet_risk": b1_betting_risk_range()}
    t["study_c"], t["study_c_facts"] = table_study_c()
    return t


def main() -> None:
    t = build()
    for name, key in [("agents_b1_scale_problem.csv", "b1_scale"), ("agents_b1_effects.csv", "b1_effects"),
                      ("agents_b1_dose_position.csv", "b1_dose"), ("agents_b1_baselines.csv", "b1_base"),
                      ("agents_b2_replication.csv", "b2_rep"), ("agents_b2_harm_by_ad.csv", "b2_harm"),
                      ("agents_b2_pooled_effects.csv", "b2_pooled"), ("agents_b2_position.csv", "b2_pos"),
                      ("agents_b2_twin_correlations.csv", "b2_twins"), ("firms_panel.csv", "panel"),
                      ("firms_profiles.csv", "profiles"), ("firms_similarity.csv", "sim"),
                      ("firms_monthly_similarity.csv", "monthly"), ("firms_distinctive_features.csv", "dist"),
                      ("snap1000_corpus.csv", "snap1000"), ("assoc_asymmetry.csv", "asym"),
                      ("assoc_study_c_look_size.csv", "study_c"), ("assoc_spillover_z.csv", "spill")]:
        write_csv(name, t[key])
    def r4(obj):
        if isinstance(obj, float):
            return round(obj, 4)
        if isinstance(obj, dict):
            return {k: r4(v) for k, v in obj.items()}
        return obj

    (OUT / "facts.json").write_text(json.dumps(r4({"agents_b1_behaviour": t["b1_behaviour"],
                                                "agents_b2_integrity": t["b2_integrity"],
                                                "firms_panel": t["panel_facts"],
                                                "assoc_study_c": t["study_c_facts"],
                                                "assoc_profile_direction": t["profile"],
                                                "agents_b1_betting_risk": t["b1_bet_risk"]}), indent=1, sort_keys=True) + "\n")
    (OUT / "beer_harm_by_ad.svg").write_text(svg_harm(t["b2_harm"]))
    (OUT / "firm_prominence.svg").write_text(svg_prominence(t["profiles"]))
    (OUT / "RESULTS.md").write_text(markdown(t))
    print(f"wrote results to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
