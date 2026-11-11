"""Summarise a batch-1 run into tables a human can read.

Usage:
    uv run python -m agentic_ads.analyze_priming runs/<run-dir>

Writes to artifacts/<run-name>/:
    cell_means.csv          mean outcome per ad x prime set x position (averaged over draws)
    effects_vs_neutral.csv  each prime set minus the neutral feed, same ad and position
    position_effects.csv    k=1,3,5 before vs ad-first, per ad x prime set
    trails_sample.md        side-by-side trails for one draw of each cell
    summary.md              headline tables
"""
from __future__ import annotations

import csv
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCORED = ["chance_ahead", "risk", "pressure", "norm", "appeal", "spend", "delegate"]
LABEL = {"chance_ahead": "Better off (1-5)", "risk": "Risk (1-5)", "pressure": "Pushiness (1-5)",
         "norm": "Normal (1-5)", "appeal": "Appeal (1-5)", "spend": "P(spend €10)",
         "delegate": "P(agent shows ad)"}


def load(run: Path):
    feeds = {json.loads(l)["feed_id"]: json.loads(l) for l in (run / "feeds.jsonl").open()}
    resp = defaultdict(dict)
    for l in (run / "responses.jsonl").open():
        r = json.loads(l)
        resp[r["feed_id"]][r["question_id"]] = r
    return feeds, resp


def value(r):
    if r["kind"] == "rating":
        return r["mean"]
    if r["kind"] == "choice":
        return r["p_A"]
    return None


def se(xs):
    return st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan")


def main(run_arg: str) -> Path:
    run = Path(run_arg).resolve()
    feeds, resp = load(run)
    out = ROOT / "artifacts" / run.name
    out.mkdir(parents=True, exist_ok=True)

    cells = defaultdict(lambda: defaultdict(list))  # (ad, set, pos) -> q -> [values over draws]
    low_mass = 0
    for fid, f in feeds.items():
        for q in SCORED:
            r = resp[fid].get(q)
            if not r:
                continue
            if r["valid_mass"] < 0.8:
                low_mass += 1
            cells[(f["ad_id"], f["ad_category"], f["prime_set"], f["position"])][q].append(value(r))

    with (out / "cell_means.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["ad_id", "category", "prime_set", "position", "n_draws"] + SCORED)
        for k in sorted(cells):
            w.writerow(list(k) + [len(cells[k][SCORED[0]])] + [round(st.mean(cells[k][q]), 3) for q in SCORED])

    # Effect of each prime set vs neutral, same ad, ad shown last after 5 images.
    eff_rows = []
    for (ad, cat, ps, pos), qs in cells.items():
        if pos != "before_k5" or ps == "neutral":
            continue
        base = cells.get((ad, cat, "neutral", "before_k5"))
        if not base:
            continue
        row = {"ad_id": ad, "category": cat, "prime_set": ps}
        for q in SCORED:
            d = st.mean(qs[q]) - st.mean(base[q])
            s = math.sqrt(se(qs[q]) ** 2 + se(base[q]) ** 2)
            row[q] = round(d, 3)
            row[q + "_se"] = round(s, 3)
        eff_rows.append(row)
    with (out / "effects_vs_neutral.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(eff_rows[0].keys()))
        w.writeheader(); w.writerows(sorted(eff_rows, key=lambda r: (r["category"], r["ad_id"], r["prime_set"])))

    # Pooled by category x prime set (averaging over ads), for the headline table.
    pooled = defaultdict(lambda: defaultdict(list))
    for r in eff_rows:
        for q in SCORED:
            pooled[(r["category"], r["prime_set"])][q].append(r[q])

    # Position: does effect grow with k, and is ad-first different?
    pos_rows = []
    for (ad, cat, ps, pos), qs in cells.items():
        if ps in ("neutral", "none"):
            continue
        base = cells.get((ad, cat, "neutral", "before_k5"))
        row = {"ad_id": ad, "category": cat, "prime_set": ps, "position": pos}
        for q in ("chance_ahead", "risk", "appeal", "spend"):
            row[q] = round(st.mean(qs[q]) - st.mean(base[q]), 3)
        pos_rows.append(row)
    with (out / "position_effects.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(pos_rows[0].keys()))
        w.writeheader(); w.writerows(sorted(pos_rows, key=lambda r: (r["category"], r["ad_id"], r["prime_set"], r["position"])))
    pos_pool = defaultdict(lambda: defaultdict(list))
    for r in pos_rows:
        for q in ("chance_ahead", "risk", "appeal", "spend"):
            pos_pool[(r["category"], r["prime_set"], r["position"])][q].append(r[q])

    # Baselines: ad alone vs neutral feed.
    base_lines = []
    for (ad, cat, ps, pos), qs in sorted(cells.items()):
        if ps == "none":
            nb = cells[(ad, cat, "neutral", "before_k5")]
            base_lines.append((ad, cat, {q: st.mean(qs[q]) for q in SCORED}, {q: st.mean(nb[q]) for q in SCORED}))

    # Trails: one draw per cell, ad last after 5.
    trails = defaultdict(dict)
    for fid, f in feeds.items():
        if f["draw"] == 0 and f["position"] in ("before_k5", "ad_only"):
            trails[f["ad_id"]][f["prime_set"]] = (resp[fid]["stands_out"]["text"], resp[fid]["trail"]["text"])
    with (out / "trails_sample.md").open("w") as h:
        h.write("# Trails, draw 0, ad shown after 5 images (or alone)\n\n")
        for ad in sorted(trails):
            h.write(f"## {ad}\n\n")
            for ps in ["none"] + sorted(k for k in trails[ad] if k != "none"):
                if ps in trails[ad]:
                    so, tr = trails[ad][ps]
                    h.write(f"**{ps}** — stands out: _{so}_\n\n> {tr}\n\n")

    # Prime mentions in trails (crude keyword check, exploratory).
    KW = {"win": ["celebrat", "victory", "win", "cheer", "trophy"], "loss": ["sad", "stress", "debt", "loss", "distress", "despair", "worr"],
          "social_drink": ["pub", "bar", "crowd", "friends", "social"], "drink_harm": ["police", "crash", "accident", "breath", "drunk"],
          "look_bet": ["leaf", "leaves", "plant", "flower", "nature", "green"], "look_beer": ["leaf", "leaves", "honey", "autumn", "golden", "amber", "droplet"],
          "neutral": ["weather", "soup", "park", "library", "bench", "food"]}
    mention = defaultdict(list)
    for fid, f in feeds.items():
        if f["position"] == "before_k5" and f["prime_set"] in KW:
            t = resp[fid]["trail"]["text"].lower()
            mention[(f["ad_category"], f["prime_set"])].append(any(k in t for k in KW[f["prime_set"]]))

    def fmt(x, q):
        return f"{x:+.2f}" if q not in ("spend", "delegate") else f"{x:+.2f}"

    with (out / "summary.md").open("w") as h:
        h.write(f"# Batch 1 summary: `{run.name}`\n\n")
        h.write(f"Feeds: {len(feeds)}. Scored answers with <80% probability on valid options: {low_mass}.\n\n")
        h.write("## 1. Baselines: the ad alone vs the ad after 5 neutral images\n\n")
        h.write("| Ad | | " + " | ".join(LABEL[q] for q in SCORED) + " |\n|" + "---|" * (len(SCORED) + 2) + "\n")
        for ad, cat, alone, neut in base_lines:
            h.write(f"| {ad} | alone | " + " | ".join(f"{alone[q]:.2f}" for q in SCORED) + " |\n")
            h.write(f"| | neutral feed | " + " | ".join(f"{neut[q]:.2f}" for q in SCORED) + " |\n")
        h.write("\n## 2. Effect of each prime set vs the neutral feed (ad last, 5 primes; averaged over ads in category)\n\n")
        h.write("Positive = higher than after neutral images. Ratings are on the 1-5 scale; P() rows are probability points.\n\n")
        h.write("| Category | Prime set | " + " | ".join(LABEL[q] for q in SCORED) + " |\n|" + "---|" * (len(SCORED) + 2) + "\n")
        for (cat, ps) in sorted(pooled):
            h.write(f"| {cat} | {ps} | " + " | ".join(fmt(st.mean(pooled[(cat, ps)][q]), q) for q in SCORED) + " |\n")
        h.write("\n## 3. Does the effect grow with more primes, and vanish when the ad comes first?\n\n")
        h.write("Difference vs neutral feed, averaged over ads in category.\n\n")
        h.write("| Category | Prime set | Position | Better off | Risk | Appeal | P(spend) |\n|---|---|---|---|---|---|---|\n")
        order = {"before_k1": 1, "before_k3": 2, "before_k5": 3, "ad_first": 4}
        for (cat, ps, pos) in sorted(pos_pool, key=lambda k: (k[0], k[1], order[k[2]])):
            v = pos_pool[(cat, ps, pos)]
            h.write(f"| {cat} | {ps} | {pos} | " + " | ".join(f"{st.mean(v[q]):+.2f}" for q in ("chance_ahead", "risk", "appeal", "spend")) + " |\n")
        h.write("\n## 4. Does the trail mention the preceding images? (keyword check, exploratory)\n\n")
        h.write("| Category | Prime set | Share of trails mentioning primes |\n|---|---|---|\n")
        for k in sorted(mention):
            h.write(f"| {k[0]} | {k[1]} | {sum(mention[k])/len(mention[k]):.0%} (n={len(mention[k])}) |\n")
    print(out)
    return out


if __name__ == "__main__":
    main(sys.argv[1])
