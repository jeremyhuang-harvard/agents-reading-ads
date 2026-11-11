# brand-associations: directed celebrity-brand associations

Original code and outputs from our implicit-ads project (November 2026). It builds
representations of celebrities and brands from public data and asks a directional question that
a similarity score cannot answer: when people think of the celebrity, does the brand come to mind,
and when they think of the brand, does the celebrity?

Three pieces of work, in the order we did them:

1. **Event demo** (`src/implicit_ads/demo/`, `docs/demo-*.md`). Five celebrity-product appearances
   (Taylor Swift x New Balance 550, Kanye West x Adidas Energy Boost, Meghan Markle x Outland Denim,
   plus two benchmarks) traced from appearance to identification, amplification, search attention,
   coverage and archived product-page stock, with focal vs sibling vs competitor spillover.
2. **Look-size studies** (`scripts/explore/`, `docs/explore-findings.md`). Items worn together in
   one celebrity outfit compete for search attention: the more brands identified in a look, the
   less each one gains.
3. **Directed associations** (`src/implicit_ads/assoc/`, `docs/assoc-design.md`). Forward and
   backward association between celebrities and brands from news coverage (GDELT, Common Crawl
   News), Wikipedia text and reader clickstream, Google related searches, Sarkar-style embedding
   vectors and a local language model's free associations; event studies for Sydney Sweeney x
   Novig and Tate McRae x Adidas; a 110-entity multi-source profile.

The theory behind it is in [`docs/vision.md`](docs/vision.md). Results:
[`../results/RESULTS.md`](../results/RESULTS.md) part 3. Interpretation:
[`../my-takeaways.md`](../my-takeaways.md). Our briefs at the time are self-contained HTML files in
`output/assoc/` and `output/demo/`. Every file: [`../DATA.md`](../DATA.md) part 3.

## Layout

```
config/    entity frame and ambassador pairs (assoc/ambassadors.json), events, demo cases, look lists
src/implicit_ads/   demo pipeline, association measures and sources, profiles, trajectories
scripts/   brief and figure builders, explore/ studies, scaffold check
data/raw/       captured inputs we may share (clickstream extracts, Trends payloads, our model outputs, gold labels)
data/derived/   our derived tables, vectors and samples
output/    briefs, figures and tables
docs/      vision, design, feasibility and findings notes
tests/     original tests (30 pass with `uv run --extra dev --extra demo --with scipy pytest`)
```

## Rerun

No API key. Network access to public sources; the language-model steps need an Apple-silicon Mac.

```bash
make demo                 # event demo: archive, attention, coverage, build (cached; slow first run)
make qwen-server          # in another terminal, for the local-LLM labels
make demo-classify
make assoc                # association measures: wiki, gdelt, docs, embed, analyze
make assoc-llm            # local Qwen retrieval probabilities
uv run --extra assoc python scripts/build_profile_brief.py
uv run python scripts/explore/analyze_study_c.py      # needs numpy
```

Set your own contact address in `USER_AGENT` (`src/implicit_ads/demo/http.py`) first; Wikimedia
asks for one. Fresh runs will differ from ours: news indexes, Trends sampling and Wikipedia all
change over time. The shipped `data/` is the record; `make_results.py` at the top level works only
from it.

## What changed from the original repository

- Excluded: cached web pages and news articles (`data/raw/demo/http_cache/`), Common Crawl News
  full texts (`data/raw/assoc/ccnews/`) and extracted article text (`data/derived/demo/article_text/`),
  all third-party copyright; the 107 MB per-document embedding cache (regenerable; averaged vectors
  are shipped); the StockX-derived Study B table and figure, which our notes flagged as needing
  terms clearance (the script remains); a private meeting outline, its builder and the
  presentation decks; `output/presentation/case_figures.html` and its builder (it embeds the StockX
  figure and imports the excluded outline's styles); a planning note for an internal presentation;
  `AGENTS.md`, the scaffold README and CI.
- `src/implicit_ads/demo/http.py`: our contact email in the User-Agent replaced by a placeholder.
- `scripts/check_scaffold.py`: no longer requires the excluded files or the two `.gitkeep`
  placeholders.
- `docs/ads-as-cues-linkages.html`, `output/demo/implicit_ads_demo_findings.html` and its template:
  removed one internal note and one sentence.
- Files come from the `research/initial-theory` branch; data and outputs were never committed in
  the original repository and are copied from the working copy.
