# Demo pipeline: collecting the end-to-end chain

`make demo` runs a cached, rate-limited pipeline over the cases in
[`config/demo_cases.json`](../config/demo_cases.json). It records each link in
the chain—relationship → appearance → identification → amplification →
attention → market response—and labels every timeline row `observed`
(retrieved by the pipeline) or `reported` (company/press claim).

## Stages

| Stage | Source | Writes (`data/derived/demo/`) | Notes |
|---|---|---|---|
| `archive` | Wayback CDX + raw captures of brand product pages | `archive_captures.csv`, `archive_snapshots.csv` | Page status, price, size-level availability; tracked URLs reveal affiliate/email links. One fetch per product per day, capped by `max_fetches`. |
| `attention` | Google Trends (unofficial `pytrends`), Wikimedia pageviews | `trends_daily.csv`, `pageviews_daily.csv` | Trends normalized within payload group; zeros may be below threshold. Pageviews start July 2015. |
| `coverage` | Seed URLs, Wayback CDX publisher discovery, GDELT DOC (2017+) | `coverage_articles.csv`, `gdelt_volume_daily.csv`, `article_text/` | Articles fetched from Wayback where archived (avoids bot walls), live otherwise; rule-based identification level, actor type, retail/affiliate links, sellout mentions. |
| `classify` (optional) | Local Qwen3-8B via `mlx_lm.server` | `coverage_llm_labels.csv` | Prompt `coverage-v2`: excerpts around mentions only. Asks whether the article is about the focal appearance, the identification level and which other products are named. `model_predicted`, kept separate from rule codes. |
| `validate` (optional) | `data/raw/demo/validation/gold_labels_*.csv` | `validation_scores.csv` | Precision and recall of rule v1, rule v2 and Qwen against hand labels, with tuning and held-out splits. |
| `spillover` | Derived tables | `spillover_attention.csv`, `spillover_inventory.csv`, `spillover_mentions.csv`, `spillover_llm_products.csv`; `output/demo/spillover_overview.png`, `spillover_inventory.png` | Compares focal, sibling and competitor products using the roles in config. See [`demo-spillover.md`](demo-spillover.md). |
| `build` | Derived tables | `output/demo/timelines.csv`, `summary.md`, `<case>_chain.png` | Three-panel figure: coverage by identification level, attention and availability. |

**On-topic articles.** An article is on-topic (`on_topic_rule`) when the celebrity is named within 500 characters of a brand, model or exact-product mention. Kanye cases require a model-level mention, because "Kanye" and "adidas" co-occur on nearly every sneaker-site page. `dup_key` groups syndicated copies by headline.

```bash
make test                          # offline parser/coder tests
make demo                          # archive, attention, coverage, build
make demo DEMO_ARGS="--cases taylor_nb550 --stages coverage,build"
make qwen-server                   # in another terminal
make demo-classify                 # optional local-LLM labels
make demo DEMO_ARGS="--stages validate,spillover"
uv run --with python-pptx python scripts/build_demo_slides.py   # demo slides → output/presentation/
uv run --extra demo python scripts/build_findings_report.py     # readable HTML report → output/demo/
```

## Usage limits and cost

- **No metered LLM API calls.** Collection and rule-based coding are plain
  Python. Optional labeling runs on local Qwen.
- **Every HTTP response is cached** under `data/raw/demo/http_cache`; reruns
  and figure changes never re-hit sources. Raw data are gitignored and
  treated as immutable.
- **Per-host throttles:** Wayback 1.5 s, GDELT 6 s (its stated limit is one
  request per 5 s), Wikimedia 0.2 s, other hosts 3 s; Trends 12 s between
  uncached payloads. 429/5xx retries use bounded exponential backoff and
  honor `Retry-After` up to 120 s.
- **Budgets:** `max_fetches` per case for product pages; `--max-articles`
  (default 120) per case for coverage.

## Division of labor for scale-up

- Collection, parsing and counting: deterministic scripts.
- High-volume, low-difficulty labeling (actor type, identification level,
  frame): local Qwen, validated against a hand-coded sample before use.
- Ambiguous cases, exact-SKU verification and synthesis: frontier model or
  human review.

## Known limits

- Archived pages are sparse and irregular; absence of a capture is not
  evidence of anything.
- Availability is inventory, not sales; Shopify `available` can mean
  preorder.
- GDELT DOC does not cover 2015; the Kanye cases rely on seeds and archived
  publisher URL discovery.
- Wayback article copies may postdate publication; publication time comes
  from page metadata or URL path, with the source recorded.
- `pytrends` is unofficial and can break or be throttled; failures are
  logged and do not stop other stages.
