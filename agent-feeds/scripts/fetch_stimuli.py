#!/usr/bin/env python3
"""Rebuild the stimulus images (data/raw/stimuli_batch1, stimuli_batch2) byte-for-byte.

Added for the public release, which ships no images. Every stimulus is listed with its
SHA-256 in config/stimuli/batch{1,2}_manifest.json:

* ads: Snap Ads Gallery creatives collected by ../ad-library. The source file (source_sha256)
  is taken from ../ad-library/data/raw if you have already run its fetch_media.py, otherwise
  downloaded from the URL in ../ad-library/data/media_manifest.csv. It is then re-encoded
  exactly as we did: Pillow, convert("RGB"), JPEG quality 95.
* primes: Wikimedia Commons files. The 960-px-wide Commons thumbnail is downloaded through
  the Commons API and re-encoded with Pillow, convert("RGB"), JPEG quality 90. Licences and
  authors are recorded per image in the manifest; respect them if you reuse the images.

    uv run --extra vlm python scripts/fetch_stimuli.py      # needs Pillow (in the vlm extra)

Each written file is checked against the manifest SHA-256. Pillow/libjpeg versions can in
principle change JPEG bytes; we verified a byte-identical rebuild with Pillow 13.0.0.
run_priming.py refuses to run on any mismatch, so a mismatch is reported loudly here.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ADLIB = ROOT.parent / "ad-library"
UA = "agents-reading-ads-replication/1.0 (non-commercial academic research)"
AD_QUALITY, PRIME_QUALITY, PRIME_WIDTH = 95, 90, 960


def get(url: str) -> bytes:
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:  # Wikimedia rate-limits bursts; back off and retry
            if e.code != 429 and e.code < 500:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or min(120, 5 * 2 ** attempt)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(raw: bytes, quality: int) -> bytes:
    buf = io.BytesIO()
    Image.open(io.BytesIO(raw)).convert("RGB").save(buf, "JPEG", quality=quality)
    return buf.getvalue()


def ad_source(source_sha: str, media: dict[str, dict]) -> bytes:
    row = media[source_sha]
    local = ADLIB / row["local_path"]
    if local.exists() and sha(local.read_bytes()) == source_sha:
        return local.read_bytes()
    data = get(row["url"])
    if sha(data) != source_sha:
        raise RuntimeError(f"source checksum mismatch for {source_sha}; try ../ad-library/scripts/fetch_media.py")
    return data


def prime_source(title: str) -> bytes:
    q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo",
                                "iiprop": "url", "iiurlwidth": PRIME_WIDTH, "format": "json"})
    info = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))
    page = next(iter(info["query"]["pages"].values()))
    return get(page["imageinfo"][0]["thumburl"])


def main() -> int:
    media = {r["sha256"]: r for r in csv.DictReader((ADLIB / "data" / "media_manifest.csv").open())}
    done: set[str] = set()
    bad = 0
    for man in ("config/stimuli/batch1_manifest.json", "config/stimuli/batch2_manifest.json"):
        m = json.loads((ROOT / man).read_text())
        items = [("ad", a) for a in m["ads"]] + [("prime", p) for p in m["primes"]]
        for kind, it in items:
            dst = ROOT / it["local"]
            if it["local"] in done or (dst.exists() and sha(dst.read_bytes()) == it["sha256"]):
                done.add(it["local"])
                continue
            if kind == "ad":
                out = encode(ad_source(it["source_sha256"], media), AD_QUALITY)
            else:
                out = encode(prime_source(it["title"]), PRIME_QUALITY)
                time.sleep(1.0)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(out)
            done.add(it["local"])
            if sha(out) != it["sha256"]:
                bad += 1
                print(f"MISMATCH {it['id']}: rebuilt file differs from the manifest checksum", file=sys.stderr)
    print(f"{len(done)} stimulus files in place; {bad} checksum mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
