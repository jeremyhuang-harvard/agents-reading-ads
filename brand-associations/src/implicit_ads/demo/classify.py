"""Optional local-LLM coding of coverage articles (Qwen3 via mlx_lm.server).

This is high-volume, low-difficulty labeling, so it runs on the local
Qwen3-8B model rather than a metered API. Start the server first:

    make qwen-server     # mlx_lm.server --model mlx-community/Qwen3-8B-4bit --port 8080

Outputs are *model_predicted* and written to a separate file
(``coverage_llm_labels.csv``) so they never overwrite rule-based codes.
Results are cached by (text hash, prompt version, model).
"""

from __future__ import annotations

import csv
import json
import re
from urllib.request import Request, urlopen

from .config import DERIVED_DIR, ROOT
from .coverage import context_windows

ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "mlx-community/Qwen3-8B-4bit"
PROMPT_VERSION = "coverage-v2"
CACHE = ROOT / "data" / "raw" / "demo" / "llm_labels" / f"{PROMPT_VERSION}.jsonl"
TEXT_DIR = DERIVED_DIR / "article_text"

# v1 (first 3,500 chars of page text, seven-way outlet type) agreed with rules on
# 17/94 articles: page text starts with navigation boilerplate, and outlet type is
# better taken from the frozen domain roster in coverage.ACTOR_TYPES. v2 sends only
# excerpts around celebrity/product mentions and asks narrower questions.
LABELS = {
    "focal_id_level": ["none", "brand", "model", "exact"],
    "primary_frame": ["celebrity_news", "product_identification", "shopping_guide", "market_response", "industry_analysis", "other"],
}

SYSTEM = (
    "You code excerpts from one web article. Decide whether the article reports the specific celebrity "
    "appearance described, and how precisely it identifies the product worn there.\n"
    "about_focal_appearance: true only if the excerpts describe the celebrity wearing the focal product at the "
    "described appearance (or its immediate aftermath, e.g. sellouts or sales caused by it). False for other "
    "outfits, other dates, endorsement deals, unrelated news, or sidebars/related-story links.\n"
    "focal_id_level, about the item worn at that appearance: exact = names the colorway, style code or product "
    "name (e.g. 'white/red 550', 'all-white Energy Boost ESM', 'black Harriet jeans'); model = names the model "
    "line only; brand = names only the brand; none = not identified or not about the appearance.\n"
    "other_products: up to 6 other specific footwear/apparel products or brands the article names "
    "(siblings of the same brand, competitors, or other items in the outfit); [] if none.\n"
    "Return only JSON with keys: about_focal_appearance (bool), focal_id_level, primary_frame, "
    "reports_sellout_or_restock (bool), reports_sales_or_traffic_numbers (bool), other_products (list of strings). "
    "Allowed values: " + json.dumps(LABELS)
)


def _ask(case: dict, title: str, text: str) -> dict:
    focal = case["focal"]
    excerpts = context_windows(text, case["identification"]) or [text[:1200]]
    user = (
        f"Case: {case['label']}. Appearance: {case['event_label']} on {case['event_date']}.\n"
        f"Focal product: {focal['brand']} {focal['model']}"
        + (f" ({focal['colorway']})" if focal.get("colorway") else "")
        + f", code {focal.get('sku') or 'n/a'}.\n"
        f"Article title: {title}\nExcerpts:\n" + "\n---\n".join(f"[{i + 1}] {e}" for i, e in enumerate(excerpts))
        + "\n/no_think"
    )
    body = json.dumps({
        "model": MODEL, "temperature": 0, "max_tokens": 300,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
    }).encode()
    req = Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=180) as resp:
        content = json.loads(resp.read())["choices"][0]["message"]["content"]
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.S)
    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        raise ValueError(f"no JSON in model output: {content[:200]}")
    label = json.loads(match.group(0))
    for key, allowed in LABELS.items():
        if label.get(key) not in allowed:
            label[key] = "invalid:" + str(label.get(key))
    return label


def run(cases: list[dict], log=print) -> None:
    path = DERIVED_DIR / "coverage_articles.csv"
    if not path.exists():
        raise SystemExit("run the coverage stage first")
    by_case = {c["case_id"]: c for c in cases}
    cache: dict[str, dict] = {}
    if CACHE.exists():
        for line in CACHE.read_text().splitlines():
            row = json.loads(line)
            cache[row["key"]] = row["label"]
    CACHE.parent.mkdir(parents=True, exist_ok=True)

    out = []
    with path.open(encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r.get("text_sha256") and r["case_id"] in by_case]
    for row in rows:
        key = f"{row['text_sha256']}|{PROMPT_VERSION}|{MODEL}"
        if key not in cache:
            text_path = TEXT_DIR / f"{row['text_sha256'][:24]}.txt"
            text = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
            try:
                label = _ask(by_case[row["case_id"]], row["title"], text)
            except Exception as exc:
                log(f"[classify] {row['url']}: {type(exc).__name__}: {exc}")
                continue
            cache[key] = label
            with CACHE.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"key": key, "label": label}) + "\n")
        out.append({"case_id": row["case_id"], "url": row["url"], "model": MODEL, "prompt_version": PROMPT_VERSION,
                    "epistemic_status": "model_predicted", **cache[key]})
    with (DERIVED_DIR / "coverage_llm_labels.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["case_id", "url", "model", "prompt_version", "epistemic_status", *LABELS.keys(),
                  "about_focal_appearance", "reports_sellout_or_restock", "reports_sales_or_traffic_numbers",
                  "other_products"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out)
    log(f"[classify] labeled {len(out)} articles ({len(rows) - len(out)} failed)")
