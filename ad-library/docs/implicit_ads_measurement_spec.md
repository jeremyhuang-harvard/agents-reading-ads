# Multimodal measurement specification for backgrounded brand exposure

**Prepared:** October 15, 2026  
**Status:** Pilot specification

## Recommended design

Treat “implicit advertising” as a **set of separately measurable signals**, not a single model label. The pipeline should produce:

1. **Literal observations:** visible text, logos, products, people, speech, captions, geometry, timing.
2. **Entity links:** observed mark → candidate brand; face → approved ambassador roster; product → catalog item.
3. **Relational judgments:** person wearing product, person handling product, brand shown in background, spoken mention aligned with product appearance.
4. **Construct ratings:** prominence, naturalness, commercial-context likelihood.
5. **Disclosure evidence:** what disclosure appeared, where, when, for how long, and whether it was readable/audible.
6. **A calibrated ad hypothesis:** evidence for commercial placement—not a claim that sponsorship actually occurred.

A crucial distinction:

- **Brand presence** is observable.
- **Promotional presentation** is inferential.
- **Material connection or paid sponsorship** is normally unknown without disclosure, metadata, or external records.
- **No detected disclosure** is not the same as **no disclosure** unless every relevant modality was adequately observed.

Do not initially collapse these into one “implicit-ad score.” Store the components, validate them independently, and learn a composite only after human construct validation.

---

# 1. Processing architecture

## Stage A — Immutable GABRIEL creative bundle

Create one immutable bundle per image or video:

```text
bundle/
  manifest.json
  original/
    creative.mp4
  derivatives/
    proxy.mp4
    audio.wav
    frames/
    thumbnails/
    captions.json
  platform_metadata.json
  checksums.json
```

The manifest should record:

- `creative_id`, source platform, post/account IDs where permitted;
- original URL or acquisition source;
- acquisition timestamp;
- media SHA-256;
- width, height, frame rate, duration, codec, rotation;
- audio channels and sample rate;
- embedded or platform captions;
- preprocessing software and parameters;
- rights/access class;
- derivative hashes.

All frames, audio, captions, prompts, reference catalogs, and model outputs should be integrity-bound to the bundle hash. Outputs should be append-only by run ID rather than overwritten.

## Stage B — Temporal decomposition

For short video:

1. Detect shot boundaries.
2. Always include first and last frames and both sides of each transition.
3. Sample each shot at a pilot rate such as 2–4 frames/second.
4. Add adaptive samples when OCR, object proposals, motion, or audio mentions change.
5. Run dense propagation/tracking between analyzed frames.
6. Re-run dense inference in intervals containing a possible logo, disclosure, product interaction, or ambassador.

TransNet V2 is a suitable shot-boundary baseline, while ByteTrack provides a strong tracking baseline. SAM 2 is useful for propagating object masks through video once objects have been proposed. [12][13][2]

For still images, represent the asset as one scene with one time interval. Duration-dependent fields should be `not_applicable`, not zero.

---

# 2. Modality-specific measurement

## Logo and wordmark detection

Use a three-route ensemble:

### A. Closed-set logo detector

Fine-tune a detector on:

- target advertiser logos;
- legacy and alternate marks;
- monochrome and low-contrast variants;
- packaging marks;
- partial and distorted logos;
- negative examples containing visually similar symbols.

LogoDet-3K and OpenLogo provide appropriate starting points and evaluation concepts, but a domain-specific catalog is necessary for reliable creator-video measurement. [3]

### B. Open-vocabulary proposals

Use Grounding DINO or an equivalent open-vocabulary detector to propose regions for prompts such as:

- “logo,” “brand mark,” “wordmark”;
- “watch,” “shoe,” “handbag,” “drink can”;
- named brands and product categories.

Then use SAM 2 to obtain masks and propagate them temporally. Grounding DINO is explicitly designed for language-conditioned open-set detection; SAM 2 supports promptable segmentation in images and video. [1][2]

### C. OCR-based wordmark route

Run OCR over:

- the full frame at multiple scales;
- detector-proposed logo and product regions;
- high-saliency regions;
- packaging, apparel, screens, signs, and disclosures.

Normalize OCR text conservatively:

- preserve the raw string;
- store normalized Unicode separately;
- record script and language;
- compare against brand aliases with edit-distance and phonetic retrieval;
- use an LLM only to rerank candidates, never to replace the OCR evidence.

PaddleOCR is a practical multilingual OCR starting point; its primary technical report describes an OCR/VLM system covering more than 100 languages. [4]

**Recommendation:** treat logo detector, OCR wordmark match, and product-catalog match as independent evidence. Their agreement should raise confidence; one model should not silently overwrite another.

---

## Product, apparel, watch, and object recognition

Use a hierarchy:

```text
object class
  └── product category
       └── brand
            └── product family
                 └── exact SKU candidate
```

Recommended procedure:

1. Produce object boxes and masks.
2. Classify broad category.
3. Extract multiple visual embeddings:
   - full object crop;
   - masked crop;
   - detail crops such as watch face, shoe side, handbag hardware;
   - context-free crop with surrounding person/background removed.
4. Retrieve nearest catalog candidates.
5. Rerank using OCR, color, shape, model year, packaging, and contextual constraints.
6. Return top-\(k\) candidates and margins—not an exact SKU if evidence is insufficient.

CLIP is a useful retrieval baseline, but category-specific systems and training data should be used for fine-grained products. DeepFashion2 supplies apparel detection, landmark, segmentation, and retrieval tasks; Product1M addresses instance-level product retrieval using image and text information. [7][5][6]

For every product link, preserve:

```json
{
  "category": "watch",
  "brand_candidate": "Example Brand",
  "product_candidates": [
    {"catalog_id": "W123", "score": 0.71},
    {"catalog_id": "W127", "score": 0.64}
  ],
  "link_state": "candidate",
  "exact_sku_state": "unknown"
}
```

A category may be present while brand or SKU remains unknown.

---

## Face, person, and ambassador linkage

Separate four tasks:

1. **Person detection and tracking**
2. **Face detection and quality assessment**
3. **Identity comparison**
4. **Role linkage**

RetinaFace and ArcFace are appropriate technical baselines for face localization and embedding comparison. [8][9]

Identity comparison should be restricted to an approved, licensed, or consented roster. Do not perform unconstrained internet identification.

Store links at distinct evidence levels:

- `confirmed_metadata`: platform or campaign record identifies the person;
- `roster_verified`: similarity to an approved reference set exceeds a validated open-set threshold;
- `human_confirmed`;
- `visual_candidate`: similarity only;
- `unknown`.

A visual match alone must not establish that someone is a paid ambassador. Represent that separately:

```text
person identity
    ≠ ambassador role
    ≠ material commercial relationship
```

Role evidence can come from campaign metadata, contracts, disclosures, account tags, or a maintained ambassador registry. If none exists, `ambassador_relationship = unknown`.

Also detect relations such as:

- wearing;
- holding;
- using;
- consuming;
- pointing at;
- looking at;
- speaking about;
- spatially adjacent to.

These relations are often more informative than identity alone.

---

## Audio mentions and captions

Run:

1. Voice-activity detection.
2. Speech recognition.
3. Word-level alignment.
4. Speaker segmentation where multiple speakers matter.
5. Brand/product entity extraction.
6. Phonetic retrieval for misrecognized names.
7. Alignment of mentions with visual tracks.

Whisper provides a multilingual speech-recognition baseline; WhisperX adds word-level timestamps and speaker-attribution components. [10][11]

Keep three text streams separate:

- ASR transcript;
- platform/creator captions;
- OCR text rendered inside the video.

Do not overwrite one with another. Differences can be analytically important—for example, a product may be spoken but omitted from captions.

An audio mention record should include:

```json
{
  "raw_text": "this new Rolecks...",
  "normalized_entity_candidate": "Rolex",
  "start_ms": 4200,
  "end_ms": 4680,
  "speaker_track_id": "person_01",
  "match_method": ["phonetic", "contextual"],
  "entity_confidence": 0.78,
  "alignment_confidence": 0.91
}
```

---

# 3. Geometry and exposure metrics

Compute metrics from masks where possible, boxes only as a fallback. Every aggregate should declare its geometry source.

## Screen time

For entity \(e\), calculate the union of time intervals in which it is visibly present:

\[
T_e = \mu\left(\bigcup_i [t_{i,start},t_{i,end}]\right)
\]

Report:

- visible screen time in milliseconds;
- percentage of valid video duration;
- longest continuous appearance;
- number of appearances;
- first and last appearance;
- simultaneous screen time with a named person, product, or spoken mention.

Do not add overlapping tracks for the same entity. Use union time.

Also report denominator coverage. If only 80% of frames were successfully processed, distinguish:

- share of valid observed time;
- lower bound over total video;
- unknown unprocessed time.

## Pixel share

For each frame:

\[
P_{e,t} = \frac{|M_{e,t}^{visible}|}{|F_t^{valid}|}
\]

Aggregate using duration-weighted mean, median, maximum, and 90th percentile:

\[
\bar{P}_e =
\frac{\sum_t \Delta t_t P_{e,t}}
     {\sum_t \Delta t_t}
\]

Provide both:

- **conditional pixel share:** while the entity is visible;
- **unconditional pixel-time share:** over the whole creative.

The latter captures duration and size jointly.

## Centrality

For mask centroid \((x,y)\), normalized to \([0,1]\):

\[
C = 1 -
\frac{\sqrt{(x-0.5)^2 + (y-0.5)^2}}
     {\sqrt{0.5^2 + 0.5^2}}
\]

Also calculate:

- overlap with central 25% and central 50% regions;
- rule-of-thirds proximity;
- distance from caption/UI obstruction regions;
- face-to-brand spatial distance.

Centrality is not the same as visual attention. Add an independently validated saliency measure, such as the proportion of predicted fixation mass inside the entity mask. DeepGaze IIE is a suitable saliency baseline and explicitly addresses calibration and out-of-domain behavior. [15]

## Foreground/background

Represent foreground status as evidence, not a brittle binary label. Candidate features:

- monocular depth percentile;
- occlusion ordering;
- sharpness relative to the scene;
- size relative to known objects;
- contact or attachment to a foreground person;
- scene-plane membership;
- detector/VLM scene relation.

Depth Anything V2 is a suitable monocular-depth baseline. [14]

Recommended fields:

```text
depth_percentile
foreground_probability
plane = foreground | midground | background | unknown
attached_to_person
evidence_methods[]
```

## Occlusion

Distinguish:

- frame-boundary truncation;
- occlusion by another object;
- self-occlusion;
- motion blur;
- overlay/UI occlusion;
- unreadability despite visible pixels.

Where an amodal extent can be estimated:

\[
V_{e,t} =
\frac{|M^{visible}_{e,t}|}
     {|M^{amodal}_{e,t}|}
\]

Store the estimate and its confidence. If no validated amodal estimator exists for that object class, set the visible fraction to `unknown`; do not infer that a visible mask is the full object.

---

# 4. Disclosure detection

Disclosure detection should examine:

- OCR text in the image/video;
- spoken audio;
- captions;
- platform “paid partnership” metadata;
- post description and hashtags, if included in the bundle;
- visual badges or standardized platform labels.

Maintain jurisdiction- and language-specific lexicons, but use semantic classification around the literal text. Examples include `ad`, `advertisement`, `sponsored`, `paid partnership`, gifted-product language, and local-language equivalents.

Measure:

- exact text/audio evidence;
- disclosure type;
- first appearance;
- duration;
- screen location;
- pixel height;
- contrast/readability;
- whether it is truncated or behind interface chrome;
- whether it appears before, during, or after the brand exposure;
- whether spoken and visual disclosures agree;
- language correspondence with the creative.

FTC guidance states that disclosure should be hard to miss and placed with the endorsement; its guidance also specifically addresses disclosure in pictures, video, live streams, and audio. The 2023 revised Endorsement Guides are the applicable primary regulatory reference for US-focused coding. [22][23]

The output should be **descriptive**, not a legal verdict:

```text
disclosure_detected = present
disclosure_readability = 0.82
disclosure_precedes_first_brand_exposure = false
compliance_judgment = not_assessed
```

---

# 5. Scene context, prominence, and naturalness

## Scene context

Use a controlled taxonomy plus free-text evidence:

- setting: home, retail, workplace, event, studio, outdoors;
- activity: unboxing, tutorial, routine, review, performance, interview;
- product relation: incidental, decorative, worn, handled, demonstrated, consumed;
- camera treatment: establishing shot, close-up, rack focus, repeated insert;
- narrative role: central goal, supporting tool, ambient prop;
- commercial cues: call-to-action, price, discount code, purchase link, launch language.

A VLM can classify these relations from evidence packets containing selected frames, tracks, transcripts, and OCR. It should not be asked to rediscover all low-level evidence from a compressed video.

## Prominence

Prominence should initially be a vector:

```text
screen_time_share
pixel_time_share
max_pixel_share
centrality
saliency_capture
foreground_probability
closeup_count
repeat_appearance_count
audio_mention_count
name_readability
person_interaction
```

Add a human-rated overall prominence score only after defining anchored examples:

- **1:** barely detectable;
- **2:** visible but peripheral;
- **3:** clearly noticeable;
- **4:** repeatedly or centrally emphasized;
- **5:** dominant subject of the creative.

Train a calibrated ordinal model on those labels. Do not invent hand-tuned weights and call the result validated prominence.

## Naturalness

Naturalness is a subjective construct and should be coded dimensionally:

- narrative relevance;
- interaction plausibility;
- continuity with surrounding content;
- camera motivation;
- verbal/visual congruence;
- degree of forced repetition;
- degree to which branding exceeds what the scene requires.

Recommended output:

```json
{
  "naturalness_rating": 3,
  "scale": "1_forced_to_5_organic",
  "dimensions": {
    "narrative_relevance": 4,
    "interaction_plausibility": 4,
    "camera_motivation": 2,
    "branding_excess": 2
  },
  "evidence": ["scene_03", "track_logo_02", "mention_04"],
  "state": "observed"
}
```

A VLM can pre-code this, but the pilot’s human labels define the construct. The model must not be treated as the source of ground truth.

---

# 6. Combining specialist models with LLMs/VLMs

## Specialist models should own

- coordinates and masks;
- OCR strings;
- face and object embeddings;
- tracks;
- depth;
- speech timestamps;
- scene boundaries;
- pixel and duration arithmetic.

## LLMs/VLMs should own or assist with

- entity normalization and alias resolution;
- relation classification;
- scene-context coding;
- disclosure semantics;
- narrative relevance;
- naturalness;
- explaining conflicting evidence;
- selecting cases for human review.

CLIP supports open-ended visual-language retrieval; LLaVA is a primary example of instruction-tuned multimodal reasoning. However, object-hallucination work such as POPE demonstrates why VLM assertions should be grounded in independent detections and evidence regions rather than accepted as literal observations. [7][16][17]

## Evidence-bound inference packet

Send the VLM:

```json
{
  "question": "Is product_07 being deliberately demonstrated?",
  "scene_frames": ["frame_0042", "frame_0048", "frame_0055"],
  "highlighted_regions": ["product_07", "person_01"],
  "specialist_observations": {
    "relation_candidates": ["holding", "looking_at"],
    "ocr": ["EXAMPLE"],
    "audio": "I have been using this every day..."
  },
  "allowed_labels": [
    "demonstrated",
    "incidental_use",
    "background_only",
    "insufficient_evidence"
  ]
}
```

Require the response to cite track, frame, OCR, or transcript IDs. Reject unsupported entities and require `insufficient_evidence` when the packet does not establish the answer.

---

# 7. Machine-readable schema

A compact top-level design:

```json
{
  "schema_version": "implicit_ads_measurement/0.1.0",
  "creative": {
    "creative_id": "cr_123",
    "bundle_hash": "sha256:...",
    "media_type": "video",
    "duration_ms": 18420,
    "width": 1080,
    "height": 1920,
    "language_candidates": ["en"],
    "platform_metadata_state": "observed"
  },
  "run": {
    "run_id": "run_456",
    "pipeline_version": "0.3.0",
    "code_commit": "abc123",
    "model_manifest_hash": "sha256:...",
    "prompt_manifest_hash": "sha256:...",
    "catalog_hash": "sha256:...",
    "created_at": "2026-10-15T14:00:00Z"
  },
  "entities": [
    {
      "entity_id": "brand_01",
      "entity_type": "brand",
      "canonical_id": "catalog:brand:example",
      "canonical_name": "Example",
      "link_state": "candidate",
      "candidate_links": [
        {
          "canonical_id": "catalog:brand:example",
          "score": 0.94,
          "methods": ["logo_detector", "ocr"]
        }
      ]
    }
  ],
  "tracks": [
    {
      "track_id": "logo_track_01",
      "entity_id": "brand_01",
      "observation_state": "present",
      "intervals": [
        {
          "start_ms": 3100,
          "end_ms": 7800,
          "keyframes": [
            {
              "frame_id": "f_0093",
              "timestamp_ms": 3100,
              "bbox_xywh_norm": [0.42, 0.31, 0.18, 0.09],
              "mask_ref": "masks/logo_track_01/f_0093.rle",
              "visible_pixel_share": 0.013,
              "centrality": 0.88,
              "saliency_mass": 0.21,
              "depth_percentile": 0.24,
              "occlusion_fraction": 0.08,
              "geometry_source": "sam2",
              "confidence": 0.91
            }
          ]
        }
      ],
      "aggregates": {
        "screen_time_ms": 4700,
        "screen_time_share": 0.255,
        "conditional_mean_pixel_share": 0.019,
        "pixel_time_share": 0.0048,
        "mean_centrality": 0.81,
        "foreground_probability": 0.73
      }
    }
  ],
  "text_observations": [
    {
      "observation_id": "ocr_01",
      "modality": "visual_ocr",
      "raw_text": "#ad",
      "normalized_text": "#ad",
      "start_ms": 9200,
      "end_ms": 11100,
      "region_ref": "region_77",
      "language": "en",
      "confidence": 0.96
    }
  ],
  "relations": [
    {
      "subject_id": "person_01",
      "predicate": "wearing",
      "object_id": "product_03",
      "start_ms": 0,
      "end_ms": 18420,
      "state": "present",
      "confidence": 0.93,
      "evidence_refs": ["track_person_01", "track_product_03"]
    }
  ],
  "disclosures": [
    {
      "disclosure_id": "disc_01",
      "type": "explicit_ad",
      "state": "present",
      "modalities": ["visual_ocr"],
      "first_start_ms": 9200,
      "duration_ms": 1900,
      "precedes_first_brand_exposure": false,
      "readability_score": 0.77,
      "evidence_refs": ["ocr_01"]
    }
  ],
  "constructs": {
    "prominence": {
      "state": "observed",
      "rating": 4,
      "scale_version": "prominence_v1",
      "confidence": 0.79,
      "evidence_refs": ["logo_track_01", "mention_02"]
    },
    "naturalness": {
      "state": "unknown",
      "reason_codes": ["insufficient_narrative_context"]
    },
    "commercial_presentation": {
      "state": "observed",
      "probability": 0.84,
      "calibration_version": "commercial_v2"
    },
    "paid_sponsorship": {
      "state": "unknown",
      "reason_codes": ["no_material_connection_records"]
    }
  },
  "quality": {
    "analyzable_time_share": 0.98,
    "analyzable_pixel_share": 0.99,
    "audio_coverage_share": 0.94,
    "unsupported_languages": [],
    "warnings": []
  },
  "human_review": {
    "status": "pending",
    "priority": 0.72,
    "reason_codes": ["high_impact_low_confidence"]
  }
}
```

## Required state semantics

Every substantive field should use:

```text
present
absent
unknown
not_applicable
```

Definitions:

- `present`: affirmative evidence meets a validated threshold.
- `absent`: the relevant modality was observed with sufficient coverage and the event was not found.
- `unknown`: evidence is missing, unreadable, occluded, unsupported, contradictory, or below the decision threshold.
- `not_applicable`: the construct does not apply to this media unit.

Never encode `unknown` as `false`, zero, an empty array, or a low confidence score.

---

# 8. Confidence, calibration, and auditing

## Confidence

Do not expose one opaque confidence number. Preserve:

- raw model score;
- calibrated probability;
- detection stability across frames;
- agreement across methods;
- catalog retrieval margin;
- evidence coverage;
- subgroup/calibration stratum;
- human-review status.

Temperature scaling is a straightforward calibration baseline; conformal methods can provide prediction sets or abstention regions under stated exchangeability assumptions. [18][19]

Calibrate each claim type separately:

```text
logo present
brand identity correct
exact product correct
face roster match correct
spoken mention correct
disclosure present
commercial presentation
naturalness rating
```

A score calibrated for logo presence is not transferable to SKU identity or sponsorship.

## Audit record

For every output retain:

- bundle and derivative hashes;
- exact model artifacts and weights;
- code commit;
- detector prompts;
- VLM system/user prompts;
- decoding parameters and seeds where applicable;
- brand/product/ambassador catalog version;
- raw specialist outputs;
- raw model response before parsing;
- parser/schema version;
- rejected outputs and retry history;
- reviewer decisions and prior values;
- manual override reason.

Run controlled counterfactual audits:

- remove brand names from the prompt;
- blur logos while retaining products;
- crop out the person;
- remove transcript/audio;
- replace catalog candidate order;
- test mirrored, compressed, darkened, and UI-obscured variants.

These tests reveal shortcut reliance and whether the VLM is reasoning from supplied evidence or prior brand knowledge.

---

# 9. Human-validation design

## Pilot sample

Use approximately 500–1,000 creatives, stratified by:

- image versus video;
- platform and aspect ratio;
- language;
- common versus rare brands;
- apparel, watch, packaged good, technology, service;
- large versus small placement;
- foreground versus background;
- disclosed versus potentially undisclosed;
- high, medium, and low model confidence;
- cases where specialist models disagree.

Oversample hard negatives: logo-like graphics, generic products, counterfeit marks, OCR near-matches, celebrity lookalikes, background television screens, and brands mentioned critically rather than promoted.

## Annotation workflow

1. Two blinded annotators independently code each gold item.
2. Neither sees model predictions initially.
3. A senior adjudicator resolves disagreements.
4. Preserve both original labels and adjudicated labels.
5. Include duplicate “sentinel” items to estimate within-rater consistency.
6. Re-annotate a temporal holdout after codebook revisions.
7. Keep test data locked after model-selection begins.

Use different interfaces for:

- frame/mask annotation;
- track continuity;
- transcript correction;
- entity linking;
- scene relations;
- subjective prominence/naturalness coding.

## Evaluation metrics

| Component | Primary measures |
|---|---|
| Logo/object detection | precision, recall, AP by size and brand |
| Segmentation | mask IoU, boundary F-score |
| Tracking | HOTA/IDF1, fragmentation, temporal IoU |
| OCR | character and word error rates; brand-link accuracy |
| Product retrieval | Recall@1, Recall@5, Recall@10, MRR |
| Face-roster linkage | TAR at fixed FAR, open-set false-match rate |
| ASR | WER plus brand-name recall |
| Screen time | absolute error and temporal IoU |
| Pixel share | absolute percentage-point error |
| Disclosure detection | recall, precision, onset/duration error |
| Prominence/naturalness | weighted agreement, ordinal error, ICC/alpha |
| Confidence | reliability plots, Brier score, ECE |
| Abstention | risk-coverage curve |
| Final ad hypothesis | precision-recall curve by deployment threshold |

Use Krippendorff-style reliability for human categorical/ordinal coding and Dawid–Skene-style latent-label aggregation only as a sensitivity analysis, not a substitute for adjudication. [20][21]

Report every measure by:

- platform;
- language/script;
- brand prevalence;
- object category;
- skin-tone/face-quality strata where identity matching is permitted;
- logo size;
- occlusion;
- video compression;
- foreground/background;
- creator versus professionally produced content.

## Pilot acceptance gates

Suggested provisional gates:

- disclosure recall at least 0.95 on the locked pilot set;
- brand-presence precision and recall at least 0.90 for supported brands;
- screen-time median absolute error below 250 ms or 5% of asset duration;
- pixel-share median absolute error below two percentage points;
- exact-SKU outputs suppressed unless validated precision exceeds 0.90;
- face linkage operated at a predeclared low false-match rate;
- subjective model-human disagreement no greater than human-human disagreement;
- calibrated probabilities within acceptable subgroup reliability bounds;
- all unsupported cases abstain rather than default to absence.

These are pilot gates, not universal standards. Tighten them according to downstream harm: compliance screening should optimize disclosure recall, while public ambassador attribution should require much higher identity precision.

---

# 10. Concrete implementation stack

A practical pilot stack:

- **Media:** FFmpeg/ffprobe.
- **Shot boundaries:** TransNet V2.
- **Open-vocabulary proposals:** Grounding DINO.
- **Masks/video propagation:** SAM 2.
- **Tracking:** ByteTrack plus mask-association logic.
- **Logo route:** fine-tuned detector trained on the target brand catalog.
- **OCR:** PaddleOCR plus crop-specific OCR ensemble.
- **Visual retrieval:** CLIP baseline plus category-specific apparel/product embeddings.
- **Products:** DeepFashion2/Product1M-derived approaches for apparel and catalog retrieval.
- **Faces:** RetinaFace plus ArcFace, restricted to approved rosters.
- **Depth:** Depth Anything V2.
- **Saliency:** DeepGaze IIE.
- **Speech:** Whisper plus WhisperX-style alignment.
- **Semantic adjudication:** an evidence-bound VLM with strict JSON output.
- **Text/entity logic:** deterministic lexicons and catalog retrieval first; LLM reranking second.
- **Storage:** immutable GABRIEL bundles, object storage for media/masks, Parquet for observations, relational tables for entities/tracks/runs, and JSON Schema for interchange.
- **Review UI:** synchronized video, transcript, tracks, masks, evidence, and one-click `present/absent/unknown` decisions.

The first pilot should benchmark components and annotation reliability. It should **not** attempt production-scale automation or a universal ad score.

---

## Sources

[1] https://arxiv.org/abs/2303.05499 — Grounding DINO  
[2] https://arxiv.org/abs/2408.00714 — SAM 2  
[3] https://arxiv.org/abs/1807.01964 and https://arxiv.org/abs/2008.05359 — OpenLogo and LogoDet-3K  
[4] https://arxiv.org/abs/2507.05595 — PaddleOCR 3.0 technical report  
[5] https://openaccess.thecvf.com/content_CVPR_2019/html/Ge_DeepFashion2_A_Versatile_Benchmark_for_Detection_Pose_Estimation_Segmentation_and_CVPR_2019_paper.html — DeepFashion2  
[6] https://openaccess.thecvf.com/content/ICCV2021/html/Zhan_Product1M_Towards_Weakly_Supervised_Instance-Level_Product_Retrieval_via_Cross-Modal_Pretraining_ICCV_2021_paper.html — Product1M  
[7] https://proceedings.mlr.press/v139/radford21a.html — CLIP  
[8] https://openaccess.thecvf.com/content_CVPR_2020/html/Deng_RetinaFace_Single-Shot_Multi-Level_Face_Localisation_in_the_Wild_CVPR_2020_paper.html — RetinaFace  
[9] https://openaccess.thecvf.com/content_CVPR_2019/html/Deng_ArcFace_Additive_Angular_Margin_Loss_for_Deep_Face_Recognition_CVPR_2019_paper.html — ArcFace  
[10] https://arxiv.org/abs/2212.04356 — Whisper  
[11] https://arxiv.org/abs/2303.00747 — WhisperX  
[12] https://arxiv.org/abs/2008.04838 — TransNet V2  
[13] https://arxiv.org/abs/2110.06864 — ByteTrack  
[14] https://arxiv.org/abs/2406.09414 — Depth Anything V2  
[15] https://openaccess.thecvf.com/content/ICCV2021/html/Linardos_DeepGaze_IIE_Calibrated_Prediction_in_and_Out-of-Domain_for_State-of-the-Art_Saliency_ICCV_2021_paper.html — DeepGaze IIE  
[16] https://arxiv.org/abs/2304.08485 — Visual Instruction Tuning / LLaVA  
[17] https://aclanthology.org/2023.emnlp-main.20/ — POPE object-hallucination evaluation  
[18] https://proceedings.mlr.press/v70/guo17a.html — neural-network calibration  
[19] https://arxiv.org/abs/2107.07511 — conformal prediction overview  
[20] https://doi.org/10.2307/2346806 — Dawid–Skene  
[21] https://doi.org/10.1080/19312450709336664 — Krippendorff-style reliability  
[22] https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers — FTC Disclosures 101  
[23] https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 — FTC Endorsement Guides
