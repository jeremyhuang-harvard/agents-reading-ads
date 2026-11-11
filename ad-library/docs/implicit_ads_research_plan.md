# Backgrounded brand exposure research plan

**Captured:** October 15, 2026  
**Status:** New workstream; pilot-first steering plan

## Decision

Start a distinct workstream on **backgrounded brand exposure**: brand-linked stimuli that are available in a person's media or physical environment but are not the focal task and do not foreground an explicit sales pitch.

Use “implicit ads” or “innocuous ads” as intuitive project language, but do not make either term the measurement construct. “Implicit” can mean low attention, absent awareness, implicit memory, indirect persuasion, or undisclosed sponsorship. The empirical objects must remain separate.

This workstream should run beside—not replace—the official-ad-repository pilot. The repository study measures creatives that platforms recognize as advertisements. This workstream asks about the much larger and harder-to-observe set of brand appearances in ordinary content: apparel, watches, venue signs, broadcast backgrounds, press walls, creator sets, sports clips, screenshots, products in use, ambassadors who do not explicitly pitch, and later “spotter” or outfit-review posts that identify what was originally a weak cue.

## Corrected thesis

The important claim is not simply that subtle branding influences people without awareness. That formulation is both too broad and difficult to establish.

A sharper thesis is:

> Repeated, low-prominence brand appearances can build or reactivate brand–person, brand–occasion, brand–identity, and brand–category associations. Their effects depend on what the viewer already knows and has experienced, whether the brand is actually noticed or later identified, whether the appearance seems chosen rather than paid, and whether downstream accounts transform an ambiguous appearance into explicit product information.

The empirical opportunity created by multimodal models is to measure the **appearance layer** at scale: what brand was present, where, for how long, attached to whom, in what context, with what prominence and disclosure. That does not by itself reveal actual attention, sponsorship, or causal impact, but it creates the data foundation those questions previously lacked.

## Central distinctions

### 1. Appearance is not advertising status

A visible Kalshi logo can be:

- contracted product placement;
- an event, team, podcast, or venue sponsorship;
- an ambassador obligation;
- apparel or set decoration supplied without posting requirements;
- an affiliate or creator campaign;
- organic use;
- incidental background clutter;
- a repost whose original provenance is unknown.

The project should first record the observable appearance. Commercial provenance is a separate, evidence-graded field.

### 2. Corpus presence is not viewer exposure

Use an explicit ladder:

1. the content existed;
2. a viewer was eligible to receive it;
3. it was served;
4. it was viewable;
5. the viewer dwelled;
6. the viewer fixated on the branded region;
7. the viewer noticed or identified the brand;
8. the appearance changed later retrieval or choice.

A public view count supports an opportunity-to-see proxy for the post. It is not a count of logo impressions.

### 3. Retrieval and memory formation are different

A background appearance can:

- retrieve an existing consumption or category memory;
- create or strengthen a brand–context or brand–person association;
- convey beliefs, status, popularity, or social proof;
- trigger skepticism once commercial intent is recognized.

The strongest connection to *Ads as Cues* is not a positive average exposure effect. It is an `exposure × prior memory stock × cue similarity` pattern, including effects on close rivals and the total category.

### 4. The original appearance and later identification are different treatments

A celebrity wearing a watch or an athlete appearing near a Kalshi logo may provide only a weak visual cue. A watchspotter, outfit reviewer, fan account, journalist, affiliate, or brand repost can later name the brand and model. That downstream post changes the treatment from an ambiguous visual association to explicit information.

The project should preserve the full cascade:

`original appearance → specialist identification → reposts/editorial coverage → affiliate or brand amplification → search/site/app behavior`

## Primary research questions

1. **Prevalence:** How often do betting and prediction-market brands appear in nominally non-ad content, and how prominent are they?
2. **Provenance:** Which appearances can be linked to known sponsorships, ambassador relationships, platform partnerships, disclosures, or brand reposts?
3. **Selection:** Which people, events, settings, and content genres carry these brands?
4. **Amplification:** Which appearances are subsequently identified or explained by specialist, fan, editorial, or affiliate accounts?
5. **Memory:** Do backgrounded appearances change immediate or delayed accessibility even when viewers do not classify the content as advertising?
6. **Non-endorsement premium:** Holding the visual appearance constant, does believing that a wearer chose a product without compensation generate more trust or demand than knowing the appearance was paid?
7. **History and similarity:** Are effects larger among people with relevant prior product use, category experience, fandom, or memories of close rival brands?
8. **Category spillovers:** Does a Kalshi appearance cue prediction markets or sports betting broadly, including rivals, rather than only Kalshi?
9. **Interference:** Under a crowded feed, do strong unrelated cues suppress retrieval of the focal brand or category?
10. **Policy blind spot:** How much commercially relevant brand exposure lies outside official ad repositories and platform disclosure systems?

## Data model

Build four linked ledgers.

### Appearance ledger

One row per brand–object–person–scene episode:

- stable asset and appearance IDs;
- platform, timestamp, creator/channel, event, and source provenance;
- brand, product category, model/SKU candidates, and confidence;
- logo/product masks and evidence frames;
- visible duration and temporal intervals;
- conditional pixel share and full-asset pixel-time share;
- centrality, foreground/background, occlusion, readability, and predicted saliency;
- person–product relation: worn, held, used, consumed, discussed, praised, or merely adjacent;
- audio mention, captions, OCR, tags, links, codes, and calls to action;
- exact disclosure evidence and where/when it appeared;
- original post, repost, editorial item, specialist identification, affiliate post, or brand repost;
- public views/engagement with retrieval timestamp;
- rights/access class and archival permissions.

### Relationship ledger

One dated episode per person/property–brand relationship:

- confirmed ambassador or sponsorship;
- team, league, venue, event, podcast, platform, or production partnership;
- gifted or loaned product;
- affiliate relationship;
- one-off paid campaign;
- rumored or uncertain relationship;
- no known relationship after documented search;
- verified absence of a material relationship, where evidence permits;
- effective dates, announcement dates, end dates, evidence, and confidence.

“No disclosure” and “no known relationship” must never be coded as organic.

### Amplification graph

Link the original appearance to every later identification or amplification:

- amplifier type;
- first-identification timestamp and lag;
- whether the brand/model was named;
- neutral, editorial, affiliate, or brand-controlled provenance;
- audience and engagement snapshot;
- links, shopping functions, or promo codes;
- evidence that the original and amplified items are the same appearance.

### Viewer-exposure panel

Only where consented platform, experiment, eye-tracking, or data-donation data exist:

- assignment/eligibility;
- served and viewable timestamps;
- dwell and fixation;
- notice and brand identification;
- inferred commercial relationship;
- prior brand/category history;
- immediate and delayed memory;
- search, site/app behavior, choice, and purchase outcomes.

## Source strategy

No platform currently supplies broad discovery, reusable media, exposure counts, and reliable sponsorship status together. Use a linked-source design.

### Immediate public pilot: YouTube and Shorts

YouTube is the strongest immediate discovery source because it supports historical search, channel enumeration, stable video IDs, public view counts, and a creator-supplied paid-product-placement field. Under standard API policy, treat metadata and embedded/manual review as the default; do not assume public videos may be downloaded and retained for automated frame analysis.

Target:

- 100–200 seed entities across Kalshi, Polymarket, sportsbooks, sports media accounts, leagues, teams, athletes, creators, podcasts, and known ambassadors;
- 3,000–5,000 metadata records sampled by creator, keyword, event, and date;
- a 500-item manually reviewed validation set using embedded playback or another permitted media route;
- explicit metric-snapshot dates;
- unweighted prevalence and view-weighted opportunity-to-see reported separately.

### Parallel applications

- TikTok Research API for date-, keyword-, hashtag-, creator-, and region-bounded discovery;
- Meta Content Library/API for public Instagram/Reels and Facebook content in the approved research environment;
- creator-authorized Instagram/YouTube analytics for real account-side views, watch time, and reach;
- official commercial-content/ad libraries as positive benchmarks for disclosed and recognized paid content.

### Licensed and commercial sources

Run bounded procurement tests rather than buying broad suites immediately:

- Relo Metrics or comparable sports-logo measurement for broadcast and social sports media;
- SponsorUnited for sponsor, property, athlete, and activation relationships;
- one creator-deal discovery source such as Tubular DealMaker or Modash;
- Hive or an equivalent logo API as a build-versus-buy detector benchmark;
- Getty/AP or another licensed editorial archive for high-resolution sports and celebrity imagery.

Require a 200-item row-level evaluation export with source IDs, timestamps, boxes, confidence, audience-metric provenance, historical coverage, and academic retention rights.

## Measurement system

Treat the system as an ensemble with evidence-bound judgments.

### Specialist components

- FFmpeg/ffprobe for media normalization;
- shot-boundary detection;
- open-vocabulary object/logo proposals;
- segmentation and temporal propagation;
- closed-set logo detection for the focal brand dictionary;
- multilingual OCR;
- product/apparel/watch retrieval against a versioned catalog;
- person tracking and restricted-roster identity comparison where justified;
- speech recognition and word-level alignment;
- depth, occlusion, and visual-saliency estimation.

### LLM/VLM roles

Use GABRIEL or another evidence-bound multimodal layer for:

- entity normalization;
- person–product and brand–scene relations;
- disclosure semantics;
- narrative role and plot/task integration;
- naturalness versus forced presentation;
- promotional-presentation likelihood;
- conflict explanation and human-review routing.

Do not let the VLM invent geometry, timestamps, literal OCR, sponsorship, or identity. Every judgment should cite evidence frame, track, OCR, transcript, or metadata IDs.

### State semantics

Every substantive field uses:

- `present`;
- `absent` only after adequate observation;
- `unknown` for missing, unreadable, unsupported, contradictory, or low-confidence evidence;
- `not_applicable`.

There should be no single “implicit-ad score” in the pilot. Preserve the components until construct validity and downstream weighting are established.

## Pilot A: betting/prediction-market appearance corpus

### Objective

Prove that the project can discover, archive where permitted, and reliably measure backgrounded appearances of betting and prediction-market brands.

### Scope

Start with Kalshi and Polymarket, then add a small operator comparison set. Focus on:

- sports creator videos and Shorts;
- sports podcasts and studio sets;
- athlete and league content;
- event footage and press backdrops;
- screen recordings and market screenshots;
- branded apparel and accessories;
- reposts by fan, news, and commentary accounts.

### Sample

1. Collect 3,000–5,000 metadata candidates.
2. Deduplicate reposts and exact media where possible.
3. Draw a 500-item stratified validation sample, oversampling likely positives, small/background marks, ambiguous disclosure, and hard negatives.
4. Obtain a lawful media-processing route for at least 100–200 assets before building automated frame extraction.
5. Human-code two independent passes with adjudication.

### Outputs

- prevalence by platform, content genre, event, creator type, and brand;
- distribution of duration, size, centrality, foreground status, and disclosure;
- view-weighted opportunity-to-see indices with sensitivity to extreme view counts;
- known-relationship versus unknown-relationship appearances;
- original versus amplified appearances;
- false-negative estimate for official ad/commercial-content libraries;
- model precision, recall, calibration, and subgroup reliability;
- representative evidence packets, not public accusations of undisclosed advertising.

### Go/no-go gates

Proceed to scale only if:

- supported-brand presence reaches at least 0.90 precision and recall on the locked set;
- disclosure detection reaches at least 0.95 recall on observable cases;
- screen-time error is below 250 ms or 5% of asset duration on the validation set;
- rights/access terms permit the intended derivatives and retention;
- at least 100 confirmed or high-confidence appearances remain after validation;
- the sample contains enough variation in prominence, context, and commercial evidence to support substantive comparisons.

## Pilot B: watch-wearing non-endorsement and amplification experiment

Use watches as the clean mechanism domain even though betting is the main substantive domain. Watches have frequent incidental wearing, visually identifiable products, known ambassador relationships, specialized spotters, model-level search, and plausible cases where the wearer need not say anything.

Create a realistic feed experiment using matched versions of the same source asset. Cross:

1. product identity visible versus removed while keeping the watch/object present;
2. paid-partnership, no-relationship-information, and factually supportable non-sponsored framing;
3. no amplification, neutral watchspotter identification, and affiliate/shoppable identification;
4. immediate versus 48–72-hour outcomes.

Primary outcomes:

- unrestricted search terms;
- incentivized brand/category choice;
- unaided brand/category recall;
- delayed recognition with matched lures;
- source memory and perceived commercial relationship.

The decisive tests are:

- an identifiable-product increment relative to the same object with identity removed;
- stronger effects among prior category users and for similar brands/categories;
- a belief-framing non-endorsement premium conditional on equal identification;
- neutral specialist amplification of correct identification and search;
- possible commercialization reversal when affiliate or brand amplification raises clicks but lowers authenticity;
- persistence after 48–72 hours;
- no generalized lift for unrelated brands.

This experiment supplies causal proof of the mechanism before a harder field study of betting-brand appearances.

## Longer-run designs

Rank in this order:

1. feed factorial with delayed memory and real search/choice;
2. eye-tracking add-on to test whether famous wearers draw attention toward or away from the object;
3. public appearance corpus and amplification graph;
4. consented viewer data-donation panel;
5. rule-driven sponsorship, logo-removal, clean-feed, or contract-expiry event study;
6. platform, brand, retailer, or specialist-reviewer randomized holdout.

For every causal design, measure own brand, close rivals, total category, adjacent categories, and preregistered dissimilar categories. A positive own-brand coefficient alone cannot distinguish cueing from information, persuasion, status signaling, targeting, or selection.

## Legal and ethical boundary

The project is a measurement study, not an automated compliance-enforcement system.

- Code observable brand presence, promotional presentation, disclosure evidence, and relationship evidence separately.
- Do not call an unlabeled appearance illegal or undisclosed paid advertising solely from model inference.
- Preserve exact UI/render evidence because platform labels may not be embedded in media files.
- Use approved APIs, controlled research environments, licensed archives, or permissioned feeds; do not bypass access controls.
- Minimize collection of ordinary-user identities, faces, locations, and social graphs.
- Restrict raw media and identity crosswalks; publish aggregate results and redacted/cropped examples where possible.
- Obtain IRB/ethics and legal review before a viewer panel, biometric identification, sensitive inference, or public naming of individuals.
- Restrict person identification to public figures or approved/consented rosters and operate at a predeclared low false-match rate.

## Immediate execution sequence

### Phase 0 — Specification

1. Freeze the terminology, units, and state semantics.
2. Adopt `config/implicit_ads_codebook.json` as the pilot schema.
3. Build the first Kalshi/Polymarket brand-alias and logo catalog.
4. Define media-rights classes and allowed derivatives.
5. Prepare the 500-item human annotation guide.

### Phase 1 — Metadata discovery

1. Implement a YouTube/Shorts metadata collector.
2. Create creator, event, brand, and keyword strata.
3. Snapshot public metrics and paid-placement metadata.
4. Apply to TikTok Research API and Meta Content Library in parallel.

### Phase 2 — Human-validated corpus

1. Review 500 embedded/permitted assets.
2. Double-code a locked subset.
3. Build the relationship ledger and initial amplification graph.
4. Report prevalence, disclosure, and opportunity-to-see without causal language.

### Phase 3 — Automated measurement proof

1. Obtain 100–200 lawfully processable media assets.
2. Benchmark an in-house detector against one commercial provider.
3. Run the multimodal pipeline and calibrate each output separately.
4. Stop if the system cannot abstain reliably on unknown cases.

### Phase 4 — Mechanism experiment

1. Assemble 24–40 watch-wearing stimuli.
2. Validate visual edits and relationship framing.
3. Run the feed pilot with immediate and delayed outcomes.
4. Use the results to decide whether the first full paper should emphasize memory retrieval, non-endorsement, or reviewer amplification.

## Deliverables now in the repository

- `docs/implicit_ambient_advertising_framing.md` — concepts, mechanisms, and discriminating hypotheses;
- `docs/implicit_brand_exposure_data_sources.md` — platform, vendor, licensed-source, and access matrix;
- `docs/implicit_ads_measurement_spec.md` — multimodal pipeline, schema, confidence, and validation plan;
- `docs/implicit_exposure_causal_designs.md` — estimands and pilot-to-paper designs;
- `docs/implicit_ads_policy_ethics.md` — US/EU/UK disclosure and research boundaries;
- `config/implicit_ads_codebook.json` — initial machine-readable measurement codebook.

## Bottom line

The strongest program has two coordinated tracks:

1. a **betting/prediction-market measurement pilot** that establishes how much backgrounded brand exposure exists and how it can be measured; and
2. a **watch-wearing causal pilot** that cleanly tests the non-endorsement premium, specialist amplification, delayed memory, and prior-experience heterogeneity.

Together they turn the intuition about “innocuous ads” into a falsifiable research agenda. The key empirical object is not a binary ad label but a chain: **appearance → attention/identification → memory retrieval or association formation → amplification → behavior**.