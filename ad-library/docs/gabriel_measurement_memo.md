# Technical memo: A GABRIEL measurement pipeline for multimodal betting advertisements

**Date:** 2026-10-08  
**Scope:** Paid or owned betting advertisements represented by images, video, audio, text, and landing pages.  
**Design status:** Concrete research specification; the Ads-as-Cues variables below are a proposed operationalization to be frozen only after expert and coder review.

## Executive design

Treat each advertisement as a **versioned creative bundle**, not as a single file. The bundle is the unit of analysis and may contain copy, still images, video frames, transcript, audio, landing-page text/screenshots, placement metadata, and delivery metadata. GABRIEL then serves as a measurement layer over those components: it prepares media paths, extracts factual offer terms, classifies cue presence, rates cue intensity, codes evidence spans, discovers candidate cues, compares variants, normalizes duplicates and identifiers, tests shortcut inference, and supports human audit. GABRIEL is a prompt wrapper and workflow toolkit—not a trained domain model—and its official materials emphasize stable prompts, structured outputs, batching, retries, checkpoints, and raw-response audit trails.[1][2][6]

The core estimand is **cue content/potency**, not causal exposure impact. Content analysis can measure whether an advertisement contains an urgent, socially normalizing, affectively arousing, low-friction gambling cue. It cannot by itself estimate whether a person saw the ad, noticed it, remembered it, or gambled because of it. Those require impression/frequency data, audience linkage, surveys/experiments, or behavioral outcomes.

## 1. Measurement model grounded in Ads-as-Cues

Use Ads-as-Cues as a layered model:

1. **Cue availability:** Is a gambling-relevant stimulus present and perceivable?
2. **Cue salience:** How strongly does it capture attention?
3. **Cue meaning:** What learned association does it activate—reward, excitement, fandom, belonging, expertise, escape, scarcity, or safety?
4. **Cue actionability:** How directly and easily can the viewer act now?
5. **Cue inhibition:** Are risk, age, terms, and responsible-gambling messages sufficiently prominent to counter the appetitive cue?
6. **Exposure context:** Where, when, how often, and to whom was it delivered? This layer comes primarily from platform logs, not creative analysis.

### Recommended primary variables

| Construct family | Variable | Type / range | Operational definition |
|---|---|---:|---|
| Identification | `gambling_ad_present` | boolean | Creative promotes a wagering operator, sportsbook, casino, lottery, betting product, odds, or gambling-linked offer. |
| Identification | `operator_brand`, `product_type`, `sport_event`, `jurisdiction` | categorical/text | Literal entities visible or audible in the bundle. |
| Reward cue | `financial_inducement_present` | boolean | Bonus, free bet, odds boost, cashback, matched deposit, token, prize, or similar inducement. |
| Reward cue | `inducement_strength` | 0–100 | Magnitude and prominence of promised reward, considering qualifying conditions only when perceivable. |
| Reward cue | `win_salience` | 0–100 | Degree to which winning, payout, profit, jackpots, or successful bettors dominate the creative. |
| Immediacy | `urgency_scarcity` | 0–100 | Countdown, “bet now,” limited-time framing, live/in-play timing, expiring boost, or imminent event pressure. |
| Actionability | `betting_actionability` | 0–100 | Presence and clarity of odds, selections, QR/deep link, direct CTA, and an obvious path from cue to wager. |
| Friction | `perceived_ease` | 0–100 | Creative depicts betting as fast, simple, effortless, one-tap, or requiring little deliberation. This is perceived—not audited—friction. |
| Attention | `sensory_salience` | 0–100 | Visual contrast, motion, rapid cutting, large typography, sonic intensity, repetition, and foreground prominence. |
| Affect | `arousal_excitement` | 0–100 | Suspense, celebration, crowd energy, fast pacing, emphatic voice/music, or emotional intensity. |
| Affect | `positive_affect` | 0–100 | Joy, humor, triumph, anticipation, or pleasurable atmosphere tied to gambling. |
| Social cue | `social_proof_normalization` | 0–100 | Betting is represented as common, routine, socially approved, or something “everyone” does. |
| Identity cue | `sport_fandom_linkage` | 0–100 | Wagering is fused with team loyalty, event participation, fan identity, or being a “real” supporter. |
| Identity cue | `celebrity_influencer_presence` | boolean + entities | Recognizable public figure or influencer endorses, narrates, demonstrates, or normalizes betting. |
| Identity cue | `belonging_status_expertise` | 0–100 | Betting is linked to social belonging, masculinity/femininity, sophistication, insider knowledge, status, or skill. |
| Personal relevance | `targeting_cues` | multi-label | Youthful aesthetics, local team/geography, gender coding, cultural references, language, life-stage, or inferred audience segment. Record only observable cues, not inferred platform targeting. |
| Risk attenuation | `risk_minimization_claim` | boolean | “Risk-free,” “no sweat,” “money back,” “safe,” or equivalent framing that may reduce perceived downside. |
| Risk inhibition | `responsible_gambling_prominence` | 0–100 | Perceptual prominence and comprehensibility of safer-gambling messaging, not mere presence. |
| Risk inhibition | `terms_prominence` | 0–100 | Legibility/audibility, duration, contrast, font size, speech speed, and proximity of material offer terms. |
| Risk inhibition | `age_restriction_prominence` | 0–100 | Salience of age eligibility or exclusion. |
| Balance | `benefit_risk_imbalance` | -100–100 | Positive values mean appetitive/reward cues dominate; negative values mean risk/inhibitory information dominates. Derive only after validating component measures. |
| Composite | `cue_potency_index` | 0–100 | Pre-registered weighted composite of reward, salience, affect, normalization, urgency, and actionability minus inhibitory prominence. Report components alongside it. |
| Exposure metadata | `impressions`, `frequency`, `reach`, `placement`, `timestamp`, `audience_segment` | numeric/categorical | Imported delivery facts. Never infer these from creative content. |

Do not collapse to `cue_potency_index` during exploratory work. First establish reliability and construct validity for each component. A composite can hide opposite mechanisms—for example, a visually intense ad with no inducement versus a visually plain ad with a strong bonus.

## 2. Canonical data model and annotation schema

### 2.1 Creative-bundle table

One row per immutable ad version:

```text
ad_id                 stable concept ID across reposts/encodes
creative_version_id   hash-addressed version of exact bundle
campaign_id           advertiser campaign ID if available
operator_id            canonical operator ID
captured_at_utc        capture timestamp
valid_from/to          observed campaign interval
source_platform        TV, radio, social, display, affiliate, owned web, etc.
placement_context      pre-roll, in-feed, stadium, podcast, search, landing page
country/jurisdiction   observed delivery/legal context
language               primary and secondary languages
text_asset             supplied copy/caption/alt text
image_paths            ordered list
video_path             original video
frame_paths             sampled + scene-change + OCR-triggered frames
transcript              time-aligned ASR or supplied captions
speaker_turns           optional diarization
music_sfx_notes         optional deterministic audio features
landing_url             original URL
landing_snapshot_pdf    immutable render
landing_screenshot_paths ordered screenshots
landing_text            cleaned DOM text
terms_text              extracted fine print / conditions
impressions/frequency   external exposure variables when available
parent_ad_id             variant/derivation relation
content_sha256           hashes for every asset and bundle manifest
```

Keep source material and derived representations side by side. Direct image/audio/PDF analysis preserves visual, acoustic, and layout evidence that OCR/transcription can erase; the official guide explicitly distinguishes these modalities and recommends preserving raw sources.[2][3]

### 2.2 Row-level annotation object

```json
{
  "ad_id": "string",
  "creative_version_id": "string",
  "annotation_spec_version": "ads_cues_v1.0.0",
  "primitive": "extract|classify|rate|codify|whatever",
  "model": "live_verified_model_slug",
  "model_snapshot_or_alias_date": "2026-10-08",
  "run_id": "uuid",
  "run_index": 1,
  "modality": "text|image|audio|pdf|fusion",
  "field": "urgency_scarcity",
  "value": 72,
  "present": true,
  "confidence": 0.84,
  "evidence": [
    {
      "asset_id": "video_main",
      "modality": "video_frame",
      "start_ms": 12300,
      "end_ms": 14800,
      "frame_id": "scene_07_frame_02",
      "bbox_xyxy_norm": [0.08, 0.71, 0.92, 0.96],
      "verbatim_text": "BOOST ENDS AT KICKOFF",
      "rationale": "Explicit expiry tied to an imminent event"
    }
  ],
  "unknown_reason": null,
  "parse_success": true,
  "qc_flags": [],
  "prompt_hash": "sha256:...",
  "attribute_definition_hash": "sha256:...",
  "input_manifest_hash": "sha256:...",
  "gabriel_git_commit": "9caced978453d4ae857118eed01ed6abe9e72723",
  "code_commit": "git-sha",
  "created_at_utc": "ISO-8601"
}
```

### 2.3 Required value rules

- Use `null` plus `unknown_reason` for genuinely unobservable information; never force zero.
- A zero rating means **observable absence**, not missing media or failed parsing.
- Boolean positives require evidence. High-risk ratings (`>=80`) and adjudication cases also require evidence.
- Evidence must point to a text span, frame/bounding box, timestamp, audio interval, or landing-page element.
- Keep literal extraction separate from interpretive coding. Example: `bonus_amount="$200"` is extraction; `inducement_strength=80` is rating.
- Keep `ad_content_targeting_cues` separate from platform-supplied `audience_segment`; the former does not prove actual targeting.

## 3. Mapping GABRIEL primitives to the pipeline

GABRIEL officially supports text, entity, web, image, audio, and PDF modalities for measurement helpers; `whatever` can attach image and audio columns for custom multimodal calls. Native video is not listed as a modality, so video must be decomposed into frames, transcript, and audio before fusion.[2][4]

| Primitive | Betting-ad use | Inputs | Outputs / variables | Guardrail |
|---|---|---|---|---|
| `load` | Inventory folders of screenshots, images, audio, and PDF snapshots. | Immutable asset directories. | File paths, directory tags, source IDs. | Add hashes and manifest yourself; `load` is preparation, not provenance completeness.[5] |
| `filter` | Cheaply exclude obvious non-ads, non-gambling content, corrupt assets, and irrelevant landing pages. | OCR text, captions, filenames, transcript snippets. | `candidate_keep`, score, reason. | Optimize recall; audit false negatives because screening can erase the target population. |
| `extract` | Obtain literal offer and compliance facts. | Per-modality asset or fused text. | Operator, product, sport, odds, bonus amount, deposit, rollover, expiry, eligibility, CTA, promo code, RG/age text, celebrity names. | Use typed fields, `unknown`, verbatim evidence, and one row per offer when multiple offers occur. `extract` may expand rows.[2][3] |
| `classify` | Detect cue presence and ad type. | Asset-level or bundle-level representations. | Boolean/multi-label fields: inducement, urgency, live betting, social proof, fandom, celebrity, risk-minimization, youth-oriented cues, product category. | Labels are independent by default; explicitly require “choose exactly one” only for mutually exclusive taxonomies, then audit.[3][4] |
| `rate` | Measure cue intensity. | Text/image/audio/PDF or fused bundle. | 0–100 ratings listed in §1. | Anchor 0/25/50/75/100 in definitions. Keep per-run values before averaging. |
| `rank` | Obtain robust relative ordering where absolute scales are unstable. | Matched sets of ads. | Relative z-scores for cue potency, sensory salience, terms prominence, or youth appeal. | Use within comparable strata (same format/language/product); rankings are sample-relative.[2] |
| `codify` | Locate the direct signal that produced a label/rating. | Transcript, copy, OCR, landing text. | Coded spans for inducement, urgency, normalization, risk minimization, RG, age, material terms. | Preserve offsets/timecodes. Use this evidence for signal stripping and coder audit. |
| `discover` | Exploratory contrast between predefined groups. | High- versus low-engagement ads, youth-heavy versus adult-heavy placements, or relapse-triggering versus neutral ratings. | Candidate discriminating features and prevalence differences. | Discovery does not establish a construct. Human-review terms, freeze definitions, then measure on a held-out corpus.[3] |
| `bucket` | Consolidate discovered terms or open-ended tactics into a compact taxonomy. | Candidate cue descriptions. | Reviewed cue-family names and definitions. | It returns a taxonomy, not row-level assignments; apply reviewed buckets with `classify`.[2][3] |
| `compare` | Compare A/B variants, pre/post regulation creatives, image versus landing page, or operator pairs. | Paired columns/bundles. | Differences in inducement, urgency, prominence, compliance, and CTA. | Randomize left/right order or run both directions to test order effects. |
| `deduplicate` | Collapse exact/re-encoded/reposted creatives and near-identical offer wording. | Fingerprints, OCR, transcripts, captions, frame summaries. | Canonical `ad_id`, duplicate cluster, representative. | Do exact perceptual/hash matching first; use semantic deduplication second. Do not merge legally meaningful changes in terms, odds, disclaimer, or duration. |
| `merge` | Link creatives to operator registry, campaign records, placement logs, sports fixtures, or regulatory complaints. | Canonical names/IDs on both tables. | Crosswalk and confidence. | Prefer deterministic IDs first; accept fuzzy matches only above validated thresholds and manually inspect ambiguous/high-value links. |
| `debias` | Test whether a rating comes from the intended cue rather than brand, team, celebrity, or general excitement. | Original and signal-stripped text, plus remaining-signal measure. | Raw, stripped, and debiased scores. | Run construct-specific stripping. Do not “debias” away a variable that is substantively part of the cue.[4][6] |
| `paraphrase` | Produce controlled de-branded or de-identified copies for shortcut tests. | Copy/transcript/landing text. | Brand-neutral, team-neutral, celebrity-neutral, or amount-neutral versions. | Validate semantic preservation and changed-only-as-intended before using. |
| `deidentify` | Protect user-generated testimonials, complaint text, or research-participant data. | Text containing PII. | Deidentified text plus mapping. | Usually unnecessary for public ad creative; store mappings under stricter access control. |
| `view` | Human audit of sampled texts, ratings, and coded passages. | Result DataFrames. | Visual review set and adjudication notes. | Use stratified samples, not only random examples or spectacular failures.[2][4] |
| `whatever` | Custom fusion across transcript + frames + landing-page screenshot/text, strict evidence objects, or bespoke routing. | Prompt rows plus image/audio attachments. | Bundle-level JSON with cross-modal evidence and contradiction flags. | Use strict schema where supported; web search and JSON mode cannot currently be combined, and audio needs a compatible audio model.[3][4] |

## 4. Attribute and prompt examples

### 4.1 Rating definitions

```python
CUE_RATINGS = {
    "urgency_scarcity": """
Rate 0-100 how strongly this ad pressures the audience to wager soon.
0: no time pressure or scarcity.
25: weak generic prompt to act.
50: explicit limited-time/live-event framing but not dominant.
75: repeated or prominent deadline, countdown, kickoff lock, or in-play immediacy.
100: the creative is organized around immediate action and loss of opportunity.
Judge only observable content. Do not infer urgency from the operator, sport, or event.
""",
    "social_proof_normalization": """
Rate 0-100 how strongly the ad depicts betting as ordinary, expected, socially
approved, or integral to enjoying sport/social life. Do not count the mere
presence of several people unless their behavior or framing normalizes betting.
""",
    "responsible_gambling_prominence": """
Rate perceptual prominence and comprehensibility, not mere existence. Consider
screen area, contrast, duration, speech speed/volume, placement, repetition,
and whether the message can realistically be noticed and understood.
""",
    "betting_actionability": """
Rate how directly a viewer can translate the ad into a wager using visible or
audible selections, odds, promo code, QR/deep link, explicit CTA, and procedural
clarity. Do not use knowledge of the operator's actual app UX.
"""
}
```

### 4.2 Classification labels

```python
CUE_LABELS = {
    "financial_inducement": "A bonus, free bet, odds boost, cashback, matched deposit, prize, or similar wagering-linked incentive is offered.",
    "risk_minimization": "The ad frames wagering or an offer as risk-free, no-sweat, protected, money-back, safe, or otherwise downplays potential loss.",
    "live_betting": "The ad promotes or demonstrates wagering during an event or on rapidly changing in-play markets.",
    "social_normalization": "The ad explicitly presents gambling as common, expected, routine, or socially approved.",
    "fandom_identity": "The ad links wagering to team loyalty, supporter identity, or fuller participation in a sporting event.",
    "celebrity_endorsement": "A recognizable public figure appears to endorse, recommend, use, narrate, or normalize the betting product."
}
```

### 4.3 Extraction fields

```python
OFFER_FIELDS = {
    "operator_brand": "Exact operator/brand stated or visibly displayed; unknown if absent.",
    "offer_type": "One of: free_bet, odds_boost, matched_deposit, cashback, bonus_credit, prize, other, none, unknown.",
    "headline_amount": "Largest promoted monetary/percentage amount exactly as shown.",
    "minimum_deposit": "Required deposit exactly as shown; unknown if not observable.",
    "minimum_odds": "Qualifying minimum odds exactly as shown.",
    "rollover_or_playthrough": "Exact wagering/playthrough requirement.",
    "expiry": "Exact expiry/deadline or event trigger.",
    "eligibility": "New/existing customer, geography, age, payment method, or other eligibility conditions.",
    "call_to_action": "Verbatim primary CTA.",
    "responsible_gambling_text": "Verbatim safer-gambling message.",
    "age_text": "Verbatim age restriction.",
    "material_terms_evidence": "Verbatim terms plus asset, timestamp/frame, and bounding box."
}
```

### 4.4 Fusion prompt for `whatever`

```text
You are coding one immutable betting-ad creative bundle. Use only supplied assets.
Return the strict annotation object. Integrate modalities, but preserve separate
evidence references. If modalities conflict, do not silently reconcile them:
set `cross_modal_conflict=true`, list the conflict, and use `unknown` where the
bundle does not support a defensible value.

Rules:
1. Literal fields require verbatim evidence.
2. Interpretive ratings require at least one grounded cue.
3. Do not infer audience delivery, personal targeting, legal compliance, or app UX.
4. Distinguish absence from unobservability.
5. Fine print that is technically present but unreadable receives low prominence.
6. A sports celebrity's presence is not automatically an endorsement; code the role.
7. Report modality contribution for each rating: text, visual, speech, music/SFX,
   landing page, or interaction design.
```

## 5. Multimodal processing

### 5.1 Images

1. Preserve original image and hash.
2. Run deterministic OCR to obtain candidate text and bounding boxes.
3. Use `extract(..., modality="image")` for visible terms/entities and `rate`/`classify` for visual cue variables.
4. Start with low/auto image detail for screening; rerun high/original detail when fine print, odds, small badges, or crowded layouts affect the outcome. GABRIEL exposes image-detail passthroughs for this purpose.[2][3]
5. Store both OCR and direct-vision results; disagreement becomes a QC flag.

### 5.2 Video

Because video is not a listed native GABRIEL modality, create synchronized derivatives:

- scene-boundary frames;
- fixed-interval frames (for example, 1 fps) plus dense sampling around terms/CTA/disclaimers;
- OCR per frame with persistence duration;
- supplied captions or ASR transcript with word timestamps;
- audio track;
- shot pace, text-on-screen duration, and disclaimer exposure computed deterministically;
- original video retained as the authoritative source.

Analyze frame batches as images, transcript as text, and audio as audio. Fuse at the bundle level with `whatever`. Weight repeated frames by **screen time**, not frame count, or a three-second disclaimer sampled at 10 fps will be overcounted relative to a three-second disclaimer sampled at 1 fps.

### 5.3 Audio

Use two paths:

- **Transcript path:** claims, offer terms, urgency words, spoken disclaimers, endorsement language.
- **Raw-audio path:** arousal, pacing, crowd noise, celebratory music, urgency prosody, and relative audibility of disclaimers.

Route raw audio only to a currently supported audio model; the official guide says audio uses Chat Completions, requires an audio-capable model, and is not supported in batch mode. Verify the live model slug before execution.[2][3]

### 5.4 Landing pages

Capture an immutable research snapshot at observation time:

- URL and redirect chain;
- full-page screenshot(s);
- print-to-PDF snapshot;
- cleaned DOM text;
- visible text with bounding boxes;
- modal/pop-up/cookie state;
- CTA targets and number of steps to registration/deposit, collected deterministically where permitted;
- locale, viewport, user agent, and capture timestamp.

Analyze PDF/screenshot for visual prominence and DOM text for literal terms. Do not use live web search as a substitute for the historical landing page; pages change and web retrieval can introduce future information.

### 5.5 Cross-modal conflict policy

Examples:

- Voice says “risk-free,” on-screen terms say “bonus bet returned”: retain both, flag semantic conflict.
- Caption says `$200`, landing page says `$100`: code version inconsistency rather than choosing one.
- Responsible-gambling text exists in DOM but is below the fold and absent from screenshot: presence may be true, prominence low.
- Music/crowd audio conveys excitement while copy is neutral: rate audio arousal separately, then fuse transparently.

## 6. End-to-end pseudocode

Model identifiers below are symbolic. The official repository warns that model slugs, availability, endpoint support, and pricing change; verify the live model catalog, organization provisioning, and pricing before a paid run, then choose the smallest model that meets the validated standard.[2][3]

```python
import asyncio, hashlib, json, os
import pandas as pd
import gabriel

FAST = os.environ["GABRIEL_FAST_MODEL"]          # verified live
BALANCED = os.environ["GABRIEL_BALANCED_MODEL"] # verified live
STRONG = os.environ["GABRIEL_STRONG_MODEL"]     # verified live
AUDIO = os.environ["GABRIEL_AUDIO_MODEL"]       # verified live
ROOT = "/research/betting_ads/runs/ads_cues_v1_0_0"

async def measure_ads(bundle_df: pd.DataFrame):
    # 0. Mechanical preflight (outside GABRIEL)
    assert bundle_df.creative_version_id.is_unique
    assert bundle_df.input_manifest_hash.notna().all()

    # 1. High-recall screening on cheap textual derivatives
    screened = await gabriel.filter(
        bundle_df,
        column_name="screening_text",
        condition=(
            "Keep if this may promote gambling, betting, sportsbook, casino, "
            "lottery, wagering odds, or a gambling-linked offer. Keep uncertain cases."
        ),
        threshold=0.20,
        n_runs=3,
        model=FAST,
        save_dir=f"{ROOT}/01_filter",
        reset_files=False,
    )

    # 2. Literal fields by modality
    text_extract = await gabriel.extract(
        screened,
        column_name="fused_text",
        attributes=OFFER_FIELDS,
        types={"operator_brand": str, "call_to_action": str},
        additional_instructions=(
            "Use unknown when not observable. Return verbatim evidence and source offsets. "
            "Create separate offer records if more than one materially distinct offer appears."
        ),
        n_runs=2,
        model=BALANCED,
        modality="text",
        save_dir=f"{ROOT}/02_extract_text",
        reset_files=False,
    )

    image_extract = await gabriel.extract(
        screened.dropna(subset=["hero_image_path"]),
        column_name="hero_image_path",
        attributes=OFFER_FIELDS,
        n_runs=2,
        model=BALANCED,
        modality="image",
        image_detail="auto",
        save_dir=f"{ROOT}/02_extract_image",
        reset_files=False,
    )

    # 3. Presence and intensity measurements
    labels = await gabriel.classify(
        screened,
        column_name="fused_text",
        labels=CUE_LABELS,
        n_runs=5,
        min_frequency=0.60,
        model=FAST,
        modality="text",
        save_dir=f"{ROOT}/03_classify",
        reset_files=False,
    )

    ratings = await gabriel.rate(
        screened,
        column_name="fused_text",
        attributes=CUE_RATINGS,
        n_runs=5,
        model=BALANCED,
        modality="text",
        save_dir=f"{ROOT}/04_rate",
        reset_files=False,
    )

    # 4. Evidence coding
    coded = await gabriel.codify(
        screened,
        column_name="fused_text",
        categories={
            "inducement_evidence": "Exact passages offering wagering-linked value.",
            "urgency_evidence": "Exact passages imposing time/event pressure.",
            "normalization_evidence": "Exact passages presenting betting as normal/socially approved.",
            "risk_minimization_evidence": "Exact passages that downplay risk or loss.",
            "responsible_gambling_evidence": "Exact responsible/safer-gambling passages.",
            "material_terms": "Exact eligibility, deposit, odds, rollover, expiry, and exclusion terms."
        },
        n_rounds=2,
        model=BALANCED,
        save_dir=f"{ROOT}/05_codify",
        reset_files=False,
    )

    # 5. Multimodal fusion. `fusion_prompt` requests strict evidence JSON.
    fusion_input = build_fusion_rows(screened, text_extract, image_extract, labels, ratings, coded)
    fused = await gabriel.whatever(
        df=fusion_input,
        column_name="fusion_prompt",
        identifier_column="creative_version_id",
        image_column="representative_frame_path",
        audio_column="audio_path",
        model=STRONG,
        json_mode=True,
        n_parallels=650,
        save_dir=f"{ROOT}/06_fusion",
        reset_files=False,
        return_original_columns=True,
    )

    # 6. Deterministic QC and escalation
    qc = compute_qc(fused)  # range, null, evidence, contradiction, vote entropy, run SD
    escalate_ids = qc.query(
        "parse_failure or missing_required_evidence or cross_modal_conflict "
        "or vote_entropy > @ENTROPY_LIMIT or run_sd > @SD_LIMIT"
    ).creative_version_id

    escalated = await rerun_with_stronger_model_and_high_detail(
        fusion_input[fusion_input.creative_version_id.isin(escalate_ids)],
        save_dir=f"{ROOT}/07_escalation"
    )

    # 7. Merge only after exact ID checks; preserve both original and escalated values.
    final = deterministic_resolve(fused, escalated, qc)
    write_versioned_release(final, spec="ads_cues_v1.0.0")
    return final

asyncio.run(measure_ads(bundle_df))
```

GABRIEL writes cleaned outputs, raw-response checkpoints, and task metadata in `save_dir`; compatible runs can resume with `reset_files=False`. A changed prompt, model, attribute definition, labels, batching meaning, or schema should use a fresh directory or intentional reset so incompatible cached outputs are not mixed.[2][3]

## 7. Human validation protocol

The OpenAI-hosted paper frames validation around **accuracy** (agreement with accepted benchmarks) and **directness** (measurement driven by the intended content rather than memorized or correlated cues). It compares model-human agreement with human-human agreement and tests prompt robustness and signal stripping.[6] Apply the same logic specifically to betting ads.

### 7.1 Gold-standard sample

Draw a stratified sample before seeing model errors:

- all modalities and platforms;
- product types and operators;
- short/long creatives;
- inducement/no-inducement;
- high/low terms prominence;
- languages and jurisdictions;
- youth-relevant and adult-oriented placements;
- edge cases: affiliate/editorial hybrids, brand-only sponsorship, satire, non-gambling sports content;
- oversample rare/high-stakes labels, then use sample weights for prevalence estimates.

Recommended phases:

1. **Development set:** 150–300 bundles for codebook revision.
2. **Locked validation set:** at least 500 bundles if estimating common binary performance; enlarge for rare labels and subgroup claims.
3. **Drift set:** rolling sample from later campaigns/platforms, never used to tune the locked specification.

### 7.2 Human coding

- Two independent coders per item; three for ambiguous/high-stakes dimensions.
- Coders are blinded to model outputs and, when feasible, advertiser/campaign metadata not needed for coding.
- Train with an explicit manual containing anchors and boundary cases.
- Record raw individual judgments before adjudication.
- Adjudication creates a consensus label but does not overwrite the individual labels needed to estimate human-human reliability.
- Capture coder confidence and `unknown/unobservable` separately.

### 7.3 Metrics

| Variable type | Human-human | Model-human | Additional checks |
|---|---|---|---|
| Boolean | Krippendorff’s alpha or Gwet’s AC1; percent agreement | sensitivity, specificity, precision, recall, F1, AC1/alpha | prevalence-adjusted confusion matrix; subgroup error |
| Nominal multi-class | alpha; macro agreement | macro/micro F1; confusion matrix | mutually exclusive violation rate |
| Ordinal/0–100 | ICC(2,1), ICC(2,k), weighted kappa, Spearman | ICC/Spearman, MAE, mean bias, calibration slope/intercept | Bland–Altman limits; error by score range |
| Evidence spans | span/token overlap and boundary distance | precision/recall of supported evidence | unsupported-positive rate |
| Extraction | exact/normalized match | field accuracy, completeness, hallucination rate | material-term omission rate |

Primary acceptance criteria should be construct-specific and preregistered. An example—not a universal standard—is: model-human reliability no worse than the lower 95% bound of individual-human-versus-consensus reliability, F1 >= 0.80 for common safety-relevant booleans, and unsupported-positive rate < 2%. Rare cues may need precision-recall targets rather than accuracy.

### 7.4 Directness tests

For each important cue, create controlled counterfactuals:

- remove inducement text while preserving operator, sport, celebrity, colors, and general excitement;
- remove brand/team identity while preserving the offer;
- remove countdown/urgency language while preserving offer value;
- remove music/crowd audio while preserving speech;
- obscure fine print while preserving headline claims, and vice versa;
- replace bonus amount while preserving layout;
- compare original and de-branded paraphrases.

The target rating should attenuate when its direct signal is removed, while unrelated control ratings should remain stable. `debias` implements the paper’s signal-stripping logic: measure original score `y`, stripped score `s`, remaining direct signal `r`, estimate the residual inference component, and subtract it from the original.[4][6]

## 8. Inter-run reliability

Use repeated runs to characterize stochastic measurement error, not merely to manufacture consensus. GABRIEL exposes `n_runs` for rate, classify, extract, compare, discover, deduplicate, merge, and filtering workflows, with task-specific aggregation.[4]

### Protocol

1. On the pilot and validation sets, run `n_runs=5`; use `n_runs=3` at scale only after stability is established.
2. Preserve every run-level value before aggregation.
3. For booleans, compute vote share, entropy, pairwise agreement, and any-label flip rate.
4. For ratings, compute within-item SD, ICC across runs, median absolute pairwise difference, and rank correlation.
5. Repeat a smaller panel on different dates or model snapshots to distinguish within-model randomness from model drift.
6. Re-run with one semantically equivalent prompt variant on a subset; the paper reports strong stability across large prompt variations, but this must be checked for the betting-ad codebook rather than assumed.[6]
7. Define escalation rules, for example:
   - boolean vote share in `[0.4, 0.8]`;
   - rating SD > 12 points;
   - high/low decision changes under plausible threshold choices;
   - extraction fields disagree across runs;
   - evidence differs in a materially contradictory way.

Do not report only the averaged score. Release `mean`, `median`, `sd`, `min`, `max`, `n_successful_runs`, and disagreement flags.

## 9. Cost-aware model routing

The official operating guide recommends piloting candidate models on representative examples and choosing the smallest model that reliably meets the research standard; it also warns that cost estimates are planning aids and live model/pricing/endpoint support must be verified.[2][3]

### Routing ladder

1. **Mechanical, no model:** file hashes, exact duplicate detection, video segmentation, OCR/ASR generation, DOM extraction, duration/font/contrast computations.
2. **Fast/lowest-cost model:** high-recall `filter`, obvious entity extraction, common boolean cue labels, duplicate candidate screening.
3. **Balanced model:** nuanced ratings, evidence coding, material-terms extraction, multimodal image analysis.
4. **Strong model:** cross-modal fusion, conflicting evidence, satire/affiliate hybrids, complex legal terms, low-confidence/escalated cases.
5. **Human:** unresolved high-stakes claims, validation sample, material-term omissions, or cases where model disagreement would alter a substantive conclusion.

### Conditional routing

```text
if corrupt_or_missing_asset: quarantine
elif exact_hash_duplicate: inherit annotations only if all material fields match
elif high_recall_filter_negative and audited_probability < threshold: stop
else:
    run cheap classification/extraction
    if parse failure, low confidence, disagreement, fine-print dependence,
       cross-modal conflict, rare label, or subgroup known to underperform:
        escalate model and/or image detail
    if still unresolved and safety/substantive impact is high:
        human adjudication
```

### Modality-specific savings

- Images: low/auto detail first; high/original only for fine print, dense odds, or QC failures.
- Video: analyze scene/key frames and screen-time-weighted OCR rather than every frame.
- Audio: transcript first for semantic claims; raw audio only for acoustic constructs or transcript uncertainty.
- Landing pages: deterministic DOM extraction first; model calls on relevant sections/screenshots.
- Deduplication: exact/perceptual matching, embeddings shortlist, then GPT confirmation. GABRIEL’s `merge` and `deduplicate` already use embeddings-assisted candidate reduction.[2][4]
- Attribute batching: keep related attributes together unless pilots show schema/context degradation; the official guide advises not splitting preemptively.[3]

Budget by **prompt count × modality × expected retries × escalation rate**, then compare cost per validated field, not cost per API call.

## 10. Provenance, versioning, and release discipline

GABRIEL’s repository supports checkpointing, raw response files, cleaned outputs, and run metadata, but the research pipeline should add a stricter manifest. The checked-out official source at the time of this memo was commit `9caced978453d4ae857118eed01ed6abe9e72723`; pin a commit or released package version for every production dataset.[1][3]

### Required run manifest

```yaml
study_id: betting_ads_cues
release_id: 2026q4_ads_cues_v1_0_0
annotation_spec_version: 1.0.0
gabriel:
  package_version: pinned
  git_commit: 9caced978453d4ae857118eed01ed6abe9e72723
models:
  fast: {slug: verified-live-slug, endpoint: responses, checked_at: 2026-10-08}
  audio: {slug: verified-live-slug, endpoint: chat-completions, checked_at: 2026-10-08}
prompts:
  extract_sha256: ...
  classify_sha256: ...
  rate_sha256: ...
attributes_sha256: ...
json_schema_sha256: ...
input_manifest_sha256: ...
code_git_commit: ...
preprocessing:
  ocr_engine_version: ...
  asr_engine_version: ...
  frame_extraction_config: ...
run:
  started_at_utc: ...
  completed_at_utc: ...
  n_rows_requested: ...
  n_rows_complete: ...
  reset_files: false
  random_seeds: {...}
validation:
  human_codebook_version: ...
  gold_set_hash: ...
```

### Semantic versioning

- **PATCH:** parsing/QC correction that does not alter construct meaning; reprocess affected rows and document impact.
- **MINOR:** add a variable or non-breaking modality; do not silently backfill with a different model/spec.
- **MAJOR:** change construct definitions, anchors, fusion policy, model family in a way that changes comparability, or annotation unit. Create a new dataset release.

Store immutable raw assets, raw model responses, parsed long-form annotations, aggregate wide tables, validation labels, and analysis-ready releases separately. Never overwrite historical landing-page snapshots or campaign versions.

## 11. Failure modes and mitigations

| Failure mode | Consequence | Detection | Mitigation |
|---|---|---|---|
| Construct leakage / shortcut inference | Brand/team/celebrity drives a cue rating without direct cue evidence. | Signal stripping; de-branding; unrelated control ratings. | `codify`, controlled `paraphrase`, `debias`, evidence requirement. |
| Exposure/content conflation | Claims about behavioral impact from creative features alone. | Missing impression/person linkage. | Label estimand as content potency; merge delivery/outcome data separately. |
| Fine-print invisibility | Terms extracted although no viewer could realistically perceive them. | Compare presence with size/contrast/duration/audibility. | Separate `terms_present` from `terms_prominence`; high-detail rerun. |
| OCR/ASR error | Wrong odds, amounts, expiry, or disclaimer. | OCR-direct vision disagreement; transcript confidence; cross-run mismatch. | Preserve raw media; second OCR/ASR; human adjudication for material terms. |
| Video sampling miss | One-frame CTA/disclaimer or fast flash is omitted. | Dense sampling around OCR changes; duration checks. | scene + fixed interval + change-triggered extraction. |
| Cross-modal contradiction | Incorrectly reconciled offer or risk claim. | Explicit conflict fields. | Preserve both values; do not collapse without rule/human review. |
| Duplicate leakage | Same creative appears in train/validation or is counted repeatedly. | exact/perceptual/audio/transcript fingerprints. | deduplicate before splitting; cluster-level sample assignment. |
| Over-deduplication | Materially different terms/offer variants are merged. | Compare offer fields and frame deltas within cluster. | immutable `creative_version_id`; cluster at concept level but retain versions. |
| Prompt/schema drift | Incomparable measurements across waves. | prompt/definition/schema hashes. | new `save_dir`, semantic release, bridge study on frozen panel. |
| Cached-run contamination | Old responses mixed with new specification. | manifest mismatch. | block resume unless spec hashes match; use fresh directory/reset. Official guidance warns against mixing changed specifications.[2][3] |
| Model drift/alias movement | Ratings change without code changes. | frozen-panel rerun; exact model identifier/date. | pin snapshot where possible; bridge calibration; version release. |
| Class imbalance | High accuracy hides failure on rare harmful cues. | prevalence, PR curves, stratified metrics. | oversample rare cases; precision/recall criteria; weighted estimates. |
| Correlated attributes in one prompt | Halo effects across ratings. | single-attribute versus joint-prompt experiment. | retain joint prompt if equivalent; split only affected attributes. |
| Order/position effects | First label, left comparison item, or frame order biases output. | reverse/randomized order tests. | randomized ordering with stable seed; bidirectional compare. |
| Unsupported confidence | Model emits high confidence without evidence. | evidence-confidence consistency checks. | derive QC confidence from runs/evidence/validation, not self-report alone. |
| Missingness coded as zero | Downward bias and false absence. | missing-asset and parse-success checks. | explicit unknown states; exclude/impute transparently. |
| Translation/cultural error | Cue meaning varies by language/jurisdiction. | subgroup validation with native-language coders. | language-specific definitions and models; avoid English-only fusion where nuance matters. |
| Regulatory/legal overclaim | Measurement presented as legal compliance decision. | absence of jurisdiction-specific legal review. | describe observable content; route legal judgments to qualified counsel. |
| Discovery overfit | Features discovered and tested on same corpus appear stronger than they are. | held-out performance. | human freeze taxonomy; confirm on new campaigns/time period. |
| Human gold-standard weakness | Model evaluated against inconsistent coders. | HH reliability and coder diagnostics. | revise manual, retrain, retain individual labels, compare MH with HH. |

## 12. Minimum acceptance gates before scaling

1. **Data integrity:** 100% unique `creative_version_id`; asset hashes and capture timestamps present.
2. **Completeness:** expected row/field counts reconciled; parse failures and missing media explicitly reported.
3. **Human validity:** preregistered model-human metrics meet thresholds on locked data and important subgroups.
4. **Inter-run stability:** acceptable ICC/agreement and bounded uncertainty; disagreement routed rather than hidden.
5. **Directness:** target ratings attenuate under signal removal while control attributes remain substantially stable.
6. **Evidence:** all safety-relevant positives and material extracted terms have grounded evidence.
7. **Drift:** frozen-panel comparison completed whenever model, prompt, preprocessing, or codebook changes.
8. **Cost:** observed pilot cost and escalation rate fit the approved budget with contingency for retries/media.
9. **Auditability:** raw responses, manifests, code commit, GABRIEL version, model IDs, prompt hashes, and human labels retained.
10. **Interpretation:** release documentation distinguishes creative cues, delivered exposure, audience response, and causal effects.

## Sources

[1] OpenAI GABRIEL repository — https://github.com/openai/GABRIEL  
[2] GABRIEL README, pinned commit — https://github.com/openai/GABRIEL/blob/9caced978453d4ae857118eed01ed6abe9e72723/README.md  
[3] GABRIEL agent guide, pinned commit — https://github.com/openai/GABRIEL/blob/9caced978453d4ae857118eed01ed6abe9e72723/AGENTS.md  
[4] GABRIEL public API source, pinned commit — https://github.com/openai/GABRIEL/blob/9caced978453d4ae857118eed01ed6abe9e72723/src/gabriel/api.py  
[5] GABRIEL file loading source, pinned commit — https://github.com/openai/GABRIEL/blob/9caced978453d4ae857118eed01ed6abe9e72723/src/gabriel/utils/file_utils.py  
[6] *GPT as a Measurement Tool* (OpenAI-hosted paper) — https://cdn.openai.com/pdf/7517a586-5bfa-4b87-bd3d-6ea0e9e844c7/GPT-as-a-measurement-tool.pdf  
[7] OpenAI, “Scaling social science research” — https://openai.com/index/scaling-social-science-research/

