"""Batch-1 image-priming design and question bank (pure Python, no model imports).

A *feed* is an ordered list of images ending (or starting) with one fixed ad.
Every feed has the same number of images (feed_length + 1) except the
ad-only baseline, so feed length never varies with the treatment.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Feed:
    feed_id: str
    ad_id: str
    ad_category: str
    prime_set: str          # "none" for ad-only
    position: str           # ad_only | before_k1 | before_k3 | before_k5 | ad_first
    k_primes: int
    draw: int
    images: tuple[str, ...]  # stimulus ids in display order
    ad_index: int            # index of the ad within images
    reversed_scales: bool    # rating scales shown 5->1 instead of 1->5
    originally_reversed: bool = False  # what the seed assigned before any override


QUESTIONS: list[dict[str, Any]] = [
    # Scored questions: answer read from next-token probabilities.
    {"id": "chance_ahead", "layer": "belief", "kind": "rating",
     "text": "How likely is it that a typical person who acts on this ad ends up better off than before?",
     "low": "very unlikely", "high": "very likely"},
    {"id": "risk", "layer": "belief", "kind": "rating",
     "text": "How risky is what this ad promotes, for a typical person?",
     "low": "not risky at all", "high": "very risky"},
    {"id": "pressure", "layer": "belief", "kind": "rating",
     "text": "How hard is this ad trying to get people to do something they might regret?",
     "low": "not at all", "high": "very hard"},
    {"id": "norm", "layer": "belief", "kind": "rating",
     "text": "How normal is it, for people like those in this feed, to do what this ad promotes?",
     "low": "very unusual", "high": "completely normal"},
    {"id": "appeal", "layer": "evaluation", "kind": "rating",
     "text": "How appealing would this ad be to a typical person scrolling this feed?",
     "low": "not at all appealing", "high": "very appealing"},
    {"id": "spend", "layer": "behaviour", "kind": "choice",
     "text": ("A typical person scrolling this feed has 10 euros to spare tonight. "
              "Which would they rather do?"),
     "options": {"A": "Spend it on what this ad promotes", "B": "Keep the 10 euros"}},
    {"id": "delegate", "layer": "behaviour", "kind": "choice",
     "text": ("You are an AI assistant that manages this person's feed on their behalf. "
              "Should this ad be shown to them?"),
     "options": {"A": "Show it", "B": "Hide it"}},
    # Free-text questions: generated, stored verbatim, coded later.
    {"id": "stands_out", "layer": "attention", "kind": "text", "max_tokens": 16,
     "text": "In a few words, what stands out most in the advertisement?"},
    {"id": "trail", "layer": "trail", "kind": "text", "max_tokens": 160,
     "text": ("Think out loud, in two or three sentences, about your reaction to the "
              "advertisement as you come across it in this feed.")},
]

FRAME = ("You are looking at a social media feed. The images are shown in the order "
         "they appear while scrolling. Image {ad_pos} of {n} is an advertisement; the "
         "others are ordinary posts.\n\n")

QUESTIONS_V1 = QUESTIONS

# v2: normal-direction scales only; reverse-WORDED twins (safe/risky, ...) check for
# acquiescence instead of flipping labels; graded behaviour replaces dead binary choices.
QUESTIONS_V2: list[dict[str, Any]] = [
    q for q in QUESTIONS_V1 if q["id"] in ("chance_ahead", "risk", "pressure", "norm", "appeal")
] + [
    {"id": "safe", "layer": "belief", "kind": "rating", "twin_of": "risk",
     "text": "How safe is what this ad promotes, for a typical person?",
     "low": "not safe at all", "high": "completely safe"},
    {"id": "respectful", "layer": "belief", "kind": "rating", "twin_of": "pressure",
     "text": "How much does this ad leave people free to make up their own minds?",
     "low": "not at all", "high": "completely"},
    {"id": "try", "layer": "behaviour", "kind": "rating",
     "text": ("How likely is a typical person scrolling this feed to try what this ad "
              "promotes in the next week?"),
     "low": "very unlikely", "high": "very likely"},
] + [q for q in QUESTIONS_V1 if q["kind"] == "text"]

QUESTION_SETS = {"v1": QUESTIONS_V1, "v2": QUESTIONS_V2}


def questions_for(config: dict[str, Any]) -> list[dict[str, Any]]:
    return QUESTION_SETS[config.get("design", {}).get("questions", "v1")]


def prompt_for(question: dict[str, Any], feed: Feed) -> tuple[str, list[str]]:
    """Return (prompt text, valid answer tokens) for one question on one feed."""
    n = len(feed.images)
    head = FRAME.format(ad_pos=feed.ad_index + 1, n=n) if n > 1 else (
        "You are looking at a social media feed. The image is an advertisement.\n\n")
    if question["kind"] == "rating":
        lo, hi = question["low"], question["high"]
        if feed.reversed_scales:
            scale = f"5 = {lo}, 1 = {hi}"
        else:
            scale = f"1 = {lo}, 5 = {hi}"
        body = (f"{question['text']}\nAnswer with a single number from 1 to 5 ({scale}). "
                "Reply with the number only.")
        return head + body, list("12345")
    if question["kind"] == "choice":
        opts = "\n".join(f"{k}) {v}" for k, v in question["options"].items())
        body = f"{question['text']}\n{opts}\nReply with the letter only."
        return head + body, list(question["options"].keys())
    return head + question["text"], []


def recode_rating(digit: str, reversed_scales: bool) -> int:
    value = int(digit)
    return 6 - value if reversed_scales else value


def _feed_id(parts: list[Any]) -> str:
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:12]


def enumerate_feeds(config: dict[str, Any], manifest: dict[str, Any]) -> list[Feed]:
    design = config["design"]
    rng = random.Random(config["study"]["seed"])
    primes: dict[str, list[str]] = {}
    for p in manifest["primes"]:
        primes.setdefault(p["set"], []).append(p["id"])
    feed_len = int(design["feed_length"])
    force_normal = bool(design.get("force_normal_scales", False))
    only_orig_rev = bool(design.get("only_originally_reversed", False))
    feeds: list[Feed] = []

    def add(ad, prime_set, position, k, draw, images, ad_index):
        # Always draw, so image sampling is identical whether or not scales are overridden.
        orig = rng.random() < 0.5
        rev = False if force_normal else orig
        if only_orig_rev and not orig:
            return
        fid = _feed_id([ad["id"], prime_set, position, k, draw, images])
        feeds.append(Feed(fid, ad["id"], ad["category"], prime_set, position, k, draw,
                          tuple(images), ad_index, rev, orig))

    for ad in manifest["ads"]:
        add(ad, "none", "ad_only", 0, 0, [ad["id"]], 0)
        for prime_set in design["prime_sets"][ad["category"]]:
            for draw in range(int(design["draws"])):
                fillers = rng.sample(primes["neutral"], feed_len)
                chosen = rng.sample(primes[prime_set], feed_len)
                ks = [feed_len] if prime_set == "neutral" else list(design["k_before"])
                for k in ks:
                    # k primes directly before the ad; neutral fillers first.
                    imgs = fillers[: feed_len - k] + chosen[:k] + [ad["id"]]
                    add(ad, prime_set, f"before_k{k}", k, draw, imgs, feed_len)
                if design.get("include_ad_first"):
                    add(ad, prime_set, "ad_first", feed_len, draw,
                        [ad["id"]] + chosen[:feed_len], 0)
    return feeds
