"""Free association from a local language model (open vocabulary, like human association norms).

Human associative strength is measured by free association: show a cue, record what people name,
and FSA(cue -> target) = share of participants who produce the target (Nelson et al. 2004; Small
World of Words, De Deyne et al. 2019). Here the "participants" are independent samples from a local
LM (temperature 1). Each sample lists up to 10 associates of the cue, and

    fwd(c, b) = share of celebrity-c samples whose list names brand b
    bwd(c, b) = share of brand-b samples whose list names celebrity c

Nothing restricts the model to the candidate set, so the measure says whether Adidas is part of
what Tate McRae is (and what else is), not just whether Adidas beats Nike in a forced choice.
A rank-weighted version (mean 1/rank, 0 if absent) is also stored. Every raw sample is kept in
data/raw/assoc/freeassoc/<model>.jsonl (append-only, resumable).

Label: model_predicted. Knowledge cutoff caveat as in llm.py.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict

from .config import DERIVED, RAW, Frame
from .sources import matcher

PROMPT = ("Free association task. Write the first {k} things that come to mind when you think of \"{cue}\" "
          "(people, brands, products, places, words). One per line, no numbering, no explanations.")


def parse(text: str, k: int = 10) -> list[str]:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    items = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip().strip('"').strip()
        if line and len(line) <= 60:
            items.append(line)
    return items[:k]


def strengths(samples: dict[str, list[list[str]]], frame: Frame) -> list[dict]:
    pats = {e.id: matcher(e) for e in frame.entities}
    def stats(cue, tgt):
        lists = samples.get(cue, [])
        if not lists:
            return None, None
        hits, rr = 0, 0.0
        for items in lists:
            ranks = [i + 1 for i, it in enumerate(items) if pats[tgt].search(it)]
            if ranks:
                hits += 1
                rr += 1 / ranks[0]
        return hits / len(lists), rr / len(lists)
    rows = []
    for c in frame.celebrities:
        for b in frame.brands:
            f, fr = stats(c.id, b.id)
            g, gr = stats(b.id, c.id)
            rows.append({"celebrity": c.id, "brand": b.id, "fwd": "" if f is None else f"{f:.4f}", "bwd": "" if g is None else f"{g:.4f}",
                         "fwd_rr": "" if fr is None else f"{fr:.4f}", "bwd_rr": "" if gr is None else f"{gr:.4f}",
                         "n_fwd": len(samples.get(c.id, [])), "n_bwd": len(samples.get(b.id, []))})
    return rows


def run(frame: Frame, model_id: str, n: int = 20, k: int = 10, temp: float = 1.0, log=print) -> None:
    import mlx.core as mx
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    slug = re.sub(r"[^A-Za-z0-9]+", "-", model_id.split("/")[-1]).lower()
    raw = RAW / "freeassoc" / f"{slug}.jsonl"
    raw.parent.mkdir(parents=True, exist_ok=True)
    done = defaultdict(int)
    if raw.exists():
        for line in raw.open():
            r = json.loads(line)
            done[r["cue"]] += 1
    model, tok = load(model_id)
    sampler = make_sampler(temp=temp, top_p=0.95)
    with raw.open("a") as h:
        for e in frame.entities:
            for s in range(done[e.id], n):
                mx.random.seed(10_000 + s)
                msgs = [{"role": "user", "content": PROMPT.format(k=k, cue=e.name)}]
                prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)
                text = generate(model, tok, prompt=prompt, max_tokens=160, sampler=sampler, verbose=False)
                h.write(json.dumps({"cue": e.id, "cue_name": e.name, "sample": s, "seed": 10_000 + s, "temp": temp,
                                    "model": model_id, "prompt": PROMPT, "text": text}, ensure_ascii=False) + "\n")
                h.flush()
            log(f"[freeassoc] {e.id}: {n} samples")
    summarize(frame, slug, k, log)


def summarize(frame: Frame, slug: str, k: int = 10, log=print) -> None:
    raw = RAW / "freeassoc" / f"{slug}.jsonl"
    samples = defaultdict(list)
    for line in raw.open():
        r = json.loads(line)
        samples[r["cue"]].append(parse(r["text"], k))
    rows = strengths(samples, frame)
    with (DERIVED / f"directed_freeassoc_{slug}.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # What each cue's association list is made of (open vocabulary).
    with (DERIVED / f"freeassoc_{slug}_top.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["cue", "response", "share_of_samples"])
        for cue, lists in samples.items():
            cnt = Counter(it.casefold() for items in lists for it in set(items))
            for resp, c in cnt.most_common(15):
                w.writerow([cue, resp, f"{c / len(lists):.3f}"])
    log(f"[freeassoc] wrote directed_freeassoc_{slug}.csv ({sum(len(v) for v in samples.values())} samples)")
