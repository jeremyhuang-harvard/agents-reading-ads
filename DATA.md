# Data codebook

Every data and output file in this repository, what produced it, and what its fields mean.
The index tables are machine-checked: `tests/test_results.py` fails if a tracked file under a
data, run or output folder is not matched by one of the backticked path patterns below
(`*` matches any characters, including `/`).

Conventions

- **Ours** = produced by our code or our model runs (CC BY 4.0). **Library** = captured verbatim
  from a public ad library or other public source; it stays under that source's terms.
- Paths inside JSON files are relative to the part folder they sit in (for example
  `data/raw/...` inside `ad-library/`). Absolute paths from our machines were rewritten this
  way; nothing else in the saved data was changed except where noted.
- Creatives (images, videos, frames) are never included. Where a file refers to one, it does so
  by SHA-256; `ad-library/data/media_manifest.csv` maps every SHA-256 to its public source URL.

---

## Part 1. `ad-library/`: scraped ad libraries and firm representations

Raw captures (Library). One folder per collection run, named `run_id=<UTC timestamp>`.

| path pattern | what it is |
|---|---|
| `ad-library/data/raw/snap_fr_betting_competitors/run_id=2026-10-21T005219.747976+0000/records.jsonl` | **The five-firm panel.** 3,241 Snap Ads Gallery records, one per ad, for Winamax, PMU, Unibet (`Kindred London Ltd`), Betsson (`Betsson France SA`) and bet365 in France. Fields: `ad_id`; `category`; `query_advertiser` and `query_country` (the search that found it); `captured_at_utc`; HTTP status fields for the search and (skipped) detail requests; `ad` = the full library record (`name` = campaign name, `ad_account_name`, `paying_advertiser_name`, `profile_name`, `status` ACTIVE/PAUSED, `ad_type`, `creative_type`, `headline`, `call_to_action`, `languages`, `start_date`, `impressions_total` and `impressions_map` by EU country, `targeting_v2` with age/gender/device targeting, media download links, `composite_preview.ad_snaps` for multi-snap Story ads); `media` = the primary creative we downloaded (`role`, `media_type`, `url`, `http_status`, `content_type`, `byte_length`, `sha256`, `local_path`); `media_error`. |
| `ad-library/data/raw/snap_fr_betting_competitors/run_id=2026-10-21T005219.747976+0000/manifest.json` | Run manifest: endpoints, capture time, per-firm quota and whether pagination was exhausted or capped, counts of ads/media/errors, storage used. |
| `ad-library/data/raw/snap_fr_betting_competitors/run_id=*/raw/search/*.json` | Verbatim JSON pages returned by the Snap Ads Gallery search endpoint, `stratum_<firm index>_page_<n>.json`. `records.jsonl` is built from these. |
| `ad-library/data/raw/snap_fr_betting_competitors/story_backfill_run_id=*/records.jsonl` | One row per Story snap downloaded by `src/backfill_story_media.py` for the 1,155 Story ads whose media sat in `composite_preview.ad_snaps`: `ad_id`, `query_advertiser`, `snap_index`, `media_type`, `retrieved_at_utc`, `http_status`, `content_type`, `byte_length`, `sha256`, `local_path`. |
| `ad-library/data/raw/snap_fr_betting_competitors/story_backfill_run_id=*/manifest.json` | Backfill counts: links, downloaded, failed, files reused from the base run, new files and bytes. |
| `ad-library/data/raw/snap_fr_betting_competitors/run_id=2026-10-21T003157.817999+0000/*` | **Invalidated first attempt** (163 records) at the same panel, stopped when we found API errors could be mislabelled as exhausted pagination. `INVALIDATED.json` records why. Kept for completeness; do not analyse. |
| `ad-library/data/raw/snap_1000/run_id=2026-10-14T234838.202710+0000/*` | **The 1,000-ad pilot corpus**: 250 betting, 250 alcohol and 500 non-vice control ads from France, Germany and the Netherlands. Same record, manifest and `raw/search` layout as the panel. |
| `ad-library/data/raw/snap_1000/run_id=2026-10-14T234051.466297+0000/*` | Interrupted first attempt at the 1,000-ad corpus (646 records, no manifest). Superseded by the run above. |
| `ad-library/data/raw/snap_1000/story_backfill_run_id=*` | Story-snap backfill for the 1,000-ad corpus (same fields as the panel backfill). |
| `ad-library/data/raw/snap_calibration/run_id=*` | Two calibration runs (10 and 100 ads) made before the pilot, including `raw/detail/*.json` responses from the per-ad detail endpoint, which rate-limited us (HTTP 429). |
| `ad-library/data/raw/bing_poc/run_id=*/manifest.json` | Five-ad Microsoft Advertising (Bing) EU Ad Library proof of concept: request, checksum of the raw response, and per ad `ad_id`, `advertiser_id`, `advertiser_name`, `title`, `description`, URLs, asset list and the representative image we downloaded (`sha256`, `local_path`). |
| `ad-library/data/raw/bing_poc/run_id=*/raw/*.json` | Verbatim Bing Ad Library API response. |
| `ad-library/data/raw/tiktok_sin_poc/run_id=*/manifest.json` | Five deliberately chosen TikTok Commercial Content Library ads (three Winamax betting, two Pernod Ricard alcohol): selection method, per ad `ad_id`, `detail_url`, first/last shown, objective, reach band, advertiser, ad text, video `sha256` and a representative frame `sha256`. |
| `ad-library/data/raw/tiktok_sin_poc/run_id=*/records/*` | The same per-ad metadata, one JSON file per ad. |
| `ad-library/data/raw/tiktok_sin_poc/run_id=*/raw/*` | Text copy of each ad's public library detail page (dates, reach by country, targeting summary). |
| `ad-library/data/media_manifest.csv` | **Added for this release.** One row per (ad, media file) the collectors stored: `source` (snap/bing/tiktok), `run`, `ad_id`, `advertiser_query`, `role` (top_snap, app_install_preview, story_snap, representative_media, video), `snap_index`, `media_type`, `sha256`, `bytes`, `url` (public library link recorded at collection time), `detail_url`, `local_path`. 4,982 rows, 1,480 unique files. Built by `scripts/make_media_manifest.py`; used by `scripts/fetch_media.py`. |

Processed outputs (Ours unless noted).

| path pattern | what it is |
|---|---|
| `ad-library/data/processed/competitor_discovery_v1/sample_manifest.json` | Open-ended discovery pass, stratified sample: prompt version and hash, seed, per-firm sample size, model alias, source runs, video protocol, and `items` (neutral `coding_id` CD-xxx, `sha256`, firm, media type). |
| `ad-library/data/processed/competitor_discovery_v1/results.jsonl` | Sonnet's open-ended description of each sampled creative (prompt in `src/discover_competitor_associations.py`): `coding_id`, `sha256`, `status`, `labels` (verbatim text, translation, scene, people, entities, offer, prominent elements, payoff and risk depiction, cues linked to the brand, borrowed meanings, framing, intended association, tone, responsible-gambling messages), `raw_response`, `model_alias`, `model_usage`, `cost_equivalent_usd`, `duration_s`, `attempt`, `prompt_version`, `coded_at_utc`. Used to draft the codebook. |
| `ad-library/data/processed/competitor_labels_v1/manifest.json` | Full labelling run: prompt and codebook versions and hashes, model route, source runs, video protocol, and `items` mapping each neutral `coding_id` (LC-xxxx) to a creative `sha256`, firm(s) and media type. 951 unique creatives. |
| `ad-library/data/processed/competitor_labels_v1/prompt_template.txt` | The exact prompt sent for every creative (built from `config/competitor_association_codebook_v1.json`). |
| `ad-library/data/processed/competitor_labels_v1/results.jsonl` | **The creative labels.** One row per call: `coding_id`, `sha256`, `status` (951 ok, 3 failed attempts later retried), `labels` (fields defined in `config/competitor_association_codebook_v1.json`: verbatim text and translation, scene, people, entities, `sports`, `competition_level`, `occasion`, `cues_linked_to_brand` with `cue_type`, `borrowed_meaning` = 17 categories each with `prominence` 0-3 and evidence, `primary_framing`, `offer` with `type`, `amount_eur`, `guaranteed_or_risk_free_language`, `most_prominent_element`, `first_noticed_element`, `template`, `brand_prominence` 0-3, regulatory fields, `intended_association`, `tone`), plus `raw_response`, usage, cost, duration, attempt, prompt version, time. Model: Claude Sonnet via the Claude Code CLI; the model saw only the creative, never firm names or metadata. |
| `ad-library/data/processed/competitor_labels_v1/transcripts.jsonl` | Local Whisper (mlx-whisper large-v3-turbo) transcripts of video audio: `coding_id`, `sha256`, `has_audio`, `duration_s`, `text`, `model`. |
| `ad-library/data/processed/competitor_analysis_v1/ad_label_panel.jsonl` | **Ad-level panel**, one row per ad (3,241): `ad_id`, `firm`, `start`, `status`, `impressions`, `ad_type`, `headline`, `campaign_name`, the creative `sha256` and `coding_id` it was coded under, `labelled`, `borrowed` (category -> prominence), `framing`, `offer_type`, `offer_eur`, `risk_free_language`, `sports`, `competition_level`, `template`, `most_prominent`, `teams`, `events`, `intended_association`, `tone`. Built by `src/analyze_competitor_positioning.py`; Story ads take the label of their first snap. |
| `ad-library/data/processed/competitor_analysis_v1/analysis_summary.json` | Firm profiles from the same script: for each firm, shares of ads (and of impressions; and of currently active ads) with each borrowed meaning at prominence >= 2, framing, offer type, template, most prominent element, competition level, sport and risk-free language; first and last start dates; launches by month. |
| `ad-library/data/processed/competitor_analysis_v1/ads_as_cues_metrics.json` | From `src/ads_as_cues_metrics.py`: firm-pair cosine similarity of ad-text stems and of coded cue features (by ads and by impressions), monthly similarity of same-month launches, each firm's most representative features (share ÷ rival share), and brand-prominence / repetition measures. |
| `ad-library/data/processed/snap_validation_v1/manifest.json` | Blinded 60-creative validation packet (30 images, 30 videos) drawn from the 1,000-ad corpus: sample size, seed, fields, provenance and per-file hashes. Media copies are not included. |
| `ad-library/data/processed/snap_validation_v1/image_calibration_manifest.json` | The 3-image calibration packet used to test the model runner. |
| `ad-library/data/processed/snap_validation_v1/coding_sheet.csv` | Blank human coding sheet (one row per `coding_id`, SCV-xxx; columns per field with `__evidence` and `__unknown_reason`). No human coding has been done yet. |
| `ad-library/data/processed/snap_validation_v1/coding_instructions.md` | Instructions for the human coders. |
| `ad-library/data/processed/snap_validation_v1/linkage_key.csv` | Unblinding key: `coding_id` -> representative ad, media hash, category, country, advertiser, headline, impressions, reuse count, exposure bin, start date, status. |
| `ad-library/data/processed/snap_validation_v1/gabriel_image_*/pre_run_manifest.json` | Frozen pre-run fingerprint for each GABRIEL run. |
| `ad-library/data/processed/snap_validation_v1/gabriel_image_*/*/run_manifest.json` | Final run manifest (model, provider, hashes of packet, prompt, codebook and outputs). |
| `ad-library/data/processed/snap_validation_v1/gabriel_image_*/*/model_codes.csv` | Model codes per creative for the frozen validation codebook (`config/snap_validation_codebook_v1.json`): one column per field plus `__evidence` and `__unknown_reason`. Model `gpt-5.6-sol` through GABRIEL. |
| `ad-library/data/processed/snap_validation_v1/gabriel_image_*/*/raw/image_arm_responses*` | GABRIEL's raw per-creative responses and run metadata. **Edited for release:** the `image_data` column, which held a base64 copy of the creative, is blank; `media_sha256` identifies the creative. |
| `ad-library/data/processed/bing_gabriel_poc/*` | Five-ad GABRIEL feature-discovery proof of concept on the Bing ads: per-ad salience features (`per_ad/`) and the synthesized candidate taxonomy (`synthesis/`), each with GABRIEL run metadata. |
| `ad-library/data/processed/tiktok_sin_gabriel_poc/*` | The same proof of concept on the five TikTok betting/alcohol ads. Write-up: `docs/tiktok_sin_gabriel_poc_results.md`. |
| `ad-library/data/processed/snap_1000_preview/preview_index.json` | Index of a 10-ad visual preview of the 1,000-ad corpus (`ad_id`, category, advertiser, country, headline, `source_media_sha256`). The preview images and contact sheet are not included. |
| `ad-library/data/*/.gitkeep` | Empty placeholders. |

## Part 2. `agent-feeds/`: a vision-language model reads ads in a feed

Model: `mlx-community/Qwen3-VL-8B-Instruct-4bit` (revision recorded in each manifest), run
locally with MLX, temperature 0. Each **feed** is one ad plus up to five other images; each
question is a separate forward pass over the same feed.

| path pattern | what it is |
|---|---|
| `agent-feeds/runs/*/feeds.jsonl` | One row per feed: `feed_id` (hash of the design cell and image order), `ad_id`, `ad_category` (betting/beer/control), `prime_set` (neutral, win, loss, look_bet, social_drink, drink_harm, look_beer; `none` for the ad alone), `position` (`ad_only`, `before_k1`/`k3`/`k5` = k primes directly before the ad with neutral fillers first, `ad_first` = ad then 5 primes), `k_primes`, `draw` (independent random image draw), `images` (stimulus ids in display order; ids are defined in `config/stimuli/*.json`), `ad_index`, `reversed_scales` (rating labels shown 5 -> 1), `originally_reversed`. |
| `agent-feeds/runs/*/responses.jsonl` | One row per feed x question: `feed_id`, `question_id`, `layer`, `kind`, `prompt` (exact text). Rating questions: `probs` = probability of each answer 1-5 after renormalising over the five digits (and recoding reversed scales so 5 is always high), `valid_mass` (probability on the valid digits before renormalising), `top_token`, `mean` = expected rating, the outcome analysed everywhere. Choice questions: `probs`, `valid_mass`, `top_token`, `p_A`. Text questions: `text`. Question wording: `src/agentic_ads/priming_design.py` (v1 in batch 1, v2 in batch 2). |
| `agent-feeds/runs/*/manifest.json` | Run provenance: git commit and dirty flag, finish time, runtime, number of feeds, model id and revision, package versions, Python and platform, config and stimulus-manifest SHA-256 (hashes of the files **before** we rewrote absolute paths in the stimulus manifests), resize settings, decoding, output hashes. |
| `agent-feeds/runs/batch1-image-priming-7bb222afcc-20261021T023027Z/*` | 6-feed pilot of batch 1 (the first real run). |
| `agent-feeds/runs/batch1-image-priming-61d1c48aaf-20261021T024258Z/*` | **Batch 1**: 568 feeds x 9 questions, 8 ads, 5 draws, k = 1, 3, 5 and ad-first. Half the feeds used reversed scale labels. |
| `agent-feeds/runs/batch1-rerun-normal-scale-311cfa8d08-20261021T182547Z/*` | The 276 reversed-scale feeds of batch 1 rerun on the normal scale (same seed, so identical feed ids and images). Together with batch 1's normal-scale feeds this is "clean batch 1". |
| `agent-feeds/runs/batch2-beer-priming-9a960c96e6-20261021T194553Z/*` | **Batch 2**: 888 feeds x 10 questions (v2: reverse-worded twins `safe`/`respectful`, graded `try`), 4 Heineken ads (two alcohol-free) plus 2 betting and 2 control ads, 10 draws, k = 1, 5 and ad-first. The run was resumed after crashes; 24 answer rows were written twice and are bit-identical to the originals. Analyses drop the repeats. |
| `agent-feeds/artifacts/batch1-image-priming-61d1c48aaf-20261021T024258Z/*` | Auto-generated first-read tables for batch 1 from `src/agentic_ads/analyze_priming.py` (cell means, effects vs neutral, position effects, sample trails, summary). They mix reversed and normal scales and **should not be interpreted**; kept because the first-read notes cite them. |
| `agent-feeds/tmp/smoke-runs/context-interpretation-smoke-*/*` | Six runs of the original scaffold's **mock** pipeline (`config/smoke.toml`, deterministic mock engine): personas, contexts, cells, responses, summary, manifest. Plumbing checks only; mock responses have no behavioural meaning. |
| `agent-feeds/exploration/worked_example_*.json` | First hand-run probes of the outcome suite on one Heineken-style feed with Qwen3-VL Instruct and Thinking variants: per condition, the salient element, ratings and (Thinking) reasoning traces. Walkthrough: `exploration/worked_example_walkthrough.md`. |
| `agent-feeds/exploration/worked_example_walkthrough.md` | Question-by-question walkthrough of those probes. |
| `agent-feeds/data/raw/README.md` | Raw-input policy from the original scaffold. |
| `agent-feeds/data/raw/manifest.json` | Empty raw-input manifest from the original scaffold (stimuli are listed in `config/stimuli/`). |
| `agent-feeds/*/.gitkeep` | Empty placeholders. |

Stimulus manifests live in `agent-feeds/config/stimuli/batch{1,2}_manifest.json` (configuration,
not data): for each ad, its Snap `snap_ad_id`, advertiser, campaign name, headline, impressions,
`source_path` (now relative, into `ad-library/`), `source_sha256` and the processed file's `sha256`;
for each of the 70 primes, its Wikimedia Commons `title`, `page`, `license`, `artist`, search
`query` and `sha256`.

## Part 3. `brand-associations/`: directed celebrity-brand associations

Design and caveats: `brand-associations/docs/assoc-design.md` (association measures),
`docs/demo-pipeline.md` and `docs/demo-spillover.md` (event demo), `docs/explore-findings.md`
(look-size studies). Entities and pairs are frozen in `config/assoc/ambassadors.json`.

| path pattern | what it is |
|---|---|
| `brand-associations/data/raw/assoc/clickstream/*.filtered.tsv` | Wikimedia clickstream (English Wikipedia, monthly, CC0) filtered to frame entities: `prev`, `curr`, `type`, `n`. |
| `brand-associations/data/raw/assoc/clickstream/*.manifest.json` | Source dump URL, compressed size and hash, rows kept, titles, fetch time. |
| `brand-associations/data/raw/assoc/freeassoc/qwen3-8b-4bit.jsonl` | Ours. Local Qwen3-8B free-association samples, 30 per cue: `cue`, `cue_name`, `sample`, `seed`, `temp`, `model`, `prompt`, `text`. |
| `brand-associations/data/raw/demo/llm_labels/coverage-v*.jsonl` | Ours. Local Qwen3-8B labels of news articles (prompt v1 used page text, v2 excerpts): `key` = article text hash, prompt version and model; `label`. |
| `brand-associations/data/raw/demo/trends/*.json` | Google Trends daily series captured for the demo cases (one payload per file). |
| `brand-associations/data/raw/demo/validation/gold_labels*_v1.csv` | Gold labels for article coding (tuning and held-out sets): `case_id`, `url`, `about_focal_appearance`, `focal_id_level`, `note`, `coder` (an AI assistant working from keyword-in-context excerpts; needs a human spot-check), `coded_on`. |
| `brand-associations/data/raw/explore/trends/*.json` | Google Trends captures for the look-size studies: `spec` (terms, geography, window) and `data` (`time_*` = interest over time, `region_*` = interest by metro, `related_*` = related queries). |
| `brand-associations/data/raw/README.md` | Raw-input policy from the original scaffold. |
| `brand-associations/data/derived/assoc/directed_*.csv` | One file per association measure, one row per celebrity x brand: `fwd` = strength of the brand given the celebrity, `bwd` = strength of the celebrity given the brand, plus measure-specific columns (cosine and ranks for embeddings; PMI and template spread for LLM log-probs; reciprocal ranks and counts for free association; sentence counts for Wikipedia mentions). |
| `brand-associations/data/derived/assoc/cells.csv` | Every celebrity x brand x measure in the 22-celebrity, 30-brand pilot frame: `fwd`, `bwd`, `asym` = log fwd − log bwd, `is_pair` (configured ambassador pair), size ratios (log brand − log celebrity pageviews or coverage). Feeds `output/assoc/summary.md` and results table 3.1. |
| `brand-associations/data/derived/assoc/pair_panel.csv` | The 23 pilot pairs, wide by measure. |
| `brand-associations/data/derived/assoc/profile_shares.csv` | Multi-source association profiles (110-entity frame): `source` (wiki_text, news, wiki_clicks, search, llm), `from`, `to`, `share` = share of `from`'s units that involve `to`, `units_from`. |
| `brand-associations/data/derived/assoc/profile_pairs.csv` | Every entity pair with both directions per source, combined rank-based strength, `asym_log10_a_over_b` (mean log10 ratio across sources with both directions) and how many sources point each way. |
| `brand-associations/data/derived/assoc/profile_scales.json` | Typical share per source (for putting sources on a common scale). |
| `brand-associations/data/derived/assoc/profile_vectors_*.npz` | Multi-source entity embeddings (bge-base), raw and name-masked. |
| `brand-associations/data/derived/assoc/vectors_embed_*.npz` | Sarkar-style coverage vectors per entity for each encoder. |
| `brand-associations/data/derived/assoc/llm_qwen3-8b-4bit.*` | Forward/backward next-token log-probabilities and priors from local Qwen3-8B (`.npz`) and their metadata (`.meta.json`). |
| `brand-associations/data/derived/assoc/freeassoc_qwen3-8b-4bit_top.csv` | Most frequent free-association responses per cue: `cue`, `response`, `share_of_samples`. |
| `brand-associations/data/derived/assoc/clickstream_*.csv` | Clickstream flows between frame entities (pooled and monthly) and each entity's monthly outflow by next page. |
| `brand-associations/data/derived/assoc/documents_events.jsonl` | News headlines (GDELT) per entity and event window: `event`, `entity`, `window`, `date`, `domain`, `url`, `text` (headline only). |
| `brand-associations/data/derived/assoc/documents_wikipedia.jsonl` | Wikipedia paragraphs per entity (`doc_id`, `entity`, `source`, `date`, `text`). Wikipedia text is CC BY-SA 4.0. |
| `brand-associations/data/derived/assoc/event_*` | Event studies (Sweeney x Novig, Tate McRae x Adidas 2026): daily pageviews, Trends series, related queries by period, and article counts by period and week with forward/backward shares. |
| `brand-associations/data/derived/assoc/events_meta.json` | Event dates and windows used. |
| `brand-associations/data/derived/assoc/trajectories_*.csv` | How far each entity's embedding moves toward the other after an event, by encoder, raw and name-masked, with placebo entities. |
| `brand-associations/data/derived/assoc/sweeney_gdelt_topic_mix.json` | Topic mix of Sweeney news coverage (GDELT). |
| `brand-associations/data/derived/assoc/wiki_entities.csv` | Wikipedia title, pageviews over the window and extract length per entity. |
| `brand-associations/data/derived/demo/coverage_articles.csv` | One row per discovered article about a demo case: URL, domain, title, publication date and day relative to the appearance, how it was found and fetched, rule-based codes (actor type, identification level, relevance, retail and affiliate links, sellout mentions), text length and hash, a short evidence span. Article text is not included. |
| `brand-associations/data/derived/demo/coverage_llm_labels.csv` | Qwen labels per article (model-predicted). |
| `brand-associations/data/derived/demo/archive_captures.csv` | Wayback Machine captures of brand product pages found for each case. |
| `brand-associations/data/derived/demo/archive_snapshots.csv` | Parsed product-page snapshots: stock status, countdowns, list price, sizes available. |
| `brand-associations/data/derived/demo/*_daily.csv` | Daily attention series per case (GDELT article volume, Wikipedia pageviews, Google Trends). |
| `brand-associations/data/derived/demo/spillover_*.csv` | Focal vs sibling vs competitor measures: search z-scores by window (`spillover_attention`), product-page depletion (`spillover_inventory`), co-mentions in coverage (`spillover_mentions`), Qwen's open list of other products (`spillover_llm_products`). |
| `brand-associations/data/derived/demo/validation_*` | Article-coding validation: tuning and held-out samples, and precision/recall/accuracy per coder. |
| `brand-associations/output/assoc/summary.md` | Pilot asymmetry summary (regenerated as results table 3.1). |
| `brand-associations/output/assoc/brief_stats.json` | Article counts behind the first association brief. |
| `brand-associations/output/assoc/*.html` | Our briefs (first look, two cases, multi-source profiles), self-contained HTML; embedded images are our charts. |
| `brand-associations/output/assoc/*.png` | Our charts for those briefs. |
| `brand-associations/output/demo/*` | Demo case outputs: per-case evidence chains, attention heatmaps, spillover charts, `summary.md`, `timelines.csv`, the HTML findings report, the Trends case figure with its data, and product-page snapshots. |
| `brand-associations/output/explore/study_*/*.csv` | Look-size studies: metro panels (Study A), item-level lifts for Taylor Swift's game-day looks (Study C, `looks_items.csv`), re-cueing series (Study D). Study B (StockX) is not included. |
| `brand-associations/output/explore/figures/study_*.png` | Figures for Studies A, C and D. |
| `brand-associations/output/presentation/*` | Two figures (ambassador contrast, Novig before/after) and an equation markup page made for a presentation. |

## `results/`

Generated by `analysis/make_results.py`; do not edit. `RESULTS.md` has every table with notes.

| path pattern | what it is |
|---|---|
| `results/RESULTS.md` | All tables below, formatted, with definitions. |
| `results/agents_*.csv` | Agent-feed tables: scale problem, batch 1 effects / dose / baselines, batch 2 replication / harm by ad / pooled effects / position / twin correlations. Effect columns are differences on the 1-5 scale; `*_ci90_excludes_0` flags the seeded bootstrap. |
| `results/firms_*.csv` | Five-firm panel composition, firm profiles, pairwise and monthly similarity, distinctive features. |
| `results/snap1000_corpus.csv` | Composition and media coverage of the 1,000-ad corpus. |
| `results/assoc_*.csv` | Association asymmetry summary, Study C look-size lifts, demo spillover z-scores. |
| `results/facts.json` | Scalar facts quoted in the write-up (run integrity, label counts, regression coefficients). |
| `results/*.svg` | The two headline figures. |
