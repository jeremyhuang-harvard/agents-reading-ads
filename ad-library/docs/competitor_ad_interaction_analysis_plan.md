# Five-firm competitor advertising and interaction analysis

## Decision

Build a targeted French Snapchat panel with up to 1,000 disclosed ad records for each of Winamax, PMU, Unibet/Kindred, Betsson, and bet365. Treat the panel as a map of observable competitive creative activity within one platform-country market—not as a representative sample of all French betting advertising or proof of delivered exposure.

PMU currently exposes only 605 records through the frozen query, so its stratum will be exhausted rather than padded with another firm's ads. The other firms will be capped at 1,000 even if the archive contains more.

## Research objects

The project should store four linked objects rather than collapsing each ad into one opaque vector.

### 1. Ad-record ledger

One row per disclosed ad record:

- stable Snap ad ID;
- advertiser query, normalized company, and disclosed payer;
- campaign start date and collection-time status;
- disclosed impressions and targeting fields;
- format and ad type;
- immutable creative SHA-256;
- source-run, retrieval time, and raw-response provenance.

This layer captures campaign variation when firms reuse the same creative with different timing, targeting, or delivery.

### 2. Creative ledger

One row per unique media SHA-256:

- modality, dimensions, duration, audio availability, and deterministic derivatives;
- OCR text, spoken text, visible brands, people, teams, leagues, and events;
- offer amount, bonus form, odds, urgency, call to action, and eligibility terms;
- color, composition, motion, music, arousal, affect, social setting, and responsible-gambling prominence;
- evidence spans or timestamps and explicit unknown values;
- versioned human/model coding provenance.

This is the interpretable representation of what the advertisement is doing.

### 3. Embedding ledger

Store several versioned representations for each creative rather than one universal embedding:

- visual embedding from the unbranded and original creative;
- OCR/copy embedding;
- combined multimodal embedding;
- video temporal embedding when a full-video protocol is ready;
- brand-masked embedding created after logos and brand names are removed;
- structured-feature vector from the creative ledger.

Every row should include the model, revision, preprocessing recipe, derivative checksum, and vector dimension. Raw vectors belong in Parquet or a vector-capable analytical store outside Git; Git should contain schemas, model specifications, checksums, and aggregate results.

### 4. Pairwise and temporal interaction ledger

For every analytically relevant ad pair, store:

- same/different advertiser;
- creative and campaign dates;
- cosine distance in each embedding space;
- structured-feature agreement and disagreement;
- shared context, sport, event, offer, emotion, audience identity, and visual motif;
- whether one creative precedes the other by 1, 2, 4, or 8 weeks;
- nearest-rival and nearest-own-brand ranks.

Do not materialize all 25 million possible pairs without need. Retain nearest neighbors, matched same-period rivals, and aggregated brand-period centroids.

## Analysis program

### A. Map the competitive creative space

1. Cluster brand-masked multimodal embeddings and separately cluster the interpretable feature vectors.
2. Label clusters from representative creatives: football fandom, welcome bonus, live-betting action, odds-led utility, humor, celebrity, social viewing, horse racing, premium expertise, urgency, and responsible-gambling messaging.
3. Report each firm's share within every cluster and each cluster's advertiser concentration.
4. Use two-dimensional projections only for visualization; conduct inference in the original vector space.

This identifies the market's semantic “territories” without assuming in advance that every firm is competing on football or price.

### B. Measure similarity, differentiation, and brand distinctiveness

For each company and month or quarter, estimate:

- **within-brand cohesion:** average distance among its own creatives;
- **between-brand separation:** distance between advertiser centroids;
- **market distinctiveness:** distance from the market centroid;
- **nearest-rival similarity:** distance to the closest competitor creative in the same time window;
- **brand predictability:** cross-validated accuracy of predicting the advertiser from brand-masked content;
- **prototype dependence:** distance from the category-wide betting-ad prototype.

High masked-brand prediction accuracy means firms occupy distinguishable creative positions. Low accuracy and systematic confusion between two firms suggest shared memory turf.

### C. Define and measure “memory turf”

Represent memory turf as associations between brands and recurring retrieval cues—not merely visual similarity. Candidate cue families include:

- football generally and named leagues, clubs, or tournaments;
- horse racing;
- expertise, statistics, and control;
- excitement, humor, friendship, and social viewing;
- large welcome bonuses and other financial inducements;
- immediacy, live action, and ease of placing a bet;
- national or local identity;
- celebrity or athlete associations;
- safer-gambling and legitimacy cues.

For each cue or cluster, calculate brand share, concentration, exclusivity, and change over time. A firm is **claiming rival turf** when it increases its share of a cue cluster previously dominated by a competitor. A firm is **carving a niche** when it persistently occupies cues with low rival presence and remains distinguishable after branding is masked.

Add a later recall experiment: show brand-masked creatives or short textual cue descriptions and ask blinded human participants which advertiser comes to mind. The resulting confusion matrix is a direct test of whether competitors occupy overlapping retrieval structures. LLM guesses may be exploratory but cannot substitute for human memory evidence.

### D. Analyze strategic interaction over time

Aggregate creatives into advertiser-week or advertiser-month representations. For every new campaign, compare its embedding and structured features with:

1. the advertiser's own strictly prior centroid;
2. each rival's strictly prior centroid;
3. a leave-one-out contemporaneous market centroid built without the focal ad or campaign;
4. the nearest earlier rival creative.

All response measures must use **strictly prior own-brand and rival windows** whose records were observable by a frozen **information cutoff**. The reference-window end must precede the focal campaign start; do not let a campaign define its own baseline. Any contemporaneous comparison must be a **leave-one-out contemporaneous benchmark**: explicitly exclude the focal ad, its duplicate ad occurrences, and any aggregate containing them. Features, centroids, nearest-neighbor indexes, and normalization constants must exclude records first observed after the information cutoff. These rules prohibit focal leakage and future leakage into predictors, benchmarks, or reference windows.

Store the focal and comparison ad IDs or period IDs, reference-window start and end, information cutoff, embedding specification ID, and leave-one-out status with every pairwise or period-level result. Recompute rather than reuse an aggregate when its provenance cannot prove these restrictions.

Construct descriptive directed measures:

- **convergence response:** firm B moves closer to firm A's prior creative territory;
- **contrast response:** firm B moves farther from A while holding its own prior position as the baseline;
- **context encroachment:** B enters a cue/event cluster historically concentrated in A;
- **offer response:** B changes bonus size, terms, urgency, or actionability following A's campaign;
- **response lag:** strongest movement at 1-, 2-, 4-, or 8-week lags;
- **innovation persistence:** whether a new territory remains associated with the entrant or is rapidly copied.

Use permutation and placebo dates to determine whether apparent lead–lag patterns exceed what would arise from common seasonality. Football calendars, tournaments, regulatory changes, and holidays can make every advertiser move together; archive timing alone does not establish that one firm reacted to another.

For permutations and placebos, rebuild every feature with the same historical availability rule. Never fit preprocessing, clusters, centroids, or hyperparameters on future periods and then apply them retrospectively to a focal date.

### E. Incumbent–challenger hypotheses

Do not assign “incumbent” from intuition. Define it using an external market-share measure if obtainable, and report archive share and disclosed impressions only as separate platform-specific proxies.

Then test two nonexclusive challenger strategies:

1. **Differentiation:** challengers are farther from the incumbent centroid, have higher niche-cluster concentration, and are easier to identify from brand-masked creative qualities.
2. **Associative encroachment:** challengers increasingly use contexts strongly associated with the incumbent—such as a specific league, football identity, or live-betting use case—while differentiating on offer, emotion, or visual style.

The most interesting cases may combine both: the challenger enters the incumbent's context but changes the claim made inside it.

## Initial structured measurement families

Freeze the final instrument only after inspecting a stratified sample, but begin with these families:

1. sport, league, club, event, and season;
2. product and wager type;
3. welcome offer, bonus amount, odds, and material terms;
4. urgency, scarcity, actionability, and live-betting orientation;
5. expertise, control, simplicity, luck, and risk-minimization claims;
6. fandom, national identity, friendship, and social normalization;
7. celebrity, athlete, team, or broadcaster association;
8. humor, excitement, suspense, triumph, and positive affect;
9. visual salience, color palette, typography, density, and brand-code prominence;
10. responsible-gambling and age-restriction prominence;
11. audience and implied user identity;
12. explicit comparative or category-leadership claims.

Literal extraction, categorical labels, ratings, and strategic interpretation must remain separate fields.

## Recommended sequence

1. Complete and verify the five-firm collection, preserving advertiser shortfalls.
2. Deduplicate at both ad-ID and creative-SHA levels and describe creative reuse.
3. Draw a blinded inspection sample across advertiser, time, modality, and exposure.
4. Extend the validated still-image codebook with competitor-positioning fields and independently human-code the inspection sample.
5. Generate original and brand-masked embeddings under a frozen preprocessing specification.
6. Produce the static competitive map and advertiser-confusion analysis.
7. Build time-indexed centroids, nearest-rival matches, and lead–lag encroachment measures.
8. Select concrete campaign episodes for qualitative inspection and eventual human memory experiments.

## Interpretation limits

- Archive presence is availability, not individual exposure.
- Disclosed impressions are displays, not unique reach or memory.
- Advertisers jointly respond to sports calendars, news, regulation, and demand.
- Start dates provide campaign timing but not complete delivery histories.
- Pairwise similarity is descriptive; it does not prove copying, interference, or strategic intent.
- The strongest claim available from this corpus alone is that firms' observable creative positions converge, diverge, or enter one another's previously occupied cue spaces over time.
