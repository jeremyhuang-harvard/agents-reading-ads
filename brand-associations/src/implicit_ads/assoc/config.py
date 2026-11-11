"""Load and validate the celebrity/brand frame."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "config" / "assoc" / "ambassadors.json"
RAW = ROOT / "data" / "raw" / "assoc"
DERIVED = ROOT / "data" / "derived" / "assoc"
OUTPUT = ROOT / "output" / "assoc"


@dataclass(frozen=True)
class Entity:
    id: str
    kind: str  # "celebrity" | "brand"
    name: str
    wiki: str | None
    gdelt: str
    group: str  # domain for celebrities, category for brands
    match: tuple[str, ...] = ()  # lower-case strings that identify the entity inside search queries
    exclude_after: tuple[str, ...] = ()  # words that disqualify a match when they follow it ("Lincoln Lawyer")
    exclude_before: tuple[str, ...] = ()  # words that disqualify a match when they precede it ("Abraham Lincoln")
    match_short: tuple[str, ...] = ()  # extra strings trusted only in short texts (search queries, free-association items)

    @property
    def patterns(self) -> tuple[str, ...]:
        import unicodedata

        base = self.name.casefold()
        plain = "".join(ch for ch in unicodedata.normalize("NFKD", base) if not unicodedata.combining(ch))
        return tuple(dict.fromkeys((base, plain, *self.match)))


@dataclass(frozen=True)
class Pair:
    celebrity: str
    brand: str
    relation: str
    since: str
    evidence: str
    source: str


@dataclass
class Frame:
    version: str
    start: str
    end: str
    celebrities: list[Entity]
    brands: list[Entity]
    pairs: list[Pair]
    path: Path = field(default=DEFAULT_CONFIG)

    @property
    def entities(self) -> list[Entity]:
        return self.celebrities + self.brands

    def get(self, entity_id: str) -> Entity:
        for e in self.entities:
            if e.id == entity_id:
                return e
        raise KeyError(entity_id)

    def index(self, kind: str) -> dict[str, int]:
        group = self.celebrities if kind == "celebrity" else self.brands
        return {e.id: i for i, e in enumerate(group)}


def load(path: str | Path = DEFAULT_CONFIG) -> Frame:
    path = Path(path)
    raw = json.loads(path.read_text())
    celebs = [Entity(c["id"], "celebrity", c["name"], c.get("wiki"), c.get("gdelt") or f'"{c["name"]}"', c.get("domain", ""),
                     tuple(c.get("match", ())), tuple(c.get("exclude_after", ())), tuple(c.get("exclude_before", ())),
                     tuple(c.get("match_short", ())))
              for c in raw["celebrities"]]
    brands = [Entity(b["id"], "brand", b["name"], b.get("wiki"), b.get("gdelt") or f'"{b["name"]}"', b.get("category", ""),
                     tuple(b.get("match", ())), tuple(b.get("exclude_after", ())), tuple(b.get("exclude_before", ())),
                     tuple(b.get("match_short", ())))
              for b in raw["brands"]]
    pairs = [Pair(p["celebrity"], p["brand"], p.get("relation", ""), p.get("since", ""), p.get("evidence", ""), p.get("source", ""))
             for p in raw["pairs"]]
    frame = Frame(raw["version"], raw["window"]["from"], raw["window"]["to"], celebs, brands, pairs, path)
    validate(frame)
    return frame


def validate(frame: Frame) -> None:
    ids = [e.id for e in frame.entities]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate entity ids: {sorted(dupes)}")
    names = [e.name.casefold() for e in frame.entities]
    if len(set(names)) != len(names):
        raise ValueError("duplicate entity names (candidate strings must be unique)")
    c_ids = {e.id for e in frame.celebrities}
    b_ids = {e.id for e in frame.brands}
    for p in frame.pairs:
        if p.celebrity not in c_ids or p.brand not in b_ids:
            raise ValueError(f"pair references unknown entity: {p}")
        if not p.source.startswith("http"):
            raise ValueError(f"pair without a source URL: {p}")
    seen = set()
    for p in frame.pairs:
        key = (p.celebrity, p.brand)
        if key in seen:
            raise ValueError(f"duplicate pair {key}")
        seen.add(key)
    if frame.start >= frame.end:
        raise ValueError("window.from must precede window.to")
