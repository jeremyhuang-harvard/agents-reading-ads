#!/usr/bin/env python3
"""Open-ended association discovery pass on a stratified sample of competitor creatives.

Labels unique creatives (by SHA-256) with Sonnet via the logged-in Claude Code CLI
(`claude -p`), one creative per call, read-only tool access. The model sees only
neutral copies of the media (CD-xxx), never firm names or metadata. Results are
appended to results.jsonl as they arrive; reruns skip completed creatives.

Run with: uv run --with opencv-python-headless python src/discover_competitor_associations.py ...
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROMPT_VERSION = "competitor_discovery_prompt_v1.0.0"

PROMPT = """You are coding a French online sports-betting advertisement from Snapchat for an academic study of how advertisements create associations in memory.

Read the file(s): {files}
{video_note}
Describe only what is observable. Do not guess the advertiser from outside knowledge; report a brand only if it is visible or audible. Transcribe French text verbatim.

Return JSON only, no prose and no code fences, with exactly these keys:
{{
  "visible_text_verbatim": ["each distinct text element, verbatim, in reading order"],
  "text_english": "faithful English translation of all text",
  "scene_description": "2-4 sentences: setting, objects, layout, colours, photo vs graphic vs app screenshot",
  "people": "who appears (count, apparent age group, gender presentation, role e.g. fan, athlete, celebrity, friends), or 'none'",
  "entities": {{"sports": [], "competitions_or_events": [], "teams_or_national_sides": [], "named_athletes_or_celebrities": [], "brands_visible": []}},
  "offer": {{"present": false, "type": "e.g. welcome bonus, free bet, boosted odds, cashback, none", "amount_or_value": null, "odds_shown": [], "deadline_or_urgency": null}},
  "most_prominent_element": "the single element that dominates visually",
  "first_noticed_element": "what a viewer would most likely notice first",
  "payoff_depiction": "how winning or gains are depicted (amounts, multipliers, celebration), or 'none'",
  "risk_or_probability_information": "any odds-as-probability, risk, loss, or responsible-gambling content, or 'none'",
  "winning_scenario_shown": {{"present": false, "description": null}},
  "cues_linked_to_brand": [{{"cue": "a specific context the ad ties the brand to", "cue_type": "event | team | sport | time | place | social_setting | emotion | identity | activity | other", "evidence": "visible or audible basis"}}],
  "borrowed_meaning": [{{"domain": "a domain of meaning the ad borrows from (free text, e.g. fandom, expertise, friendship, national pride, luxury, humour)", "evidence": "basis"}}],
  "how_betting_is_framed": "what kind of activity the ad presents betting as (free text)",
  "intended_association": "one sentence: what the ad wants viewers to link the brand with",
  "tone": "a few words",
  "age_and_responsible_gambling_messages": "verbatim messages and how prominent they are, or 'none'",
  "coder_notes": "ambiguity or quality issues, or empty string"
}}"""

VIDEO_NOTE = ("These are {n} still frames sampled at roughly 10%, 50%, and 90% of a video ad, in order. "
              "Audio is not available; do not infer speech or music.")

_print_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def index_creatives(run_dir: Path, backfill_dir: Path | None) -> dict[str, dict]:
    """Map sha256 -> {firms, media_type, path} across the base run and Story backfill."""
    out: dict[str, dict] = {}

    def add(sha: str, firm: str, mtype: str | None, path: Path) -> None:
        kind = "VIDEO" if path.suffix.lower() in {".mp4", ".mov", ".webm"} else "IMAGE"
        rec = out.setdefault(sha, {"sha256": sha, "firms": set(), "media_type": kind, "path": path, "ads": 0})
        rec["firms"].add(firm)
        rec["ads"] += 1

    for line in (run_dir / "records.jsonl").open():
        r = json.loads(line)
        m = r.get("media")
        if m and m.get("sha256") and m.get("local_path"):
            add(m["sha256"], r["query_advertiser"].strip(), m.get("media_type", ""), run_dir / m["local_path"])
    if backfill_dir:
        for line in (backfill_dir / "records.jsonl").open():
            r = json.loads(line)
            if r.get("sha256") and r.get("local_path"):
                add(r["sha256"], r["query_advertiser"].strip(), r.get("media_type", ""), (backfill_dir / r["local_path"]).resolve())
    return out


def sample(creatives: dict[str, dict], per_firm: int, seed: int) -> list[dict]:
    by_firm: dict[str, list[dict]] = defaultdict(list)
    for c in creatives.values():
        if len(c["firms"]) == 1:
            by_firm[next(iter(c["firms"]))].append(c)
    rng = random.Random(seed)
    chosen = []
    for firm in sorted(by_firm):
        pool = sorted(by_firm[firm], key=lambda c: c["sha256"])
        chosen.extend(rng.sample(pool, min(per_firm, len(pool))))
    rng.shuffle(chosen)
    return chosen


def extract_frames(video: Path, dest_stem: Path, fractions=(0.1, 0.5, 0.9)) -> list[Path]:
    import cv2  # provided via `uv run --with opencv-python-headless`

    cap = cv2.VideoCapture(str(video))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    paths = []
    for i, f in enumerate(fractions, 1):
        if n > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(n - 1, int(n * f))))
        ok, frame = cap.read()
        if not ok:
            continue
        p = dest_stem.with_name(f"{dest_stem.name}_f{i}.jpg")
        cv2.imwrite(str(p), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        paths.append(p)
    cap.release()
    return paths


def build_packet(chosen: list[dict], out: Path) -> list[dict]:
    inputs = out / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    items = []
    for i, c in enumerate(chosen, 1):
        cid = f"CD-{i:03d}"
        src = Path(c["path"])
        if sha256_file(src) != c["sha256"]:
            raise SystemExit(f"checksum mismatch for {src}")
        if c["media_type"] == "VIDEO":
            files = extract_frames(src, inputs / cid)
            if not files:
                raise SystemExit(f"no frames extracted from {src}")
        else:
            dst = inputs / f"{cid}{src.suffix.lower()}"
            shutil.copyfile(src, dst)
            files = [dst]
        items.append({
            "coding_id": cid,
            "sha256": c["sha256"],
            "firm": next(iter(c["firms"])),
            "media_type": c["media_type"],
            "ads_using_creative": c["ads"],
            "input_files": [f.name for f in files],
            "input_sha256": {f.name: sha256_file(f) for f in files},
        })
    return items


def parse_json(text: str) -> dict:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in response")
    obj = json.loads(t[start:end + 1])
    required = re.findall(r'^  "([a-z_]+)":', PROMPT, flags=re.M)
    missing = [k for k in required if k not in obj]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    return obj


def code_one(item: dict, inputs: Path, model: str, timeout: int, attempts: int) -> dict:
    files = ", ".join(item["input_files"])
    note = VIDEO_NOTE.format(n=len(item["input_files"])) if item["media_type"] == "VIDEO" else ""
    prompt = PROMPT.format(files=files, video_note=note)
    last_err = None
    for attempt in range(1, attempts + 1):
        started = time.time()
        try:
            proc = subprocess.run(
                ["claude", "-p", prompt, "--model", model, "--allowedTools", "Read", "--output-format", "json"],
                cwd=inputs, capture_output=True, text=True, timeout=timeout,
            )
            envelope = json.loads(proc.stdout)
            if envelope.get("is_error"):
                raise RuntimeError(str(envelope.get("result"))[:300])
            raw = envelope.get("result", "")
            labels = parse_json(raw)
            return {
                "coding_id": item["coding_id"], "sha256": item["sha256"], "status": "ok",
                "labels": labels, "raw_response": raw,
                "model_alias": model, "model_usage": list((envelope.get("modelUsage") or {}).keys()),
                "cost_equivalent_usd": envelope.get("total_cost_usd"),
                "duration_s": round(time.time() - started, 1), "attempt": attempt,
                "prompt_version": PROMPT_VERSION, "coded_at_utc": utc_now(),
            }
        except Exception as exc:  # noqa: BLE001 - record and retry
            last_err = f"{type(exc).__name__}: {str(exc)[:300]}"
            if "usage limit" in last_err.lower() or "rate limit" in last_err.lower():
                time.sleep(min(600, 60 * attempt))
            else:
                time.sleep(5 * attempt)
    return {"coding_id": item["coding_id"], "sha256": item["sha256"], "status": "failed",
            "error": last_err, "prompt_version": PROMPT_VERSION, "coded_at_utc": utc_now()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--backfill-dir", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--per-firm", type=int, default=20)
    ap.add_argument("--seed", type=int, default=2026102101)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--parallelism", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--attempts", type=int, default=3)
    args = ap.parse_args()

    out = args.output_dir
    manifest_path = out / "sample_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        items = manifest["items"]
    else:
        creatives = index_creatives(args.run_dir, args.backfill_dir)
        items = build_packet(sample(creatives, args.per_firm, args.seed), out)
        manifest = {
            "created_at_utc": utc_now(), "prompt_version": PROMPT_VERSION,
            "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
            "seed": args.seed, "per_firm": args.per_firm, "model_alias": args.model,
            "source_run": str(args.run_dir), "backfill_run": str(args.backfill_dir),
            "unique_creatives_indexed": len(creatives),
            "video_protocol": "3 still frames at ~10/50/90%; no audio (exploratory only)",
            "items": items,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))

    results_path = out / "results.jsonl"
    done = set()
    if results_path.exists():
        for line in results_path.open():
            r = json.loads(line)
            if r.get("status") == "ok":
                done.add(r["coding_id"])
    todo = [it for it in items if it["coding_id"] not in done]
    print(f"{len(items)} creatives; {len(done)} already done; {len(todo)} to code", flush=True)

    ok = fail = 0
    with cf.ThreadPoolExecutor(max_workers=args.parallelism) as pool, results_path.open("a") as fh:
        futures = [pool.submit(code_one, it, out / "inputs", args.model, args.timeout, args.attempts) for it in todo]
        for n, fut in enumerate(cf.as_completed(futures), 1):
            res = fut.result()
            with _print_lock:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
                fh.flush()
                ok += res["status"] == "ok"
                fail += res["status"] != "ok"
                if n % 10 == 0 or n == len(todo):
                    print(f"{utc_now()[11:19]} coded {len(done) + ok}/{len(items)}, failed {fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
