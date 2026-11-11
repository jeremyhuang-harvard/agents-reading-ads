# Empirical outcome and identification designs

**Status:** Design menu for steering. No result below is an empirical finding. Public-data event studies measure changes in public attention, retrieval, and association; they do not establish individual exposure or sales causality.

## Recommendation in one sentence

Build the first presentation-quality pilot as a **small stacked event study of 6–10 sportswear celebrity launches/appearances**, with Tate McRae × adidas Originals Sport as the flagship case, using anchored query-level Google Trends, hourly/daily Wikipedia attention, and timestamped YouTube comments; present it as evidence on **association dynamics and competitor leakage**, not as a causal estimate of sales effectiveness.

## What each outcome means

- **Effectiveness:** Does the event increase focal-brand retrieval, attention, consideration, or choice?
- **Interference:** Does a cue retrieve rivals or the category as well as the focal brand? The useful outcome is usually the focal brand's share of all retrieved brands, not just its level.
- **Directed association:** Does celebrity/topic `C` retrieve brand `B` more strongly than brand `B` retrieves `C`? This requires separate outcomes in both directions.

A joint query such as `Tate McRae adidas` is not automatically directional. Directionality comes from a denominator or elicitation frame: joint searches as a share of all Tate McRae searches versus joint searches as a share of all adidas searches, or separate prompts that begin from the celebrity versus the brand.

## Ranking: strongest to weakest identification

The ranking is by the credibility of the stated estimand, not by ease or field realism. The strongest design—the human randomized experiment—is listed first even though the recommended first operational pilot is the public-data event study.

| Rank | Design | Primary estimand | Main classification | Causal language |
|---:|---|---|---|---|
| 1 | Matched human randomized cue experiment | ATE of distinctive versus generic cue on focal and rival retrieval | Effectiveness, interference, directed association | Yes, for the tested stimuli and recruited population |
| 2 | Unanticipated viral-appearance stacked event study | Dynamic ATT of a plausibly unscheduled appearance on public retrieval outcomes | Effectiveness and directed association; interference as a secondary outcome | Quasi-causal only after strong event-screening and pretrend tests |
| 3 | Planned campaign-launch stacked event study | Dynamic change in focal and reciprocal association around launch | Effectiveness, interference, directed association | Descriptive unless a defensible comparison or external shock is available |
| 4 | Competitor-spillover triple difference | Change in rival retrieval relative to focal retrieval, unrelated brands, and untreated events | Interference | Quasi-causal only to the extent the parent event design is credible |
| 5 | Comment/text retrieval event study | Change in spontaneous focal, category, and rival mentions in event-linked discourse | Interference and directed association | Descriptive; commenters and content supply are selected |
| 6 | Prospective query/suggestion association panel | Change in rank/share of focal and rival brands conditional on celebrity and reciprocal queries | Directed association | Measurement/descriptive, not causal |
| 7 | Matched LLM experiment | Model-system ATE of cue condition on retrieval distributions | Mechanism calibration; all three constructs | Causal for the model–prompt system, not for people |

## 1. Matched human randomized cue experiment

- **Estimand:** For target population `P`, the average treatment effect of a distinctive celebrity cue rather than a generic category cue on (i) unaided focal-brand retrieval, (ii) number/share of rival brands retrieved, (iii) delayed recognition and recall, and (iv) choice or willingness to pay. A second estimand is the asymmetry contrast: `Pr(B retrieved | C cue) - Pr(C retrieved | B cue)`.
- **Treatment/event:** Random assignment to matched creative conditions: generic product/category; distinctive orthogonal celebrity; category-congruent celebrity; no-celebrity control; optionally relationship disclosure versus no disclosure. Hold product, copy length, visual prominence, offer, and exposure time fixed.
- **Outcome:** First brand named; full ordered recall list; focal-brand rank; rival count; focal share among retrieved brands; category retrieval; confidence; delayed recall; recognition false positives; choice/WTP. Elicit celebrity→brand and brand→celebrity in separate randomized blocks.
- **Time frequency:** Immediate, 10–20 minute distractor delay, and optionally 24–72 hour follow-up.
- **Controls/estimator:** Randomization strata for baseline category use and celebrity familiarity; treatment-cell mean differences or regression adjustment; item and respondent random effects for repeated items; prespecified family-wise correction.
- **Threats:** Demand effects, unequal celebrity familiarity/liking, imperfectly matched creatives, repeated-measures contamination, attrition at delay, and a sample that is not the campaign's audience.
- **Placebos/falsification:** Unrelated celebrity–brand pairs; logo-masked creative; celebrity-name-only versus image-only cues; option-order permutations; neutral surface rewrites; outcomes for brands outside the category; manipulation checks that do not reveal the hypothesis.
- **Measures:** **Effectiveness + interference + directed association.** This is the cleanest mechanism test but not a field sales estimate.

## 2. Unanticipated viral-appearance stacked event study

- **Estimand:** Event-time ATT at horizon `k`: the change in conditional focal-brand retrieval after a plausibly unscheduled celebrity appearance, relative to a matched counterfactual path. Key outcomes are `S(C+B)/S(C)`, `S(C+B)/S(B)`, and focal share among `C+brand` searches. Here `S(.)` denotes consistently scaled or within-request anchored search interest.
- **Treatment/event:** First timestamp at which a visible but not preannounced celebrity–brand appearance becomes public, plus a separate timestamp for later explicit identification by media, fan, reviewer, or brand accounts. The original appearance and downstream amplification are separate treatments.
- **Outcome:** Query-level joint searches; related-query rank; celebrity and brand Wikipedia pageviews; focal and rival brand mentions in posts/comments; number and timing of identification articles/videos; competitor-query spillovers.
- **Time frequency:** Hourly for the first 72 hours where available; daily for ±28 or ±56 days; weekly for persistence.
- **Controls/estimator:** Stacked event study with pair fixed effects and calendar-date fixed effects; matched untreated celebrity–brand pairs in the same category; same celebrity's unrelated queries; same brand's non-celebrity queries; category-seasonality controls. Do not control for media amplification in the main total-effect specification because it is a mediator; add a secondary decomposition around the identification timestamp.
- **Threats:** The appearance may not truly be unplanned; celebrity news may jointly drive attention; reverse causality if the brand seeded the event; event-time selection based on virality; incomplete capture of the first appearance; Google Trends sampling and low-volume censoring.
- **Placebos/falsification:** Event-study leads; pseudo-event dates; pair-label permutations; wrong-brand outcomes; unrelated-category queries; matched celebrities experiencing similar news without the brand; alternative first-seen timestamps; excluding events with concurrent campaigns, product launches, scandals, or earnings news.
- **Measures:** Primarily **effectiveness and directed association**, with **interference** measured through rival retrieval. This is the strongest public-data field design if event provenance is credible.

## 3. Planned campaign-launch stacked event study

- **Estimand:** Dynamic change around launch in (i) celebrity→brand conditional search, (ii) brand→celebrity conditional search, (iii) focal-brand share of category/competitor search, and (iv) persistence or decay. Across events, estimate heterogeneity by prior distinctiveness, category congruence, and celebrity prominence.
- **Treatment/event:** Official campaign announcement, first public creative upload, first celebrity-account post, and first paid-media date where observable. Choose one primary timestamp before viewing outcomes and retain the others as staged-treatment markers.
- **Outcome:** Anchored Google Trends query series; related queries; Wikipedia pageviews; YouTube upload/search/comment outcomes; news or web co-mentions; prospective autocomplete/SERP ranks. Avoid stock returns or firm-wide sales as the primary outcome because the treatment is too small relative to the firm and concurrent news.
- **Time frequency:** Daily ±56 days as default; hourly ±72 hours for Wikipedia and timestamped comments; weekly to six months for decay.
- **Controls/estimator:** Stacked difference-in-differences/event study with not-yet-treated campaigns where feasible; event fixed effects; calendar-date fixed effects; category-by-week effects; matched celebrity–brand pairs based on pre-event search levels/trends, fame, geography, category, and launch season. Estimate each event separately before pooling.
- **Threats:** Anticipation, coordinated paid media, product availability, promotions, celebrity appearances, launch-day press, algorithmic recommendation, endogenous campaign timing, heterogeneous treatment timing, and contamination of controls by category-wide campaigns.
- **Placebos/falsification:** Pretrend coefficients; shifted launch dates; untreated brands in the same category; unrelated celebrities; non-launch geographies where rollout differs; negative-control queries; leave-one-event-out estimates; randomization inference over matched event dates.
- **Measures:** **Effectiveness + interference + directed association**, but normally descriptive. A launch event bundles celebrity, product, creative, PR, and paid distribution.

## 4. Competitor-spillover triple difference

- **Estimand:** The event-induced change in rival retrieval relative to the focal brand, net of the same focal–rival difference for untreated events or unrelated brands. A useful primary outcome is `focal mentions / (focal + named rivals)` and a secondary outcome is the extensive margin of any rival retrieval.
- **Treatment/event:** The campaign launch or viral appearance from Designs 2–3.
- **Outcome:** Search interest for `celebrity + focal brand`, `celebrity + rival`, focal/rival Wikipedia attention, rival mentions in comments, and category-only searches. Prespecify the competitor set using pre-event market/category definitions, not post-event search results.
- **Time frequency:** Daily, with hourly windows for the immediate spike.
- **Controls/estimator:** Triple interaction `post × treated pair × focal-versus-rival`; pair, brand, query, and date fixed effects; category-by-date effects; leave-one-out category aggregates; pre-event search-share weights.
- **Threats:** Competitors launch simultaneously, rivalry is misclassified, low-volume rival queries are censored, focal and rival series are jointly normalized, and category demand shocks affect all brands. A rise in rival searches can be category expansion rather than harmful interference.
- **Placebos/falsification:** Unrelated brands; second-tier rivals unlikely to be retrieved; pre-event pseudo-treatments; competitor lists defined from an earlier frozen period; re-estimation excluding each major rival; tests using category volume as a denominator.
- **Measures:** Primarily **interference**. This is best treated as a prespecified module inside Designs 2–3 rather than a stand-alone causal design.

## 5. Comment/text retrieval event study

- **Estimand:** Change in the probability that an event-linked text unit spontaneously names the focal brand, a rival, or the category, and the change in which entity is named first. Directionality is measured by separately sampling content centered on the celebrity and content centered on the brand.
- **Treatment/event:** Campaign/appearance timestamp and subsequent amplification timestamps. For a platform-specific design, compare comments by elapsed time after the same creative is posted to brand, celebrity, and media channels.
- **Outcome:** Focal/rival/category mention indicators; first-mentioned entity; co-mention graph; questions such as “what brand is that?”; explicit product identification; sentiment as secondary, not primary; retrieval precision after brand masking.
- **Time frequency:** Comment timestamp or hour; aggregate hourly/daily. YouTube's API can return comment threads for a video, filter by search terms, order by time or relevance, and paginate up to 100 results per request.[4] YouTube search can identify public videos by query and publication window, although search collection is quota-limited and should be cached.[5][6]
- **Controls/estimator:** Video/channel fixed effects where repeated content exists; elapsed-time bins; matched non-campaign celebrity videos; matched brand videos without the celebrity; language, channel type, video topic, and visible title/description controls. Preserve deleted/unavailable content as missing, not zero.
- **Threats:** Commenters are selected; platform ranking changes who comments; titles/descriptions may explicitly state the brand; moderation/deletion; bots and coordinated promotion; API search does not recover all platform content; channel audiences differ sharply.
- **Placebos/falsification:** Mask brand and celebrity names in titles/descriptions when coding text; compare literal mentions with semantically inferred mentions; unrelated videos from the same channels; shuffled event labels; pre-event videos; bot/duplicate filters; human validation of a locked text sample.
- **Measures:** **Interference + directed association**, with weak evidence on effectiveness. It is a behavioral trace of public discourse, not population memory.

## 6. Prospective query/suggestion association panel

- **Estimand:** Change in the rank, presence, or share of focal and rival brands retrieved by a fixed query battery beginning from a celebrity versus a brand. Examples: autocomplete completions, related queries, and clean-session search-result counts/ranks.
- **Treatment/event:** None is required for the measurement panel; campaign and appearance dates can be overlaid as interruptions. The cleanest use is prospective daily collection before a known launch or across many launches.
- **Outcome:** Whether the focal brand appears; rank; number of rivals; category words; reciprocal celebrity appearance; result-domain composition; Google Trends conditional/joint-query indices.
- **Time frequency:** Daily at fixed UTC/local times; multiple repeated pulls to estimate sampling/platform variance.
- **Controls/estimator:** Fixed geography, language, device/user-agent, clean profile, exact query strings, and query order; query and day fixed effects; common anchor query in every Google Trends request; repeated samples. Google describes Trends as an anonymized, categorized, aggregated sample of actual searches, so sampling variance and normalization are part of the measurement process.[2] The restricted Google Trends API alpha offers a rolling five-year window, regular daily/weekly/monthly/yearly aggregation, and consistently scaled data, but public access is not guaranteed.[1]
- **Threats:** Personalization, localization, platform experiments, opaque autocomplete filtering, scraping blocks, normalization across requests, sparse queries, and simultaneity between web content and user search. Result counts are especially noisy and should not be a primary outcome.
- **Placebos/falsification:** Stable benchmark queries; repeated same-day pulls; alternate clean endpoints/geographies; spelling variants; irrelevant celebrities and brands; frozen query order; audit for interface changes.
- **Measures:** Primarily **directed association**. Without an event and comparison group, it is measurement rather than identification.

## 7. Matched LLM experiment

- **Estimand:** For a fixed model–snapshot–prompt system, the treatment effect of cue condition on the distribution of first brand retrieved, rival count, focal share, reciprocal retrieval, confidence, and choice. A separate estimand is the human–LLM gap in the treatment-effect vector.
- **Treatment/event:** The same randomized matched stimuli as Design 1, including cue removal and brand/celebrity masking.
- **Outcome:** Structured first answer before explanation; ordered retrieval list; probability or repeated-draw share; reciprocal prompts; category and competitor retrieval; answer change when the cue is ablated. Explanations are collected after closed-ended/short-answer outcomes.
- **Time frequency:** Repeated independent calls across model families, snapshots, prompt templates, and dates; repetitions are nested draws from a model system, not independent people.
- **Controls/estimator:** Exact prompt and decoding manifests; randomized option/order labels; multiple model families; item fixed effects; crossed model × prompt analysis; comparison with a held-out human sample.
- **Threats:** Training-data familiarity with famous campaigns, instruction-following rather than human retrieval, prompt sensitivity, correlated repeated draws, model updates, image-versus-text modality mismatch, and self-fulfilling model coding.
- **Placebos/falsification:** Novel fictitious brands/celebrities; deep paraphrases; option-order permutations; cue ablations; unrelated pairings; brand-masked images; novel-domain transfer; predeclared equivalence margins against human treatment effects.
- **Measures:** **Effectiveness + interference + directed association for the model system.** Use as a cheap instrument-development and stimulus-screening fallback, not as evidence about consumers.

## Public/scrapable data stack

1. **Google Trends:** Query-level attention and related queries. Use common-anchor request groups, repeat pulls, save raw CSV/JSON, and never compare separately normalized series without overlap. Google Trends is sampled and aggregated rather than a search census.[2] The alpha API would improve cross-request scaling if access is granted.[1]
2. **Wikimedia:** Daily API series for easy collection plus Pageview Complete dumps for hourly per-article data. The complete dumps provide per-article time series with hourly counts embedded in each row and long historical coverage.[3] Wikipedia is an attention outcome, not a brand-search or purchase outcome.
3. **YouTube:** Public upload metadata, search results, video statistics snapshots, and timestamped comments. Comment collection must paginate and record collection time because counts, moderation, and availability change.[4][5]
4. **Official campaign/brand/celebrity pages:** Exact launch and asset timestamps, campaign copy, declared relationships, and product availability. Preserve separate timestamps for announcement, first creative, first celebrity post, and first amplification.
5. **Public web/news/social pages:** Appearance and amplification ledger. Store URL, timestamp, visible text, author/channel, and evidence type. Archive only where terms and law permit; retain hashes and metadata even when media cannot be redistributed.

## First presentation-quality pilot

### Scope

Use a bounded **sportswear/activewear market** because the rival set is legible and the theory offers variation between category-congruent athletes and profession-orthogonal musicians/actors. Assemble 6–10 U.S.-relevant launches or viral appearances from 2024–2026 with verified timestamps, at least 56 pre-event days, and nonzero pre-event query volume. Freeze focal brand, top 3–5 rivals, celebrity aliases, category terms, and event exclusions before downloading outcomes.

Use **Tate McRae × adidas Originals Sport** as the flagship visualization. adidas records the collection reveal on July 22, 2026 and release on July 23, 2026, with Tate McRae, Emilia Mernes, and Harper Murray fronting the campaign.[7] This case is useful because adidas has a large independent baseline, making it possible—though not guaranteed—to observe a larger celebrity→brand movement than brand→celebrity movement.

### Primary estimands

1. **Directional association:** Post-event change in anchored `Tate McRae + adidas` interest relative to all Tate McRae interest, versus the same joint query relative to all adidas interest.
2. **Competitor leakage:** Post-event change in adidas share of `adidas + Nike + Puma + New Balance` retrieval conditional on Tate McRae/category queries.
3. **Persistence:** Decay of the two effects over 1, 7, 28, and 56 days.
4. **Text validation:** Share of event-linked YouTube comments that spontaneously retrieve adidas, a rival, or only the category.

### Estimation and figures

- Estimate event-specific indexed changes first; then pool with a stacked event study using event and calendar-date fixed effects.
- Main window: daily `[-56,+56]`; immediate window: hourly `[-72,+72]` where data permit.
- Do not report a single “campaign effect” from the flagship case. Label it a **descriptive event-time association**.
- Figure 1: celebrity→brand and brand→celebrity indices on the same event-time axis.
- Figure 2: focal versus rival retrieval shares, with category volume shown separately.
- Figure 3: hourly attention/retrieval around reveal, release, celebrity post, and first major amplification.
- Figure 4: comment retrieval composition with 95% intervals and human-validation agreement.
- Figure 5: placebo-date/permuted-pair distribution with the observed event marked.

### Go/no-go rules

Proceed to a larger observational paper only if: (i) at least 6 events have usable pre-period query volume; (ii) anchored repeated pulls are stable enough to distinguish event movement from sampling noise; (iii) at least one event has a credible unscheduled or geographically staggered exposure; and (iv) competitor outcomes are not mostly censored at zero. If these gates fail, move directly to the matched human experiment and use the public corpus only to select realistic stimuli and document prior associations.

## Interpretation boundaries

- An event-study spike can show that public retrieval moved after an event; it does not show that an individual saw the creative or that the campaign caused sales.
- Co-mentions and embeddings are measurements of association, not identifying variation.
- Rival-search increases can mean harmful interference, category expansion, controversy, or comparison shopping; distinguish them with focal share, category volume, text, and timing.
- Media amplification is often part of the treatment mechanism. Control for it only in a secondary mediation/decomposition analysis, not in the primary total event-time effect.
- The pilot's strongest credible claim is: **distinctive celebrity events are followed by asymmetric changes in public retrieval, with measurable variation in competitor leakage.** Stronger causal language requires the randomized human design or a genuinely exogenous field event.

## Sources

[1] Google Trends API Alpha — https://developers.google.com/search/apis/trends

[2] FAQ about Google Trends data — https://support.google.com/trends/answer/4365533?hl=en

[3] Wikimedia Pageview Complete dumps — https://dumps.wikimedia.org/other/pageview_complete/readme.html

[4] YouTube Data API commentThreads.list — https://developers.google.com/youtube/v3/docs/commentThreads/list

[5] YouTube Data API search.list — https://developers.google.com/youtube/v3/docs/search/list

[6] YouTube Data API quota calculator — https://developers.google.com/youtube/v3/determine_quota_cost

[7] adidas unveils Originals Sport — https://news.adidas.com/training/adidas-unveils-originals-sport--bringing-signature-originals-style-to-performance-training/s/e69aab2f-b1c8-419b-97e5-4a5a1ba6ef02
