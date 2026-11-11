# Directed celebrity–brand associations

Status: codebase plus a pilot frame of 22 celebrities, 30 brands and 23 ambassador pairs. Code: `src/implicit_ads/assoc/`. Frame: `config/assoc/ambassadors.json`. Tests: `tests/test_assoc.py`.

## The question

The hypothesis to test is that a cue retrieves a target with different strength depending on direction. For example:

- Thinking of **Tate McRae** should call up **Adidas** fairly strongly.
- Thinking of **Adidas** should call up Tate McRae only weakly.

That asymmetry is the memory side of *Ads as Cues*, where a cue retrieves goods and the goods it retrieves compete. It also matters for interference: an ambassador helps the brand when the celebrity → brand link is strong, whether or not brand → celebrity is.

## Why vectors alone cannot answer it, and what to do instead

Sarkar ("Economic Representations", 2026) represents each firm as the average embedding of its news coverage. The similarity between two such vectors (cosine) is **symmetric**: sim(Tate, Adidas) = sim(Adidas, Tate). Direction has to come from somewhere else.

The repo gets it from **competitive retrieval over a frozen candidate set**. This is the same structure as *Ads as Cues*, where a cue retrieves goods in proportion to similarity, normalized by everything else the cue calls up:

```
P(b | c) = S(c,b) / Σ_b' S(c,b')        (celebrity cue, competing brands)
P(c | b) = S(c,b) / Σ_c' S(c',b)        (brand cue, competing celebrities)
```

With symmetric S, the asymmetry is exactly

```
log P(b|c) − log P(c|b) = log Σ_c' S(c',b) − log Σ_b' S(c,b')
                        = crowding at the brand cue − crowding at the celebrity cue.
```

So the Tate → Adidas > Adidas → Tate prediction is a statement about **interference**. Adidas has many associated celebrities competing when Adidas is the cue (the psychology literature calls this the *fan effect*). Tate has few associated brands competing when Tate is the cue. Brand size matters only through this crowding. That makes the asymmetry a natural measure of when interference is larger or smaller. `measures.crowding` returns the two log-Z terms, so each asymmetry can be split into the two cues' crowding.

**A trap to avoid.** With raw co-occurrence counts and the cue's total volume as the denominator, P(b|c) = N(c,b)/N(c). The asymmetry then reduces to log N(b) − log N(c), a size ratio by construction (`test_conditional_counts_asymmetry_is_pure_size`). The repo reports this measure (`gdelt_conditional`) only as a benchmark. The informative measures normalize over the candidate set.

## Associative strength as composition (not similarity)

Similarity asks whether two vectors point in the same direction: McDonald's ≈ Burger King. **Associative strength** asks whether one entity is a *component* of the other's representation. Is Adidas part of what "Tate McRae" is made of, and is Tate part of what "Adidas" is made of? Psychology calls these forward and backward associative strength (FSA/BSA; Nelson, McEvoy & Schreiber 2004). They can differ, and neither requires the two entities to be alike. The repo measures composition four ways. Each writes `directed_<measure>.csv` with `fwd` = strength of b in c and `bwd` = strength of c in b.

| measure | what "Adidas is a component of Tate" means | label |
|---|---|---|
| `components_<encoder>` | **Exact decomposition of Tate's coverage vector.** Tate's vector is the mean of her documents' embeddings. The Adidas component is the share of that vector's length contributed by Tate documents that mention Adidas: π(Adidas \| Tate) × alignment. π is the share of Tate's coverage that mentions Adidas (GDELT population count when available, otherwise the document sample). Alignment is how central those documents are to Tate's representation (>1 = core coverage, <1 = passing mentions). Shares over a partition sum to 1. | derived |
| `nnls_<encoder>` | Tate's vector written as a non-negative combination of a generic celebrity centroid plus brand vectors. The weight on Adidas is its loading. The centroid absorbs shared "celebrity-ness", so similar-but-unrelated brands get no loading. Secondary measure, because collinear rival brands make the weights unstable. | derived |
| `wiki_mentions` | Share of Tate's Wikipedia article sentences that mention Adidas, versus the share of Adidas's article sentences that mention Tate. | observed |
| `freeassoc_<model>` | **Open-vocabulary free association,** the standard way associative strength is measured in humans. Thirty independent LM samples each list ten things that come to mind for the cue. FSA = share of samples naming the target. There is no candidate list, so the output also shows what else each cue is made of (`freeassoc_<model>_top.csv`). | model_predicted |
| `clickstream_conditional` | Share of all clicks out of Tate's Wikipedia article that go to Adidas's article, versus the reverse. Observed navigation. | observed |

Composition and the competitive shares above answer different questions:

- **Composition** asks how much of Tate is Adidas.
- **Competitive retrieval** asks, given Tate as the cue, how likely Adidas is to win against the other brands.

The second is the composition of Tate divided by everything else in Tate that competes with Adidas. Reporting both separates *association strength* from *interference*.

**Human ground truth.** The Small World of Words norms (SWOW-EN18; De Deyne et al. 2019) give human FSA for about 12,000 English cues, brands among them. They are free for non-commercial research but require registration (name and email; CC BY-NC-ND). They would anchor the LM free-association measure on brand cues. Registration needs the PI's approval.

## Measures (each writes `data/derived/assoc/directed_<measure>.csv`)

| measure | source | what P(b given c) means | label |
|---|---|---|---|
| `gdelt_conditional` | GDELT English news counts | share of c's articles that mention b (size benchmark) | observed |
| `gdelt_share` | same, full celebrity × brand matrix | b's share of c's co-coverage with all candidate brands | observed |
| `trends_related` | Google Trends related queries (US) | share of c's top related-search weight whose query names b | observed |
| `clickstream_conditional` | Wikimedia clickstream (monthly dump) | share of clicks out of c's article that go to b's article | observed |
| `embed_<encoder>` | Sarkar-style coverage vectors | softmax of cosine over candidates, τ = 1/20 | derived |
| `llm_<model>` | local Qwen3-8B, next-token log-probabilities | P that the model names b after a prompt about c, normalized over candidates; PMI version subtracts brand popularity | model_predicted |

**Representations.** Each entity's documents are its GDELT headlines (four quarterly windows, up to 75 each, syndicated duplicates dropped) plus its Wikipedia paragraphs. Each document is embedded, embeddings are averaged within each period, then the periods are averaged. This follows Sarkar's firm–year construction.

The default encoder is Sarkar's released `suproteem/RepresentLM-v2`. Its base model was trained on newspapers through 1979, which suits Sarkar's no-lookahead design but may handle modern vocabulary poorly. Pass a second `--backend st:BAAI/bge-base-en-v1.5` to check robustness. `--mask-names` replaces entity names with `[NAME]`, so similarity reflects context rather than literal co-mentions.

**LLM measure.** The model has a training cutoff (Qwen3: early 2025). For deals announced after that, the model measures associations *before* the deal. That works as a pre-period baseline, not a measure of the deal.

## Size covariates

Wikipedia pageviews understate brands (Tate McRae's article had 2.0M views over the window and Adidas's 0.83M), because people go to brand websites rather than brand Wikipedia pages. GDELT article counts are the primary size measure. Pageviews are reported alongside.

## Running

```
make assoc                                   # wiki, gdelt, docs, embed, analyze (cached; ~90 min first run)
make assoc ASSOC_ARGS="--stages trends,analyze"
make assoc ASSOC_ARGS="--stages clickstream,analyze --months 2026-09,2026-10"
make assoc ASSOC_ARGS="--stages embed,analyze --backend st:suproteem/RepresentLM-v2 --backend st:BAAI/bge-base-en-v1.5"
make assoc-llm                               # local Qwen; Apple silicon
```

Outputs:

- `data/derived/assoc/cells.csv`: every celebrity × brand × measure.
- `pair_panel.csv`: configured pairs, wide by measure, with size ratios.
- `output/assoc/summary.md`.
- `output/assoc/asymmetry_<measure>.png`: forward vs backward retrieval, and asymmetry vs size ratio.

## Predictions to test

1. **Direction:** for small-celebrity / big-brand pairs, asymmetry > 0 (Tate → Adidas > Adidas → Tate). For big-celebrity / smaller-brand pairs (Jung Kook – Calvin Klein, Caitlin Clark – Dick's), it should flip.
2. **Interference, not size:** conditional on size, asymmetry should rise with the brand cue's crowding (number and strength of other celebrities the brand calls up) and fall with the celebrity's (number of other brands). This is the fan effect.
3. **Shared ambassadors dilute:** brands with several ambassadors in the frame (Adidas: Tate, Emilia Mernes, Harper Murray, Bad Bunny, Jenna Ortega) should show weaker brand → ambassador retrieval for each one.
4. **Link to outcomes:** pairs where the celebrity → brand link is strong should show stronger focal-brand search and stockout responses to appearances (`docs/demo-spillover.md`). This connects the representation layer to the event studies.

## Limitations

- The pilot pairs were hand-picked to span size ratios, not sampled. A frozen frame would come from a consecutive announcement list. Bookingagentinfo's brand-ambassador category is a candidate, but its terms need checking first.
- Candidate-set composition drives every normalized measure. Changing the brand list changes P(b|c), so the frame is versioned and frozen before outcomes are inspected.
- GDELT search is keyword-based, so names like "Puma", "Chanel" and "On" are ambiguous. The queries use phrases and alternative names where possible.
- None of these measures is an individual consumer's memory. They are corpus, search, navigation or model proxies for collective association, and the next validation step is an elicited free-association survey.
