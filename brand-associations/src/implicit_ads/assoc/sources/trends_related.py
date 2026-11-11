"""Google Trends related queries as a directed retrieval measure.

For a cue term (e.g. "Tate McRae"), Trends lists the top queries searched alongside it with
relative weights (0-100). The forward share of brand b is the weight of related queries that
mention b divided by the total weight of the cue's top list; the backward share uses the brand's
list and celebrity names. Because each cue's list is normalized within itself, this is a
competition-normalized retrieval share from search behavior (US, frame window).
"""

from __future__ import annotations

import csv

from ...explore import trends as T
from ..config import DERIVED, Frame
from . import matcher


def shares(top: list[dict], targets: list, patterns: dict) -> dict[str, float]:
    total = sum(float(r.get("value", 0)) for r in top)
    out = {t.id: 0.0 for t in targets}
    if total <= 0:
        return out
    for r in top:
        q = str(r.get("query", ""))
        for t in targets:
            if patterns[t.id].search(q):
                out[t.id] += float(r.get("value", 0)) / total
    return out


def collect(frame: Frame, geo: str = "US", log=print) -> None:
    pats = {e.id: matcher(e) for e in frame.entities}
    rows, raw = [], []
    fwd, bwd = {}, {}
    for e in frame.entities:
        try:
            rel = T.related(e.name, frame.start, frame.end, geo=geo)
        except Exception as exc:  # pytrends raises assorted errors; keep going
            log(f"[trends] {e.id}: ERROR {exc}")
            continue
        top = rel.get("top", []) or []
        raw.append((e.id, len(top)))
        targets = frame.brands if e.kind == "celebrity" else frame.celebrities
        s = shares(top, targets, pats)
        for t_id, v in s.items():
            if e.kind == "celebrity":
                fwd[(e.id, t_id)] = v
            else:
                bwd[(t_id, e.id)] = v
        log(f"[trends] {e.id}: {len(top)} related queries; matched {sum(v > 0 for v in s.values())} targets")
    for c in frame.celebrities:
        for b in frame.brands:
            if (c.id, b.id) in fwd or (c.id, b.id) in bwd:
                rows.append({"celebrity": c.id, "brand": b.id, "fwd": fwd.get((c.id, b.id), ""), "bwd": bwd.get((c.id, b.id), "")})
    DERIVED.mkdir(parents=True, exist_ok=True)
    with (DERIVED / "directed_trends_related.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["celebrity", "brand", "fwd", "bwd"])
        w.writeheader()
        w.writerows(rows)
