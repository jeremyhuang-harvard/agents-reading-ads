"""Associative strength as *composition*, not similarity.

Similarity asks whether two vectors point the same way (McDonald's ~ Burger King). Associative
strength asks whether one entity is a *component* of the other's representation: is Adidas part of
what "Tate McRae" is made of, and is Tate part of what "Adidas" is made of? In psychology these are
forward and backward associative strength (FSA/BSA; Nelson, McEvoy & Schreiber 2004). They differ
in general, and neither needs the two entities to be alike.

This module measures composition in two ways.

1. Document decomposition (exact, Sarkar-compatible). An entity's vector is the mean of its
   documents' unit embeddings, x_c = (1/N) sum_d e_d, so its length splits additively over documents:

       ||x_c|| = (1/N) sum_d e_d . x_hat_c.

   The component share of brand b in celebrity c is the part of that sum contributed by c's
   documents that mention b:

       share(b in c) = sum_{d in c, d mentions b} e_d . x_hat_c  /  sum_{d in c} e_d . x_hat_c
                     = pi(b | c) * alignment(b in c)

   pi(b | c) is the fraction of c's coverage that mentions b. alignment is how central those
   documents are to c's overall representation (mean e_d . x_hat_c over mentioning docs divided by
   the mean over all docs). A brand mentioned only in passing in off-topic coverage gets
   alignment < 1; a brand woven into the core of the celebrity's coverage gets alignment > 1.

   Because sampled document sets rarely contain the reverse mention (few Adidas headlines name Tate),
   the population version replaces the sample pi with GDELT's population count N(c and b) / N(c)
   and keeps the sample alignment, estimated from co-mention documents (pooled if fewer than
   `min_docs`, neutral = 1 if none).

2. Sparse non-negative decomposition (vector algebra). Write each celebrity vector as a non-negative
   combination of a generic "celebrity" centroid plus the brand vectors (and each brand vector as a
   brand centroid plus celebrity vectors). The loading on Adidas in Tate's decomposition is Adidas's
   weight as a component of Tate. The generic centroid absorbs shared "celebrity-ness", so the
   loadings pick up specific components rather than category similarity. This is fragile when
   candidate vectors are collinear (Nike/Adidas/Puma), so treat it as a secondary measure.
"""

from __future__ import annotations

import csv
from collections import defaultdict

import numpy as np

from . import embed
from .config import DERIVED, Frame
from .sources import matcher


def decompose(E: np.ndarray, mentions: np.ndarray) -> dict:
    """E: (N, K) unit document embeddings of one cue; mentions: (N,) bool for one target."""
    x = E.mean(axis=0)
    xhat = x / max(np.linalg.norm(x), 1e-12)
    align = E @ xhat
    total = align.sum()
    n_m = int(mentions.sum())
    out = {"n_docs": len(E), "n_mention": n_m, "pi_sample": n_m / len(E) if len(E) else 0.0,
           "share_sample": float(align[mentions].sum() / total) if total > 0 else 0.0,
           "alignment": float(align[mentions].mean() / align.mean()) if n_m and align.mean() > 0 else None}
    return out


def nnls_loadings(target: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Non-negative least squares weights w >= 0 minimizing ||basis.T w - target||."""
    from scipy.optimize import nnls

    w, _ = nnls(np.asarray(basis, float).T, np.asarray(target, float))
    return w


def contribution_shares(target: np.ndarray, basis: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Share of the fitted vector's projection on the target direction contributed by each basis vector."""
    t = target / max(np.linalg.norm(target), 1e-12)
    contrib = w * (basis @ t)
    tot = contrib.sum()
    return contrib / tot if tot > 0 else np.zeros_like(contrib)


def _gdelt_pi(frame: Frame) -> tuple[dict, dict]:
    path = DERIVED / "gdelt_counts.csv"
    marg, joint = {}, {}
    if path.exists():
        for r in csv.DictReader(path.open()):
            if r["n"] == "":
                continue
            n = float(r["n"])
            if r["celebrity"] and r["brand"]:
                joint[(r["celebrity"], r["brand"])] = n
            else:
                marg[r["celebrity"] or r["brand"]] = n
    return marg, joint


def run(frame: Frame, backend: str, sources=("gdelt", "wikipedia"), min_docs: int = 3, log=print) -> None:
    enc = embed.Encoder(backend)
    docs = embed.load_documents(frame, sources)
    pats = {e.id: matcher(e) for e in frame.entities}
    marg, joint = _gdelt_pi(frame)
    # Co-mention headlines (documents mentioning both) are used only to estimate alignment, never the shares.
    joint_docs = defaultdict(list)
    for d in embed.load_documents(frame, ("gdelt_joint",)).values():
        for dd in d:
            joint_docs[dd["pair"]].append(dd["text"])
    joint_emb = {k: enc.encode(sorted(set(v))) for k, v in joint_docs.items()}
    emb, vec = {}, {}
    for e in frame.entities:
        ds = docs.get(e.id, [])
        if ds:
            emb[e.id] = enc.encode([d["text"] for d in ds])
            vec[e.id] = emb[e.id].mean(axis=0)

    # Co-mention documents for each pair, pooled from both sides (used for alignment when a side has few).
    rows = []
    for c in frame.celebrities:
        for b in frame.brands:
            rec = {"celebrity": c.id, "brand": b.id}
            for cue, tgt, side in ((c, b, "fwd"), (b, c, "bwd")):
                if cue.id not in emb:
                    continue
                ds = docs[cue.id]
                m = np.array([bool(pats[tgt.id].search(d["text"])) for d in ds])
                d = decompose(emb[cue.id], m)
                align = d["alignment"] if d["n_mention"] >= min_docs else None
                align_src = "own" if align is not None else ""
                if align is None:  # pool co-mention docs from the other side, scored against this cue's direction
                    other = docs.get(tgt.id, [])
                    m2 = [i for i, dd in enumerate(other) if pats[cue.id].search(dd["text"])]
                    pool = [emb[cue.id][m]] + ([emb[tgt.id][m2]] if m2 and tgt.id in emb else [])
                    pool += [joint_emb[f"{c.id}|{b.id}"]] if f"{c.id}|{b.id}" in joint_emb else []
                    pool = np.concatenate(pool) if sum(len(p) for p in pool) else np.zeros((0, emb[cue.id].shape[1]))
                    if len(pool) >= min_docs:
                        xhat = vec[cue.id] / np.linalg.norm(vec[cue.id])
                        align = float((pool @ xhat).mean() / (emb[cue.id] @ xhat).mean())
                        align_src = "pooled"
                    else:
                        align, align_src = 1.0, "neutral"
                n_joint = joint.get((c.id, b.id))
                pi_pop = n_joint / marg[cue.id] if n_joint is not None and marg.get(cue.id) else None
                rec.update({f"{side}_pi_sample": round(d["pi_sample"], 6), f"{side}_share_sample": round(d["share_sample"], 6),
                            f"{side}_n_mention": d["n_mention"], f"{side}_n_docs": d["n_docs"],
                            f"{side}_alignment": round(align, 4), f"{side}_alignment_source": align_src,
                            f"{side}_pi_population": "" if pi_pop is None else f"{pi_pop:.6g}",
                            side: f"{(pi_pop if pi_pop is not None else d['pi_sample']) * align:.6g}"})
            rows.append(rec)
    name = f"components_{embed.slug(backend)}"
    _write(DERIVED / f"directed_{name}.csv", rows)
    log(f"[components] {backend}: wrote directed_{name}.csv "
        f"({sum(1 for r in rows if r.get('fwd_n_mention', 0) > 0)} cells with own-sample co-mentions celebrity side, "
        f"{sum(1 for r in rows if r.get('bwd_n_mention', 0) > 0)} brand side)")

    # Sparse non-negative decomposition in vector space.
    cs = [c for c in frame.celebrities if c.id in vec]
    bs = [b for b in frame.brands if b.id in vec]
    Xc = np.stack([vec[c.id] for c in cs])
    Xb = np.stack([vec[b.id] for b in bs])
    fwd = np.zeros((len(cs), len(bs)))
    bwd = np.zeros((len(cs), len(bs)))
    for i in range(len(cs)):
        others = np.delete(Xc, i, axis=0).mean(axis=0, keepdims=True)
        basis = np.vstack([others, Xb])
        w = nnls_loadings(Xc[i], basis)
        fwd[i] = contribution_shares(Xc[i], basis, w)[1:]
    for j in range(len(bs)):
        others = np.delete(Xb, j, axis=0).mean(axis=0, keepdims=True)
        basis = np.vstack([others, Xc])
        w = nnls_loadings(Xb[j], basis)
        bwd[:, j] = contribution_shares(Xb[j], basis, w)[1:]
    nn_rows = [{"celebrity": c.id, "brand": b.id, "fwd": f"{fwd[i, j]:.6g}", "bwd": f"{bwd[i, j]:.6g}"}
               for i, c in enumerate(cs) for j, b in enumerate(bs)]
    _write(DERIVED / f"directed_nnls_{embed.slug(backend)}.csv", nn_rows)
    log(f"[components] nnls: {int((fwd > 0).sum())} nonzero celebrity->brand loadings, {int((bwd > 0).sum())} brand->celebrity")


def _write(path, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def top_components(frame: Frame, backend: str, k: int = 5) -> dict[str, list[tuple[str, float]]]:
    """Convenience: the k largest components of each entity (for reports)."""
    path = DERIVED / f"directed_components_{embed.slug(backend)}.csv"
    out = defaultdict(list)
    for r in csv.DictReader(path.open()):
        if r.get("fwd"):
            out[r["celebrity"]].append((r["brand"], float(r["fwd"])))
        if r.get("bwd"):
            out[r["brand"]].append((r["celebrity"], float(r["bwd"])))
    return {e: sorted(v, key=lambda x: -x[1])[:k] for e, v in out.items()}
