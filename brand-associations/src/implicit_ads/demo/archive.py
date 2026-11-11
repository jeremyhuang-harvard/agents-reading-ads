"""Archived product-page snapshots (Internet Archive Wayback Machine).

For each case we enumerate archived URLs under the brand's product-page
prefixes (CDX API), attribute every capture to a product key (style code or
Shopify handle), and fetch one raw capture per product per day to parse page
status, price and size-level availability.

Two observed products are written:
- ``archive_captures.csv``: every CDX row, including tracking/affiliate query
  strings, which are themselves evidence of commerce links circulating;
- ``archive_snapshots.csv``: parsed page observations.

Availability is an inventory observation, not a sales count. Shopify
``available`` can be true for preorder/backorder.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date
from urllib.parse import parse_qs, urlencode, urlparse

from . import http
from .config import DERIVED_DIR

CDX = "https://web.archive.org/cdx/search/cdx?"
AFFILIATE_KEYS = ("irclickid", "irgwc", "ranMID", "ranSiteID", "clickid", "afsrc", "aff", "affiliate")


def cdx_rows(prefix: str, start: str, end: str, regex: str | None = None, limit: int = 2000) -> list[dict]:
    params = {
        "url": prefix,
        "from": start,
        "to": end,
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype",
        "filter": "statuscode:200",
        "limit": limit,
    }
    query = urlencode(params)
    if regex:
        query += "&" + urlencode({"filter": f"original:{regex}"})
    resp = http.get(CDX + query)
    if not resp.ok:
        raise RuntimeError(f"CDX query failed for {prefix}: {resp.error}")
    rows = resp.json() or []
    if not rows:
        return []
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:]]


def commerce_tags(url: str) -> dict[str, str]:
    """Return tracking parameters that reveal affiliate or email traffic."""
    qs = {k.lower(): v[0] for k, v in parse_qs(urlparse(url).query).items()}
    medium = qs.get("utm_medium", "")
    ecid = qs.get("ecid", "")
    channel = ""
    partner = ""
    if medium.lower() == "affiliate" or any(k.lower() in qs for k in AFFILIATE_KEYS) or ecid.lower().startswith("af_"):
        channel = "affiliate"
        partner = qs.get("utm_campaign", "") or (ecid[3:] if ecid.lower().startswith("af_") else "")
    elif medium.lower() in {"email", "emarsys"} or "sc_src" in qs or ecid.lower().startswith("db_"):
        channel = "email"
        partner = qs.get("utm_campaign") or ecid
    elif qs.get("cm_mmc") or medium:
        channel = "paid_or_tracked"
        partner = qs.get("cm_mmc") or qs.get("utm_source", "")
    return {"channel": channel, "partner": partner}


def product_key(url: str, parser: str, sku_regex: str) -> str | None:
    parsed = urlparse(url)
    if parser == "newbalance":
        qs = parse_qs(parsed.query)
        for key, values in qs.items():
            if key.endswith("_style") and re.fullmatch(sku_regex, values[0]):
                return values[0]
        return None  # family page; resolved from page content after fetch
    if parser == "adidas":
        match = re.search(rf"/({sku_regex})\.html", parsed.path)
        return match.group(1) if match else None
    if parser == "shopify":
        match = re.search(r"/products/([a-z0-9-]+)$", parsed.path.rstrip("/"))
        return match.group(1) if match else None
    raise ValueError(f"unknown parser {parser}")


# ---------------------------------------------------------------- parsers


def parse_adidas(text: str) -> dict:
    # Rendered callout only; the JS template contains "{0}" and never matches \d+.
    countdown = re.search(r"COMING SOON!?(?:\s|<[^>]+>)*Available in (\d+) days", text)
    meta = re.search(r'itemprop="availability"\s+content="https?://schema\.org/(\w+)"', text)
    status = "unknown"
    if countdown:
        status = "coming_soon"
    elif meta:
        status = {"InStock": "in_stock", "OutOfStock": "out_of_stock", "PreOrder": "preorder"}.get(meta.group(1), meta.group(1))
    add_to_bag_disabled = bool(re.search(r'addtocartbutton[^"]*disabled[^>]*>\s*<span class="text">\s*Add To Bag', text))
    price = re.search(r'itemprop="price"[^>]*content="([\d.]+)"', text) or re.search(r'data-sale-price="([\d.]+)"', text)
    return {
        "page_status": status,
        "countdown_days": int(countdown.group(1)) if countdown else None,
        "list_price": price.group(1) if price else None,
        "sizes_total": None,
        "sizes_available": None,
        "page_style": None,
        "add_to_bag_disabled": add_to_bag_disabled,
    }


def parse_newbalance(text: str) -> dict:
    sizes: dict[str, str] = {}
    for size, state in re.findall(r'data-attr-value="(\d{1,2}(?:\.5)?)"[^>]*?\b(selectable|unselectable)\b', text):
        sizes.setdefault(size, state)
    avail = re.search(r'"availability":"https?://schema.org/(\w+)"', text)
    price = re.search(r'"price":"([\d.]+)"', text)
    style = re.search(r"/is/image/NB/([a-z0-9]+)_nb_0\d", text)
    return {
        "page_status": avail.group(1) if avail else "unknown",
        "countdown_days": None,
        "list_price": price.group(1) if price else None,
        "sizes_total": len(sizes) or None,
        "sizes_available": sum(1 for s in sizes.values() if s == "selectable") if sizes else None,
        "page_style": style.group(1).upper() if style else None,
    }


def parse_shopify(text: str) -> dict:
    variants: dict[str, str] = {}
    for match in re.finditer(r'\{"id":\d+,"title":"([^"]+)","option1":"[^"]*"[^{}]*?"available":(true|false)', text):
        variants.setdefault(match.group(1), match.group(2))
    price = re.search(r"\$(\d{2,3}\.\d{2})", text)
    return {
        "page_status": "preorder_capable" if "preorder" in text.lower() else "standard",
        "countdown_days": None,
        "list_price": price.group(1) if price else None,
        "sizes_total": len(variants) or None,
        "sizes_available": sum(1 for v in variants.values() if v == "true") if variants else None,
        "page_style": None,
    }


PARSERS = {"adidas": parse_adidas, "newbalance": parse_newbalance, "shopify": parse_shopify}


def collect(cases: list[dict], log=print) -> None:
    capture_rows: list[dict] = []
    snapshot_rows: list[dict] = []
    for case in cases:
        spec = case.get("archive")
        if not spec:
            log(f"[archive] {case['case_id']}: no archive spec; skipped")
            continue
        event = date.fromisoformat(case["event_date"])
        focal = case["focal"].get("sku")
        rows = []
        for prefix in spec["prefixes"]:
            try:
                rows += cdx_rows(prefix, spec["from"], spec["to"])
            except RuntimeError as exc:
                log(f"[archive] {case['case_id']}: {exc}")
        rows = [r for r in rows if not r["original"].endswith((".oembed", ".js", ".json", ".xml"))]
        log(f"[archive] {case['case_id']}: {len(rows)} CDX rows")

        # One fetch per (product key, day); family pages are keyed after parsing.
        by_day: dict[tuple, dict] = {}
        for row in rows:
            key = product_key(row["original"], spec["parser"], spec["sku_regex"])
            ts = row["timestamp"]
            day = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
            tags = commerce_tags(row["original"])
            capture_rows.append({
                "case_id": case["case_id"], "capture": ts, "capture_date": day,
                "relative_day": (date.fromisoformat(day) - event).days,
                "product_key": key or "", "is_focal": key == focal,
                "commerce_channel": tags["channel"], "commerce_partner": tags["partner"],
                "original_url": row["original"],
            })
            group = (key or urlparse(row["original"]).path, day)
            # Prefer the focal product and clean URLs (fewer query params).
            current = by_day.get(group)
            if current is None or len(row["original"]) < len(current["original"]):
                by_day[group] = row

        # Prioritise focal product, then the event window, then everything else.
        def priority(item):
            (key, day), _ = item
            rel = abs((date.fromisoformat(day) - event).days)
            return (0 if key == focal or (focal and focal.lower() in key.lower()) else 1, rel)

        budget = spec.get("max_fetches", 60)
        for (key, day), row in sorted(by_day.items(), key=priority)[:budget]:
            raw_url = f"https://web.archive.org/web/{row['timestamp']}id_/{row['original']}"
            resp = http.get(raw_url)
            base = {
                "case_id": case["case_id"], "capture": row["timestamp"], "capture_date": day,
                "relative_day": (date.fromisoformat(day) - event).days, "archive_url": raw_url,
            }
            if not resp.ok:
                snapshot_rows.append({**base, "product_key": key, "error": resp.error})
                continue
            parsed = PARSERS[spec["parser"]](resp.text)
            resolved = key if re.fullmatch(spec["sku_regex"], key or "") else (parsed.get("page_style") or key)
            snapshot_rows.append({
                **base, "product_key": resolved, "is_focal": resolved == focal,
                **parsed, "bytes": len(resp.body), "error": "",
            })
        log(f"[archive] {case['case_id']}: parsed {sum(1 for r in snapshot_rows if r['case_id']==case['case_id'])} snapshots")

    _write(DERIVED_DIR / "archive_captures.csv", capture_rows)
    _write(DERIVED_DIR / "archive_snapshots.csv", snapshot_rows)


def _write(path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
