"""Cached public-data collectors for the association measures.

All HTTP goes through implicit_ads.demo.http (disk cache, per-host throttling, bounded retries).
Every collector writes a long-format CSV/JSONL under data/derived/assoc/ and never overwrites raw caches.
"""

from __future__ import annotations

import re

from ..config import Entity


def matcher(entity: Entity) -> re.Pattern:
    """Word-boundary regex for an entity's match strings (used on search queries and headlines)."""
    alts = sorted((re.escape(p) for p in entity.patterns if p), key=len, reverse=True)
    before = "".join(f"(?<!{re.escape(w)} )" for w in entity.exclude_before)
    after = f"(?!\\s+(?:{'|'.join(re.escape(w) for w in entity.exclude_after)})\\b)" if entity.exclude_after else ""
    return re.compile(before + r"(?<![\w])(?:" + "|".join(alts) + r")(?![\w])" + after, re.IGNORECASE)


def short_matcher(entity: Entity) -> re.Pattern:
    """Matcher for short texts (search queries, free-association items): adds `match_short` strings."""
    if not entity.match_short:
        return matcher(entity)
    from dataclasses import replace

    return matcher(replace(entity, match=entity.match + entity.match_short))
