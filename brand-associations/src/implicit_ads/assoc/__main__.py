"""CLI: uv run --extra assoc python -m implicit_ads.assoc --stages wiki,gdelt,docs,embed,analyze

Stages (run in order; each reads the previous stages' files under data/derived/assoc/):
  wiki         Wikipedia titles, pageviews (size), article paragraphs (documents)
  gdelt        GDELT co-coverage counts (--gdelt-scope all|pairs)          ~70 min for the pilot frame
  docs         GDELT headlines per entity (documents for representations)   ~20 min
  trends       Google Trends related-queries retrieval shares (US)          ~15 min
  clickstream  Wikimedia clickstream flows (--months 2026-09,2026-10)       ~450 MB streamed per month
  joint        GDELT headlines mentioning both members of each pair (co-mention documents)
  profile      multi-source entity vectors + directed association profiles (Wikipedia text and clicks, news, search, LM)
  embed        Sarkar-style coverage vectors (--backend hash|st:<model>)
  components   associative strength as composition: share of c's vector made of b-coverage, and NNLS loadings
  llm          directed forced-choice retrieval from a local LM (--model, needs mlx-lm on Apple silicon)
  freeassoc    open-vocabulary free association from a local LM (--samples)
  trajectories entity vectors before/after dated events; who moved toward whom (config/assoc/events.json)
  ccnews       stream Common Crawl News WARCs, keep English articles naming frame entities (--months, --files-per-month, --workers)
  ccdocs       build entity mention-context documents and monthly co-mention counts from kept CC-NEWS articles
  event        weekly composition before/after a campaign (config `events`; --event id)
  analyze      pair panel, summary table, figures
"""

from __future__ import annotations

import argparse
import sys
import time

from . import analyze, config

ALL = ["wiki", "gdelt", "docs", "joint", "trends", "clickstream", "embed", "components", "llm", "freeassoc", "event", "trajectories", "ccnews", "ccdocs", "profile", "analyze"]
DEFAULT = ["wiki", "gdelt", "docs", "embed", "analyze"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m implicit_ads.assoc")
    ap.add_argument("--config", default=str(config.DEFAULT_CONFIG))
    ap.add_argument("--stages", default=",".join(DEFAULT), help=f"comma list from {ALL}")
    ap.add_argument("--gdelt-scope", default="all", choices=["all", "pairs"])
    ap.add_argument("--backend", action="append", help="embedding backend(s); repeatable. Default: st:suproteem/RepresentLM-v2")
    ap.add_argument("--mask-names", action="store_true", help="replace entity names in documents with [NAME] before embedding")
    ap.add_argument("--model", default="mlx-community/Qwen3-8B-4bit")
    ap.add_argument("--months", default="2026-09,2026-10")
    ap.add_argument("--event", action="append", help="event id(s) from config `events` (stage event)")
    ap.add_argument("--no-collect", action="store_true", help="trajectories: reuse collected headlines")
    ap.add_argument("--files-per-month", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--samples", type=int, default=30, help="free-association samples per cue")
    args = ap.parse_args(argv)

    stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    unknown = set(stages) - set(ALL)
    if unknown:
        ap.error(f"unknown stages {sorted(unknown)}")
    frame = config.load(args.config)
    t0 = time.time()

    def log(msg):
        print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)

    log(f"frame {frame.version}: {len(frame.celebrities)} celebrities, {len(frame.brands)} brands, {len(frame.pairs)} pairs")
    for stage in ALL:
        if stage not in stages:
            continue
        log(f"== stage {stage}")
        if stage == "wiki":
            from .sources import wiki

            wiki.collect(frame, log)
        elif stage == "gdelt":
            from .sources import gdelt

            gdelt.collect_counts(frame, args.gdelt_scope, log)
        elif stage == "docs":
            from .sources import gdelt

            gdelt.collect_headlines(frame, log=log)
        elif stage == "joint":
            from .sources import gdelt

            gdelt.collect_joint(frame, log=log)
        elif stage == "trends":
            from .sources import trends_related

            trends_related.collect(frame, log=log)
        elif stage == "clickstream":
            from .sources import clickstream

            clickstream.collect(frame, args.months.split(","), log)
        elif stage == "embed":
            from . import embed

            for backend in args.backend or ["st:suproteem/RepresentLM-v2"]:
                embed.run(frame, backend, mask=args.mask_names, log=log)
        elif stage == "components":
            from . import components

            for backend in args.backend or ["st:suproteem/RepresentLM-v2"]:
                components.run(frame, backend, log=log)
        elif stage == "llm":
            from . import llm

            llm.run(frame, args.model, log=log)
        elif stage == "freeassoc":
            from . import freeassoc

            freeassoc.run(frame, args.model, n=args.samples, log=log)
        elif stage == "event":
            import json as _json

            from . import event

            ids = args.event or [e["id"] for e in _json.loads(frame.path.read_text()).get("events", [])]
            for eid in ids:
                event.run(frame, eid, log)
        elif stage == "trajectories":
            from . import trajectories

            trajectories.run(frame, args.backend or ["st:BAAI/bge-base-en-v1.5", "st:suproteem/RepresentLM-v2"],
                             collect_docs=not args.no_collect, only=args.event, log=log)
        elif stage == "ccnews":
            from .sources import ccnews

            ccnews.collect(frame, args.months.split(","), args.files_per_month, args.workers, log)
        elif stage == "ccdocs":
            from .sources import ccnews

            ccnews.build_documents(frame, log=log)
        elif stage == "profile":
            from . import profile

            profile.build(frame, (args.backend or ["st:BAAI/bge-base-en-v1.5"])[0], log=log)
        elif stage == "analyze":
            analyze.run(frame, log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
