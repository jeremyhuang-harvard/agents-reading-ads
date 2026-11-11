"""Directed retrieval probabilities from a local language model.

A language model trained on a large web corpus is used as a *model* of the culture's associative
memory (label: model_predicted). For a celebrity cue we score how likely the model is to complete a
prompt with each candidate brand, and normalize over the frozen brand set:

    P_LM(b | c) = exp(log p(" b" | prompt(c))) / sum_b' exp(log p(" b'" | prompt(c)))

and symmetrically for brand cues over the celebrity set. Several paraphrased templates are averaged
in log space. A "prior" template with no cue ("Name a brand.") gives each candidate's popularity,
so PMI-style associations (log P(b|c) - log P_prior(b)) can be separated from sheer familiarity.

Caveat: the model's knowledge has a training cutoff (Qwen3: early 2025). Deals announced after the
cutoff are measured *before* the deal reached the training corpus, which makes those pairs a useful
pre-period baseline rather than a measure of the ambassadorship itself.
"""

from __future__ import annotations

import csv
import json
import re
from typing import Callable

import numpy as np

from .config import DERIVED, Frame

DEFAULT_MODEL = "mlx-community/Qwen3-8B-4bit"

FORWARD = [  # cue: celebrity, candidates: brands
    "Question: Which brand do you most associate with {cue}?\nAnswer:",
    "When people think of {cue}, the first brand that comes to mind is",
    "{cue} has a well-known partnership with the brand",
]
BACKWARD = [  # cue: brand, candidates: celebrities
    "Question: Which celebrity do you most associate with the brand {cue}?\nAnswer:",
    "When people think of {cue}, the first celebrity that comes to mind is",
    "{cue} has a well-known partnership with the celebrity",
]
PRIOR = {"brand": "Question: Name a brand.\nAnswer:", "celebrity": "Question: Name a celebrity.\nAnswer:"}

# logprob_fn(prompt, [continuations]) -> list of total log probabilities of each continuation
LogprobFn = Callable[[str, list[str]], list[float]]


def mlx_logprob_fn(model_id: str = DEFAULT_MODEL) -> LogprobFn:
    import mlx.core as mx
    from mlx_lm import load

    model, tok = load(model_id)

    def fn(prompt: str, conts: list[str]) -> list[float]:
        # One unpadded sequence per candidate: padded batches with the 4-bit kernels shifted
        # scores by up to ~0.4 nats in testing, so exactness is preferred over speed here.
        p_ids = tok.encode(prompt, add_special_tokens=False)
        out = []
        for cont in conts:
            c = tok.encode(cont, add_special_tokens=False)
            logits = model(mx.array([p_ids + c])).astype(mx.float32)
            logp = np.array(logits - mx.logsumexp(logits, axis=-1, keepdims=True))[0]
            pos = np.arange(len(p_ids) - 1, len(p_ids) - 1 + len(c))
            out.append(float(logp[pos, c].sum()))
        return out

    return fn


def _log_softmax(x: np.ndarray) -> np.ndarray:
    m = x.max()
    return x - (m + np.log(np.exp(x - m).sum()))


def directed(frame: Frame, logprob: LogprobFn, log=print) -> dict:
    """Returns log-share matrices [celebrity, brand] per template, their means, and priors."""
    cs, bs = frame.celebrities, frame.brands
    b_conts = [" " + b.name for b in bs]
    c_conts = [" " + c.name for c in cs]
    fwd_t = np.zeros((len(FORWARD), len(cs), len(bs)))
    bwd_t = np.zeros((len(BACKWARD), len(cs), len(bs)))
    raw_f = np.zeros_like(fwd_t)
    raw_b = np.zeros_like(bwd_t)
    for k, tmpl in enumerate(FORWARD):
        for i, c in enumerate(cs):
            lp = np.array(logprob(tmpl.format(cue=c.name), b_conts))
            raw_f[k, i] = lp
            fwd_t[k, i] = _log_softmax(lp)
        log(f"[llm] forward template {k + 1}/{len(FORWARD)} done")
    for k, tmpl in enumerate(BACKWARD):
        for j, b in enumerate(bs):
            lp = np.array(logprob(tmpl.format(cue=b.name), c_conts))
            raw_b[k, :, j] = lp
            bwd_t[k, :, j] = _log_softmax(lp)
        log(f"[llm] backward template {k + 1}/{len(BACKWARD)} done")
    prior_b = _log_softmax(np.array(logprob(PRIOR["brand"], b_conts)))
    prior_c = _log_softmax(np.array(logprob(PRIOR["celebrity"], c_conts)))
    # Average templates in log space, then renormalize within each cue.
    fwd = np.apply_along_axis(_log_softmax, 1, fwd_t.mean(axis=0))
    bwd = np.apply_along_axis(_log_softmax, 0, bwd_t.mean(axis=0))
    return {"log_fwd": fwd, "log_bwd": bwd, "log_fwd_t": fwd_t, "log_bwd_t": bwd_t, "raw_fwd": raw_f, "raw_bwd": raw_b,
            "log_prior_b": prior_b, "log_prior_c": prior_c}


def run(frame: Frame, model_id: str = DEFAULT_MODEL, logprob: LogprobFn | None = None, log=print) -> None:
    logprob = logprob or mlx_logprob_fn(model_id)
    res = directed(frame, logprob, log)
    name = "llm_" + re.sub(r"[^A-Za-z0-9]+", "-", model_id.split("/")[-1]).lower()
    DERIVED.mkdir(parents=True, exist_ok=True)
    np.savez(DERIVED / f"{name}.npz", **res, celebrities=[c.id for c in frame.celebrities], brands=[b.id for b in frame.brands])
    with (DERIVED / f"directed_{name}.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["celebrity", "brand", "fwd", "bwd", "pmi_fwd", "pmi_bwd", "template_sd_asym"])
        asym_t = res["log_fwd_t"] - res["log_bwd_t"]
        for i, c in enumerate(frame.celebrities):
            for j, b in enumerate(frame.brands):
                lf, lb = res["log_fwd"][i, j], res["log_bwd"][i, j]
                w.writerow([c.id, b.id, f"{np.exp(lf):.6g}", f"{np.exp(lb):.6g}", f"{lf - res['log_prior_b'][j]:.4f}",
                            f"{lb - res['log_prior_c'][i]:.4f}", f"{asym_t[:, i, j].std():.4f}"])
    (DERIVED / f"{name}.meta.json").write_text(json.dumps({"model": model_id, "forward": FORWARD, "backward": BACKWARD,
                                                           "prior": PRIOR, "label": "model_predicted"}, indent=2))
    log(f"[llm] wrote directed_{name}.csv")
