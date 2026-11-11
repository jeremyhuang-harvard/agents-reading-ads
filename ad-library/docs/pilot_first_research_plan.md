# Pilot-first research plan

**Captured:** October 8, 2026  
**Status:** Current execution strategy

## Decision

Start smaller than the full causal research agenda and first prove that the advertisement-collection and GABRIEL measurement pipeline works end to end.

The pilot should use whichever EU or platform advertising repository is easiest to access reliably and lawfully. The immediate objective is to produce a real corpus, inspect the available metadata, measure interpretable attributes, and generate descriptive results quickly. It is not yet to establish the project's final causal thesis.

## Phase 1: Descriptive EU advertising pilot

### Target corpus

Collect approximately **2,000–2,500 advertisements** from one accessible source.

If the source exposes product or advertiser categories, deliberately oversample:

- gambling, sportsbooks, casinos, lotteries, and prediction markets;
- alcohol and tobacco or nicotine products where available;
- other regulated or potentially harmful products;
- a broad comparison sample of ordinary consumer advertising.

If category metadata are missing or unreliable, collect a general sample first, classify it using text and creative content, and construct the vice-advertising subset afterward.

### Media preparation

- **Image advertisements:** submit the original image directly to GABRIEL where supported. Preserve the exact source file and its hash.
- **Video advertisements:** retain the original video, sample frames at fixed intervals and scene changes, construct contact sheets, and append any supplied copy, OCR, captions, or transcript. Keep time-aligned derivatives so later measurements can point back to specific evidence.
- **Text or landing-page advertisements:** retain the original text and an immutable screenshot or PDF where collection terms permit.
- Treat each advertisement as a versioned creative bundle rather than a single text string.

### Metadata audit

Before finalizing the sample, document exactly what the source supplies:

- native advertisement and advertiser identifiers;
- creative format and downloadable media;
- first and last delivery dates;
- countries and languages;
- payer and beneficiary;
- targeting criteria;
- reach, impressions, or bounded estimates;
- spend or bounded estimates;
- product category or advertiser industry;
- landing page and call to action;
- status, removals, and later revisions;
- retention window and historical coverage.

Missing metadata should be treated as a finding rather than silently inferred.

### Initial GABRIEL codebook

Develop approximately **30 attributes** across these families:

1. Ad and product identification
2. Financial inducements and offer strength
3. Winning, payout, or reward salience
4. Urgency, scarcity, and event immediacy
5. Betting or purchase actionability
6. Perceived ease and low-friction framing
7. Visual and sensory salience
8. Emotional arousal and positive affect
9. Social proof and normalization
10. Sport, cultural, or identity linkage
11. Celebrity and influencer endorsement
12. Status, expertise, and insider framing
13. Youthfulness or youth-oriented aesthetics
14. Gender and family framing
15. Traditionalism, modernity, and value cues
16. Risk-minimization claims
17. Responsible-use or responsible-gambling prominence
18. Terms-and-conditions prominence
19. Age-restriction prominence
20. Overall benefit-risk imbalance

Begin with the existing `config/ad_codebook.json`, expand it only after inspecting a representative development sample, and preserve component measures rather than immediately reducing everything to a single index.

### Cost-aware model strategy

- Use a lower-cost capable multimodal model for screening and first-pass measurements.
- Use repeated runs on a smaller validation sample to measure stochastic reliability.
- Route uncertain, conflicting, high-stakes, or evidence-poor cases to a stronger model or human coder.
- Freeze prompts, codebook version, model identifiers, preprocessing, and output schema before the full pilot run.
- Keep raw model responses, evidence spans, prompt hashes, and per-run values.

### First outputs

Produce:

- summary distributions for each measured attribute;
- missingness, disagreement, and reliability diagnostics;
- comparisons across product categories;
- gambling and other vice-advertising cuts;
- brand-within-category comparisons;
- country and language comparisons;
- one or two maps of Europe where the source supports credible geographic fields;
- representative high-, middle-, and low-scoring creatives for human inspection.

The purpose of these outputs is to identify which constructs vary meaningfully, which measurements are reliable, and which empirical questions merit deeper work.

## Phase 2: Controlled ad-variant experiment

After the descriptive pipeline works, build an experiment that changes one feature while holding the rest of an advertisement as constant as possible.

Candidate manipulations include:

- depicted age;
- depicted or targeted gender;
- color palette;
- youthfulness;
- family-values framing;
- traditional versus modern framing;
- urgency or scarcity;
- celebrity presence;
- reward salience;
- responsible-gambling or risk-warning prominence.

Use real advertisements where licensing and research approval permit, or construct synthetic variants. Manipulations should be validated to ensure that the intended feature changed without unintentionally changing brand quality, legibility, visual polish, or other confounds.

Survey participants about outcomes such as:

- attention and recall;
- emotional response;
- perceived relevance;
- product and brand attitudes;
- perceived risk and expected reward;
- trust;
- purchase, click, signup, or wagering intention;
- perceived target audience;
- recognition of disclosures and material terms.

The specific manipulations should be selected using evidence from Phase 1 rather than chosen entirely in advance.

## Near-term acceptance criteria

The first phase is successful when:

1. One source yields at least 2,000 usable ad records with a documented sampling process.
2. Creative media or faithful visual derivatives are available for a substantial share of the sample.
3. The source's metadata and historical limitations are documented.
4. A frozen GABRIEL specification produces analysis-ready outputs for the corpus.
5. A blinded human-coded sample provides reliability and error estimates.
6. The project produces reproducible descriptive plots and category/brand/geographic comparisons.
7. The results identify two or more concrete attributes suitable for controlled manipulation in Phase 2.
