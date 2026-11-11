"""Common Crawl News (CC-NEWS): full-text news articles mentioning frame entities.

CC-NEWS publishes every news page Common Crawl fetches as monthly WARC files (~370-500 files of
~1 GB per month; https://data.commoncrawl.org/crawl-data/CC-NEWS/). We stream a deterministic,
evenly spaced sample of files per month (never storing the WARCs), keep English HTML pages that
mention at least one frame entity, extract the main article text (trafilatura), and write one
gzipped JSONL per WARC file under data/raw/assoc/ccnews/<YYYY-MM>/ with a .done marker, so the
job is resumable and every kept article is traceable to its WARC file.

Records: url, warc_date, title, hits {entity_id: count}, text (main text, truncated). Article text
is copyrighted publisher content: it stays in data/raw (git-ignored) and is used only to compute
derived measures (co-mention composition, embeddings).

Ambiguous names (Puma the animal, Jennie, Jimin, ...) must co-occur with a context term.
"""

from __future__ import annotations

import gzip
import json
import os
import re
import time
from html import unescape
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from ...demo.http import USER_AGENT
from ..config import DERIVED, RAW, Frame
from . import matcher

BASE = "https://data.commoncrawl.org/"
OUT = RAW / "ccnews" / os.environ["CCNEWS_TAG"] if os.environ.get("CCNEWS_TAG") else RAW / "ccnews"
MAX_TEXT = 15000

# entity id -> regex that must also appear somewhere in the article text
REQUIRE = {
    "puma": r"sneaker|shoe|footwear|sportswear|apparel|brand|kit|collab|Fenty|Rihanna|A\$AP|LaMelo",
    "on_running": r"running|sneaker|shoe|Zendaya|Federer|Cloud",
    "jennie": r"BLACKPINK|Blackpink|K-pop|Chanel|Calvin Klein",
    "jimin": r"BTS|K-pop|Dior",
    "jisoo": r"BLACKPINK|Blackpink|K-pop|Dior",
    "lisa": r"BLACKPINK|Blackpink|K-pop|Louis Vuitton",
    "skims": r"Kardashian|shapewear|brand|underwear",
    "crocs": r"clog|shoe|footwear|brand|Jibbitz",
    "air_jordan": r"sneaker|shoe|Nike|Jordan Brand|Air Jordan",
    "dicks": r"Dick's Sporting Goods|retailer",
    "american_eagle": r"jeans|denim|Outfitters|AEO|Sweeney|retailer|apparel|Aerie|Tru Kolors",
    "nike": r"sneaker|shoe|footwear|sportswear|apparel|brand|Swoosh|Jordan|athlete|deal|kit",
    "gucci": r"fashion|brand|Kering|runway|luxury|handbag|ambassador",
    "lincoln": r"\bcar\b|vehicle|SUV|Navigator|Aviator|Nautilus|Corsair|Ford|automaker|dealership|McConaughey",
    "corona": r"beer|cerveza|Constellation|Modelo|brew|lime|Snoop",
    "sauvage": r"Dior|fragrance|cologne|perfume|scent|Depp",
    "the_general": r"insurance|insurer|Shaq|O'Neal",
    "rolex": r"watch|Rolex|timepiece",
}
CASE_SENSITIVE = {"skims": r"\bSkims\b|\bSKIMS\b", "lisa": r"\bLalisa\b|BLACKPINK'?s Lisa|Blackpink'?s Lisa|Lisa of BLACKPINK"}


HEAD_FIELDS = re.compile(
    r"<title[^>]*>(.*?)</title>"
    r"|<meta[^>]+(?:property|name)=[\"'](?:og:title|og:description|description|twitter:title|twitter:description)[\"'][^>]*content=[\"']([^\"']*)"
    , re.IGNORECASE | re.DOTALL)


def month_paths(month: str) -> list[str]:
    y, m = month.split("-")
    with urlopen(Request(f"{BASE}crawl-data/CC-NEWS/{y}/{m}/warc.paths.gz", headers={"User-Agent": USER_AGENT}), timeout=120) as r:
        return gzip.decompress(r.read()).decode().split()


def sample(paths: list[str], k: int) -> list[str]:
    if k >= len(paths):
        return paths
    step = len(paths) / k
    return [paths[int(step * i + step / 2)] for i in range(k)]


def _patterns(frame: Frame) -> dict:
    pats = {}
    for e in frame.entities:
        rx = re.compile(CASE_SENSITIVE[e.id]) if e.id in CASE_SENSITIVE else matcher(e)
        req = re.compile(REQUIRE[e.id]) if e.id in REQUIRE else None
        pats[e.id] = (rx, req)
    alts = []
    for e in frame.entities:
        alts += [re.escape(p) for p in e.patterns if len(p) >= 4]
    body = "|".join(sorted(set(alts), key=len, reverse=True))
    prefilter = re.compile(rb"(?<![\w])(?:" + body.encode() + rb")(?![\w])", re.IGNORECASE)
    return {"entities": pats, "prefilter": prefilter}


def _is_english(head: bytes) -> bool:
    m = re.search(rb"<html[^>]*\blang=[\"']?([a-zA-Z-]+)", head[:4000], re.IGNORECASE)
    return (m is None) or m.group(1).lower().startswith(b"en")


def process_file(path: str, frame_path: str) -> dict:
    """Stream one WARC file; returns stats. Runs in a worker process."""
    import trafilatura
    from warcio.archiveiterator import ArchiveIterator

    from .. import config as cfg

    frame = cfg.load(frame_path)
    P = _patterns(frame)
    month = re.search(r"CC-NEWS/(\d{4})/(\d{2})/", path)
    folder = OUT / f"{month.group(1)}-{month.group(2)}"
    folder.mkdir(parents=True, exist_ok=True)
    stem = Path(path).name.removesuffix(".warc.gz")
    done = folder / f"{stem}.done"
    if done.exists():
        return json.loads(done.read_text())
    stats = {"file": path, "records": 0, "html": 0, "prefilter": 0, "kept": 0, "started": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    tmp = folder / f"{stem}.jsonl.gz.tmp"
    for attempt in range(5):
        try:
            with urlopen(Request(BASE + path, headers={"User-Agent": USER_AGENT}), timeout=300) as resp, gzip.open(tmp, "wt") as out:
                for rec in ArchiveIterator(resp):
                    if rec.rec_type != "response":
                        continue
                    stats["records"] += 1
                    ctype = (rec.http_headers.get_header("Content-Type") or "") if rec.http_headers else ""
                    if "html" not in ctype:
                        continue
                    body = rec.content_stream().read()
                    stats["html"] += 1
                    head = body[: (body.find(b"</head>") + 7) if b"</head>" in body[:300000] else 60000]
                    if not _is_english(head):
                        continue
                    hl = head.decode("utf-8", "replace")
                    lede = " ".join((m.group(1) or m.group(2) or "") for m in HEAD_FIELDS.finditer(hl))
                    lede = re.sub(r"\s+", " ", unescape(lede))
                    # cheap screen: the article is *about* an entity when its title/description names it
                    about = [eid for eid, (rx, _) in P["entities"].items() if rx.search(lede)]
                    if not about:
                        continue
                    stats["prefilter"] += 1
                    text = trafilatura.extract(body.decode("utf-8", "replace"), include_comments=False,
                                               include_tables=False, fast=True) or ""
                    if len(text) < 300:
                        continue
                    full = lede + "\n" + text
                    about = [eid for eid in about if P["entities"][eid][1] is None or P["entities"][eid][1].search(full)]
                    if not about:
                        continue
                    hits = {}
                    for eid, (rx, req) in P["entities"].items():
                        n = len(rx.findall(text))
                        if n and (req is None or req.search(full)):
                            hits[eid] = n
                    title_m = re.search(r"<title[^>]*>(.*?)</title>", hl, re.IGNORECASE | re.DOTALL)
                    out.write(json.dumps({"url": rec.rec_headers.get_header("WARC-Target-URI"),
                                          "warc_date": rec.rec_headers.get_header("WARC-Date"),
                                          "title": unescape(re.sub(r"\s+", " ", title_m.group(1))).strip()[:300] if title_m else "",
                                          "lede": lede[:1000], "about": about, "hits": hits, "text": text[:MAX_TEXT]},
                                         ensure_ascii=False) + "\n")
                    stats["kept"] += 1
            break
        except Exception as exc:  # network resets / 503 slow-down: retry the whole file
            stats["error"] = f"{type(exc).__name__}: {exc}"
            time.sleep(30 * (attempt + 1))
            stats.update({"records": 0, "html": 0, "prefilter": 0, "kept": 0})
    else:
        return stats
    tmp.replace(folder / f"{stem}.jsonl.gz")
    stats.pop("error", None)
    stats["finished"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    done.write_text(json.dumps(stats))
    return stats


def collect(frame: Frame, months: list[str], files_per_month: int, workers: int = 4, log=print) -> None:
    from multiprocessing import get_context

    jobs = []
    for m in months:
        try:
            jobs += sample(month_paths(m), files_per_month)
        except Exception as exc:  # noqa: BLE001
            log(f"[ccnews] {m}: cannot list files ({exc})")
    (OUT).mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps({"months": months, "files_per_month": files_per_month, "files": jobs,
                                                   "frame_version": frame.version}, indent=2))
    log(f"[ccnews] {len(jobs)} WARC files across {len(months)} months, {workers} workers")
    t0, kept = time.time(), 0
    with get_context("spawn").Pool(workers) as pool:
        for i, st in enumerate(pool.imap_unordered(_worker, [(p, str(frame.path)) for p in jobs]), 1):
            kept += st.get("kept", 0)
            log(f"[ccnews] {i}/{len(jobs)} {Path(st['file']).name}: {st.get('html', 0)} html, {st.get('prefilter', 0)} prefiltered, "
                f"{st.get('kept', 0)} kept {st.get('error', '')} | total kept {kept} | {(time.time() - t0) / 60:.1f} min")


def _worker(args):
    return process_file(*args)


def iter_articles(months: list[str] | None = None):
    for folder in sorted(OUT.glob("20??-??")):
        if months and folder.name not in months:
            continue
        for f in sorted(folder.glob("*.jsonl.gz")):
            with gzip.open(f, "rt") as h:
                for line in h:
                    yield folder.name, json.loads(line)


def build_documents(frame: Frame, window_chars: int = 600, log=print) -> None:
    """Mention-context documents per entity (for monthly vectors) and article-level co-mention counts."""
    pats = {e.id: matcher(e) for e in frame.entities}
    seen, n_docs = set(), 0
    co = {}
    with (DERIVED / "documents_ccnews.jsonl").open("w") as h:
        for month, art in iter_articles():
            key = art["title"].casefold() or art["url"]
            if key in seen:  # syndicated copies
                continue
            seen.add(key)
            ents = sorted(art["hits"])
            for a in ents:
                co.setdefault(month, {}).setdefault((a, a), 0)
                co[month][(a, a)] += 1
                for b in ents:
                    if a < b:
                        co[month][(a, b)] = co[month].get((a, b), 0) + 1
                m = pats[a].search(art["text"])
                if not m:
                    continue
                s = max(0, m.start() - window_chars // 2)
                h.write(json.dumps({"entity": a, "source": "ccnews", "doc_id": art["url"], "date": art["warc_date"][:10],
                                    "period": month, "text": art["text"][s:s + window_chars],
                                    "co_entities": [x for x in ents if x != a]}, ensure_ascii=False) + "\n")
                n_docs += 1
    with (DERIVED / "ccnews_comention_monthly.csv").open("w") as h:
        h.write("month,a,b,n_articles\n")
        for month, d in sorted(co.items()):
            for (a, b), n in sorted(d.items()):
                h.write(f"{month},{a},{b},{n}\n")
    log(f"[ccnews] {len(seen)} unique articles -> {n_docs} entity-context documents")
