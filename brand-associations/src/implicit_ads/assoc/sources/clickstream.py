"""Wikimedia clickstream: directed navigation between entity articles.

The monthly English clickstream dump (~450 MB gzip) lists (referrer, target, type, n) for every
article-to-article transition seen at least 10 times. Reading the Tate McRae article and clicking
through to Adidas is a behavioral, directed association; the reverse click is a separate count.

The dump is streamed and filtered on the fly; only rows touching a frame entity are kept
(data/raw/assoc/clickstream/<month>.filtered.tsv) together with a manifest recording the dump URL,
compressed bytes and SHA-256, so the filtered file is auditable without storing the dump.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from ...demo.http import USER_AGENT
from ..config import DERIVED, RAW, Frame

DUMP = "https://dumps.wikimedia.org/other/clickstream/{month}/clickstream-enwiki-{month}.tsv.gz"


class _HashingReader:
    def __init__(self, raw):
        self.raw, self.sha, self.bytes = raw, hashlib.sha256(), 0

    def read(self, n=-1):
        chunk = self.raw.read(n)
        self.sha.update(chunk)
        self.bytes += len(chunk)
        return chunk


def fetch(month: str, titles: set[str], log=print):
    folder = RAW / "clickstream"
    folder.mkdir(parents=True, exist_ok=True)
    out, manifest = folder / f"{month}.filtered.tsv", folder / f"{month}.manifest.json"
    if out.exists() and manifest.exists():
        if set(titles) <= set(json.loads(manifest.read_text()).get("titles", [])):
            log(f"[clickstream] cached {out.name}")
            return out
        log(f"[clickstream] cached {out.name} lacks new titles; re-streaming")
    url = DUMP.format(month=month)
    log(f"[clickstream] streaming {url}")
    kept = 0
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=120) as resp:
        reader = _HashingReader(resp)
        tmp = out.with_suffix(".tmp")
        with gzip.GzipFile(fileobj=reader) as gz, tmp.open("w") as h:
            for i, line in enumerate(gz):
                prev, curr, *_ = line.decode("utf-8", "replace").split("\t", 2)
                if prev in titles or curr in titles:
                    h.write(line.decode("utf-8", "replace"))
                    kept += 1
                if i % 5_000_000 == 0 and i:
                    log(f"[clickstream] {i:,} rows scanned, {kept:,} kept")
        tmp.replace(out)
    manifest.write_text(json.dumps({"url": url, "compressed_bytes": reader.bytes, "sha256_compressed": reader.sha.hexdigest(),
                                    "rows_kept": kept, "titles": sorted(titles),
                                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=2))
    return out


def collect(frame: Frame, months: list[str], log=print) -> None:
    """Pooled flows over `months` (clickstream_flows.csv), plus per-month flows between frame entities
    (clickstream_flows_monthly.csv) and the full outflow composition of every entity page
    (clickstream_outflow_monthly.csv: where readers go next from each entity's article)."""
    ents = list(csv.DictReader((DERIVED / "wiki_entities.csv").open()))
    title_of = {r["entity"]: r["wiki_title"] for r in ents if r["wiki_title"]}
    entity_of = {t: e for e, t in title_of.items()}
    titles = set(title_of.values())
    flows: dict[tuple[str, str], int] = {}
    outflow: dict[str, int] = {}
    monthly, composition = [], []
    for month in months:
        try:
            path = fetch(month, titles, log)
        except Exception as exc:  # a month missing from the dump server should not stop the panel
            log(f"[clickstream] {month}: {exc}")
            continue
        m_flows: dict[tuple[str, str], int] = {}
        m_out: dict[str, int] = {}
        m_in: dict[str, int] = {}
        dest: dict[str, dict[str, int]] = {}
        for line in path.open():
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 4:
                continue
            prev, curr, typ, n = parts
            n = int(n)
            if curr in titles:
                m_in[curr] = m_in.get(curr, 0) + n
            if prev in titles:
                m_out[prev] = m_out.get(prev, 0) + n
                dest.setdefault(prev, {})[curr] = dest.setdefault(prev, {}).get(curr, 0) + n
                if curr in titles and typ == "link":
                    m_flows[(prev, curr)] = m_flows.get((prev, curr), 0) + n
        for (a, b), n in m_flows.items():
            flows[(a, b)] = flows.get((a, b), 0) + n
            monthly.append({"month": month, "from": entity_of[a], "to": entity_of[b], "n": n,
                            "outflow_from": m_out.get(a, 0), "inflow_to": m_in.get(b, 0)})
        for t, n in m_out.items():
            outflow[t] = outflow.get(t, 0) + n
        for t, d in dest.items():
            for target, n in sorted(d.items(), key=lambda x: -x[1])[:60]:
                composition.append({"month": month, "entity": entity_of[t], "next_page": target, "n": n,
                                    "share_of_outflow": round(n / m_out[t], 6), "target_entity": entity_of.get(target, "")})
        log(f"[clickstream] {month}: {len(m_flows)} entity-to-entity links")
    rows = []
    for c in frame.celebrities:
        for b in frame.brands:
            tc, tb = title_of.get(c.id), title_of.get(b.id)
            if not tc or not tb:
                continue
            rows.append({"celebrity": c.id, "brand": b.id, "n_c_to_b": flows.get((tc, tb), 0), "n_b_to_c": flows.get((tb, tc), 0),
                         "outflow_c": outflow.get(tc, 0), "outflow_b": outflow.get(tb, 0)})
    for name, data in (("clickstream_flows.csv", rows), ("clickstream_flows_monthly.csv", monthly),
                       ("clickstream_outflow_monthly.csv", composition)):
        if data:
            with (DERIVED / name).open("w", newline="") as h:
                w = csv.DictWriter(h, fieldnames=list(data[0]))
                w.writeheader()
                w.writerows(data)
    log(f"[clickstream] {sum(r['n_c_to_b'] > 0 for r in rows)} celebrity->brand and "
        f"{sum(r['n_b_to_c'] > 0 for r in rows)} brand->celebrity links with traffic across {len(months)} months")
