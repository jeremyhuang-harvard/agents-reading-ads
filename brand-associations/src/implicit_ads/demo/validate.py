"""Validate article coding against hand-coded gold labels.

Gold files live in data/raw/demo/validation/ (immutable inputs). Two splits:
``gold_labels_v1.csv`` was coded while diagnosing the first rule set, so the
revised rule (``on_topic_rule``) was tuned on it — treat its scores as
in-sample. ``gold_labels_heldout_v1.csv`` was drawn and coded after the rule
change and is the honest test.
"""

from __future__ import annotations

import csv
import json

from .config import DERIVED_DIR, ROOT

GOLD_DIR = ROOT / "data" / "raw" / "demo" / "validation"
SPLITS = {"tuning": "gold_labels_v1.csv", "heldout": "gold_labels_heldout_v1.csv"}


def _read(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _truthy(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def scores(pairs: list[tuple[bool, bool]]) -> dict:
    tp = sum(1 for g, p in pairs if g and p)
    fp = sum(1 for g, p in pairs if not g and p)
    fn = sum(1 for g, p in pairs if g and not p)
    tn = sum(1 for g, p in pairs if not g and not p)
    n = len(pairs)
    return {
        "n": n, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "recall": round(tp / (tp + fn), 3) if tp + fn else None,
        "accuracy": round((tp + tn) / n, 3) if n else None,
    }


def run(cases, log=print) -> None:
    arts = {a["url"]: a for a in _read(DERIVED_DIR / "coverage_articles.csv")}
    llm = {r["url"]: r for r in _read(DERIVED_DIR / "coverage_llm_labels.csv")}
    rows = []
    for split, name in SPLITS.items():
        gold = _read(GOLD_DIR / name)
        if not gold:
            continue
        coders = {
            "rule_v1_cooccurrence": lambda a, q: _truthy(a.get("relevant")),
            "rule_v2_proximity": lambda a, q: _truthy(a.get("on_topic_rule")),
            "qwen_v2": lambda a, q: _truthy(q.get("about_focal_appearance")) if q else None,
            "rule_v2_and_qwen_v2": lambda a, q: (_truthy(a.get("on_topic_rule")) and _truthy(q.get("about_focal_appearance"))) if q else None,
        }
        for coder, fn in coders.items():
            pairs, level_hits, level_n = [], 0, 0
            for g in gold:
                a = arts.get(g["url"])
                if a is None:
                    continue
                pred = fn(a, llm.get(g["url"]))
                if pred is None:
                    continue
                truth = g["about_focal_appearance"] == "1"
                pairs.append((truth, pred))
                if truth and pred:
                    level_n += 1
                    if coder.startswith("qwen") or coder.endswith("qwen_v2"):
                        level = llm[g["url"]].get("focal_id_level")
                    elif coder == "rule_v2_proximity":
                        level = a.get("linked_level")
                    else:
                        level = a.get("id_level")
                    level_hits += level == g["focal_id_level"]
            rows.append({"split": split, "coder": coder, **scores(pairs),
                         "id_level_agreement_on_true_positives": f"{level_hits}/{level_n}" if level_n else ""})
    out = DERIVED_DIR / "validation_scores.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["split"])
        writer.writeheader()
        writer.writerows(rows)
    for r in rows:
        log(f"[validate] {r['split']:7} {r['coder']:22} n={r['n']:>2} P={r['precision']} R={r['recall']} "
            f"acc={r['accuracy']} level={r['id_level_agreement_on_true_positives']}")
    (DERIVED_DIR / "validation_scores.json").write_text(json.dumps(rows, indent=2))
