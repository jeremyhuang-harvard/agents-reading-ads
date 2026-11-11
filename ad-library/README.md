# ad-library: scraping public ad libraries and representing firms by their ads

Original code and data from our betting-ads project (October 2026). Two stages:

1. **Collection.** Bounded, checkpointed collectors for the **Snap Ads Gallery** (public,
   no account needed), plus five-ad proofs of concept on the **Microsoft Advertising (Bing) EU
   Ad Library** and the **TikTok Commercial Content Library**. Every capture keeps the verbatim API
   response, a normalized record per ad, and a SHA-256 for every creative file.
2. **Firm representations.** Every unique creative of five French sports-betting firms
   (Winamax, PMU, Unibet, Betsson, bet365) is coded by a model against a frozen codebook, and
   each firm is represented by the mix of cues its ads use: what they borrow meaning from
   (fandom, national pride, money, humour...), how they frame betting, what offer they push,
   what dominates the creative, which sports and events they attach to. From those we compare
   strategies: firm profiles, cue similarity between firms and over time, and the features
   most representative of each firm.

Results: [`../results/RESULTS.md`](../results/RESULTS.md) part 2. Interpretation:
[`../my-takeaways.md`](../my-takeaways.md). Every file: [`../DATA.md`](../DATA.md) part 1.
Our working memo linking the panel to *Ads as Cues*: [`docs/ads_as_cues_data_linkages.md`](docs/ads_as_cues_data_linkages.md).

## Layout

```
config/   collection rosters, the frozen association codebook, validation codebook and sample spec
src/      collectors, backfill, labelling, analysis and report builders (run from this folder)
scripts/  added for this release: make_media_manifest.py, fetch_media.py
data/raw/        library captures, one folder per run (creatives not included)
data/processed/  our labels, panels, summaries and validation runs
data/media_manifest.csv   every creative's SHA-256 and public URL
docs/     plans, collection results, measurement memos, feasibility notes
tests/    the original offline tests (137 pass with `uv run --locked --all-groups pytest`)
```

## Get the creatives back

The ad images and videos are third-party copyrighted works and are not redistributed. Re-download
them from the public libraries and verify them against our checksums:

```bash
python scripts/fetch_media.py --run snap_fr_betting_competitors   # the five-firm panel (~400 MB)
python scripts/fetch_media.py                                    # everything (~0.7 GB, 1,480 files)
```

Files land where the original code expects them. Snap links recorded at collection time still
worked when we checked (November 2026); if one has expired the script asks the public Snap detail
endpoint for a fresh link. TikTok's signed video links expire within a day, so those five videos
have to be re-found by hand from the `detail_url` in the manifest. Please respect each library's
terms and rate limits; the scripts pause between requests.

## Rerun

```bash
uv sync --locked --all-groups
```

Collection (no key; network):

```bash
# 1,000-ad pilot corpus (betting / alcohol / controls in FR, DE, NL)
uv run python src/collect_snap_ads.py --roster config/snap_1000_roster.json --target 1000 \
  --max-storage-gb 30 --per-file-max-mb 250 --detail-limit 0 --delay-seconds 0.3 \
  --output-root data/raw/snap_1000
# five-firm French sports-betting panel (quota 1,000 per firm)
uv run python src/collect_snap_ads.py --roster config/snap_fr_sports_betting_competitors_5x1000_v1.json \
  --target 5000 --output-root data/raw/snap_fr_betting_competitors
# Story ads keep their media inside composite_preview.ad_snaps; older collector versions missed it
uv run python src/backfill_story_media.py data/raw/snap_fr_betting_competitors/run_id=<RUN_ID>
# Bing proof of concept
uv run python src/collect_bing_ads.py --limit 5 --output-root data/raw/bing_poc
```

The TikTok sample was gathered by hand from public library pages (no collector script); its
selection is described in `data/raw/tiktok_sin_poc/run_id=*/manifest.json`.

A new collection will not reproduce ours: ads are added, paused and removed, and impression counts
keep growing. Our captures are the record.

Firm representations (needs the creatives, see above):

```bash
RUN=data/raw/snap_fr_betting_competitors/run_id=2026-10-21T005219.747976+0000
BF=data/raw/snap_fr_betting_competitors/story_backfill_run_id=2026-10-21T005219.747976+0000
# open-ended discovery on 20 creatives per firm, used to draft the codebook (Claude Code CLI)
uv run --with opencv-python-headless python src/discover_competitor_associations.py \
  --run-dir $RUN --backfill-dir $BF --output-dir data/processed/competitor_discovery_v1
# code all 951 unique creatives with the frozen codebook (Claude Code CLI; mlx-whisper for audio)
uv run --with opencv-python-headless --with mlx-whisper --with av python src/label_competitor_creatives.py \
  --run-dir $RUN --backfill-dir $BF --output-dir data/processed/competitor_labels_v1
# free, offline, stdlib: ad-level panel and firm profiles, then Ads-as-Cues metrics
python src/analyze_competitor_positioning.py --run $RUN --backfill $BF \
  --labels data/processed/competitor_labels_v1 --out data/processed/competitor_analysis_v1
python src/ads_as_cues_metrics.py
# HTML landscape report with creative thumbnails (needs the creatives and opencv)
uv run --with opencv-python-headless python src/build_competitor_report_data.py
python src/render_competitor_landscape.py
```

The labelling scripts call Sonnet through the logged-in Claude Code CLI (`claude -p`), one
creative per call with read-only file access. You need Claude Code with your own account or
`ANTHROPIC_API_KEY`. The two offline steps are free and rebuild our committed outputs byte for byte
(checked in `../tests/test_results.py`).

Validation packet and GABRIEL runs:

```bash
uv run python src/build_snap_validation_sample.py --records data/raw/snap_1000/run_id=<RUN_ID>/records.jsonl \
  --spec config/snap_validation_sample_v1.json --codebook config/snap_validation_codebook_v1.json \
  --output-dir data/processed/snap_validation_v1
uv run python src/run_snap_validation_gabriel.py --packet-manifest data/processed/snap_validation_v1/manifest.json \
  --codebook config/snap_validation_codebook_v1.json --output-dir data/processed/snap_validation_v1/gabriel_image_arm \
  --expected-count 30 --parallelism 2 --reset
uv run python src/run_gabriel_salience_poc.py --manifest data/raw/bing_poc/run_id=<RUN_ID>/manifest.json
```

GABRIEL runs went through the Hermes agent CLI with a ChatGPT login (`--provider openai-codex`,
model `gpt-5.6-sol`; see `make_hermes_response_fn` in `src/run_gabriel_salience_poc.py`). To rerun
with your own key, drop the custom `response_fn` and let GABRIEL call the OpenAI API with
`OPENAI_API_KEY`.

## What changed from the original repository

- Excluded: creatives and all copies of them; an unrelated data workstream and its tests; private
  planning documents; an internal guard script that forbade committing data (and its test); the
  HTML reports and `report_data.json`, which embed creative thumbnails (rebuild them with the
  commands above).
- Absolute paths in four scripts (`ads_as_cues_metrics.py`, `build_competitor_report_data.py`,
  `render_competitor_landscape.py`) and in saved JSON/CSV files were made relative to this folder.
- `Makefile`: removed the `boundaries` target that called the excluded guard.
- `docs/ads_as_cues_data_linkages.md`: removed a closing section of internal open questions.
- `data/processed/snap_validation_v1/*/*/raw/image_arm_responses.csv`: blanked the `image_data`
  column (a base64 copy of each creative).
- Added `scripts/make_media_manifest.py`, `scripts/fetch_media.py` and `data/media_manifest.csv`.
- Files come from three branches of the original repository: `research/issue-7-fr-betting-competitors`
  (the latest), `research/issue-4-snap-validation` (validation packet and GABRIEL runner) and
  `research/implicit-innocuous-ads` (the backgrounded-brand-exposure design docs and codebook,
  a workstream that never reached data).
