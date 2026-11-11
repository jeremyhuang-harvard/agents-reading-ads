"""GDELT DOC 2.0: co-coverage counts (N_c, N_b, N_cb) and headline documents for representations.

Counts use mode=timelinevolraw summed over the window (English-language sources only, so the
two directions are measured on the same corpus). GDELT asks for at most one request per 5 s;
implicit_ads.demo.http enforces 6 s and caches every response, so the full C x B matrix
(~700 queries for the pilot frame) takes about 70 minutes once and is free to re-run.
"""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from urllib.parse import urlencode

from ...demo import http
from ..config import DERIVED, Frame

URL = "https://api.gdeltproject.org/api/v2/doc/doc?"
LANG = "sourcelang:english"


def _call(query: str, start: str, end: str, mode: str, **extra) -> dict:
    params = {"query": f"{query} {LANG}", "mode": mode, "format": "json",
              "startdatetime": start.replace("-", "") + "000000", "enddatetime": end.replace("-", "") + "235959", **extra}
    resp = http.get(URL + urlencode(params))
    if not resp.ok:
        return {"error": resp.error or f"HTTP {resp.status}"}
    try:
        return json.loads(resp.text) if resp.text.strip() else {}
    except json.JSONDecodeError:
        return {"error": resp.text[:200]}


def count(query: str, start: str, end: str) -> tuple[int | None, str]:
    data = _call(query, start, end, "timelinevolraw", timelinesmooth=0)
    if "error" in data:
        return None, data["error"]
    series = (data.get("timeline") or [{}])[0].get("data", [])
    return int(sum(x.get("value", 0) for x in series)), ""


def collect_counts(frame: Frame, scope: str = "all", log=print) -> None:
    """scope='all' fills the full C x B matrix (needed for competition-normalized shares);
    scope='pairs' only the configured pairs plus marginals."""
    DERIVED.mkdir(parents=True, exist_ok=True)
    out = DERIVED / "gdelt_counts.csv"
    rows = []
    for e in frame.entities:
        n, err = count(e.gdelt, frame.start, frame.end)
        rows.append({"celebrity": e.id if e.kind == "celebrity" else "", "brand": e.id if e.kind == "brand" else "",
                     "query": e.gdelt, "n": "" if n is None else n, "error": err})
        log(f"[gdelt] {e.id}: {n} {err}")
    if scope == "pairs":
        cells = [(frame.get(p.celebrity), frame.get(p.brand)) for p in frame.pairs]
    else:
        cells = [(c, b) for c in frame.celebrities for b in frame.brands]
    for i, (c, b) in enumerate(cells):
        q = f"{c.gdelt} {b.gdelt}"
        n, err = count(q, frame.start, frame.end)
        rows.append({"celebrity": c.id, "brand": b.id, "query": q, "n": "" if n is None else n, "error": err})
        if i % 25 == 0 or err:
            log(f"[gdelt] cell {i + 1}/{len(cells)} {c.id} x {b.id}: {n} {err}")
        if i % 50 == 0:
            _write(out, rows)
    _write(out, rows)


def _write(path, rows):
    with path.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["celebrity", "brand", "query", "n", "error"])
        w.writeheader()
        w.writerows(rows)


def collect_headlines(frame: Frame, per_window: int = 75, windows: int = 4, log=print) -> None:
    """Headline documents per entity, spread over equal sub-windows (Sarkar aggregates article
    embeddings within periods, then averages periods)."""
    start, end = date.fromisoformat(frame.start), date.fromisoformat(frame.end)
    step = (end - start) / windows
    docs = []
    for e in frame.entities:
        n_e = 0
        for k in range(windows):
            s = start + step * k
            t = start + step * (k + 1) - timedelta(days=1 if k < windows - 1 else 0)
            data = _call(e.gdelt, s.isoformat(), t.isoformat(), "artlist", maxrecords=per_window, sort="hybridrel")
            for art in data.get("articles", []) or []:
                title = (art.get("title") or "").strip()
                if len(title) < 20:
                    continue
                docs.append({"entity": e.id, "source": "gdelt", "doc_id": art.get("url", ""), "date": art.get("seendate", "")[:8],
                             "period": k, "domain": art.get("domain", ""), "text": title})
                n_e += 1
            if "error" in data:
                log(f"[docs] {e.id} window {k}: {data['error']}")
        log(f"[docs] {e.id}: {n_e} headlines")
    seen, unique = set(), []
    for d in docs:  # syndicated copies share a headline
        key = (d["entity"], d["text"].casefold())
        if key not in seen:
            seen.add(key)
            unique.append(d)
    with (DERIVED / "documents_gdelt.jsonl").open("w") as h:
        for d in unique:
            h.write(json.dumps(d, ensure_ascii=False) + "\n")
    log(f"[docs] wrote {len(unique)} unique headlines ({len(docs) - len(unique)} syndicated duplicates dropped)")


def collect_joint(frame: Frame, per_pair: int = 100, log=print) -> None:
    """Headlines that mention both members of each configured pair (co-mention documents)."""
    docs = []
    for p in frame.pairs:
        c, b = frame.get(p.celebrity), frame.get(p.brand)
        data = _call(f"{c.gdelt} {b.gdelt}", frame.start, frame.end, "artlist", maxrecords=per_pair, sort="hybridrel")
        n = 0
        for art in data.get("articles", []) or []:
            title = (art.get("title") or "").strip()
            if len(title) < 20:
                continue
            for ent in (c, b):  # a co-mention document belongs to both entities' coverage
                docs.append({"entity": ent.id, "source": "gdelt_joint", "pair": f"{c.id}|{b.id}", "doc_id": art.get("url", ""),
                             "date": art.get("seendate", "")[:8], "period": "joint", "domain": art.get("domain", ""), "text": title})
            n += 1
        log(f"[joint] {c.id} x {b.id}: {n} co-mention headlines {data.get('error', '')}")
    with (DERIVED / "documents_gdelt_joint.jsonl").open("w") as h:
        for d in docs:
            h.write(json.dumps(d, ensure_ascii=False) + "\n")
