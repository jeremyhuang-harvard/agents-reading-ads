"""Pure functions for directed association measures.

Conventions: matrices are indexed [celebrity, brand] (shape C x B). For every measure we
return two C x B matrices:

    fwd[c, b] = P(b | cue c)   retrieval of brand b when the celebrity is the cue
    bwd[c, b] = P(c | cue b)   retrieval of celebrity c when the brand is the cue

Key identity (why asymmetry measures interference). If retrieval is competitive,
P(b | c) = S(c, b) / sum_b' S(c, b') and P(c | b) = S(c, b) / sum_c' S(c', b), with a symmetric
strength S, then

    log P(b | c) - log P(c | b) = log sum_c' S(c', b) - log sum_b' S(c, b')
                                = log Z_brand(b) - log Z_celebrity(c),

i.e. the asymmetry equals the difference in how crowded each cue is (the "fan" of associates
competing at that cue). Symmetric similarity plus competitive retrieval is enough to generate
"Tate -> Adidas is stronger than Adidas -> Tate" whenever Adidas has many more strong associates
among celebrities than Tate has among brands. With raw co-occurrence counts and the cue's total
volume as the denominator, Z is simply the cue's marginal count, so the asymmetry collapses to
log N(brand) - log N(celebrity): a pure size effect. Measures that normalize over a candidate set
(retrieval shares) replace size with interference from the candidates actually in memory.
"""

from __future__ import annotations

import numpy as np

EPS = 1e-12


def _logsumexp(x: np.ndarray, axis: int) -> np.ndarray:
    m = np.max(x, axis=axis, keepdims=True)
    return (m + np.log(np.sum(np.exp(x - m), axis=axis, keepdims=True))).squeeze(axis)


def softmax_shares(score: np.ndarray, tau: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Competitive retrieval from a symmetric score matrix (e.g. cosine similarity).

    Returns (fwd, bwd): row-softmax over brands and column-softmax over celebrities.
    """
    z = np.asarray(score, float) / tau
    fwd = np.exp(z - _logsumexp(z, axis=1)[:, None])
    bwd = np.exp(z - _logsumexp(z, axis=0)[None, :])
    return fwd, bwd


def crowding(score: np.ndarray, tau: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """log Z for each celebrity cue (over brands) and each brand cue (over celebrities)."""
    z = np.asarray(score, float) / tau
    return _logsumexp(z, axis=1), _logsumexp(z, axis=0)


def count_shares(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Competitive retrieval from a nonnegative co-occurrence matrix N[c, b].

    P(b | c) = N[c, b] / sum_b' N[c, b'],  P(c | b) = N[c, b] / sum_c' N[c', b].
    Rows/columns with zero total return 0.
    """
    n = np.asarray(counts, float)
    row = n.sum(axis=1, keepdims=True)
    col = n.sum(axis=0, keepdims=True)
    fwd = np.divide(n, row, out=np.zeros_like(n), where=row > 0)
    bwd = np.divide(n, col, out=np.zeros_like(n), where=col > 0)
    return fwd, bwd


def conditional_from_marginals(n_c: np.ndarray, n_b: np.ndarray, n_cb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """P(b | c) = N(c and b) / N(c),  P(c | b) = N(c and b) / N(b) (cue's total volume as denominator)."""
    n_c = np.asarray(n_c, float)[:, None]
    n_b = np.asarray(n_b, float)[None, :]
    n_cb = np.asarray(n_cb, float)
    fwd = np.divide(n_cb, n_c, out=np.zeros_like(n_cb), where=n_c > 0)
    bwd = np.divide(n_cb, n_b, out=np.zeros_like(n_cb), where=n_b > 0)
    return fwd, bwd


def asymmetry(fwd: np.ndarray, bwd: np.ndarray, floor: float | None = None) -> np.ndarray:
    """log fwd - log bwd. Cells where either side is zero (below `floor`) are NaN unless a floor is given."""
    fwd = np.asarray(fwd, float)
    bwd = np.asarray(bwd, float)
    if floor is not None:
        return np.log(np.maximum(fwd, floor)) - np.log(np.maximum(bwd, floor))
    out = np.full(fwd.shape, np.nan)
    ok = (fwd > 0) & (bwd > 0)
    out[ok] = np.log(fwd[ok]) - np.log(bwd[ok])
    return out


def ranks(score: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rank of b among c's brands (1 = strongest) and rank of c among b's celebrities. Ties share the best rank."""
    s = np.asarray(score, float)
    fwd = 1 + (s[:, None, :] > s[:, :, None]).sum(axis=2)  # brands beating b for cue c
    bwd = 1 + (s[None, :, :] > s[:, None, :]).sum(axis=1)  # celebrities beating c for cue b
    return fwd.astype(float), bwd.astype(float)


def rank_asymmetry(score: np.ndarray) -> np.ndarray:
    """Positive when b ranks higher (closer to 1) among c's brands than c ranks among b's celebrities,
    after scaling ranks by candidate-set size so C and B are comparable: log(r_bwd / n_C) - log(r_fwd / n_B)."""
    rf, rb = ranks(score)
    n_c, n_b = np.asarray(score).shape
    return np.log(rb / n_c) - np.log(rf / n_b)


def cosine_matrix(x_c: np.ndarray, x_b: np.ndarray) -> np.ndarray:
    a = np.asarray(x_c, float)
    b = np.asarray(x_b, float)
    a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), EPS)
    b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), EPS)
    return a @ b.T


def pmi_adjust(logp_given_cue: np.ndarray, logp_prior: np.ndarray, axis: int) -> np.ndarray:
    """Subtract each target's unconditional log probability (popularity prior) to isolate association."""
    prior = np.asarray(logp_prior, float)
    return np.asarray(logp_given_cue, float) - (prior[None, :] if axis == 1 else prior[:, None])
