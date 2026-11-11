# Executable plan: 1,000-ad Snapchat pilot

## Decision

Proceed in two stages:

1. **Completed calibration:** 100 ads with primary creative downloads.
2. **Production pilot:** 1,000 unique ads under a hard 30 GiB storage ceiling.

The production sample is a declared quota sample for pipeline validation and comparative analysis. It is not a representative estimate of all advertising on Snapchat.

## Calibration result

The completed 100-ad run is stored locally under:

`data/raw/snap_calibration/run_id=2026-10-14T233117.961285+0000/`

Observed results:

- 100 unique ad IDs
- 45 betting ads, 20 alcohol ads, and 35 controls
- 65 unique downloaded creative files
- 35% media-hash deduplication rate
- 36 MP4 observations, 27 JPEG observations, and 3 PNG observations among records with downloaded media
- 33 records without a disclosed downloadable primary creative
- 1 media request returned HTTP 403
- 35 MB total on disk
- Mean unique creative size: 0.54 MB
- Median unique creative size: 0.37 MB
- 95th percentile: 1.92 MB
- Largest observed creative: 2.92 MB

The individual detail endpoint began returning HTTP 429 after a small number of requests. The bulk run will therefore preserve the complete search records and primary media first, with detail enrichment handled later in deliberately paced batches. Search records already contain the principal ad, payer, targeting, reach, status, and media fields needed for the first analysis.

## Storage estimate

| Scenario | Estimated storage for 1,000 ads |
|---|---:|
| Linear projection from the 100-ad run | 0.33 GiB |
| Every ad has a creative equal to the largest observed file | about 2.8 GiB plus metadata |
| Operational allocation | 5 GiB expected working envelope |
| Enforced absolute ceiling | 30 GiB |

The collector refuses to write a file that would exceed the total budget. It also applies a 250 MB per-file ceiling. The 30 GiB cap is therefore enforced rather than merely monitored.

## Sampling frame

The first 1,000-ad design targets:

- **500 vice-product ads**
  - Betting: Winamax, PMU, and bet365
  - Alcohol: Pernod Ricard, Heineken, and Grolsch
- **500 controls**
  - Nike, Adidas, Coca-Cola, McDonald's, and Carrefour
- **Countries:** France, Germany, and the Netherlands
- **Fallback controls:** Amazon and additional Carrefour records if an intended stratum is exhausted or overlaps another stratum

The versioned roster is:

`config/snap_1000_roster.json`

Search is based on disclosed paying-advertiser names. Ads are deduplicated globally by Snap ad ID and creative files are deduplicated by SHA-256 hash.

## Production command

```bash
uv run python src/collect_snap_ads.py \
  --roster config/snap_1000_roster.json \
  --target 1000 \
  --max-storage-gb 30 \
  --per-file-max-mb 250 \
  --detail-limit 0 \
  --delay-seconds 0.3 \
  --output-root data/raw/snap_1000
```

## Files produced

Each immutable run directory contains:

```text
run_id=<UTC timestamp>/
├── manifest.json
├── records.jsonl
├── raw/
│   ├── search/
│   └── detail/
└── media/
```

- `manifest.json`: source, limits, counts, per-stratum yield, roster, and storage use
- `records.jsonl`: one normalized record per ad, including the complete disclosed ad object and media provenance
- `raw/search/`: exact API search-page responses
- `raw/detail/`: detail responses when detail enrichment is enabled
- `media/`: content-addressed creative files named by SHA-256 checksum

All raw data and media remain ignored by Git. Paths inside the manifest are relative to the run directory so the directory can later be moved intact to Dropbox, Google Drive, or institutional storage.

## Validation gates after collection

The run is acceptable for the pilot only if:

1. It contains 1,000 unique ad IDs, or every declared and fallback stratum is demonstrably exhausted.
2. The manifest reports `budget_exhausted: false`.
3. Stored bytes are below 30 GiB.
4. Every downloaded file's SHA-256 matches its record.
5. Search pages and records can be parsed without corruption.
6. Category, advertiser, country, media type, missing-media, and error counts are reported.
7. At least a random visual sample of 25 creatives is inspected before GABRIEL analysis.
8. The quota sample is labeled non-representative in every descriptive output.

## Follow-on detail enrichment

Do not issue 1,000 detail requests in a burst. After the base corpus is secure:

1. Select records where the search response lacks fields needed for analysis.
2. Enrich in batches of approximately 25 records.
3. Use exponential backoff for HTTP 429 responses and honor `Retry-After` when provided.
4. Checkpoint after every batch.
5. Compare detail responses with search responses to determine whether full-corpus enrichment adds material information.

If the detail endpoint adds little beyond the search records, retain only a validation subsample rather than generating avoidable traffic.

## Moving the corpus later

Move the complete `run_id=...` directory as one unit. After transfer:

1. Compare total file count and byte count.
2. Recompute a directory checksum manifest.
3. Open and parse `manifest.json` and `records.jsonl` from the destination.
4. Verify a random sample of media hashes.
5. Only then remove the local copy.
