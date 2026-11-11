# Batch 2 findings

Run: `runs/batch2-beer-priming-9a960c96e6-20261021T194553Z/`. 888 feeds × 10 questions,
Qwen3-VL-8B-Instruct-4bit, normal-direction scales only.

**Integrity.** The run crashed 6 times with Metal out-of-memory errors while the
`agentic-norms-learning` MLX job shared the GPU, and was resumed each time from the same
directory with unchanged research code (`9a960c9`; later commits touched only docs and the
resume script). Result: **all 888 design feeds complete.** The 21 duplicate answer rows written
around crashes are bit-identical to their originals. Image orders match the design exactly. 1 of
7,104 scored answers put <80% probability on valid options. The manifest is clean (`git_dirty: false`).

Effects are vs the same ad after 5 neutral images. 90% bootstrap intervals over feeds within ad;
\* means the interval excludes zero (rough: shared images across draws are ignored).

## 1. Batch 1 replicates

Same ads, same prime sets, ad shown after 5 images; new random image draws (10 vs 5).

| Ad | Images before | Risk (b1 → b2) | Pushiness | Normal | Appeal |
|---|---|---|---|---|---|
| Heineken pint | drink-driving | +2.52 → +2.10 | +3.11 → +2.45 | −2.52 → −2.18 | −0.41 → −0.27 |
| Heineken pint | pubs | −0.55 → −0.74 | +0.16 → +0.09 | +0.96 → +1.00 | +0.19 → +0.37 |
| Heineken 0.0 drinker | drink-driving | −0.44 → −0.52 | +2.27 → +3.25 | +0.30 → −0.13 | −0.03 → −0.10 |
| Heineken 0.0 drinker | pubs | −0.36 → −0.40 | +0.11 → +0.16 | +0.54 → +0.70 | +0.15 → +0.32 |
| PMU (betting) | winning | 0.00 → 0.00 | +0.35 → +0.28 | −0.71 → −0.58 | −0.38 → −0.35 |
| Unibet (betting) | losing | −0.01 → −0.02 | +0.19 → +0.22 | −0.03 → +0.11 | +0.46 → +0.40 |

Signs and rough sizes hold across independent image draws. The beer effects are not a fluke of
which images were drawn.

## 2. New finding: the same harm images push regular beer and alcohol-free beer in opposite directions

Effect of 5 drink-driving images, by ad:

| Ad | Risk | Safe | Normal |
|---|---|---|---|
| Heineken pint (regular) | **+2.10** | **−1.81** | **−2.18** |
| Heineken Oranje fan kit (regular) | +0.48 | **−2.08** | **−1.04** |
| Heineken 0.0 drinker | **−0.52** | +0.36 | −0.13 |
| Heineken 0.0 "Ultimate" can | −0.19 | **+1.25** | **+0.77** |

For regular beer, harm images make the product look riskier and less normal: **assimilation**.
For the alcohol-free can, the same images make it look *safer and more normal*: **contrast**.
The alcohol-free product is read against the harm it avoids. This is the BGS-style salience
pattern: the context changes which attribute stands out (here, "contains alcohol" vs "doesn't"),
and the direction depends on where the ad sits relative to the context. It is the most
theoretically interesting result so far. With two 0.0 ads it needs replication on more products.

The trails show both readings at once. For the 0.0 can after drink-driving images: *"a stark
contrast… turning a public safety narrative into a pitch for a non-alcoholic alternative."*

## 3. Pooled effects (ad last, 1 or 5 images)

| Ad | Images before | Risk | Safe | Pushiness | Free to decide | Normal | Appeal | Try it |
|---|---|---|---|---|---|---|---|---|
| Beer | pubs | −0.23* | +0.65* | +0.05* | +0.10* | +0.52* | +0.23* | +0.15* |
| Beer | drink-driving | +0.27* | −0.46* | +1.17* | +0.04* | −0.48* | +0.01 | −0.02 |
| Beer | amber look-alikes | +0.08* | +0.57* | −0.02 | −0.03 | +0.17* | +0.08* | +0.06* |
| Betting | winning | −0.03* | +0.03 | +0.13* | −0.21* | −0.49* | −0.02 | +0.23* |
| Betting | losing | 0.00 | +0.11* | +0.19* | −0.10* | +0.07 | +0.18* | +0.34* |
| Betting | green/yellow look-alikes | 0.00 | +0.04* | +0.14* | −0.09* | +0.11* | −0.05 | +0.12* |
| Fanta/Nike | winning | −0.02* | −0.06* | −0.02* | −0.18* | −0.07 | +0.06 | −0.01 |
| Fanta/Nike | losing | −0.02 | −0.39* | 0.00 | +0.01 | −0.38* | −0.01 | +0.12* |
| Fanta/Nike | pubs | +0.02 | +0.01 | +0.02* | −0.10* | −0.40* | −0.05 | −0.16* |

Pooling over ads hides the regular-vs-0.0 split in §2: drink-driving effects on risk and safety
partly cancel across the four beer ads.

## 4. Position: images after the ad still matter

Beer, difference vs neutral feed:

| Images | Position | Risk | Safe | Pushiness | Normal | Appeal | Try it |
|---|---|---|---|---|---|---|---|
| Drink-driving | 1 before | +0.07 | −0.35* | +0.34* | −0.32* | +0.06* | +0.04 |
| | 5 before | +0.47* | −0.57* | +2.00* | −0.65* | −0.04 | −0.08 |
| | ad first, 5 after | +0.34* | **−1.63*** | **+2.63*** | **−0.99*** | −0.46* | −0.41* |
| Pubs | 1 before | −0.11* | +0.47* | +0.02 | +0.33* | +0.07* | +0.14* |
| | 5 before | −0.34* | +0.83* | +0.08* | +0.71* | +0.38* | +0.15* |
| | ad first, 5 after | −0.01 | **−0.59*** | **+0.76*** | +0.39* | −0.20* | −0.18* |

This replicates batch 1. Effects grow from 1 to 5 images before the ad. Images placed *after*
the ad still move the ratings strongly, sometimes more. And pub images after the ad flip
direction (less safe, pushier): contrast when context comes second, assimilation when it comes first.

## 5. Measurement checks

**Reverse-worded twins.** Across all feeds, risk and safety correlate −0.86, and pushiness and
"free to decide" correlate −0.78. So the model mostly answers both directions coherently, and
the effects are not simple yes-saying. But:

- **Within ad category the twins are weak**, especially for betting (−0.09 and −0.02): betting
  is rated very risky *and* very unsafe in every feed, so there is no variation left to correlate.
- **"Free to decide" barely moves** even where pushiness rises by +2–3. It is not tracking the
  same thing. Treat pushiness as "how much is this ad selling to someone at risk", not as respect
  for autonomy.
- **Look-alike images raise "safe" (+0.57) without lowering "risk" (+0.08).** For the subtlest
  primes, the two wordings disagree. Report surface-feature effects only when both twins agree.

**"Try it"** is graded and alive (unlike batch 1's spend/show questions), but small: at most
±0.4 on a 5-point scale.

**Still contaminated:** "normal for *people like those in this feed*" (unchanged from batch 1),
which explains Fanta/Nike "normal" falling after pubs or losing images. Fix in batch 3.

## 6. What this adds to batch 1

1. The beer effects replicate on fresh image draws, at similar sizes.
2. **Assimilation vs contrast depends on the product's position relative to the context**
   (regular vs alcohol-free beer). This is the first result that maps cleanly onto salience theory
   rather than "the model reads the feed."
3. Order-insensitivity replicates: context after the ad works as well as or better than before.
4. Betting stays at ceiling on risk. The new "try it" outcome moves slightly for betting
   (+0.2 to +0.3 after win or loss images), so ceiling on beliefs does not mean ceiling on everything.

Caveats: one model, 4 beer ads (two of them alcohol-free), no human comparison.
