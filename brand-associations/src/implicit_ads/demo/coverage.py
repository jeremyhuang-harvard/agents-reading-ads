"""Coverage ledger: discover, fetch and code articles about each case.

Discovery sources (all bounded and cached):
1. ``seed_urls`` from the source-audited dossiers;
2. Wayback CDX URL discovery over a publisher roster (URL-slug regex);
3. GDELT DOC 2.0 article lists and raw daily volume (2017 onward only).

Each article is fetched from the Wayback Machine when an archived copy exists
(stable, avoids publisher bot walls) and live otherwise. Rule-based coding
records the identification level (celebrity → brand → model → exact SKU),
commerce/affiliate links, actor type, and publication time. An optional local
LLM pass (``classify.py``) adds model-predicted labels in a separate file.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from datetime import date, datetime, timezone
from urllib.parse import quote, urlencode, urljoin, urlparse, urlunparse

from . import http
from .archive import cdx_rows
from .config import DERIVED_DIR

TEXT_DIR = DERIVED_DIR / "article_text"
LEVELS = ["none", "celebrity_only", "brand", "model", "exact"]

ACTOR_TYPES = {
    "specialist_sneaker": [
        "complex.com", "hypebeast.com", "sneakernews.com", "nicekicks.com", "solecollector.com",
        "weartesters.com", "highsnobiety.com", "kicksonfire.com", "sneakerfreaker.com", "si.com/fannation/sneakers",
        "footwearnews.com", "hypebae.com",
    ],
    "fashion_lifestyle": [
        "vogue.", "harpersbazaar.com", "elle.com", "instyle.com", "whowhatwear.com", "townandcountrymag.com",
        "people.com", "glamour.com", "cosmopolitan.com", "fashionmagazine.com", "marieclaire.", "refinery29.com",
        "hollywoodreporter.com/lifestyle/shopping", "pagesix.com", "eonline.com", "usmagazine.com", "taylorswiftstyle.com",
    ],
    "industry_marketing": ["marketingbrew.com", "wwd.com", "businessoffashion.com", "adweek.com", "retaildive.com", "modernretail.co"],
    "sports_media": ["nfl.com", "espn.com", "actionnetwork.com", "touchdownwire.usatoday.com", "si.com", "bleacherreport.com", "theathletic.com"],
}
RETAIL_DOMAINS = [
    "newbalance.com", "adidas.com", "outlanddenim.com", "crocs.com", "amazon.", "amzn.to", "stockx.com", "goat.com",
    "ebay.com", "footlocker.com", "champssports.com", "finishline.com", "nordstrom.com", "ssense.com", "farfetch.com",
    "flightclub.com", "shopbop.com", "revolve.com", "zappos.com", "dickssportinggoods.com", "jdsports.", "kith.com",
    "endclothing.com", "sneakersnstuff.com", "net-a-porter.com", "davidjones.com", "myer.com.au",
]
AFFILIATE_HOSTS = [
    "go.skimresources.com", "go.redirectingat.com", "click.linksynergy.com", "shareasale.com", "rstyle.me",
    "shopstyle.", "howl.me", "howl.link", "narrativ.com", "bam-x.com", "sovrn.co", "anrdoezrs.net", "jdoqocy.com",
    "kqzyfj.com", "tkqlhce.com", "dpbolvw.net", "awin1.com", "pntra.com", "prf.hn", "fave.co", "shop-links.co",
    "linksynergy.com", "avantlink.com", "pjtra.com", "sjv.io", "evyy.net", "pxf.io", "ojrq.net", "7eer.net",
]


# ------------------------------------------------------------- discovery


def canonical(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.").split(":")[0]
    path = re.sub(r"/+$", "", parsed.path) or "/"
    return urlunparse(("https", host, path, "", "", ""))


def gdelt(query: str, start: str, end: str, mode: str) -> dict | None:
    params = {
        "query": query, "mode": mode, "format": "json", "maxrecords": 250,
        "startdatetime": start.replace("-", "") + "000000", "enddatetime": end.replace("-", "") + "235959",
        "sort": "dateasc",
    }
    resp = http.get("https://api.gdeltproject.org/api/v2/doc/doc?" + urlencode(params))
    if not resp.ok:
        return {"error": resp.error}
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"error": resp.text[:200]}


def discover(case: dict, log) -> tuple[dict[str, dict], list[dict]]:
    spec = case["coverage"]
    found: dict[str, dict] = {}
    volume: list[dict] = []

    for url in spec.get("seed_urls", []):
        found.setdefault(canonical(url), {"url": url, "discovered_via": "seed", "gdelt_seen": "", "capture": ""})

    start, end = spec["from"].replace("-", ""), spec["to"].replace("-", "")
    for item in spec.get("archive_discovery", []):
        try:
            rows = cdx_rows(item["prefix"], start, end, regex=item.get("regex"), limit=500)
        except RuntimeError as exc:
            log(f"[coverage] {case['case_id']}: CDX discovery failed for {item['prefix']}: {exc}")
            continue
        for row in rows:
            original = row["original"]
            if re.search(r"\.(jpg|jpeg|png|gif|css|js|json|xml|webp)(\?|$)", original, re.I):
                continue
            found.setdefault(canonical(original), {"url": original.split("?")[0], "discovered_via": f"cdx:{item['prefix']}",
                                                   "gdelt_seen": "", "capture": row["timestamp"]})
        log(f"[coverage] {case['case_id']}: CDX {item['prefix']} → {len(rows)} rows")

    if int(spec["from"][:4]) >= 2017:
        for query in spec.get("gdelt_queries", []):
            arts = gdelt(query, spec["from"], spec["to"], "artlist") or {}
            if "error" in arts:
                log(f"[coverage] {case['case_id']}: GDELT artlist error {arts['error']}")
            for art in arts.get("articles", []) or []:
                found.setdefault(canonical(art["url"]), {"url": art["url"], "discovered_via": "gdelt",
                                                         "gdelt_seen": art.get("seendate", ""), "capture": ""})
            log(f"[coverage] {case['case_id']}: GDELT artlist {query!r} → {len(arts.get('articles', []) or [])}")
            tl = gdelt(query, spec["from"], spec["to"], "timelinevolraw") or {}
            for series in tl.get("timeline", []) or []:
                for point in series.get("data", []):
                    volume.append({
                        "case_id": case["case_id"], "query": query, "series": series.get("series", ""),
                        "date": f"{point['date'][:4]}-{point['date'][4:6]}-{point['date'][6:8]}",
                        "value": point.get("value"), "norm": point.get("norm"),
                    })
    elif spec.get("gdelt_queries"):
        log(f"[coverage] {case['case_id']}: GDELT DOC covers 2017+; skipped")
    return found, volume


# ------------------------------------------------------------- extraction


def fetch_article(url: str, near: str, ts_hint: str = "") -> tuple[http.Response | None, str, str]:
    """Return (response, source, snapshot_timestamp). Prefer archived copies."""
    ts = ts_hint
    if not ts:
        avail = http.get(
            "https://archive.org/wayback/available?" + urlencode({"url": url, "timestamp": near.replace("-", "")})
        )
        if avail.ok:
            closest = (avail.json() or {}).get("archived_snapshots", {}).get("closest") or {}
            if closest.get("available") and str(closest.get("status")) in {"200", "301", "302"}:
                ts = closest["timestamp"]
    if ts:
        # `closest["url"]` is itself a Wayback URL; always rebuild from the original.
        resp = http.get(f"https://web.archive.org/web/{ts}id_/{url}")
        if resp.ok and len(resp.body) > 2000:
            return resp, "wayback", ts
    resp = http.get(url, cache_errors=True)
    return (resp if resp.ok else None), "live", ""


META_DATE_PATTERNS = [
    r'<meta[^>]+(?:property|name|itemprop)="(?:article:published_time|og:published_time|datePublished|parsely-pub-date|sailthru\.date|pubdate|publish-date|dc\.date|date)"[^>]+content="([^"]+)"',
    r'<meta[^>]+content="([^"]+)"[^>]+(?:property|name|itemprop)="(?:article:published_time|datePublished)"',
    r'"datePublished"\s*:\s*"([^"]+)"',
    r'<time[^>]+datetime="([^"]+)"',
]


def published_time(page: str, url: str) -> tuple[str, str]:
    for pattern in META_DATE_PATTERNS:
        match = re.search(pattern, page, re.I)
        if match and re.match(r"\d{4}-\d{2}-\d{2}", match.group(1).strip()):
            return match.group(1).strip(), "page_metadata"
    match = re.search(r"/(20\d{2})/(\d{1,2})/(\d{1,2})/", url)
    if match:
        y, m, d = match.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}", "url_path"
    return "", ""


def visible_text(page: str) -> str:
    body = re.search(r"<article\b.*?</article>", page, re.S | re.I)
    chunk = body.group(0) if body and len(body.group(0)) > 2000 else page
    chunk = re.sub(r"<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<[^>]+>", " ", chunk)
    return re.sub(r"\s+", " ", html.unescape(chunk)).strip()


def outbound_links(page: str, base: str) -> list[str]:
    links = []
    for href in re.findall(r'href="([^"#]+)"', page, re.I):
        href = html.unescape(href)
        # Wayback rewrites links as /web/<ts>/<original>; recover the original.
        href = re.sub(r"^(?:https?://web\.archive\.org)?/web/\d+[a-z_]*/", "", href)
        if href.startswith(("http://", "https://")):
            links.append(href)
        elif href.startswith("/"):
            links.append(urljoin(base, href))
    return links


def commerce_links(links: list[str], own_host: str) -> dict:
    retail, affiliate = set(), set()
    for link in links:
        host = urlparse(link).netloc.lower()
        if not host or own_host in host:
            continue
        if any(h in host for h in AFFILIATE_HOSTS) or re.search(r"[?&](tag|irclickid|ranMID|utm_medium=affiliate)", link, re.I):
            affiliate.add(link)
        if any(d in host for d in RETAIL_DOMAINS):
            retail.add(link)
        # affiliate redirectors often embed the retailer URL
        embedded = re.search(r"(?:u|url|murl|dest|destination)=(https?%3A%2F%2F[^&]+)", link, re.I)
        if embedded and any(d in embedded.group(1).lower() for d in RETAIL_DOMAINS):
            retail.add(link)
    return {"retail_links": sorted(retail), "affiliate_links": sorted(affiliate)}


def actor_type(url: str) -> str:
    host_path = urlparse(url).netloc.lower().removeprefix("www.") + urlparse(url).path.lower()
    for actor, patterns in ACTOR_TYPES.items():
        if any(p in host_path for p in patterns):
            return actor
    return "general_news_or_other"


def identification(text: str, patterns: dict[str, list[str]]) -> dict:
    lowered = text.lower()
    hits = {level: any(re.search(p, lowered, re.I) for p in patterns.get(level, [])) for level in ["celebrity", "brand", "model", "exact"]}
    level = "none"
    if hits["exact"]:
        level = "exact"
    elif hits["model"] and hits["brand"]:
        level = "model"
    elif hits["brand"]:
        level = "brand"
    elif hits["celebrity"]:
        level = "celebrity_only"
    evidence = ""
    for key in ["exact", "model", "brand"]:
        for p in patterns.get(key, []):
            m = re.search(p, lowered, re.I)
            if m:
                evidence = text[max(0, m.start() - 140): m.end() + 140]
                break
        if evidence:
            break
    return {"id_level": level, "mentions_celebrity": hits["celebrity"], "evidence_span": evidence}


LEVELS = ["brand", "model", "exact"]
LINK_WINDOW = 500  # characters between a celebrity mention and a product mention


def linked_level(text: str, patterns: dict[str, list[str]], window: int = LINK_WINDOW) -> str:
    """Strongest product level mentioned within `window` chars of the celebrity.

    Whole-article co-occurrence is too loose: sneaker sites mention "Kanye" and
    "adidas" on nearly every page, and sidebars mention unrelated celebrities.
    """
    lowered = text.lower()
    celeb = [m.start() for p in patterns.get("celebrity", []) for m in re.finditer(p, lowered, re.I)]
    if not celeb:
        return "none"
    best = "none"
    for level in LEVELS:
        for p in patterns.get(level, []):
            for m in re.finditer(p, lowered, re.I):
                if any(abs(m.start() - c) <= window for c in celeb):
                    best = level
                    break
            if best == level:
                break
    return best


def context_windows(text: str, patterns: dict[str, list[str]], width: int = 300, limit: int = 6) -> list[str]:
    """Non-overlapping excerpts around celebrity/product mentions (for LLM coding)."""
    lowered = text.lower()
    spans: list[tuple[int, int]] = []
    for key in ["exact", "model", "brand", "celebrity"]:
        for p in patterns.get(key, []):
            for m in re.finditer(p, lowered, re.I):
                s, e = max(0, m.start() - width), min(len(text), m.end() + width)
                if not any(s < b and e > a for a, b in spans):
                    spans.append((s, e))
                if len(spans) >= limit:
                    break
    spans.sort()
    return [re.sub(r"\s+", " ", text[s:e]) for s, e in spans[:limit]]


def dup_key(title: str) -> str:
    """Syndicated copies (e.g. News Corp regional mastheads) share a headline."""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()[:80]


SELLOUT = r"sold[\s-]?out|sell(?:s|ing)? out|restock|back in stock|waitlist|wait list|backorder"
PURCHASE_CTA = r"shop (?:the|now|it)|buy (?:now|it|them|here)|where to buy|available (?:now|at|for)|\$\d{2,4}"


def code_article(case: dict, meta: dict, resp, source: str, snapshot: str) -> dict:
    page = resp.text
    title = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', page, re.I) or re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
    title = html.unescape(title.group(1)).strip() if title else ""
    site = re.search(r'<meta[^>]+property="og:site_name"[^>]+content="([^"]+)"', page, re.I)
    text = visible_text(page)
    pub, pub_source = published_time(page, meta["url"])
    if not pub and meta.get("gdelt_seen"):
        seen = meta["gdelt_seen"]
        pub, pub_source = f"{seen[:4]}-{seen[4:6]}-{seen[6:8]}T{seen[9:11]}:{seen[11:13]}:{seen[13:15]}Z", "gdelt_seendate"
    links = outbound_links(page, meta["url"])
    commerce = commerce_links(links, urlparse(meta["url"]).netloc.lower().removeprefix("www."))
    ident = identification(f"{title} {text}", case["identification"])
    link = linked_level(f"{title}. {text}", case["identification"])
    min_level = case.get("coverage", {}).get("relevance_min_level", "brand")
    digest = hashlib.sha256(text.encode()).hexdigest()
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    (TEXT_DIR / f"{digest[:24]}.txt").write_text(f"{title}\n\n{text[:30000]}", encoding="utf-8")
    try:
        pub_day = date.fromisoformat(pub[:10]) if pub else None
    except ValueError:
        pub_day = None
    return {
        "case_id": case["case_id"],
        "url": meta["url"],
        "domain": urlparse(meta["url"]).netloc.lower().removeprefix("www.").split(":")[0],
        "site_name": html.unescape(site.group(1)) if site else "",
        "title": title[:300],
        "published": pub,
        "published_source": pub_source,
        "relative_day": (pub_day - date.fromisoformat(case["event_date"])).days if pub_day else "",
        "discovered_via": meta["discovered_via"],
        "fetch_source": source,
        "wayback_snapshot": snapshot,
        "actor_type": actor_type(meta["url"]),
        **{k: v for k, v in ident.items() if k != "evidence_span"},
        "relevant": ident["id_level"] in {"brand", "model", "exact"} and ident["mentions_celebrity"],
        "linked_level": link,
        "on_topic_rule": link in LEVELS and LEVELS.index(link) >= LEVELS.index(min_level),
        "dup_key": dup_key(title),
        "n_retail_links": len(commerce["retail_links"]),
        "n_affiliate_links": len(commerce["affiliate_links"]),
        "retail_link_domains": ";".join(sorted({urlparse(u).netloc.removeprefix("www.") for u in commerce["retail_links"]})),
        "mentions_sellout_or_restock": bool(re.search(SELLOUT, text, re.I)),
        "has_purchase_cta": bool(re.search(PURCHASE_CTA, text, re.I)),
        "text_chars": len(text),
        "text_sha256": digest,
        "evidence_span": ident["evidence_span"].replace("\n", " ")[:400],
    }


def collect(cases: list[dict], log=print, max_articles: int = 120) -> None:
    articles: list[dict] = []
    volume: list[dict] = []
    for case in cases:
        if not case.get("coverage"):
            continue
        found, vol = discover(case, log)
        volume += vol
        # Seeds first, then GDELT/CDX discoveries, within a per-case budget.
        ordered = sorted(found.values(), key=lambda m: (m["discovered_via"] != "seed", m["discovered_via"]))
        near = case["event_date"]
        budget = min(max_articles, case["coverage"].get("max_articles", max_articles))
        coded = failed = 0
        for meta in ordered[:budget]:
            resp, source, snap = fetch_article(meta["url"], near, meta.get("capture", ""))
            if resp is None:
                failed += 1
                articles.append({"case_id": case["case_id"], "url": meta["url"], "discovered_via": meta["discovered_via"], "fetch_source": "failed"})
                continue
            articles.append(code_article(case, meta, resp, source, snap))
            coded += 1
        log(f"[coverage] {case['case_id']}: discovered {len(found)}, attempted {min(budget, len(ordered))}, coded {coded}, failed {failed}")
        # Write after every case so an interrupted run keeps completed work.
        _write(DERIVED_DIR / "coverage_articles.csv", articles)
        _write(DERIVED_DIR / "gdelt_volume_daily.csv", volume)


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["case_id"])
        writer.writeheader()
        writer.writerows(rows)
