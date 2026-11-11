# Snapchat measurement-validation pilot

## Decision

Validate the cue codebook on a locked sample from the completed 1,000-ad Snapchat corpus before collecting more ads or constructing a composite cue index. This phase estimates measurement reliability; it does not estimate prevalence, exposure effects, or causal effects on behavior.

## Locked sample

The sampling unit is a unique downloaded creative identified by SHA-256. A hash appearing in multiple category × country × medium cells is assigned once to the cell with the greatest aggregate disclosed impressions (lexicographic cell order breaks ties). Exposure-bin ordering uses impressions from that assigned cell only; `reuse_count` retains the number of source records across all cells. One representative record from the assigned cell supplies descriptive linkage metadata.

The versioned specification selects 60 creatives:

- 20 betting, 20 alcohol, and 20 non-vice controls;
- 10 images and 10 videos in each category;
- betting split across France and Germany;
- alcohol split across France and the Netherlands;
- controls distributed across France, Germany, and the Netherlands to mirror the combined vice-country mix;
- one seeded-random creative from each ordered exposure bin within every category × country × media cell.

This is a deliberately balanced validation sample, not a probability sample of Snapchat advertising.

## Blinding and local artifacts

`src/build_snap_validation_sample.py` creates a local packet under the ignored `data/processed/` boundary. It contains:

- `coding_sheet.csv`: coding IDs, media filenames, and blank fields only;
- `media/`: copied creatives renamed to neutral coding IDs;
- `coding_instructions.md`: the frozen field definitions and rating anchors;
- `linkage_key.csv`: category, advertiser, country, exposure, reuse, and source identifiers;
- `manifest.json`: selected-media checksums plus the source-records SHA-256 and run ID, sampling-spec SHA/version, codebook SHA/version, and both random seeds.

The builder verifies that the sampling spec's `source_run_id` matches the records parent directory, writes into a temporary sibling directory, and atomically renames it only after every checksum and artifact succeeds. Blinded field names are rejected if they could leak category, advertiser, country, headline, language, hashes, exposure, or source identifiers. Coders must not open the linkage key until independent coding and any adjudication are complete. Brand and product cues visible inside a creative cannot be blinded, but external campaign metadata are withheld.

## Measurement instrument

The frozen pilot instrument contains six boolean classifications and ten 0–100 ratings. It preserves three rules:

1. observable absence is coded as zero or false;
2. genuine unobservability is blank/null with an explicit reason;
3. positive booleans and ratings at or above 80 require visible or audible evidence.

The current instrument is in `config/snap_validation_codebook_v1.json`. Variables should be retained, revised, or dropped individually; no composite cue-potency index will be constructed in this phase.

## Human coding protocol

Use two independent coders if feasible. Each coder should:

1. work from a separate copy of the blinded sheet;
2. inspect the full creative, including complete video and audio;
3. code independently without discussing cases;
4. record evidence and unknown reasons as required;
5. preserve the first-pass sheet before adjudication.

After first-pass coding, disagreements can be adjudicated into a separate consensus sheet. Never overwrite the original coder files.

## GABRIEL protocol

`src/run_snap_validation_gabriel.py` applies exactly the frozen fields to blinded coding IDs. Before any model call it rejects absolute or escaping media paths, recalculates and verifies every image checksum, requires unique coding IDs and media hashes, and requires the production count of 30 images. Model annotations must contain exactly one field in frozen order with explicit evidence and unknown-reason keys and the codebook's evidence/null semantics.

The runner fingerprints the packet manifest, verified media hashes, prompt, codebook, provider, and model before invoking GABRIEL. Checkpoints and outputs live under the fingerprint directory. Existing unbound or mismatched output is rejected unless `--reset` is explicitly supplied, preventing stale responses from being relabeled with a current run manifest. Tests and calibration runs may intentionally use another size with `--expected-count`.

The first model arm uses the 30 still-image creatives only. Videos require a separately validated multimodal derivative—such as synchronized frame sheets, transcript, and audio features—so they are not silently treated as single thumbnails. Human–model comparisons must therefore report the image arm separately until the video protocol is frozen.

## Reliability outputs

For each field, report:

- missingness and unknown rates;
- human–human and human–model percent agreement for booleans;
- Cohen's kappa plus a prevalence-adjusted agreement diagnostic for booleans;
- mean absolute error, Spearman rank correlation, and a continuous agreement statistic for ratings;
- results by category, country/language, and medium when cell sizes permit;
- examples of high-confidence disagreement and likely shortcut inference.

Agreement is not construct validity. Variables with acceptable reliability still require substantive review and, eventually, validation against behavioral or experimental outcomes.

## Executable commands

```bash
uv run python src/build_snap_validation_sample.py \
  --records data/raw/snap_1000/run_id=<RUN_ID>/records.jsonl \
  --spec config/snap_validation_sample_v1.json \
  --codebook config/snap_validation_codebook_v1.json \
  --output-dir data/processed/snap_validation_v1

uv run python src/run_snap_validation_gabriel.py \
  --packet-manifest data/processed/snap_validation_v1/manifest.json \
  --codebook config/snap_validation_codebook_v1.json \
  --output-dir data/processed/snap_validation_v1/gabriel_image_arm \
  --expected-count 30 \
  --parallelism 2 \
  --reset
```

## Go/no-go rule

Scale model coding only after reviewing field-level reliability. Retain fields that are both interpretable and reproducible; revise ambiguous definitions and anchors; drop fields that remain unreliable after one prespecified revision. Collecting more ads does not solve a measurement instrument that cannot be coded consistently.
