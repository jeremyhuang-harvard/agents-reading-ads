#!/usr/bin/env python3
"""Label every unique competitor creative with the frozen association codebook.

Stage 1 (local, free): extract frames and transcribe audio for each video with mlx-whisper.
Stage 2 (Sonnet via the logged-in Claude Code CLI): one call per creative, Read-only tool access,
neutral IDs (LC-xxxx), no firm or metadata. Each response is validated against the codebook and
appended to results.jsonl; reruns skip completed creatives. Usage-limit errors pause and retry.

Run with:
  uv run --with opencv-python-headless --with mlx-whisper --with av \
    python src/label_competitor_creatives.py --run-dir ... --backfill-dir ... --output-dir ...
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_competitor_associations import extract_frames, index_creatives, sha256_file, utc_now  # noqa: E402

PROMPT_VERSION = "competitor_label_prompt_v1.0.0"
FRAME_FRACTIONS = (0.05, 0.25, 0.5, 0.75, 0.95)
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"
_lock = threading.Lock()


def build_prompt(cb: dict) -> str:
    cats = "\n".join(f'- "{c["name"]}": {c["definition"]}' for c in cb["borrowed_meaning_categories"])
    scale = "; ".join(f"{k} = {v}" for k, v in cb["prominence_scale"].items())
    regs = []
    for f in cb["regulatory_fields"]:
        line = f'- "{f["name"]}" ({f["type"]}): {f["definition"]}'
        if f.get("anchors"):
            line += " Anchors: " + "; ".join(f"{k} = {v}" for k, v in f["anchors"].items())
        regs.append(line)
    e = cb["enums"]
    cat_obj = ", ".join(f'"{c["name"]}": {{"prominence": 0, "evidence": ""}}' for c in cb["borrowed_meaning_categories"])
    reg_obj = ", ".join(f'"{f["name"]}": {{"value": null, "evidence": "", "unknown_reason": null}}' for f in cb["regulatory_fields"])
    return f"""You are coding a French online sports-betting advertisement from Snapchat for an academic study of how advertisements create associations in memory.

Read the file(s): {{files}}
{{video_note}}
Describe only what is observable. Report a brand only if it is visible or audible. Transcribe French text verbatim.

BORROWED-MEANING CATEGORIES. Rate each on prominence ({scale}). Give short quoted or visual evidence when prominence > 0, otherwise "".
{cats}

REGULATORY FIELDS. Booleans are true/false; ratings are integers 0-100 using the anchors. {cb["missing_value_rule"]} When value is null, give unknown_reason.
{chr(10).join(regs)}

ALLOWED VALUES
- sports (list): {e["sport"]}
- competition_level: {e["competition_level"]}
- occasion: {e["occasion"]}
- primary_framing: {e["primary_framing"]}
- offer_type: {e["offer_type"]}
- most_prominent_element, first_noticed_element: {e["element"]}
- template: {e["template"]}

Return JSON only, no prose and no code fences, with exactly these keys:
{{
  "visible_text_verbatim": ["each distinct text element, verbatim, in reading order"],
  "text_english": "faithful English translation of all visible text and speech",
  "scene_description": "2-4 sentences: setting, objects, layout, colours, photo vs graphic vs app screenshot",
  "people": "who appears (count, apparent age group, gender presentation, role), or 'none'",
  "entities": {{"competitions_or_events": [], "teams_or_national_sides": [], "named_athletes_or_celebrities": [], "brands_visible": []}},
  "sports": ["allowed values"],
  "competition_level": "allowed value",
  "occasion": "allowed value",
  "cues_linked_to_brand": [{{"cue": "specific context tied to the brand", "cue_type": "event | team | sport | time | place | social_setting | emotion | identity | activity | other", "evidence": ""}}],
  "borrowed_meaning": {{{cat_obj}}},
  "other_borrowed_meaning": "any important borrowed meaning not covered above, or empty string",
  "primary_framing": "allowed value",
  "offer": {{"type": "allowed value", "amount_eur": null, "description": "", "prominence": 0, "deadline_or_urgency": null, "guaranteed_or_risk_free_language": false}},
  "payoff_depiction": "how winning or gains are depicted, or 'none'",
  "winning_scenario_shown": false,
  "risk_or_probability_information": "verbatim or described, or 'none'",
  "most_prominent_element": "allowed value",
  "first_noticed_element": "allowed value",
  "template": "allowed value",
  "brand_prominence": 0,
  "tone": "a few words",
  "intended_association": "one sentence: what the ad wants viewers to link the brand with",
  "regulatory": {{{reg_obj}}},
  "coder_notes": "ambiguity or quality issues, or empty string"
}}"""


def validate(obj: dict, cb: dict, template_keys: list[str]) -> None:
    missing = [k for k in template_keys if k not in obj]
    extra = [k for k in obj if k not in template_keys]
    if missing or extra:
        raise ValueError(f"keys missing={missing} extra={extra}")
    e = cb["enums"]

    def need(cond: bool, msg: str) -> None:
        if not cond:
            raise ValueError(msg)

    need(isinstance(obj["sports"], list) and bool(obj["sports"]) and all(s in e["sport"] for s in obj["sports"]), f"sports {obj['sports']}")
    for k, enum in [("competition_level", "competition_level"), ("occasion", "occasion"), ("primary_framing", "primary_framing"),
                    ("most_prominent_element", "element"), ("first_noticed_element", "element"), ("template", "template")]:
        need(obj[k] in e[enum], f"{k}={obj[k]!r}")
    need(isinstance(obj["offer"], dict) and obj["offer"].get("type") in e["offer_type"], f"offer.type={obj['offer']}")
    need(obj["offer"].get("prominence") in (0, 1, 2, 3), "offer.prominence")
    need(obj["brand_prominence"] in (0, 1, 2, 3), "brand_prominence")
    need(isinstance(obj["winning_scenario_shown"], bool), "winning_scenario_shown")
    bm = obj["borrowed_meaning"]
    names = [c["name"] for c in cb["borrowed_meaning_categories"]]
    need(isinstance(bm, dict) and sorted(bm) == sorted(names), "borrowed_meaning keys")
    for n in names:
        need(isinstance(bm[n], dict) and bm[n].get("prominence") in (0, 1, 2, 3), f"borrowed_meaning.{n}")
    reg = obj["regulatory"]
    rnames = [f["name"] for f in cb["regulatory_fields"]]
    need(isinstance(reg, dict) and sorted(reg) == sorted(rnames), "regulatory keys")
    for f in cb["regulatory_fields"]:
        v = reg[f["name"]].get("value") if isinstance(reg[f["name"]], dict) else "bad"
        if v is None:
            need(bool(reg[f["name"]].get("unknown_reason")), f"{f['name']} null without reason")
        elif f["type"] == "boolean":
            need(isinstance(v, bool), f"{f['name']} not boolean")
        else:
            need(isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 100, f"{f['name']} not 0-100 int")


def transcribe(video: Path) -> dict:
    import av
    import mlx_whisper
    import numpy as np

    container = av.open(str(video))
    if not container.streams.audio:
        return {"has_audio": False, "text": ""}
    resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks = [g.to_ndarray().reshape(-1) for f in container.decode(audio=0) for g in resampler.resample(f)]
    container.close()
    if not chunks:
        return {"has_audio": False, "text": ""}
    audio = np.concatenate(chunks).astype(np.float32) / 32768
    if float(np.abs(audio).max()) < 1e-3:
        return {"has_audio": True, "silent": True, "text": ""}
    r = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER_MODEL, language="fr")
    return {"has_audio": True, "duration_s": round(len(audio) / 16000, 1), "text": r["text"].strip()}


def prepare(out: Path, creatives: dict) -> list[dict]:
    inputs = out / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    items = []
    for i, c in enumerate(sorted(creatives.values(), key=lambda c: c["sha256"]), 1):
        cid = f"LC-{i:04d}"
        src = Path(c["path"])
        if sha256_file(src) != c["sha256"]:
            raise SystemExit(f"checksum mismatch for {src}")
        if c["media_type"] == "VIDEO":
            files = extract_frames(src, inputs / cid, FRAME_FRACTIONS)
            if not files:
                raise SystemExit(f"no frames extracted from {src}")
        else:
            dst = inputs / f"{cid}{src.suffix.lower()}"
            shutil.copyfile(src, dst)
            files = [dst]
        items.append({"coding_id": cid, "sha256": c["sha256"], "firms": sorted(c["firms"]),
                      "media_type": c["media_type"], "ads_using_creative": c["ads"], "source_path": str(src),
                      "input_files": [f.name for f in files]})
    return items


def code_one(item: dict, prompt_t: str, cb: dict, keys: list[str], inputs: Path, transcripts: dict,
             model: str, timeout: int, attempts: int) -> dict:
    files = ", ".join(item["input_files"])
    note = ""
    if item["media_type"] == "VIDEO":
        t = transcripts.get(item["coding_id"], {})
        speech = t.get("text") or "(no speech detected)"
        note = (f"These are {len(item['input_files'])} still frames sampled at about 5%, 25%, 50%, 75%, and 95% of a video ad, "
                f"in order. Automatic transcript of the audio (may contain errors; music is not described): \"{speech}\"")
    prompt = prompt_t.replace("{files}", files).replace("{video_note}", note)
    last_err, tries, waits = None, 0, 0
    while tries < attempts:
        started = time.time()
        try:
            proc = subprocess.run(["claude", "-p", prompt, "--model", model, "--allowedTools", "Read", "--output-format", "json"],
                                  cwd=inputs, capture_output=True, text=True, timeout=timeout)
            env = json.loads(proc.stdout)
            if env.get("is_error"):
                raise RuntimeError(str(env.get("result"))[:300])
            raw = env.get("result", "")
            t = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            obj = json.loads(t[t.find("{"): t.rfind("}") + 1])
            validate(obj, cb, keys)
            return {"coding_id": item["coding_id"], "sha256": item["sha256"], "status": "ok", "labels": obj,
                    "raw_response": raw, "model_usage": list((env.get("modelUsage") or {}).keys()),
                    "cost_equivalent_usd": env.get("total_cost_usd"), "duration_s": round(time.time() - started, 1),
                    "attempt": tries + 1, "prompt_version": PROMPT_VERSION, "coded_at_utc": utc_now()}
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}: {str(exc)[:300]}"
            low = last_err.lower()
            if ("limit" in low or "429" in low or "overloaded" in low) and waits < 48:
                waits += 1
                with _lock:
                    print(f"{utc_now()[11:19]} {item['coding_id']} usage/rate limit; waiting 10 min ({waits})", flush=True)
                time.sleep(600)
                continue
            tries += 1
            time.sleep(5 * tries)
    return {"coding_id": item["coding_id"], "sha256": item["sha256"], "status": "failed", "error": last_err,
            "prompt_version": PROMPT_VERSION, "coded_at_utc": utc_now()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--backfill-dir", type=Path, required=True)
    ap.add_argument("--codebook", type=Path, default=Path("config/competitor_association_codebook_v1.json"))
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--parallelism", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=400)
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="code only the first N items (smoke test)")
    args = ap.parse_args()

    cb_bytes = args.codebook.read_bytes()
    cb = json.loads(cb_bytes)
    prompt_t = build_prompt(cb)
    keys = re.findall(r'^  "([a-z_]+)":', prompt_t, flags=re.M)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    mpath = out / "manifest.json"
    if mpath.exists():
        manifest = json.loads(mpath.read_text())
        if manifest["codebook_sha256"] != hashlib.sha256(cb_bytes).hexdigest() or manifest["prompt_sha256"] != hashlib.sha256(prompt_t.encode()).hexdigest():
            raise SystemExit("codebook or prompt changed since this output directory was created; use a new --output-dir")
        items = manifest["items"]
    else:
        creatives = index_creatives(args.run_dir, args.backfill_dir)
        items = prepare(out, creatives)
        manifest = {"created_at_utc": utc_now(), "prompt_version": PROMPT_VERSION,
                    "prompt_sha256": hashlib.sha256(prompt_t.encode()).hexdigest(),
                    "codebook_spec_version": cb["spec_version"], "codebook_sha256": hashlib.sha256(cb_bytes).hexdigest(),
                    "model_alias": args.model, "route": "Claude Code CLI (claude -p), Read tool only",
                    "source_run": str(args.run_dir), "backfill_run": str(args.backfill_dir),
                    "video_protocol": f"frames at {FRAME_FRACTIONS} + local {WHISPER_MODEL} French transcript; exploratory, not the frozen full-video protocol",
                    "unique_creatives": len(items), "items": items}
        mpath.write_text(json.dumps(manifest, indent=2))
        (out / "prompt_template.txt").write_text(prompt_t)
    print(f"{utc_now()[11:19]} {len(items)} creatives prepared", flush=True)

    tpath = out / "transcripts.jsonl"
    transcripts = {}
    if tpath.exists():
        transcripts = {r["coding_id"]: r for r in map(json.loads, tpath.open())}
    videos = [it for it in items if it["media_type"] == "VIDEO" and it["coding_id"] not in transcripts]
    with tpath.open("a") as fh:
        for n, it in enumerate(videos, 1):
            try:
                t = transcribe(Path(it["source_path"]))
            except Exception as exc:  # noqa: BLE001
                t = {"has_audio": None, "text": "", "error": f"{type(exc).__name__}: {exc}"[:300]}
            t.update(coding_id=it["coding_id"], sha256=it["sha256"], model=WHISPER_MODEL)
            transcripts[it["coding_id"]] = t
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
            fh.flush()
            if n % 50 == 0 or n == len(videos):
                print(f"{utc_now()[11:19]} transcribed {n}/{len(videos)} videos", flush=True)

    rpath = out / "results.jsonl"
    done = set()
    if rpath.exists():
        done = {r["coding_id"] for r in map(json.loads, rpath.open()) if r.get("status") == "ok"}
    todo = [it for it in items if it["coding_id"] not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"{utc_now()[11:19]} {len(done)} already labelled; {len(todo)} to label", flush=True)
    ok = fail = 0
    with cf.ThreadPoolExecutor(max_workers=args.parallelism) as pool, rpath.open("a") as fh:
        futs = [pool.submit(code_one, it, prompt_t, cb, keys, out / "inputs", transcripts, args.model, args.timeout, args.attempts) for it in todo]
        for n, fut in enumerate(cf.as_completed(futs), 1):
            res = fut.result()
            with _lock:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
                fh.flush()
                ok += res["status"] == "ok"
                fail += res["status"] != "ok"
                if n % 50 == 0 or n == len(todo):
                    print(f"{utc_now()[11:19]} labelled {len(done) + ok}/{len(items)}, failed {fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
