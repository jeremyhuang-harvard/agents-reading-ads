"""Prefix-cache assessment for run_priming (decision memo support; never touches runs/).

Step 0: verify images + frame text are a token-level prefix shared by every question.
Step 1: profile the old (uncached) path on 3 feeds.
Step 3: equivalence audit, old vs cached, interleaved, on N stratified feeds; plus
        question-order permutation (contamination check) and old-vs-stored determinism.
All outputs: tmp/cache_eval/.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
import tomllib
from collections import defaultdict
from pathlib import Path

import mlx.core as mx
from mlx_vlm import load
from mlx_vlm.generate import stream_generate
from mlx_vlm.generate.common import PromptCacheState
from mlx_vlm.generate.dispatch import _prepare_generation_inputs
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from agentic_ads.priming_design import enumerate_feeds, prompt_for, questions_for, recode_rating  # noqa: E402
from agentic_ads.run_priming import MAX_SIDE, resized  # noqa: E402

OUT = ROOT / "tmp/cache_eval"
OUT.mkdir(parents=True, exist_ok=True)
LIVE = Path.home() / "agentic-ad-simulations/runs/batch2-beer-priming-9a960c96e6-20261021T194553Z"
N_AUDIT = int(sys.argv[1]) if len(sys.argv) > 1 else 20

cfg = tomllib.loads((ROOT / "config/batch2.toml").read_text())
man = json.loads((ROOT / cfg["study"]["stimuli_manifest"]).read_text())
QS = questions_for(cfg)
feeds = enumerate_feeds(cfg, man)
paths = {it["id"]: (ROOT / it["local"], k) for k, items in (("ad", man["ads"]), ("prime", man["primes"])) for it in items}

model_id = cfg["model"]["id"]
model, processor = load(model_id)
mcfg = load_config(model_id)
tok = processor.tokenizer


def images(feed):
    out = []
    for sid in feed.images:
        p, kind = paths[sid]
        out.append(str(resized(p, ROOT / "data/interim/stimuli_resized" / f"{sid}.jpg", MAX_SIDE[kind])))
    return out


def full_prompt(q, feed, n_img):
    text, opts = prompt_for(q, feed)
    return apply_chat_template(processor, mcfg, text, num_images=n_img), opts


# ---- one question, old or cached path (identical except prompt_cache_state) ----
def ask(q, feed, imgs, state=None):
    prompt, opts = full_prompt(q, feed, len(imgs))
    kw = dict(max_tokens=1 if q["kind"] != "text" else q["max_tokens"], temperature=0.0)
    if state is not None:
        kw["prompt_cache_state"] = state
    t0 = time.perf_counter()
    gen = stream_generate(model, processor, prompt, imgs, **kw)
    if q["kind"] == "text":
        res = list(gen)
        out = {"text": "".join(r.text for r in res).strip(),
               "token_ids": res[-1].token_ids if res and res[-1].token_ids else None}
        first = res[0]
    else:
        first = next(gen)
        lp = mx.array(first.logprobs).astype(mx.float32).reshape(-1)
        if state is not None:
            for _ in gen:  # cache state is only saved once the generator is exhausted
                pass
        lp = lp - mx.logsumexp(lp)
        ids = [tok.encode(o, add_special_tokens=False)[0] for o in opts]
        raw = [math.exp(lp[i].item()) for i in ids]
        mass = sum(raw)
        probs = {o: v / mass for o, v in zip(opts, raw)}
        if q["kind"] == "rating":
            probs = {str(recode_rating(d, feed.reversed_scales)): p for d, p in probs.items()}
        out = {"probs": dict(sorted(probs.items())), "valid_mass": mass,
               "top_token": tok.decode([int(mx.argmax(lp).item())])}
        if q["kind"] == "rating":
            out["mean"] = sum(int(k) * v for k, v in probs.items())
    out["secs"] = time.perf_counter() - t0
    out["prompt_tokens"] = first.prompt_tokens
    out["cached_tokens"] = first.cached_tokens
    out["prompt_tps"] = first.prompt_tps
    return out


def run_feed(feed, cached, order=None):
    imgs = images(feed)
    state = PromptCacheState() if cached else None
    qs = QS if order is None else [QS[i] for i in order]
    t0 = time.perf_counter()
    res = {q["id"]: ask(q, feed, imgs, state) for q in qs}
    return res, time.perf_counter() - t0


# ---------------- Step 0: prefix check ----------------
def step0():
    report = []
    for feed in [next(f for f in feeds if f.position == "ad_only"),
                 next(f for f in feeds if f.position == "before_k5" and f.ad_category == "beer"),
                 next(f for f in feeds if f.position == "ad_first" and f.ad_category == "control")]:
        imgs = images(feed)
        seqs = []
        for q in QS:
            prompt, _ = full_prompt(q, feed, len(imgs))
            ids, _, _, _ = _prepare_generation_inputs(model, processor, prompt, imgs, None, None, {})
            seqs.append(ids.flatten().tolist())
        common = min(next((i for i, (a, b) in enumerate(zip(s, seqs[0])) if a != b), min(len(s), len(seqs[0])))
                     for s in seqs[1:])
        img_tok = getattr(model.config, "image_token_id", None) or getattr(model.config, "image_token_index", None)
        last_img = max(i for i, t in enumerate(seqs[0]) if t == img_tok)
        tail = tok.decode(seqs[0][max(0, common - 25):common])
        per_q = []
        for q, s in zip(QS, seqs):
            per_q.append({"q": q["id"], "len": len(s), "suffix_tokens": len(s) - common,
                          "suffix_start": tok.decode(s[common:common + 8])})
        report.append({"feed": feed.feed_id, "position": feed.position, "n_images": len(imgs),
                       "common_prefix_tokens": common, "last_image_token_at": last_img,
                       "frame_inside_prefix": "ordinary posts" in tok.decode(seqs[0][:common]) or feed.position == "ad_only",
                       "prefix_tail": tail, "per_question": per_q})
    ok = all(r["common_prefix_tokens"] > r["last_image_token_at"] and r["frame_inside_prefix"] for r in report)
    (OUT / "step0_prefix.json").write_text(json.dumps({"ok": ok, "feeds": report}, indent=1))
    print("STEP0 ok =", ok, [(r["n_images"], r["common_prefix_tokens"], r["per_question"][0]["len"]) for r in report], flush=True)
    return ok


# ---------------- Step 1: profile old path ----------------
def step1(sample):
    rows = []
    enc = getattr(model, "encode_images", None) or getattr(model, "encode_image", None)
    for feed in sample:
        imgs = images(feed)
        prompt, _ = full_prompt(QS[0], feed, len(imgs))
        t = time.perf_counter()
        ids, pv, mask, extra = _prepare_generation_inputs(model, processor, prompt, imgs, None, None, {})
        prep = time.perf_counter() - t
        venc = None
        if enc is not None and pv is not None:
            try:
                t = time.perf_counter(); f = enc(pv, **({k: v for k, v in extra.items() if k == "image_grid_thw"} if isinstance(extra, dict) else {}))
                mx.eval(f); venc = time.perf_counter() - t
            except Exception as e:  # noqa: BLE001
                venc = f"n/a ({type(e).__name__})"
        res, total = run_feed(feed, cached=False)
        for qid, r in res.items():
            rows.append({"feed": feed.feed_id, "ad_category": feed.ad_category, "position": feed.position,
                         "n_images": len(imgs), "q": qid, "secs": r["secs"], "prompt_tokens": r["prompt_tokens"],
                         "ttft_s": r["prompt_tokens"] / r["prompt_tps"] if r["prompt_tps"] else None,
                         "preprocess_s": prep, "vision_encode_s": venc})
        print(f"STEP1 {feed.ad_category} {feed.position} total {total:.1f}s", flush=True)
    (OUT / "step1_profile.json").write_text(json.dumps(rows, indent=1))


# ---------------- Step 3: audit ----------------
def stratified(n):
    rng = random.Random(7)
    stored = set()
    if (LIVE / "responses.jsonl").exists():
        last = QS[-1]["id"]
        for line in (LIVE / "responses.jsonl").open():
            r = json.loads(line)
            if r["question_id"] == last:
                stored.add(r["feed_id"])
    by = defaultdict(list)
    for f in feeds:
        by[f.ad_category].append(f)
    quota = {"betting": n - 2 * (n // 3), "beer": n // 3, "control": n // 3}
    pick = []
    for cat, k in quota.items():
        pool = by[cat]
        if cat == "betting":  # prefer feeds already in the live run, so we can check determinism
            pool = [f for f in pool if f.feed_id in stored] or pool
        cells = defaultdict(list)
        for f in pool:
            cells[(f.prime_set, f.position)].append(f)
        keys = list(cells); rng.shuffle(keys)
        i = 0
        while len([p for p in pick if p.ad_category == cat]) < k:
            pick.append(rng.choice(cells[keys[i % len(keys)]])); i += 1
    return pick, stored


def step3(sample, stored):
    stored_rows = defaultdict(dict)
    if stored:
        for line in (LIVE / "responses.jsonl").open():
            r = json.loads(line)
            if r["feed_id"] in {f.feed_id for f in sample}:
                stored_rows[r["feed_id"]][r["question_id"]] = r
    with (OUT / "audit.jsonl").open("w") as h:
        for i, feed in enumerate(sample):
            order = ["old", "new"] if i % 2 == 0 else ["new", "old"]
            got = {}
            for path in order:
                got[path] = run_feed(feed, cached=(path == "new"))
            h.write(json.dumps({"feed": feed.feed_id, "ad_category": feed.ad_category, "prime_set": feed.prime_set,
                                "position": feed.position, "n_images": len(feed.images), "first": order[0],
                                "old": got["old"][0], "old_secs": got["old"][1],
                                "new": got["new"][0], "new_secs": got["new"][1],
                                "stored": stored_rows.get(feed.feed_id)}) + "\n")
            h.flush()
            print(f"AUDIT {i+1}/{len(sample)} {feed.ad_category} {feed.position} old {got['old'][1]:.1f}s new {got['new'][1]:.1f}s", flush=True)
    # contamination: same feed, cached path, reversed question order
    with (OUT / "order_check.jsonl").open("w") as h:
        for feed in sample[:4]:
            fwd, _ = run_feed(feed, cached=True)
            rev, _ = run_feed(feed, cached=True, order=list(range(len(QS)))[::-1])
            h.write(json.dumps({"feed": feed.feed_id, "fwd": fwd, "rev": rev}) + "\n"); h.flush()
            print(f"ORDER {feed.feed_id} done", flush=True)


if __name__ == "__main__":
    if not step0():
        print("STOP: images + frame are not a shared token prefix; see step0_prefix.json"); sys.exit(2)
    sample, stored = stratified(N_AUDIT)
    prof = [next(f for f in sample if f.ad_category == c) for c in ("betting", "beer", "control")]
    step1(prof)
    step3(sample, stored)
    print("DONE", flush=True)
