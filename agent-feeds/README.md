# agent-feeds: a vision-language model reads ads in a social-media feed

Original code and every saved run from our agentic-ad-simulations project (October 2026).

**Question.** Hold an advertisement fixed and change only what surrounds it in a feed. Does an AI
agent's reading of the ad move, in which direction, and does it respond to what the surrounding
images *mean* or only to how they *look*?

**Design.** A local vision-language model (Qwen3-VL-8B-Instruct, 4-bit, via MLX; temperature 0) sees
a feed of images in scrolling order: one real ad plus up to five other images. The other images are
neutral posts or a themed set (pubs and beer gardens; drink-driving and crashes; sports wins;
losses and distress; colour-matched "look-alikes" with no meaning). We vary the set, how many
themed images come before the ad (1, 3 or 5) and whether they come after it instead, over several
independent random draws of images. The model then answers one question per forward pass: how
risky, how pushy, how normal, how appealing, how likely a typical person ends up better off, and
(batch 2) how safe, how much it leaves people free to decide and how likely a typical person is
to try the product. Ratings are read from the next-token probabilities over "1".."5", so every
answer is an expected value rather than a sampled digit. It also writes a short free-text
"trail" of its reaction.

Ads are real Snapchat ads from [`../ad-library`](../ad-library): four betting ads (PMU, Unibet,
Betsson, bet365), Heineken ads (regular and alcohol-free), and Fanta and Nike as non-vice
controls. Primes are Wikimedia Commons photos (authors and licences recorded per image).

Results: [`../results/RESULTS.md`](../results/RESULTS.md) part 1. Interpretation:
[`../my-takeaways.md`](../my-takeaways.md). Our findings write-ups at the time:
[`docs/batch1-findings.md`](docs/batch1-findings.md), [`docs/batch2-findings.md`](docs/batch2-findings.md).
Every file: [`../DATA.md`](../DATA.md) part 2.

## Layout

```
config/          study configs (batch1, batch1_rerun, batch2; smoke/baseline for the mock scaffold)
config/stimuli/  stimulus manifests: every ad and prime with its source and SHA-256
src/agentic_ads/ design (priming_design.py), runner (run_priming.py), first-read summaries
                 (analyze_priming.py), and the original mock persona scaffold
runs/            every saved run: feeds.jsonl, responses.jsonl, manifest.json
artifacts/       auto-generated first-read tables for batch 1 (mixed scales; superseded)
exploration/     first probes of the outcome suite, with reasoning traces
docs/            findings, research design, outcome suite, context levers, literature map,
                 prefix-cache audit (docs/notes/)
preregistration/, prompts/, schemas/   instruments from the original scaffold
scripts/         fetch_stimuli.py (added), resume_batch2.sh, eval_prefix_cache.py
tmp/smoke-runs/  six runs of the original mock pipeline (plumbing checks only)
tests/           original unit tests (stdlib; run by `make test` at the top level)
```

## The runs, in the order we made them

| run | what |
|---|---|
| `tmp/smoke-runs/*` | mock-engine plumbing checks of the first scaffold (no model) |
| `runs/batch1-image-priming-7bb222afcc-*` | 6-feed pilot of batch 1 |
| `runs/batch1-image-priming-61d1c48aaf-*` | batch 1: 568 feeds x 9 questions, 166 min; half the feeds had reversed scale labels |
| `runs/batch1-rerun-normal-scale-311cfa8d08-*` | the 276 reversed-scale feeds rerun on the normal scale, same images |
| `runs/batch2-beer-priming-9a960c96e6-*` | batch 2: 888 feeds x 10 questions, resumed after six out-of-memory crashes |

## Rerun

Needs an Apple-silicon Mac (MLX). No API key; the model downloads from Hugging Face on first use.

```bash
uv sync --extra vlm
uv run --extra vlm python scripts/fetch_stimuli.py      # rebuilds all 80 stimulus images, byte-identical
PYTHONPATH=src uv run --extra vlm python -m agentic_ads.run_priming --config config/batch1.toml
PYTHONPATH=src uv run --extra vlm python -m agentic_ads.run_priming --config config/batch1_rerun.toml
PYTHONPATH=src uv run --extra vlm python -m agentic_ads.run_priming --config config/batch2.toml
# after a crash: --resume runs/<run-dir>   (scripts/resume_batch2.sh retries automatically)
PYTHONPATH=src uv run python -m agentic_ads.analyze_priming runs/<run-dir>   # first-read tables
```

`run_priming.py` refuses to run from a dirty Git tree (pass `--allow-dirty` for a throwaway test)
and checks every stimulus against its SHA-256 first. Feed ids and image orders are fixed by the
seed in each config; `../tests/test_results.py` checks that the design code regenerates exactly the
feeds in our runs. Decoding is greedy, and the prefix-cache audit found the uncached path exactly
reproduced 200 stored answers, so on the same model revision and MLX version your answers should
match ours; on other versions expect small numerical drift.

`scripts/fetch_stimuli.py` downloads each ad from the public Snap URL recorded in
`../ad-library/data/media_manifest.csv` (or uses your local copy) and each prime from Wikimedia
Commons, then re-encodes them exactly as we did (Pillow `convert("RGB")`, JPEG quality 95 for ads
and 90 for the 960-px Commons thumbnails). We checked a fresh rebuild against all 80 checksums with
Pillow 13.0.0.

## What changed from the original repository

- Excluded: the stimulus images (ads are third-party creatives; primes are Commons files rebuilt by
  `fetch_stimuli.py`); the HTML versions of the findings (they embed the ads; the Markdown versions
  are here); contact sheets and example feeds built from the ads; run logs with machine paths; a
  machine-specific wrapper script from the `perf/prefix-cache` branch; `AGENTS.md` and the
  scaffold's README, CI and citation file (replaced at the top level).
- `config/stimuli/*.json`: each ad's `source_path` was an absolute path on our machine; it now points
  into `../ad-library/`. The config and manifest hashes recorded in `runs/*/manifest.json` refer to
  the files before this edit.
- `scripts/resume_batch2.sh`: replaced `cd /Users/...` with the script's own repository folder.
- `tests/test_priming_design.py`: the check that batch-2 stimulus files exist now runs only once they
  have been fetched.
- Added `scripts/fetch_stimuli.py`.
- Files come from the `research/initial-scaffold` branch (latest) plus `docs/notes/prefix_cache_assessment.md`
  and `scripts/eval_prefix_cache.py` from `perf/prefix-cache`. The runs, artifacts and smoke runs
  were never committed in the original repository; they are copied from the working copy.
