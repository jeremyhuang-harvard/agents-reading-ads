# Snapchat 1,000-ad pilot: collection results

## Status

The first production-oriented Snapchat Ads Gallery pilot completed successfully.

- **Collection date:** October 14, 2026
- **Run ID:** `2026-10-14T234838.202710+0000`
- **Requested ads:** 1,000
- **Collected ads:** 1,000
- **Unique ad IDs:** 1,000
- **Duplicate ad IDs:** 0
- **Storage used:** approximately 250 MB on disk
- **Configured storage ceiling:** 30 GiB
- **Storage ceiling reached:** No
- **Unique downloaded creative files:** 494
- **Creative checksum failures:** 0

Raw API responses, normalized records, creative files, provenance, and checksums are stored locally under the ignored `data/raw/snap_1000/` directory. Raw media and signed creative URLs are not committed to GitHub.

## Sample composition

### Product category

| Category | Ads |
|---|---:|
| Betting | 250 |
| Alcohol | 250 |
| Non-vice controls | 500 |
| **Total** | **1,000** |

### Query country

| Country | Ads |
|---|---:|
| France | 600 |
| Germany | 200 |
| Netherlands | 200 |

### Advertiser-query strata

| Advertiser query | Ads |
|---|---:|
| Winamax | 75 |
| PMU | 75 |
| Pernod Ricard | 150 |
| bet365 | 100 |
| Heineken | 83 |
| Grolsch | 17 |
| Nike | 170 |
| Coca-Cola | 100 |
| McDonald's | 25 |
| Carrefour | 75 |
| Adidas | 130 |

The sample is a declared quota sample designed to validate collection and support within-platform comparisons. It is not a representative estimate of the prevalence of these categories or advertisers on Snapchat.

## Creative-media results

- **Records with a downloaded creative:** 709
- **Records without a downloaded creative:** 291
- **Record-level MP4 downloads:** 419
- **Record-level JPEG downloads:** 266
- **Record-level PNG downloads:** 24
- **Unique downloaded files after SHA-256 deduplication:** 494
- **Media requests returning HTTP 403:** 23

The difference between 709 records with media and 494 unique files reflects creative reuse across multiple ad records. Some search records did not disclose a directly downloadable primary creative. Twenty-three disclosed media requests returned HTTP 403, consistent with inaccessible or expired signed media links; these records and failures were retained for possible targeted recovery.

### File-size distribution among unique media

| Statistic | Size |
|---|---:|
| Median | 0.27 MB |
| 95th percentile | 1.60 MB |
| Maximum | 4.58 MB |
| Total creative bytes | approximately 239 MB |

The observed corpus is far below the 30 GiB ceiling. At the observed rate, storage is not the binding constraint for a 1,000-ad Snap pilot.

## Detail endpoint decision

The earlier 100-ad calibration generated repeated HTTP 429 responses when requesting one detail record per ad. The 1,000-ad run therefore used the complete search records and made zero individual detail requests. This avoided unnecessary throttling while preserving the main disclosed fields present in search results.

Detail enrichment should be attempted only for records missing fields required by the analysis, in small checkpointed batches with exponential backoff. A validation subsample should first determine whether detail responses add material information beyond the search records.

## Verification performed

1. Parsed the final manifest and all 1,000 JSONL records.
2. Confirmed exactly 1,000 unique ad IDs and no duplicate IDs.
3. Confirmed 494 creative files exist locally.
4. Recomputed SHA-256 for every creative file and found zero mismatches.
5. Confirmed the collector reported `budget_exhausted: false`.
6. Confirmed the final run occupies approximately 250 MB on disk.
7. Ran the full repository test suite: **20 tests passed**.

## Next analysis steps

1. Draw a reproducible random set of 25–50 creatives for visual quality control.
2. Characterize the 291 records without downloaded media and retry the 23 HTTP-403 cases through a separate enrichment run.
3. Generate descriptive tables for advertiser, category, country, ad format, status, targeting, impressions, and media availability.
4. Run GABRIEL first on a balanced validation subset rather than all 1,000 ads.
5. Refine the feature codebook and perform human reliability checks before full-corpus scoring.
6. Package the immutable run directory for transfer to controlled cloud or institutional storage, verifying file counts and checksums after transfer.
