"""Sarkar-style coverage representations of celebrities and brands.

Following Sarkar ("Economic Representations"), each entity is represented by the average
embedding of the language written about it: embed every document (GDELT headline, Wikipedia
paragraph), average within period, then average periods, and L2-normalize. Cosine similarity
between a celebrity vector and a brand vector is symmetric; directed retrieval shares come from
softmax normalization over the frozen candidate sets (measures.softmax_shares), with the
temperature tau = 1/20 that Sarkar uses in contrastive training.

Backends
--------
hash                 deterministic hashed bag of uni/bigrams (offline tests, no downloads)
st:<model-id>        any sentence-transformers model, e.g. st:suproteem/RepresentLM-v2 (Sarkar's
                     released encoder; base model trained on historical newspapers through 1979)
                     or st:BAAI/bge-base-en-v1.5 (a modern general-purpose encoder)

Document embeddings are cached by (backend, sha256(text)) in data/derived/assoc/emb_cache/.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import measures
from .config import DERIVED, Frame
from .sources import matcher

TAU = 1 / 20


def slug(backend: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", backend).strip("-").lower()


def hash_embed(texts: list[str], dim: int = 512) -> np.ndarray:
    out = np.zeros((len(texts), dim))
    for i, t in enumerate(texts):
        toks = re.findall(r"[a-z0-9']+", t.lower())
        for gram in toks + [a + " " + b for a, b in zip(toks, toks[1:])]:
            h = int(hashlib.md5(gram.encode()).hexdigest(), 16)
            out[i, h % dim] += 1.0 if (h >> 64) & 1 else -1.0
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norms, 1e-12)


class Encoder:
    def __init__(self, backend: str):
        self.backend = backend
        self.cache_dir = DERIVED / "emb_cache" / slug(backend)
        self._model = None

    def _encode(self, texts: list[str]) -> np.ndarray:
        if self.backend == "hash":
            return hash_embed(texts)
        if self.backend.startswith("st:"):
            if self._model is None:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.backend[3:])
            return np.asarray(self._model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False))
        raise ValueError(f"unknown backend {self.backend}")

    def encode(self, texts: list[str]) -> np.ndarray:
        keys = [hashlib.sha256(t.encode()).hexdigest() for t in texts]
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        todo = [i for i, k in enumerate(keys) if not (self.cache_dir / f"{k}.npy").exists()]
        for start in range(0, len(todo), 256):
            idx = todo[start:start + 256]
            vecs = self._encode([texts[i] for i in idx])
            for i, v in zip(idx, vecs):
                np.save(self.cache_dir / f"{keys[i]}.npy", v.astype(np.float32))
        return np.stack([np.load(self.cache_dir / f"{k}.npy") for k in keys]) if keys else np.zeros((0, 1))


def load_documents(frame: Frame, sources: tuple[str, ...] = ("gdelt", "wikipedia")) -> dict[str, list[dict]]:
    docs = defaultdict(list)
    for src in sources:
        path = DERIVED / f"documents_{src}.jsonl"
        if not path.exists():
            continue
        for line in path.open():
            d = json.loads(line)
            docs[d["entity"]].append(d)
    return docs


def mask_names(text: str, patterns: list[re.Pattern]) -> str:
    for p in patterns:
        text = p.sub("[NAME]", text)
    return text


def entity_vectors(frame: Frame, encoder: Encoder, sources=("gdelt", "wikipedia"), mask: bool = False,
                   log=print) -> tuple[dict[str, np.ndarray], dict[str, int]]:
    """Mean of period means of normalized document embeddings (Wikipedia paragraphs form their own period)."""
    docs = load_documents(frame, sources)
    pats = [matcher(e) for e in frame.entities] if mask else []
    vecs, n_docs = {}, {}
    for e in frame.entities:
        ds = docs.get(e.id, [])
        n_docs[e.id] = len(ds)
        if not ds:
            log(f"[embed] {e.id}: no documents")
            continue
        texts = [mask_names(d["text"], pats) if mask else d["text"] for d in ds]
        emb = encoder.encode(texts)
        periods = defaultdict(list)
        for d, v in zip(ds, emb):
            periods[(d["source"], d.get("period", 0))].append(v)
        v = np.mean([np.mean(vs, axis=0) for vs in periods.values()], axis=0)
        vecs[e.id] = v / max(np.linalg.norm(v), 1e-12)
    return vecs, n_docs


def run(frame: Frame, backend: str, mask: bool = False, tau: float = TAU, log=print) -> Path:
    enc = Encoder(backend)
    vecs, n_docs = entity_vectors(frame, enc, mask=mask, log=log)
    cs = [c for c in frame.celebrities if c.id in vecs]
    bs = [b for b in frame.brands if b.id in vecs]
    sim = measures.cosine_matrix(np.stack([vecs[c.id] for c in cs]), np.stack([vecs[b.id] for b in bs]))
    fwd, bwd = measures.softmax_shares(sim, tau)
    r_f, r_b = measures.ranks(sim)
    name = f"embed_{slug(backend)}" + ("_masked" if mask else "")
    path = DERIVED / f"directed_{name}.csv"
    with path.open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["celebrity", "brand", "fwd", "bwd", "cosine", "rank_fwd", "rank_bwd", "n_docs_c", "n_docs_b"])
        for i, c in enumerate(cs):
            for j, b in enumerate(bs):
                w.writerow([c.id, b.id, f"{fwd[i, j]:.6g}", f"{bwd[i, j]:.6g}", f"{sim[i, j]:.6f}", int(r_f[i, j]), int(r_b[i, j]),
                            n_docs[c.id], n_docs[b.id]])
    np.savez(DERIVED / f"vectors_{name}.npz", ids=np.array([e.id for e in cs + bs]),
             vectors=np.stack([vecs[e.id] for e in cs + bs]))
    log(f"[embed] {backend}: {len(cs)} celebrities x {len(bs)} brands -> {path.name}")
    return path
