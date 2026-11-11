"""Probe the outcome protocol on Qwen3-VL-8B-Instruct-4bit.

1. Closed-ended ratings read as full probability distributions (no sampling,
   no written reasoning before the answer).
2. Binary choices (click / take offer) read the same way.
3. A free-text trail generated AFTER the choices, as a separate call, so it
   cannot change them.
"""
import json, time
from pathlib import Path
import mlx.core as mx
from mlx_vlm import load
from mlx_vlm.generate import stream_generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

IMG = Path(__file__).parent / "vlm_probe_imgs"
MODEL = "mlx-community/Qwen3-VL-8B-Instruct-4bit"
model, processor = load(MODEL); config = load_config(MODEL)
tok = processor.tokenizer if hasattr(processor, "tokenizer") else processor

FRAME = ("You are scrolling a social media feed. The images are what you saw, in order. "
         "The LAST image is an advertisement. ")

def option_ids(opts):
    ids = {}
    for o in opts:
        t = tok.encode(o, add_special_tokens=False)
        ids[o] = t[0]
    return ids

def dist(images, question, opts, prefix=""):
    prompt = apply_chat_template(processor, config, FRAME + question, num_images=len(images))
    prompt = prompt + prefix
    ids = option_ids(opts)
    for r in stream_generate(model, processor, prompt, images, max_tokens=1, temperature=0.0):
        lp = r.logprobs
        break
    lp = mx.array(lp).reshape(-1)
    raw = {o: float(mx.exp(lp[i])) for o, i in ids.items()}
    mass = sum(raw.values())
    p = {o: v / mass for o, v in raw.items()}
    return p, mass

def text(images, question, max_tokens=120):
    prompt = apply_chat_template(processor, config, FRAME + question, num_images=len(images))
    out = ""
    for r in stream_generate(model, processor, prompt, images, max_tokens=max_tokens, temperature=0.0):
        out += r.text
    return out.strip()

ad = str(IMG / "ad.png")
conds = {
    "ad_only": [ad],
    "neutral5_ad": [str(IMG / f"neu{i}.png") for i in range(5)] + [ad],
    "win5_ad": [str(IMG / f"win{i}.png") for i in range(5)] + [ad],
}
L5 = ["1", "2", "3", "4", "5"]
RATINGS = {
    "appeal": "How appealing is this ad to you? Answer with one number from 1 (not at all) to 5 (very).",
    "perceived_odds": "How likely do you think it is that someone who takes this offer ends up ahead? 1 (very unlikely) to 5 (very likely). One number.",
    "risk": "How risky does this offer seem? 1 (not risky) to 5 (very risky). One number.",
}
CHOICE = ("Would you tap the ad to claim the offer? Answer A or B.\nA) Tap to claim\nB) Keep scrolling", ["A", "B"])

for name, imgs in conds.items():
    t = time.time(); row = {"cond": name}
    for k, q in RATINGS.items():
        p, mass = dist(imgs, q, L5)
        row[k] = {"mean": round(sum(int(o) * v for o, v in p.items()), 3),
                  "p": {o: round(v, 3) for o, v in p.items()}, "mass": round(mass, 3)}
    p, mass = dist(imgs, CHOICE[0], CHOICE[1])
    row["p_tap"] = round(p["A"], 3); row["tap_mass"] = round(mass, 3)
    row["trail"] = text(imgs, "In two or three sentences, think out loud about your reaction to the ad as you see it in this feed.")
    row["secs"] = round(time.time() - t, 1)
    print(json.dumps(row, ensure_ascii=False), flush=True)
