"""Multi-source entity representations: one semantic vector and one directed association profile per entity.

Two objects, kept separate on purpose:

* ``vector[e]``: a Sarkar-style embedding. For each source, embed the text units in which the
  entity appears (article paragraphs, news title+lede, the pages its readers click next, the queries searched
  alongside it, the things a language model free-associates with it), take the weighted mean, normalize, then
  average the per-source vectors. cos(vector[A], vector[B]) is SIMILARITY ("what kind of thing is it"),
  and it is symmetric.

* ``profile[s][A][B]``: the share of A's units in source s that involve B (sentences naming B, articles naming
  B, outgoing clicks to B's page, related-search weight naming B, free-association samples naming B).
  This is ASSOCIATIVE STRENGTH, P(B | A) in source s, and it is directed: profile[A][B] != profile[B][A].
  Combined: a strength index in [0, 1] (mean within-source percentile) and an asymmetry score (mean log10 ratio).

Outputs (data/derived/assoc/): profile_shares.csv (long), profile_pairs.csv (both directions per ordered pair),
profile_vectors_<backend>.npz.  Figures are built by scripts/build_profile_brief.py.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .config import DERIVED, RAW, Frame
from .embed import Encoder, mask_names, slug
from .freeassoc import parse
from .sources import matcher, short_matcher
from .sources.wiki import sentences

SOURCES = {
    "wiki_text": "Wikipedia article (share of sentences naming the other)",
    "news": "Common Crawl News (share of articles about the entity whose text names the other)",
    "wiki_clicks": "Wikipedia readers (share of outgoing clicks to the other's page)",
    "search": "Google related searches, US (share of related-query weight naming the other)",
    "llm": "Qwen3-8B free association (share of samples naming the other)",
}
MAX_NEWS_TEXTS = 150
MIN_UNITS = {"wiki_text": 20, "news": 10, "wiki_clicks": 1000, "search": 5, "llm": 10}


def _wiki_titles(frame: Frame) -> dict[str, str]:
    path = DERIVED / "wiki_entities.csv"
    out = {}
    if path.exists():
        for r in csv.DictReader(path.open()):
            if r["wiki_title"]:
                out[r["entity"]] = r["wiki_title"]
    for e in frame.entities:
        if e.id not in out and e.wiki:
            out[e.id] = e.wiki
    return out


def wiki_text(frame, pats):
    paras = defaultdict(list)
    path = DERIVED / "documents_wikipedia.jsonl"
    for line in path.open():
        d = json.loads(line)
        paras[d["entity"]].append(d["text"])
    shares, n, texts = {}, {}, {}
    for e in frame.entities:
        sents = [s for p in paras.get(e.id, []) for s in sentences(p)]
        if not sents:
            continue
        n[e.id] = len(sents)
        shares[e.id] = {o.id: sum(bool(pats[o.id].search(s)) for s in sents) / len(sents) for o in frame.entities if o.id != e.id}
        texts[e.id] = [(p, 1.0) for p in paras[e.id]]
    return shares, n, texts


def news(frame, pats):
    arts = defaultdict(list)
    tagged = RAW / "ccnews" / f"frame-{frame.version}"  # full rescan with the current frame, if it exists
    base = tagged if tagged.exists() and any(tagged.glob("*/*.jsonl.gz")) else RAW / "ccnews"
    for f in sorted(base.glob("*/*.jsonl.gz")):
        with gzip.open(f, "rt") as h:
            for line in h:
                d = json.loads(line)
                for a in d.get("about", []):
                    arts[a].append(d)
    shares, n, texts = {}, {}, {}
    for e in frame.entities:
        docs = list({d["url"]: d for d in arts.get(e.id, [])}.values())  # dedupe by URL
        if not docs:
            continue
        n[e.id] = len(docs)
        shares[e.id] = {o.id: sum(o.id in d.get("hits", {}) for d in docs) / len(docs) for o in frame.entities if o.id != e.id}
        docs = sorted(docs, key=lambda d: d["url"])[:MAX_NEWS_TEXTS]
        texts[e.id] = [((d.get("title", "") + ". " + d.get("lede", ""))[:1000], 1.0) for d in docs]
    return shares, n, texts


def wiki_clicks(frame, pats):
    titles = _wiki_titles(frame)
    by_title = {t: eid for eid, t in titles.items()}
    out_tot, out_to, nxt = Counter(), defaultdict(Counter), defaultdict(Counter)
    for f in sorted((RAW / "clickstream").glob("*.filtered.tsv")):
        for line in f.open():
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 4:
                continue
            prev, curr, _typ, k = parts
            a = by_title.get(prev)
            if a is None:
                continue
            k = int(k)
            out_tot[a] += k
            nxt[a][curr] += k
            b = by_title.get(curr)
            if b is not None and b != a:
                out_to[a][b] += k
    shares, n, texts = {}, {}, {}
    for e in frame.entities:
        if not out_tot[e.id]:
            continue
        n[e.id] = out_tot[e.id]
        shares[e.id] = {o.id: out_to[e.id][o.id] / out_tot[e.id] for o in frame.entities if o.id != e.id}
        texts[e.id] = [(p.replace("_", " "), k / out_tot[e.id]) for p, k in nxt[e.id].most_common(40)]
    return shares, n, texts


def search(frame, pats):
    from ..explore import trends as T

    shares, n, texts = {}, {}, {}
    for e in frame.entities:
        try:
            rel = T.related(e.name, frame.start, frame.end, geo="US")
        except Exception:
            continue
        top = [r for r in (rel.get("top") or []) if float(r.get("value", 0)) > 0]
        if not top:
            continue
        tot = sum(float(r["value"]) for r in top)
        n[e.id] = len(top)
        shares[e.id] = {o.id: sum(float(r["value"]) for r in top if pats[o.id].search(str(r["query"]))) / tot
                        for o in frame.entities if o.id != e.id}
        texts[e.id] = [(str(r["query"]), float(r["value"]) / tot) for r in top]
    return shares, n, texts


def llm(frame, pats, model_slug="qwen3-8b-4bit"):
    samples = defaultdict(list)
    path = RAW / "freeassoc" / f"{model_slug}.jsonl"
    for line in path.open():
        d = json.loads(line)
        samples[d["cue"]].append(parse(d["text"]))
    shares, n, texts = {}, {}, {}
    for e in frame.entities:
        lists = samples.get(e.id)
        if not lists:
            continue
        n[e.id] = len(lists)
        shares[e.id] = {o.id: sum(any(pats[o.id].search(it) for it in items) for items in lists) / len(lists)
                        for o in frame.entities if o.id != e.id}
        cnt = Counter(it.strip().lower() for items in lists for it in items if not pats[e.id].search(it))
        texts[e.id] = [(w, k / len(lists)) for w, k in cnt.most_common(40)]
    return shares, n, texts


COLLECT = {"wiki_text": wiki_text, "news": news, "wiki_clicks": wiki_clicks, "search": search, "llm": llm}


def build(frame: Frame, backend: str = "st:BAAI/bge-base-en-v1.5", with_vectors: bool = True, log=print) -> None:
    pats = {e.id: matcher(e) for e in frame.entities}
    spats = {e.id: short_matcher(e) for e in frame.entities}
    shares, units, texts = {}, {}, {}
    for s, fn in COLLECT.items():
        try:
            shares[s], units[s], texts[s] = fn(frame, spats if s in ("search", "llm") else pats)
        except FileNotFoundError as exc:
            log(f"[profile] {s}: missing input ({exc})")
            shares[s], units[s], texts[s] = {}, {}, {}
        ok = [e for e in units[s] if units[s][e] >= MIN_UNITS[s]]
        log(f"[profile] {s}: {len(ok)}/{len(frame.entities)} entities with >= {MIN_UNITS[s]} units")

    DERIVED.mkdir(parents=True, exist_ok=True)
    with (DERIVED / "profile_shares.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["source", "from", "to", "share", "units_from"])
        for s in SOURCES:
            for a, row in shares[s].items():
                if units[s][a] < MIN_UNITS[s]:
                    continue
                for b, v in row.items():
                    if v > 0:
                        w.writerow([s, a, b, f"{v:.6g}", units[s][a]])

    # Sources live on different scales (LLM lists ~50%, clicks ~0.1%), so they are combined two scale-free ways:
    #  strength  = mean over sources of the share's percentile among that source's non-zero shares (0 if zero), in [0, 1];
    #  asymmetry = mean over sources with both directions of log10((x + e_s) / (y + e_s)), e_s = 0.1 x median non-zero share.
    nonzero, scale = {}, {}
    for s in SOURCES:
        nz = sorted(v for a, row in shares[s].items() if units[s][a] >= MIN_UNITS[s] for v in row.values() if v > 0)
        nonzero[s] = np.array(nz)
        scale[s] = float(np.median(nz)) if nz else 1.0
        log(f"[profile] {s}: median non-zero share {scale[s]:.4g} ({len(nz)} non-zero ordered pairs)")
    (DERIVED / "profile_scales.json").write_text(json.dumps(scale, indent=2))

    def pctile(s, v):
        return 0.0 if v <= 0 or not len(nonzero[s]) else float(np.searchsorted(nonzero[s], v, side="right")) / len(nonzero[s])

    ids = [e.id for e in frame.entities]
    with (DERIVED / "profile_pairs.csv").open("w", newline="") as h:
        cols = ["a", "b", "kind_a", "kind_b"]
        for s in SOURCES:
            cols += [f"{s}_a_to_b", f"{s}_b_to_a"]
        cols += ["combined_a_to_b", "combined_b_to_a", "asym_log10_a_over_b", "n_sources_a", "n_sources_b", "n_sources_both",
                 "sources_a_gt_b", "sources_b_gt_a"]
        w = csv.DictWriter(h, fieldnames=cols)
        w.writeheader()
        kinds = {e.id: e.kind for e in frame.entities}
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                r: dict[str, object] = {"a": a, "b": b, "kind_a": kinds[a], "kind_b": kinds[b]}
                fa, fb, lr, gt, lt = [], [], [], 0, 0
                for s in SOURCES:
                    x = shares[s][a][b] if a in shares[s] and units[s][a] >= MIN_UNITS[s] else None
                    y = shares[s][b][a] if b in shares[s] and units[s][b] >= MIN_UNITS[s] else None
                    r[f"{s}_a_to_b"] = "" if x is None else f"{x:.6g}"
                    r[f"{s}_b_to_a"] = "" if y is None else f"{y:.6g}"
                    if x is not None:
                        fa.append(pctile(s, x))
                    if y is not None:
                        fb.append(pctile(s, y))
                    if x is not None and y is not None:
                        e_s = 0.1 * scale[s]
                        lr.append(np.log10((x + e_s) / (y + e_s)))
                        gt += x > y
                        lt += y > x
                r["combined_a_to_b"] = f"{np.mean(fa):.4f}" if fa else ""
                r["combined_b_to_a"] = f"{np.mean(fb):.4f}" if fb else ""
                r["asym_log10_a_over_b"] = f"{np.mean(lr):.4f}" if lr else ""
                r["n_sources_a"], r["n_sources_b"], r["n_sources_both"] = len(fa), len(fb), len(lr)
                r["sources_a_gt_b"], r["sources_b_gt_a"] = gt, lt
                w.writerow(r)
    log("[profile] wrote profile_shares.csv and profile_pairs.csv")
    if not with_vectors:
        return

    # semantic vectors, names kept and masked
    enc = Encoder(backend)
    all_pats = list(pats.values())
    out: dict[str, np.ndarray] = {"ids": np.array(ids), "sources": np.array(list(SOURCES))}
    for mask in (False, True):
        mats = []
        for s in SOURCES:
            M = []
            for e in ids:
                tw = [t for t in texts[s].get(e, []) if t[0].strip()]
                if not tw or units[s].get(e, 0) < MIN_UNITS[s]:
                    M.append(None)
                    continue
                tx = [mask_names(t, all_pats) if mask else t for t, _ in tw]
                V = enc.encode(tx)
                wts = np.array([wt for _, wt in tw], dtype=float)
                v = (V * wts[:, None]).sum(0) / wts.sum()
                M.append(v / max(np.linalg.norm(v), 1e-12))
            dim = next(m.shape[0] for m in M if m is not None)
            mats.append(np.stack([m if m is not None else np.full(dim, np.nan) for m in M]))
            log(f"[profile] embedded {s} (mask={mask})")
        per = np.stack(mats)  # sources x entities x dim
        comb = np.nanmean(per, axis=0)
        comb /= np.maximum(np.linalg.norm(comb, axis=1, keepdims=True), 1e-12)
        tag = "masked" if mask else "named"
        out[f"per_source_{tag}"] = per.astype(np.float32)
        out[f"combined_{tag}"] = comb.astype(np.float32)
    np.savez_compressed(DERIVED / f"profile_vectors_{slug(backend)}.npz", **out)  # type: ignore[arg-type]
    log(f"[profile] wrote profile_vectors_{slug(backend)}.npz")
