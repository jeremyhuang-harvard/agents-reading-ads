"""Command-line entry point: ``python -m implicit_ads.demo``.

Stages (run in order by default):
  archive    Wayback product-page snapshots and tracked commerce URLs
  attention  Google Trends + Wikipedia pageviews
  coverage   article discovery, fetch and rule-based coding
  classify   optional local Qwen labels (requires `make qwen-server`)
  validate   score rule and Qwen coding against hand-coded gold labels
  spillover  focal vs sibling vs competitor attention, inventory, co-mentions
  build      timelines, figures and summary

All network access is cached under data/raw/demo, so reruns are cheap and do
not re-hit sources. No metered LLM API is used.
"""

from __future__ import annotations

import argparse
import time

from . import archive, attention, build, classify, coverage, spillover, validate
from .config import ensure_dirs, load_cases

DEFAULT_STAGES = ["archive", "attention", "coverage", "spillover", "build"]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stages", default=",".join(DEFAULT_STAGES), help="comma-separated stages")
    parser.add_argument("--cases", default="", help="comma-separated case ids (default: all)")
    parser.add_argument("--max-articles", type=int, default=120, help="per-case article fetch budget")
    args = parser.parse_args(argv)

    cases = load_cases(only=[c for c in args.cases.split(",") if c] or None)
    ensure_dirs()
    started = time.monotonic()

    def log(msg: str) -> None:
        print(f"[{time.monotonic() - started:7.1f}s] {msg}", flush=True)

    for stage in [s.strip() for s in args.stages.split(",") if s.strip()]:
        log(f"=== stage {stage} ===")
        if stage == "archive":
            archive.collect(cases, log)
        elif stage == "attention":
            attention.collect_trends(cases, log)
            attention.collect_pageviews(cases, log)
        elif stage == "coverage":
            coverage.collect(cases, log, max_articles=args.max_articles)
        elif stage == "classify":
            classify.run(cases, log)
        elif stage == "validate":
            validate.run(cases, log)
        elif stage == "spillover":
            spillover.run(cases, log)
        elif stage == "build":
            build.run(cases, log)
        else:
            raise SystemExit(f"unknown stage {stage}")
    log("done")


if __name__ == "__main__":
    main()
