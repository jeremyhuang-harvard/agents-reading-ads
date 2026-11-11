# Five-firm French sports-betting competitor panel: collection results

## Status

Collected 2026-10-21 (UTC) from the Snap Ads Gallery API with `config/snap_fr_sports_betting_competitors_5x1000_v1.json`. Every one of the 3,241 ad records has at least one downloaded image or video. Raw responses, media, and ledgers are outside Git under `data/raw/snap_fr_betting_competitors/`.

This is a targeted same-platform competitor panel. It is not a probability sample of French betting advertising, and archive presence is not exposure.

## Composition

| Company (query payer) | Ads | Pagination | Unique creatives in base run | Campaign starts |
|---|---:|---|---:|---|
| Winamax | 1,000 | capped at quota; more available | 119 | 2024-06-06 – 2026-10-16 |
| PMU | 605 | exhausted | 143 | 2026-03-02 – 2026-09-07 |
| Unibet / Kindred (`Kindred London Ltd`) | 466 | exhausted | 129 | 2024-01-30 – 2026-03-19 |
| Betsson (`Betsson France SA`) | 1,000 | capped at quota; more available | 198 | 2024-10-16 – 2026-06-02 |
| bet365 | 170 | exhausted | 87 | 2026-05-25 – 2026-09-04 |
| **Total** | **3,241** | | 676 | |

Ad types: 1,772 app install, 1,325 Story, 73 remote webpage, 63 deep link, 8 reminder.

Advertiser counts are highly unequal, and the date windows differ by firm. Cross-firm comparisons must weight or stratify by firm and period rather than pool records.

## Media coverage

- Base run: 2,086 records had media downloaded directly; 676 unique files; 339.5 MB; zero checksum failures; zero media errors; storage budget not exhausted.
- The remaining 1,155 records were Story ads whose media links sit in `composite_preview.ad_snaps` rather than at the top level. The original collector did not read that location and recorded no error.
- `src/backfill_story_media.py` downloaded all 1,325 Story-snap links for those records (some Stories contain several snaps) with zero failures. 810 matched files already stored; 275 were new unique files totaling 64.5 MB.
- The collector now reads Story-snap links directly, so future runs do not need the backfill.

Total panel storage is about 424 MB, against a 30 GiB cap.

## Earlier 1,000-ad corpus

The same backfill on `data/raw/snap_1000/run_id=2026-10-14T234838.202710+0000/` downloaded 273 Story links with zero failures (134 new unique files, 49.4 MB). Media coverage rose from 709 to 896 of 1,000 records. The remaining 104 have no media link in search results: 71 remote webpage, 18 lens remote webpage, 7 collection, 5 lens, and 3 Story records. The detail endpoint may recover some of them.

## Provenance

| Artifact | SHA-256 |
|---|---|
| Panel run manifest | `b193a66619b51aaa7fe264ebcadbfc06625235efcb9143a42d3783ff4e39b0e8` |
| Panel Story-backfill manifest | `1d01316f490a92e47702415a87371d0f9ff804c41e940aa624a6b79bd9666813` |
| 1,000-ad corpus Story-backfill manifest | `d055cec22079e5724fac0e78abe424cfc0d100bba212928889869e3e3ed40da5` |

Run ID: `run_id=2026-10-21T005219.747976+0000`.

An earlier attempt, `run_id=2026-10-21T003157.817999+0000`, was stopped after 163 records when review found that API-level errors could be mislabeled as exhausted pagination. It is marked `INVALIDATED.json` and must not be used.

## Next steps

1. Run an independent review of the fail-closed pagination, bounded retries, and versioned ledger changes. The earlier review attempt failed on a model usage limit.
2. Build the creative-level ledger, embeddings, and interaction measures in `docs/competitor_ad_interaction_analysis_plan.md`.
3. Obtain an external market-share measure before labeling any firm the incumbent.
