# Implicit advertising exposures: measurement and causal research designs

**Prepared:** October 15, 2026  
**Purpose:** Convert celebrity/wearer, sponsorship, logo, and creator-feed appearances into a pilot-first empirical agenda with distinctive tests of *Ads as Cues*.

## Executive recommendation

Treat this as **three linked datasets and three different scientific problems**, not one regression:

1. **Corpus measurement:** What branded objects, logos, wearers, settings, commercial relationships, and downstream identifications appear in content?
2. **Exposure measurement:** Which people had an opportunity to see the appearance, actually attended to it, identified the brand, and inferred sponsorship or organic use?
3. **Causal effects:** What did that exposure change in memory, search, category consideration, app/site use, and purchasing?

The highest-value first paper is a randomized feed experiment crossing **logo visibility**, **commercial-relationship framing**, and **watchspotter/outfit-reviewer amplification**, with immediate and delayed memory outcomes. It directly identifies whether a seemingly organic appearance receives a **non-endorsement premium**, whether specialist identification amplifies a weak visual cue, and whether those effects are strongest among consumers with relevant prior experience. In parallel, build a timestamped appearance-contract-event panel that can support later event studies and partnership experiments.

The theory should not be tested by asking only whether visible brands increase own-brand demand. The distinctive signature from *Ads as Cues* is a joint pattern: effects should be larger for people with relevant memory stocks, spill over toward similar brands/categories, weaken or turn negative for dissimilar wants under attention constraints, and persist in delayed accessibility even when explicit ad recognition is weak.[1]

---

## 1. Conceptual objects and estimands

### 1.1 Units

Use separate IDs for:

- `appearance_id`: one branded object-person-scene occurrence in an original image/video;
- `asset_id`: one post, broadcast clip, photograph, story, or article containing appearances;
- `wearer_id`: athlete, celebrity, creator, executive, fictional character, or ordinary user;
- `brand_model_id`: brand plus identifiable product/model/reference;
- `relationship_episode_id`: contract, gifting, loan, event sponsorship, team sponsorship, platform partnership, or verified absence of a material relationship over a dated interval;
- `amplification_id`: a watchspotter, outfit reviewer, fan account, shopping affiliate, journalist, or algorithmic recommendation that explicitly identifies the item;
- `viewer_id × exposure_time`: person-level exposure or opportunity-to-see record;
- `event_id`: game, awards show, premiere, interview, viral moment, contract announcement, contract start/end, or sponsorship change.

Do not collapse an original appearance and a later “what they wore” post. The latter changes the treatment from a weak incidental cue into an explicit brand-identification message.

### 1.2 Treatment decomposition

Let:

- `V` = visual cue intensity: no item, item with logo/model occluded, item visible without readable logo, or logo/model identifiable;
- `R` = commercial-relationship state or framing: verified organic/no material connection, ambiguous, gifted/loaned, paid ambassador, or brand-owned post;
- `D` = disclosure shown to the viewer: none, “not sponsored,” gifted, paid partnership, or brand sponsorship;
- `A` = amplification: no follow-on identification, neutral spotter/reviewer identification, affiliate/shoppable identification, or brand repost;
- `F` = exposure frequency and spacing;
- `H` = viewer’s pre-treatment memory stock: prior ownership, purchase, search, app use, category expertise, fandom, and prior exposure;
- `S` = similarity between the cue and the outcome brand/category/occasion;
- `C` = context: event importance, wearer-product fit, scene centrality, item contact/use, and competing visual information.

The clean experimental treatment is a vector `T=(V,R/D,A,F,C)`, not “saw celebrity wearing brand.”

### 1.3 Primary estimands

1. **Incidental visual-cue effect**  
   `ATE_V = E[Y(V=visible) - Y(V=occluded)]`, holding wearer, scene, audio, timing, and image quality fixed.

2. **Identifiable-logo increment**  
   `ATE_logo = E[Y(readable logo/model) - Y(same item, identity removed)]`. This separates category/style exposure from brand retrieval.

3. **Non-endorsement premium**  
   `NEP = E[Y(R=verified organic or D=not sponsored) - Y(R=paid and disclosed)]` for the same wearer, product, scene, and visual exposure. Estimate both:
   - a **belief-framing NEP**, induced by randomized disclosure text;
   - a **relationship-state NEP**, induced or recovered from actual contract status.

4. **Spotter/reviewer amplification effect**  
   `ATE_A = E[Y(original appearance + identification) - Y(original appearance only)]`.

5. **Amplification of an implicit cue**  
   `INT_AV = [Y(V=visible,A=1)-Y(V=visible,A=0)] - [Y(V=occluded,A=1)-Y(V=occluded,A=0)]`.

6. **Cue-memory complementarity**  
   The interaction of randomized exposure with pre-treatment `H`, preferably allowing concavity at very high familiarity.

7. **Similarity gradient and interference**  
   Effects on the worn brand, close rivals, total category, adjacent categories, and preregistered dissimilar categories as a function of `S`.

8. **Persistence and decay**  
   Effects at immediate, 24–72 hour, one-week, and—where behavior is passively observed—multiweek horizons.

9. **Total partnership effect**  
   The effect of a platform/brand or event sponsorship package, including paid posts, incidental appearances, amplification, algorithmic distribution, search, and substitution. This is not the same as the effect of one viewed appearance.

### 1.4 Why the “non-endorsement premium” is theoretically useful

A paid disclosure can activate persuasion knowledge; an apparently organic choice can instead be interpreted as costly personal revealed preference. FTC guidance makes clear that material connections can include payment, free or discounted products, or other relationships and should be disclosed, so “no #ad label” is not proof of no commercial connection.[2] Research on explicit declarations of non-sponsorship also implies that “not sponsored” is itself a message, not a neutral absence of advertising.[3]

The causal claim should therefore be narrow: **conditional on identical visual content, does an experimentally induced belief that the wearer selected the item without compensation increase brand response?** A stronger field claim requires dated contract, gifting, loan, and agency records—not disclosure text alone.

---

## 2. Corpus measurement: what exists in content

### 2.1 Appearance corpus

Build an append-only corpus from public posts, licensed editorial imagery, broadcast clips, brand/creator archives, event photo feeds, and specialist spotter/reviewer posts. The unit should be an appearance, with all source assets and transformations linked by stable IDs.

Core fields:

- timestamp, platform, source account, URL/archive pointer, and asset hash;
- wearer identity and role;
- event, venue, scene, and occasion;
- product category, brand, model/reference, confidence, and evidence crop;
- logo visibility, screen share, pixel area, duration, repetitions, camera centrality, and occlusion;
- wearer contact/use: merely present, worn, held, actively used, discussed, praised, or purchased;
- visual attention competitors: face, text, other brands, motion, cuts, and clutter;
- audio/text mentions and captions;
- commercial disclosure text and platform paid-partnership labels;
- best available relationship state, source, validity dates, and uncertainty;
- original appearance versus repost, editorial coverage, spotter identification, affiliate link, or brand repost;
- engagement and distribution fields, with retrieval timestamps because counts evolve;
- downstream identification lag: time from original appearance to first specialist identification.

Celebrity-focused content can generate a “vampire effect,” in which attention goes to the celebrity rather than the product; eye-tracking work suggests that wearer-product contact and gaze can redirect attention toward the product.[5] Code those features rather than treating every logo pixel as equivalent exposure.

### 2.2 Relationship and contract ledger

For each wearer-brand pair, maintain dated episodes:

- no known material connection after documented search;
- rumored/uncertain;
- stylist loan or event loan;
- gifted item;
- affiliate relationship;
- paid one-off post;
- ambassador contract;
- team, league, event, studio, or platform partnership that can constrain wardrobe/content;
- relationship announcement, effective start, renewal, suspension, and end.

Store provenance and confidence. “No known contract” must remain distinct from “verified no material connection.” Contract announcements can lag the true start; creators may receive products before public announcement; wardrobe may be selected by stylists rather than wearers.

### 2.3 Amplification graph

Construct a directed cascade:

`original appearance → fan reposts → specialist identification → mainstream fashion/watch coverage → affiliate/shoppable posts → brand repost → search/site traffic`.

For every edge, save timestamp, audience size, explicitness of brand identification, model-level information, sentiment, commercial link, and overlap with prior audiences where available. This allows estimation of:

- probability an appearance gets identified;
- time to identification;
- additional reach created by each amplifier type;
- whether the amplifier changes an implicit cue into explicit product information;
- whether brand reposting crowds out the organic-authenticity inference.

### 2.4 Measurement validation

Create a locked, stratified human-coded set oversampling small logos, partial views, videos, ambiguous disclosure, and putatively organic appearances. Report:

- brand/model precision and recall;
- temporal intersection-over-union for video appearances;
- logo visibility and prominence reliability;
- relationship-state agreement by evidence tier;
- false matches caused by visually similar products;
- performance by skin tone, gender presentation, image quality, category, platform, and language;
- sensitivity of results to high-confidence-only versus probabilistic labels.

The corpus answers prevalence and selection questions. It does **not** establish that followers saw, noticed, or were affected by the content.

---

## 3. Exposure measurement: opportunity, attention, identification, and belief

Use an explicit exposure ladder:

0. **Eligible:** viewer could have received the asset.
1. **Served:** platform recorded an impression.
2. **Viewable:** asset met a prespecified on-screen/time threshold.
3. **Dwell:** viewer remained on the asset or video segment.
4. **Fixated:** gaze entered the item/logo area of interest.
5. **Noticed:** viewer later indicates awareness that a branded object appeared.
6. **Identified:** viewer names or selects the brand/model.
7. **Commercial inference:** viewer classifies the appearance as organic, gifted, paid, or uncertain.
8. **Encoded/retrievable:** brand/category accessibility changes immediately or later.

A corpus count is level 0 at best. Platform impressions usually reach levels 1–3. Eye tracking supplies level 4. Recognition, recall, and inference tasks supply levels 5–8.

### Exposure estimands

- **Intention-to-treat (ITT):** effect of assignment to a feed containing the appearance.
- **Per-impression effect:** ITT divided by a defensible first-stage change in served/viewable exposure.
- **Effect of fixation:** only causal if fixation is experimentally shifted—for example by randomized crop, logo position, or wearer gaze—not if viewers self-select where to look.
- **Effect of identification:** identify using randomized spotter/reviewer labels or prompts; do not condition naively on successful recognizers.
- **Dose-response:** randomize frequency/spacing because organic repeat exposure is selected by fandom and algorithms.

---

## 4. Causal design portfolio

## Design 1 — Randomized logo occlusion/removal experiment

**Design.** Create matched versions of the same authentic image or clip: original; logo/model identifier removed while preserving the object; full object removed or replaced with a visually matched generic item; and, where credible, a logo-swap condition. Use inpainting and blinded visual-quality audits.

**Estimands.** `ATE_V`, `ATE_logo`, and effects on worn-brand, rival-brand, category, and dissimilar-category outcomes.

**Identifying variation.** Random assignment of asset variant, stratified by wearer and scene.

**Outcomes.** Eye fixation; unaided and aided brand recall; category accessibility; forced choice; incentivized product choice; search-box queries; delayed recognition; real click/site behavior where permitted.

**Distinctive signatures.** If the item itself cues a category, object-visible/logo-removed should raise category and rival accessibility. If brand identity matters, the readable-logo increment should disproportionately raise own-brand retrieval. Effects should be stronger for prior users/owners and may spill to similar brands.

**Threats.** Editing artifacts; demand effects; logo removal may change aesthetics; participants may scrutinize research stimuli more than real feeds; a swap can be implausible.

**Falsification tests.** Blind raters should not distinguish editing quality; edit a nonbrand region as a sham; use mirrored/cropped variants; test nonexistent-brand logos; verify no pre-treatment differences across assignment; show that effects concentrate in brand/category outcomes rather than every positive evaluation.

**Value.** Fastest clean proof that an incidental visible cue, rather than the celebrity or occasion alone, changes retrieval.

## Design 2 — Feed-based factorial lab/online experiment

**Design.** Place target appearances inside a realistic scrollable feed with distractor posts. Randomize:

- logo/object visibility `V`;
- relationship disclosure or framing `D`;
- reviewer/spotter amplification `A` shown later in the feed;
- frequency and spacing `F`;
- category-context similarity `C`.

A core `2 × 3 × 2` design is: identifiable versus identity-removed item; “paid partnership,” “not sponsored,” or no relationship information; spotter identification versus none. Add a smaller verified-organic information arm if evidence can be conveyed truthfully.

**Estimands.** ITTs for each factor; the non-endorsement premium; `A×V`; interactions with pre-treatment ownership/familiarity and cue-outcome similarity.

**Identifying variation.** Participant-level or feed-level randomization; stimuli blocked by wearer and brand so results do not depend on one celebrity.

**Outcomes.** Natural scrolling/dwell; spontaneous query entry; immediate free recall; logo and model recognition; commercial-inference beliefs; brand/category choice; delayed recall and recognition; optional browser/site visits over a consented follow-up.

**Distinctive signatures.** A non-endorsement premium should operate through perceived authenticity/revealed preference, not merely through noticing. Spotter amplification should sharply increase correct identification and search; it may reduce the premium if an affiliate or brand repost makes the cascade feel commercial. Cue effects should be larger among experienced category users, while an information account may be stronger among novices.

**Threats.** Artificial feed; explicit disclosure manipulation may dominate subtle cueing; attrition in delayed follow-up; brand-by-wearer fit confounds if stimuli are not crossed; repeated measurement can rehearse brands.

**Falsification tests.** Neutral noncommercial labels; false-but-plausible category labels prohibited, but generic factual captions can provide an attention placebo; outcomes for unshown brands; shuffled brand-wearer pairs; no-item celebrity posts; preregistered manipulation checks separated from primary outcomes; measure and report experiment guessing.

**Value.** Best pilot-to-paper path because it simultaneously identifies cueing, commercial inference, and amplification.

## Design 3 — Eye-tracking mechanism study

**Design.** Run a subset of the factorial feed stimuli in a desktop or mobile eye-tracking environment. Define face, product, logo, disclosure, caption, and other-brand areas of interest before analysis. Randomize wearer-product contact, gaze direction, crop, logo position, and reviewer overlay.

**Estimands.** Effects on first-fixation probability/time, dwell, revisits, transition from face to product, and downstream memory. Use randomized visual features as instruments for attention only if they satisfy a credible exclusion restriction; otherwise treat gaze as a mediator, not a treatment.

**Identifying variation.** Randomized visual composition and cue visibility.

**Threats.** Lab calibration and device effects; central fixation bias; altered natural viewing; eye fixation is not encoding; exclusion fails because crop/contact can affect meaning directly.

**Falsification tests.** Predefine areas; use sham shifts of irrelevant objects; replicate on mobile and desktop; verify that mechanically increased fixation predicts item-specific rather than global recall; report results both with and without low-quality calibration sessions.

**Value.** Mechanism paper or strong section of the main experiment. It explains when a famous wearer amplifies versus visually crowds out a brand.[5]

## Design 4 — Immediate and delayed memory battery

**Design.** Attach a standardized outcome schedule to Designs 1–3:

- immediate: free recall of all brands/categories, recognition with lures, implicit accessibility/lexical or categorization latency, and choice;
- 24–72 hours: surprise recall/recognition and search;
- one week: recognition, confidence, source memory, and commercial-relationship memory;
- longer horizons: passive search/site/app outcomes where consented.

**Estimands.** Treatment effects on explicit versus implicit memory, forgetting rates, source confusion, and persistence.

**Identifying variation.** Original randomized exposure; randomize whether an intermediate survey is administered so the measurement itself does not become unaccounted rehearsal.

**Threats.** Survey-induced rehearsal; differential attrition; recognition lures can create familiarity; implicit-task interpretation is contested; repeated outcomes encourage hypothesis guessing.

**Falsification tests.** Attrition bounds and inverse-probability weighting; randomize follow-up prompts; use category-matched lures; include unexposed brands; test source-memory errors (“saw on wearer” versus “saw in reviewer post”).

**Value.** Crucial because implicit exposure may change accessibility without producing accurate explicit recall. Brand-placement evidence generally finds larger memory than attitudinal or behavioral effects, so behavioral outcomes should remain primary where possible.[4]

## Design 5 — Observational viewer panel

**Design.** Recruit consented participants who link social-platform data donations or install a research browser/mobile meter, complete baseline brand/category histories, and permit passive observation of search/site/app use. Match served posts to the appearance corpus; follow outcomes at hourly, daily, and weekly frequency.

**Estimands.** Associations and, where defensible variation exists, local causal effects of viewable exposure and cumulative dose on search, site/app use, and purchase proxies. Estimate heterogeneous effects by prior category/brand behavior and similarity.

**Identifying variation.** Preferred: feed-position shocks, randomized notification timing, platform outages, or experiment assignments. Weaker: within-person event-time around first measured exposure with rich time and content controls.

**Threats.** Algorithmic targeting, fandom, reverse causality, cross-device missingness, incomplete platform coverage, shared shocks, exposure misclassification, panel Hawthorne effects, and severe selection into data donation.

**Falsification tests.** Pre-trends; future-exposure leads; outcomes before the post; unrelated brands/categories; non-logo celebrity posts; negative-control creators; compare served versus actually dwelled; sensitivity to person-day, creator-time, and event fixed effects; Oster/Rosenbaum-style sensitivity only as diagnostics, not proof.

**Value.** Bridges lab mechanism and real behavior, but should not be the first causal claim unless assignment variation is recovered.

## Design 6 — Creator contract starts, expirations, and exclusivity changes

**Design.** Build wearer-brand-week panels around contract start/end, public ambassador announcements, exclusivity clauses, and changes in allowed categories. Compare the focal brand, close rivals, and dissimilar brands for the treated wearer against matched wearers and untreated brands.

**Estimands.** Intent-to-treat effect of entering or leaving a commercial relationship on appearance frequency, disclosure, amplification, search, and sales/app outcomes; decomposition into explicit posts versus incidental wearing.

**Identifying variation.** Event-study variation around dated contract episodes; strongest when expiry or termination is predetermined, forced by eligibility/conflict rules, or caused by an external event rather than sales expectations.

**Threats.** Contracts are chosen based on expected growth; announcement timing differs from effective timing; pre-contract seeding; simultaneous campaigns/product launches; scandals or injuries; wardrobe substitution; anticipation; post-termination archival content remains online.

**Falsification tests.** Event-time leads; pseudo-start dates; unaffected geographies; nonfeatured product lines; rivals with similar trends; separate announcement from effective date; exclude scandal-driven exits; test whether pre-period organic appearances predict contract selection.

**Distinctive use.** Compare response to the same wearer’s pre-contract “organic” appearances with post-contract paid appearances. A raw pre/post gap is not the non-endorsement premium because the contract changes frequency, creative control, distribution, and selection. Use matched content or a lab re-presentation of pre/post assets to isolate belief effects.

## Design 7 — Event and sports sponsorship changes

**Design.** Exploit naming-rights changes, jersey/kit supplier switches, watch/timekeeper changes, alcohol/betting sponsor restrictions, event category exclusivity, broadcast graphics changes, or venue-logo removal. Construct event × geography × audience panels and use actual viewership as treatment intensity.

**Estimands.** Total effect of sponsorship presence on brand/category search, direct traffic, app installs/use, and sales; spillovers to rivals; persistence after the event; effects per viewer or per broadcast minute where impressions are available.

**Identifying variation.** Staggered starts/ends; contractually scheduled switches; league rules; regulatory bans; broadcaster feed differences across countries; weather or match progression that changes logo screen time but is plausibly unrelated to brand demand after controls.

**Threats.** Sponsor changes coincide with rebranding, promotions, new seasons, and team performance; audience composition changes; global spillovers contaminate controls; sponsor selection follows market strategy; event outcomes may affect both attention and demand.

**Falsification tests.** Pre-trends and event-time leads; nonbroadcast regions; categories not sold in the treated market; camera-angle/logo-screen-time first stages; brands visible elsewhere in the same broadcast; outcomes during off-season; placebo event dates; synthetic-control donor sensitivity.

**Distinctive signature.** Category-generic sponsorship should expand similar-brand/category search, whereas distinctive logo-heavy sponsorship should shift more toward the sponsor. Effects should be larger among prior category users and fans with repeated exposure.

## Design 8 — Specialist spotter/outfit-reviewer natural experiments

**Design.** Observe original appearances before and after the first watchspotter/outfit-reviewer identification. Compare identified appearances with near-threshold or delayed identifications, matched on wearer, event, initial engagement, item salience, and source reach.

**Estimands.** Effect of explicit third-party identification on brand/model search, product-page traffic, resale-listing views, and downstream reposts.

**Identifying variation.** Best candidates are randomized editorial queues, rotating reviewer shifts, temporary account outages, platform-recommendation experiments, or exogenous delay caused by difficult model identification. Without such variation, estimate descriptive amplification only.

**Threats.** Reviewers select expensive, novel, controversial, or already viral items; brands seed reviewers; model-identification difficulty affects outcomes directly; timestamps are measured with error; search spikes may help reviewers identify the item rather than result from their post.

**Falsification tests.** Minute/hour-level pre-trends; searches for the wearer versus product model; delayed posts after the underlying spike has passed; reviewer posts with no new identification; wrong-category and nonmentioned-model placebos; exclude brand-fed exclusives; compare first identification with redundant later copies.

**Value.** High distinctiveness, especially in watches and fashion, but causal credibility depends on finding an external shifter or obtaining randomized distribution from a reviewer/platform.

## Design 9 — Search trends, sales, and app/site outcomes

**Design.** Assemble an outcome hierarchy:

1. brand/model/category queries;
2. direct site/product-page visits and retailer/resale views;
3. app installs, opens, searches, watchlist/add-to-cart;
4. transactions, quantities, price paid, and returns;
5. longer-run repeat use.

Use high-frequency timestamps around appearances and amplification, but aggregate to geography-time cells when privacy or sparsity requires.

**Estimands.** Reduced-form effects of assigned exposure or exogenous events on each stage; mediation should be secondary. Report sponsor, rival, category, and dissimilar outcomes.

**Identifying variation.** Inherits identification from the experiment/event/partnership. Search trends alone are outcomes, not instruments and not evidence of exposure.

**Threats.** Search may measure curiosity rather than demand; normalized trend indices complicate comparisons; stockouts and retail distribution bind; app installs can be incentivized; cross-channel campaigns coincide; high-end products have sparse sales and resale activity.

**Falsification tests.** Query taxonomies frozen before events; typo/model-number variants; unrelated celebrities and brands; direct-navigation versus informational queries; stockout windows; returns/cancellations; searches in languages/geographies without distribution; verify that search leads rather than mechanically follows news coverage.

**Value.** Converts a memory paper into an economics paper when linked to defensible assignment.

## Design 10 — Platform/brand partnership experiment

**Design.** Ask a platform, retailer, resale marketplace, brand, or creator-management firm for an experiment rather than a broad data dump. Randomize eligible users or geographies to:

- suppress versus serve an incidental appearance;
- original wearer post versus original plus specialist identification;
- paid disclosure versus truthful organic/no-relationship information where legally and factually permissible;
- normal versus identity-occluded creative;
- frequency/spacing schedules;
- brand-distinctive versus category-generic context.

Use ghost-ad or intent-to-treat logic so optimized delivery does not create incomparable treated and control audiences. Field experiments have shown that advertising can spill over to similar competitors and stimulate competitor as well as advertiser search, so partnership outcome requests must include category and rival measures.[6][7]

**Estimands.** User- or geo-level ITT; treatment-on-served/viewed where random assignment supplies an instrument; incremental profit; category/rival spillovers; heterogeneous effects by prior purchases/searches; persistence.

**Identifying variation.** Random assignment with logged eligibility, probabilities, timestamps, noncompliance, and auction/feed-ranking state.

**Threats.** Cross-device contamination; organic copies reach controls; treatment changes auction equilibrium or creator behavior; differential attrition; interference among users; retailer inventory; partner reports attributed rather than incremental conversions.

**Falsification tests.** Assignment balance; sample-ratio mismatch; treatment-blind outcome pipelines; pre-period placebo; negative-control categories; household/geography spillover checks; reconciliation of assignment, serving, viewability, and outcome counts; long enough holdout to detect delayed effects.

**Minimum partnership request.** Data dictionary; row counts; experiment inventory; assignment and eligibility tables; impression/viewability/dwell logs; post and creative IDs; relationship/disclosure metadata; coarse prior-behavior strata; search/site/app/purchase outcomes; geography at the coarsest useful level; bot/employee exclusions; clean-room export rules.

---

## 5. A unified empirical specification

For randomized or externally shifted exposure, estimate outcomes separately for own brand, close rival, total category, adjacent category, and dissimilar categories:

```text
Y_i,b,t = α
          + β1 T_i
          + β2 T_i × PriorUse_i,b
          + β3 T_i × Similarity_b,cue
          + β4 T_i × PriorUse_i,b × Similarity_b,cue
          + β5 T_i × PaidBelief_i
          + β6 T_i × Amplified_i
          + strata / time fixed effects
          + ε_i,b,t
```

Do not put post-treatment recognition, fixation, or inferred sponsorship on the right-hand side of the primary outcome regression. Estimate those as outcomes or use a prespecified causal-mediation analysis with explicit assumptions.

### Core cross-equation predictions

1. **Memory-stock complementarity:** exposure effects rise with prior category/brand experience, possibly concavely for the most familiar users.[1]
2. **Similarity gradient:** positive effects are strongest for the worn brand and close alternatives; category-level spillovers need not be business stealing.[1][6][7]
3. **Interference:** under a fixed attention/choice budget, sufficiently dissimilar categories may lose accessibility or choice share.[1]
4. **Non-endorsement premium:** identical appearances framed as organic produce greater trust/choice than paid appearances, conditional on equal notice and identification.
5. **Amplifier conversion:** spotter/reviewer identification has a larger effect when the original appearance was noticed but not correctly identified.
6. **Commercialization reversal:** neutral expert identification can amplify the organic cue, while affiliate links or immediate brand reposts may activate persuasion knowledge and reduce the non-endorsement premium.
7. **Celebrity crowd-out boundary:** famous wearers increase reach but can reduce product processing unless item contact, gaze, plot connection, or specialist identification redirects attention.[5]
8. **Delayed accessibility:** some effects survive after explicit source memory decays; repeated exposure spacing matters more for delayed than immediate outcomes.[9][10]

A persuasive paper should show several of these restrictions together. A positive own-brand coefficient alone is compatible with information, taste, signaling, selection, and generic salience.

---

## 6. Natural-experiment candidate screen

Score every candidate event before collection:

| Criterion | Strong candidate | Weak candidate |
|---|---|---|
| Timing | contractually fixed, rule-driven, or externally imposed | chosen in response to demand |
| Treatment | visible and measurable change in logos/appearances | announcement with uncertain implementation |
| First stage | screen time, impressions, or feed serving changes sharply | inferred only from press coverage |
| Controls | untreated feeds, regions, events, brands, or categories | one national time series |
| Anticipation | little or bounded | long launch leaks/seeding |
| Other changes | isolated branding/exposure change | product, price, distribution, and campaign all change |
| Spillovers | measurable and modelable | global campaign contaminates all controls |
| Outcomes | high-frequency search/app/sales | annual aggregate revenue |

Priority candidates are forced sponsor/logo removals, broadcaster-specific clean feeds, scheduled supplier switches, eligibility conflicts, and platform experiments. Sponsorship announcements, celebrity scandals, and voluntary campaign launches are usually supporting event studies rather than stand-alone identification.

---

## 7. Ranked pilot-to-paper roadmap

### Rank 1 — Feed factorial with delayed memory and real search/choice

**Question:** Do implicit wearable cues work, is there a non-endorsement premium, and does specialist identification amplify them?

**Build:** 24–40 matched wearer-product stimuli; identity-visible/removed variants; paid/not-sponsored/no-information framing; spotter amplification; realistic distractor feed; baseline ownership/familiarity; immediate and delayed outcomes.

**Primary endpoints:** unaided brand/category recall, incentivized brand/category choice, spontaneous search, and 48–72 hour recognition. Secondary: inferred sponsorship, trust, dwell, and click.

**Go gate:** manipulations change identification and commercial belief without changing perceived image quality or wearer attractiveness; delayed follow-up retention is acceptable; results are not driven by one wearer or brand.

**Paper potential:** high. Clean causal estimates and the most direct bridge from cognitive economics to current creator ecosystems.

### Rank 2 — Eye-tracking mechanism add-on

**Question:** Does the wearer attract attention to or away from the branded object, and can contact/gaze/reviewer overlays redirect attention?

**Build:** laboratory replication using a subset of Rank 1 stimuli.

**Go gate:** reliable mobile/desktop calibration and prespecified areas of interest; meaningful treatment first stage on item/logo fixation.

**Paper role:** mechanism section in the main paper or a compact companion paper.

### Rank 3 — Public corpus plus amplification graph

**Question:** How common are putatively organic appearances, which are identified by specialist accounts, and how does the cascade change explicitness and reach?

**Build:** one bounded category—watches is ideal because model references and specialist spotters are unusually legible—over a defined set of wearers/events and 6–12 months. Add fashion/outfit reviewers only after the schema works.

**Go gate:** high precision for brand/model identification; timestamped original and first-amplifier posts; relationship-state evidence; enough unamplified appearances for comparison.

**Paper role:** measurement/descriptive paper and sampling frame. Do not label amplification coefficients causal without a credible shifter.

### Rank 4 — Data-donation observational panel

**Question:** Do naturally received appearances predict within-person search/site/app behavior, especially among prior users and after reviewer amplification?

**Build:** consented meter/data donation plus baseline histories and corpus linkage.

**Go gate:** served/viewable timestamps, enough exposed participants, cross-device coverage assessment, and at least one externally generated exposure shifter.

**Paper potential:** medium to high if assignment or feed-position variation is recoverable; otherwise validation/descriptive evidence.

### Rank 5 — Contract/event natural experiment

**Question:** What is the total market effect of starting/stopping an ambassador or sponsorship relationship, and does “organic” pre-contract wearing differ from paid post-contract wearing?

**Build:** event ledger, screen-time first stage, high-frequency search/app/sales outcomes, matched controls, and content decomposition.

**Go gate:** sharp implementation date, stable controls, no simultaneous product/distribution shock, adequate pre-period, and a measurable first stage.

**Paper potential:** high for a rare clean event; low if selected from ordinary campaign announcements.

### Rank 6 — Platform/brand/spotter partnership randomized holdout

**Question:** What is the real-world incremental effect on app use, search, transactions, and profit?

**Build:** user or geo holdout; original-only versus original-plus-amplifier arms; exposure logs and prior-behavior strata.

**Go gate:** randomization, rival/category outcomes, delayed holdout, and exportable clean-room estimates.

**Paper potential:** highest external validity but longest lead time and greatest partnership risk. Pursue in parallel, not as the only viable route.

---

## 8. Concrete first pilot

### Sample and stimulus strategy

Use watches as the first domain because incidental wearing is common, products are visible but often unidentified, commercial relationships vary, model-level search is observable, and specialist watch-identification accounts create timestamped amplification. Sample across:

- ambassadors wearing contracted brands;
- known collectors wearing noncontracted brands;
- ambiguous relationships;
- high- and low-product-fit wearers;
- prominent and subtle logos/models;
- events with dense press coverage and ordinary social posts.

Create matched treatments from the same source asset; do not compare different celebrities as the primary identification strategy.

### Experimental arms

1. item identity removed, no amplification;
2. item identifiable, no amplification;
3. item identifiable + neutral watchspotter identification;
4. item identifiable + affiliate/shoppable identification;
5. each of 2–4 crossed with paid partnership, no relationship information, or factually supportable “not sponsored” framing.

If the full factorial is too large, prioritize identifiable versus identity-removed, paid versus no relationship information, and neutral amplification versus none. Treat explicit “not sponsored” as a separate treatment because it can itself increase perceived impartiality.[3]

### Pre-treatment measures

- brand and category ownership;
- purchase/search recency and frequency;
- unaided category consideration set;
- wearer familiarity and fandom;
- category expertise;
- perceived wearer-brand fit measured on separate participants where possible;
- general ad skepticism and disclosure comprehension.

### Primary outcomes

- spontaneous search terms in an unrestricted search box;
- incentivized allocation across worn brand, close rivals, and outside-category options;
- unaided brand and category recall;
- delayed recognition with category-matched lures;
- source memory and perceived commercial relationship.

### Preregistered decisive tests

1. `visible-identifiable > identity-removed` for own-brand retrieval;
2. positive spillover to similar brands/category among prior category users;
3. `visible × prior use × similarity > 0`;
4. neutral spotter amplification increases correct brand/model identification and search;
5. paid framing lowers choice/trust relative to organic/no-relationship framing, conditional on equivalent identification—the belief-framing non-endorsement premium;
6. affiliate amplification produces more clicks but a smaller authenticity premium than neutral identification;
7. effects persist at 48–72 hours and are not explained solely by immediate explicit recall;
8. no generalized lift for unshown, dissimilar brands.

### Failure interpretation

- **No visibility effect but strong amplification effect:** raw wearable appearances may be too weak to identify; the economic treatment is the reviewer cascade.
- **Immediate recognition but no delayed/behavioral effect:** attention without durable retrieval or demand.
- **Paid disclosure raises effects:** disclosure may signal quality, legitimacy, or costly brand confidence; sponsorship can serve as a signal rather than merely trigger skepticism.[8]
- **Effects concentrated among novices:** information/awareness dominates memory-stock cueing.
- **Own brand rises while close rivals fall:** brand-specific persuasion or substitution dominates category cueing.
- **Celebrity boosts recall of self but not product:** vampire/crowd-out mechanism; test contact, gaze, and reviewer redirection.[5]

---

## 9. Reporting rules

Every result should state which layer it belongs to:

- **Corpus prevalence:** share of assets containing a detectable brand/object;
- **Opportunity to see:** served or viewable impressions;
- **Attention:** dwell/fixation;
- **Identification/memory:** notice, recall, recognition, source memory;
- **Behavior:** search, site/app activity, purchase;
- **Market effect:** total category/sponsor/rival sales or profit.

Never use “exposure” without naming the rung. Never call an appearance organic solely because it lacks a disclosure. Never condition the main causal estimate on post-treatment recognition. Never infer the reviewer effect from amplified-versus-unamplified posts without modeling reviewer selection. Report own-brand, rival, category, and negative-control outcomes together.

## Decision

Proceed immediately with the **watch-wearing factorial feed pilot**, designed around logo occlusion, relationship framing, and watchspotter amplification, and add a delayed memory wave. In parallel, build the appearance-contract-amplification corpus as the sampling frame and search for one rule-driven sponsor/logo change with a measurable first stage. Approach platforms, brands, resale marketplaces, and specialist reviewer accounts only after the pilot demonstrates a treatment first stage and fixes the exact partnership estimand.

## Sources

[1] https://www.nber.org/papers/w34387
[2] https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
[3] https://www.sciencedirect.com/science/article/pii/S0747563221001813
[4] https://www.sciencedirect.com/science/article/pii/S0167811621000185
[5] https://www.tandfonline.com/doi/full/10.1080/10641734.2023.2209848
[6] https://journals.sagepub.com/doi/10.1509/jmr.14.0274
[7] https://ideas.repec.org/a/kap/qmktec/v13y2015i2p93-115.html
[8] https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2721468
[9] https://doi.org/10.1086/209548
[10] https://onlinelibrary.wiley.com/doi/10.1111/j.1460-2466.2007.00353.x
