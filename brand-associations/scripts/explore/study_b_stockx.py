"""Study B: archived StockX product pages around celebrity events (Internet Archive captures only).

Enumerates captures with the Wayback CDX API for product-URL prefixes in a window, fetches
one raw capture per product per day (polite, cached via implicit_ads.demo.http), and parses
product-level market data embedded in the page: salesLast72Hours, lastSale, pricePremium,
lowestAsk, highestBid, deadstockSold (field names vary by page vintage).

No requests go to stockx.com itself. Terms note: see docs/ads-as-cues-linkages.html.

Run: uv run --extra demo python scripts/explore/study_b_stockx.py
Writes output/explore/study_b/stockx_snapshots.csv
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from implicit_ads.demo import http

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "explore" / "study_b"

STUDIES = {
    "taylor_nb550": {
        "event": "2023-09-24", "from": "20230701", "to": "20231231",
        "prefixes": ["stockx.com/new-balance-550-", "stockx.com/nike-dunk-low-retro-white-black",
                     "stockx.com/nike-air-force-1-low-white",
                     "stockx.com/adidas-samba-og-", "stockx.com/new-balance-9060-"],
        "focal": "new-balance-550-white-red",
    },
    "bieber_crocs": {
        "event": "2020-10-13", "from": "20200801", "to": "20210131",
        "prefixes": ["stockx.com/crocs-"],
        "focal": "crocs-classic-clog-justin-bieber",
    },
}

FIELDS = ["salesLast72Hours", "lastSale", "pricePremium", "lowestAsk", "highestBid", "deadstockSold",
          "numberOfAsks", "numberOfBids", "changeValue", "changePercentage", "volatility"]


def cdx(prefix: str, start: str, end: str) -> list[tuple[str, str]]:
    url = "https://web.archive.org/cdx/search/cdx?" + urlencode({
        "url": prefix, "matchType": "prefix", "from": start, "to": end, "output": "json",
        "filter": "statuscode:200", "fl": "original,timestamp", "limit": "5000"})
    resp = http.get(url)
    if not resp.ok:
        return []
    try:
        rows = json.loads(resp.text)[1:]
    except ValueError:
        return []
    return [(o, t) for o, t in rows]


def product_key(original: str) -> str | None:
    m = re.match(r"https?://(?:www\.)?stockx\.com/([a-z0-9][a-z0-9\-]+)/?(?:\?|$)", original)
    if not m:
        return None
    key = m.group(1)
    if key.startswith(("sell", "buy", "search", "api", "en-")) or "/" in key:
        return None
    return key


def parse(text: str, key: str) -> dict:
    """Product-level fields: take values in the segment that follows the product's urlKey."""
    out = {}
    idx = text.find(f'"urlKey":"{key}"')
    seg = text[idx: idx + 20000] if idx >= 0 else ""
    # Older pages: "market":{...} block for the product.
    m = re.search(r'"market":\{(.{0,4000}?)\}', seg or text, re.S)
    scope = (m.group(1) if m else "") + seg[:8000]
    for f in FIELDS:
        mm = re.search(rf'"{f}":(-?[\d.]+)', scope)
        if mm:
            out[f] = float(mm.group(1))
    # Newer pages nest the last sale: "salesInformation":{"lastSale":N,"salesLast72Hours":N}
    mm = re.search(r'"salesInformation":\{"lastSale":(-?[\d.]+),"salesLast72Hours":(\d+)', seg)
    if mm:
        out.setdefault("lastSale", float(mm.group(1)))
        out["salesLast72Hours"] = float(mm.group(2))
    title = re.search(r'"title":"([^"]{3,120})"', seg) or re.search(r"<title>([^<]{3,160})</title>", text)
    out["title"] = title.group(1) if title else ""
    retail = re.search(r'"retailPrice":(\d+(?:\.\d+)?)', seg) or re.search(r'"name":"retail","value":"?(\d+)', seg)
    if retail:
        out["retail"] = float(retail.group(1))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for study, spec in STUDIES.items():
        event = date.fromisoformat(spec["event"])
        caps: dict[tuple[str, str], tuple[str, str]] = {}
        for prefix in spec["prefixes"]:
            for original, ts in cdx(prefix, spec["from"], spec["to"]):
                key = product_key(original)
                if key and (key, ts[:8]) not in caps:
                    caps[(key, ts[:8])] = (original, ts)
        print(study, "product-days", len(caps), "products", len({k for k, _ in caps}), flush=True)
        for (key, day), (original, ts) in sorted(caps.items()):
            resp = http.get(f"https://web.archive.org/web/{ts}id_/{original}")
            if not resp.ok:
                continue
            parsed = parse(resp.text, key)
            d = date(int(day[:4]), int(day[4:6]), int(day[6:8]))
            rows.append({"study": study, "product": key, "is_focal": key == spec["focal"], "capture": ts,
                         "date": d.isoformat(), "relative_day": (d - event).days, **parsed})
        with (OUT / "stockx_snapshots.csv").open("w", newline="") as h:
            fields = ["study", "product", "is_focal", "capture", "date", "relative_day", "title", "retail", *FIELDS]
            w = csv.DictWriter(h, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(study, "parsed", sum(1 for r in rows if r["study"] == study), flush=True)


if __name__ == "__main__":
    main()
