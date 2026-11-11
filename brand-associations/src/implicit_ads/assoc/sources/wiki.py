"""Wikipedia: canonical titles, pageview totals (a size proxy), and article paragraphs (documents)."""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from urllib.parse import quote, urlencode

from ...demo import http
from ..config import DERIVED, Frame
from . import matcher

PAGEVIEWS = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
             "{title}/monthly/{start}00/{end}00")
API = "https://en.wikipedia.org/w/api.php?"


def resolve(title: str) -> tuple[str | None, str]:
    """Follow redirects; return (canonical title with underscores, plain-text extract)."""
    params = {"action": "query", "format": "json", "prop": "extracts", "explaintext": 1, "redirects": 1,
              "titles": title.replace("_", " "), "formatversion": 2}
    resp = http.get(API + urlencode(params))
    if not resp.ok:
        return None, ""
    pages = resp.json().get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return None, ""
    return pages[0]["title"].replace(" ", "_"), pages[0].get("extract", "")


def pageviews(title: str, start: str, end: str) -> int | None:
    s = date.fromisoformat(start).strftime("%Y%m01")
    e = date.fromisoformat(end).strftime("%Y%m%d")
    resp = http.get(PAGEVIEWS.format(title=quote(title, safe=""), start=s, end=e))
    if not resp.ok:
        return None
    return int(sum(item["views"] for item in resp.json().get("items", [])))


def paragraphs(extract: str, min_chars: int = 200, limit: int = 40) -> list[str]:
    out = []
    for block in extract.split("\n"):
        block = block.strip()
        if len(block) >= min_chars and not block.startswith("=="):
            out.append(block)
        if len(out) >= limit:
            break
    return out


def sentences(extract: str) -> list[str]:
    text = re.sub(r"\n+=+[^=\n]+=+\n+", "\n", extract)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 20]


def mention_components(frame: Frame, extracts: dict[str, str]) -> list[dict]:
    """Share of each article's sentences that mention the other entity (article composition, both directions)."""
    pats = {e.id: matcher(e) for e in frame.entities}
    sents = {k: sentences(v) for k, v in extracts.items()}
    rows = []
    for c in frame.celebrities:
        for b in frame.brands:
            sc, sb = sents.get(c.id, []), sents.get(b.id, [])
            fc = sum(bool(pats[b.id].search(x)) for x in sc)
            fb = sum(bool(pats[c.id].search(x)) for x in sb)
            rows.append({"celebrity": c.id, "brand": b.id, "fwd": f"{fc / len(sc):.6g}" if sc else "",
                         "bwd": f"{fb / len(sb):.6g}" if sb else "", "n_sent_c": len(sc), "n_sent_b": len(sb),
                         "sent_c_mentioning_b": fc, "sent_b_mentioning_c": fb})
    return rows


def collect(frame: Frame, log=print) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    rows, docs, extracts = [], [], {}
    for e in frame.entities:
        title, extract = resolve(e.wiki) if e.wiki else (None, "")
        extracts[e.id] = extract
        views = pageviews(title, frame.start, frame.end) if title else None
        rows.append({"entity": e.id, "kind": e.kind, "wiki_requested": e.wiki or "", "wiki_title": title or "",
                     "pageviews": "" if views is None else views, "extract_chars": len(extract)})
        for i, para in enumerate(paragraphs(extract)):
            docs.append({"entity": e.id, "source": "wikipedia", "doc_id": f"wiki:{title}:{i}", "date": "", "text": para})
        log(f"[wiki] {e.id}: title={title} views={views} paragraphs={sum(d['entity'] == e.id for d in docs)}")
    with (DERIVED / "wiki_entities.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (DERIVED / "documents_wikipedia.jsonl").open("w") as h:
        for d in docs:
            h.write(json.dumps(d, ensure_ascii=False) + "\n")
    comp = mention_components(frame, extracts)
    with (DERIVED / "directed_wiki_mentions.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(comp[0]))
        w.writeheader()
        w.writerows(comp)
    log(f"[wiki] article composition: {sum(r['sent_c_mentioning_b'] > 0 for r in comp)} celebrity articles mention a frame brand; "
        f"{sum(r['sent_b_mentioning_c'] > 0 for r in comp)} brand articles mention a frame celebrity")
    missing = [r["entity"] for r in rows if not r["wiki_title"]]
    if missing:
        log(f"[wiki] WARNING no Wikipedia article resolved for: {missing}")
