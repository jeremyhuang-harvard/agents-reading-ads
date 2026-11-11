"""Feasibility probe: Qwen3-VL-8B-4bit on this Mac with 1 ad + N prime images."""
import json, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

OUT = Path(__file__).parent / "vlm_probe_imgs"; OUT.mkdir(exist_ok=True)

def card(name, bg, lines, size=(512, 512)):
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except Exception: f = ImageFont.load_default()
    y = 60
    for ln in lines:
        d.text((30, y), ln, fill="white", font=f); y += 70
    p = OUT / f"{name}.png"; im.save(p); return str(p)

ad = card("ad", (20, 90, 40), ["BETNOW", "Bet £10,", "get £30", "in free bets", "18+ T&Cs apply"])
win = [card(f"win{i}", (180, 140, 0), ["JACKPOT!", f"Winner #{i}", "takes home", "£25,000"]) for i in range(5)]
neutral = [card(f"neu{i}", (60, 60, 120), ["Weather", f"Day {i}:", "light rain,", "14°C"]) for i in range(5)]

MODEL = "mlx-community/Qwen3-VL-8B-Instruct-4bit"
t0 = time.time(); model, processor = load(MODEL); config = load_config(MODEL)
print(f"load_s={time.time()-t0:.1f} mem_after_load_GB={mx.get_active_memory()/1e9:.2f}", flush=True)

Q = ("The LAST image is an advertisement. The images before it are other things you saw "
     "while scrolling. In one sentence: what is the ad offering? Then answer: on a 1-7 scale, "
     "how appealing is the ad to you? Reply as JSON {\"offer\":...,\"appeal\":n}.")

def run(images, label):
    prompt = apply_chat_template(processor, config, Q, num_images=len(images))
    mx.reset_peak_memory(); t = time.time()
    r = generate(model, processor, prompt, images, max_tokens=80, temperature=0.0, verbose=False)
    text = getattr(r, "text", r)
    print(json.dumps({"cond": label, "n_images": len(images), "secs": round(time.time()-t, 1),
                      "peak_GB": round(mx.get_peak_memory()/1e9, 2), "out": text.strip()}), flush=True)

run([ad], "ad_only")
run(neutral + [ad], "5_neutral_then_ad")
run(win + [ad], "5_win_then_ad")
