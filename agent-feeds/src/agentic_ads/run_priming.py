"""Run batch-1 image-priming feeds on a local MLX vision-language model.

Usage:
    uv run --extra vlm python -m agentic_ads.run_priming --config config/batch1.toml [--limit N] [--resume RUN_DIR]

Outputs go to runs/<study-id>-<commit>-<utc>/:
    feeds.jsonl       one row per feed (design cell, image order)
    responses.jsonl   one row per feed x question (probabilities or text)
    manifest.json     provenance: git commit, model revision, package versions, input hashes, timing
Rows are appended as each feed finishes, so an interrupted run can be resumed.
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.metadata as md
import json
import math
import platform
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from .priming_design import enumerate_feeds, prompt_for, questions_for, recode_rating
from .provenance import capture_git_provenance, sha256_file

ROOT = Path(__file__).resolve().parents[2]
MAX_SIDE = {"ad": 768, "prime": 448}


def resized(src: Path, dst: Path, max_side: int) -> Path:
    from PIL import Image
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src).convert("RGB")
        im.thumbnail((max_side, max_side))
        im.save(dst, quality=92)
    return dst


def main(argv: list[str] | None = None) -> Path:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--limit", type=int, default=None, help="run only the first N feeds (pilot)")
    ap.add_argument("--resume", default=None)
    ap.add_argument("--allow-dirty", action="store_true")
    args = ap.parse_args(argv)

    cfg_path = (ROOT / args.config).resolve()
    cfg = tomllib.loads(cfg_path.read_text())
    man_path = ROOT / cfg["study"]["stimuli_manifest"]
    manifest = json.loads(man_path.read_text())
    stim_root = ROOT / cfg["study"]["stimuli_root"]

    git = capture_git_provenance(ROOT)
    if git["git_dirty"] and not args.allow_dirty:
        sys.exit("Refusing to run from a dirty working tree (commit first, or pass --allow-dirty for a non-reproducible test).")

    # Verify every stimulus against its recorded checksum before touching the model.
    paths: dict[str, tuple[Path, str]] = {}
    for kind, items in (("ad", manifest["ads"]), ("prime", manifest["primes"])):
        for it in items:
            p = ROOT / it["local"]
            if sha256_file(p) != it["sha256"]:
                sys.exit(f"Checksum mismatch for {it['id']}: {p}")
            paths[it["id"]] = (p, kind)

    feeds = enumerate_feeds(cfg, manifest)
    QUESTIONS = questions_for(cfg)
    if args.limit:
        feeds = feeds[: args.limit]

    if args.resume:
        run_dir = Path(args.resume).resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = ROOT / cfg["study"]["output_root"] / f"{cfg['study']['id']}-{(git['git_commit'] or 'nogit')[:10]}-{stamp}"
        run_dir.mkdir(parents=True, exist_ok=False)
    feeds_f, resp_f = run_dir / "feeds.jsonl", run_dir / "responses.jsonl"
    done = set()
    if resp_f.exists():
        for line in resp_f.open():
            r = json.loads(line)
            if r["question_id"] == QUESTIONS[-1]["id"]:
                done.add(r["feed_id"])

    import mlx.core as mx
    from huggingface_hub import snapshot_download
    from mlx_vlm import load
    from mlx_vlm.generate import stream_generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config

    model_id = cfg["model"]["id"]
    snap = Path(snapshot_download(model_id))
    model, processor = load(model_id)
    mcfg = load_config(model_id)
    tok = processor.tokenizer

    def image_list(feed) -> list[str]:
        out = []
        for sid in feed.images:
            p, kind = paths[sid]
            out.append(str(resized(p, ROOT / "data/interim/stimuli_resized" / f"{sid}.jpg", MAX_SIDE[kind])))
        return out

    def score(prompt: str, imgs: list[str], opts: list[str]) -> dict:
        full = apply_chat_template(processor, mcfg, prompt, num_images=len(imgs))
        for r in stream_generate(model, processor, full, imgs, max_tokens=1, temperature=0.0):
            lp = mx.array(r.logprobs).astype(mx.float32).reshape(-1)
            break
        lp = lp - mx.logsumexp(lp)  # renormalise in float32
        ids = [tok.encode(o, add_special_tokens=False)[0] for o in opts]
        raw = [math.exp(lp[i].item()) for i in ids]
        mass = sum(raw)
        top = int(mx.argmax(lp).item())
        return {"probs": {o: v / mass for o, v in zip(opts, raw)}, "valid_mass": mass,
                "top_token": tok.decode([top])}

    def text(prompt: str, imgs: list[str], max_tokens: int) -> str:
        full = apply_chat_template(processor, mcfg, prompt, num_images=len(imgs))
        return "".join(r.text for r in stream_generate(model, processor, full, imgs,
                                                       max_tokens=max_tokens, temperature=0.0)).strip()

    started = time.time()
    todo = [f for f in feeds if f.feed_id not in done]
    print(f"run_dir={run_dir}\nfeeds total={len(feeds)} remaining={len(todo)}", flush=True)
    with feeds_f.open("a") as ff, resp_f.open("a") as rf:
        for n, feed in enumerate(todo, 1):
            t0 = time.time()
            imgs = image_list(feed)
            ff.write(json.dumps(dataclasses.asdict(feed)) + "\n")
            for q in QUESTIONS:
                prompt, opts = prompt_for(q, feed)
                row = {"feed_id": feed.feed_id, "question_id": q["id"], "layer": q["layer"],
                       "kind": q["kind"], "prompt": prompt}
                if q["kind"] == "rating":
                    s = score(prompt, imgs, opts)
                    probs = {str(recode_rating(d, feed.reversed_scales)): p for d, p in s["probs"].items()}
                    row.update(probs=dict(sorted(probs.items())), valid_mass=s["valid_mass"],
                               top_token=s["top_token"],
                               mean=sum(int(k) * v for k, v in probs.items()))
                elif q["kind"] == "choice":
                    s = score(prompt, imgs, opts)
                    row.update(probs=s["probs"], valid_mass=s["valid_mass"], top_token=s["top_token"],
                               p_A=s["probs"]["A"])
                else:
                    row["text"] = text(prompt, imgs, q["max_tokens"])
                rf.write(json.dumps(row, ensure_ascii=False) + "\n")
            rf.flush(); ff.flush()
            el = time.time() - started
            print(f"[{n}/{len(todo)}] {feed.ad_id} {feed.prime_set} {feed.position} d{feed.draw} "
                  f"{time.time()-t0:.1f}s  eta {el/n*(len(todo)-n)/60:.0f} min", flush=True)

    out = {
        "run_dir": str(run_dir.relative_to(ROOT)), **git, "allow_dirty": args.allow_dirty,
        "finished_utc": datetime.now(timezone.utc).isoformat(), "runtime_seconds": time.time() - started,
        "n_feeds": len(feeds), "limit": args.limit,
        "model_id": model_id, "model_revision": snap.name,
        "packages": {p: md.version(p) for p in ("mlx", "mlx-vlm", "transformers", "torch")},
        "python": sys.version, "platform": platform.platform(),
        "config": {"path": args.config, "sha256": sha256_file(cfg_path)},
        "stimuli_manifest": {"path": str(man_path.relative_to(ROOT)), "sha256": sha256_file(man_path)},
        "resize_max_side": MAX_SIDE, "decoding": {"temperature": 0.0},
        "outputs": {p.name: sha256_file(p) for p in (feeds_f, resp_f)},
    }
    (run_dir / "manifest.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"done: {run_dir}", flush=True)
    return run_dir


if __name__ == "__main__":
    main()
