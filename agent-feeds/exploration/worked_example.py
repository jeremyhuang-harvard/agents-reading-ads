"""Worked example: what one cell of the design produces, Instruct vs Thinking.

Conditions: ad alone vs 5 jackpot cards -> ad (synthetic stimuli).
Instruct: probabilities read directly; separate think-aloud trail.
Thinking: model reasons natively, then we read the answer distribution
right after its reasoning closes.
"""
import json, sys, time
from pathlib import Path
import mlx.core as mx
from mlx_vlm import load
from mlx_vlm.generate import stream_generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

IMG = Path(__file__).parent / "vlm_probe_imgs"
which = sys.argv[1]  # instruct | thinking
MODEL = f"mlx-community/Qwen3-VL-8B-{'Instruct' if which == 'instruct' else 'Thinking'}-4bit"
model, processor = load(MODEL); config = load_config(MODEL)
tok = processor.tokenizer

FRAME = ("You are scrolling a social media feed. The images are what you saw, in order. "
         "The LAST image is an advertisement. ")
ad = str(IMG / "ad.png")
CONDS = {"ad_only": [ad], "jackpot5_ad": [str(IMG / f"win{i}.png") for i in range(5)] + [ad]}

Q = {
  "salient": ("Which part of the ad stood out to you most? Answer with one letter.\n"
              "A) The bonus amount\nB) The brand name\nC) The green colour\nD) The 18+ / T&Cs line", list("ABCD")),
  "chance_ahead": ("How likely is it that someone who takes this offer ends up ahead? "
                   "Answer with one number from 1 (very unlikely) to 5 (very likely).", list("12345")),
  "appeal": ("How appealing is this ad to you? Answer with one number from 1 (not at all) to 5 (very).", list("12345")),
  "money": ("Choose one. Answer with one letter.\nA) Claim this offer (deposit £10, get £30 in free bets)\n"
            "B) Receive £5 in cash instead", list("AB")),
}

def next_dist(prompt, images, opts):
    ids = {o: tok.encode(o, add_special_tokens=False)[0] for o in opts}
    for r in stream_generate(model, processor, prompt, images, max_tokens=1, temperature=0.0):
        lp = mx.array(r.logprobs).astype(mx.float32).reshape(-1); break
    sel = mx.array([lp[i].item() for i in ids.values()])
    p = mx.softmax(sel).tolist()
    mass = float(mx.exp(sel).sum())
    return {o: round(v, 3) for o, v in zip(opts, p)}, round(mass, 3)

def gen(prompt, images, max_tokens):
    out = ""
    for r in stream_generate(model, processor, prompt, images, max_tokens=max_tokens, temperature=0.0):
        out += r.text
    return out

rows = []
for cname, imgs in CONDS.items():
    row = {"model": which, "cond": cname}
    for k, (q, opts) in Q.items():
        base = apply_chat_template(processor, config, FRAME + q, num_images=len(imgs))
        if which == "instruct":
            row[k] = next_dist(base, imgs, opts)
        else:
            trace = gen(base, imgs, 900)
            cut = trace.find("</think>")
            thought = trace[:cut] if cut >= 0 else trace
            p, mass = next_dist(base + thought + "</think>\n\n", imgs, opts)
            row[k] = (p, mass)
            row[k + "_trace"] = thought.replace("<think>", "").strip()
            row[k + "_trace_closed"] = cut >= 0
    if which == "instruct":
        base = apply_chat_template(processor, config,
               FRAME + "In two or three sentences, think out loud about your reaction to the ad as you see it in this feed.",
               num_images=len(imgs))
        row["trail"] = gen(base, imgs, 120).strip()
    rows.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)

Path(__file__).with_name(f"worked_example_{which}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
