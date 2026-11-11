# Batch 1 findings

> Sections 1–4 are the first read on half the data. **Section 5 is the clean result on the full batch and supersedes them.**

Run: `runs/batch1-image-priming-61d1c48aaf-20261021T024258Z/` (568 feeds x 9 questions,
Qwen3-VL-8B-Instruct-4bit, commit `61d1c48`, clean tree, 166 min).
Auto-generated tables: `artifacts/batch1-image-priming-61d1c48aaf-20261021T024258Z/`.

## 1. Measurement problem: the model ignores the scale labels

Half the feeds showed rating scales reversed ("5 = very unlikely, 1 = very likely")
to check for a preference for particular digits. Qwen largely ignored the labels and kept
answering as if 1 were low:

| Question | Mean after recoding, normal scale | Mean after recoding, reversed scale |
|---|---|---|
| Better off | 1.76 | 4.03 |
| Risk | 3.19 | 4.39 |
| Pushiness | 2.94 | 3.34 |
| Normal | 3.00 | 3.67 |
| Appeal | 2.94 | 3.35 |

Reversed-scale answers are therefore mostly noise, and because reversal was not balanced
within cells, the auto-generated `summary.md` effect tables mix the two and **should not
be interpreted**. The ad-alone baselines are also affected (5 of 8 were reversed).

The analysis below uses **only normal-scale feeds** (roughly half the data, 13–32 feeds
per cell). Intervals are 90% bootstrap intervals over feeds within ad; they ignore
shared images across draws, so treat them as rough.

## 2. Effects of preceding images vs 5 neutral images (normal scale, k = 1, 3, 5 pooled)

| Ad type | Prime set | Better off | Risk | Pushiness | Normal | Appeal |
|---|---|---|---|---|---|---|
| Beer | social drinking | +0.31 | **−0.45** | −0.14 | **+0.55** | +0.26 |
| Beer | drink-driving harm | +0.21 | −0.15 | **+0.74** | **−0.46** | +0.19 |
| Beer | colour-matched (amber) | +0.28 | −0.01 | −0.19 | +0.20 | +0.15 |
| Betting | winning | −0.16 | −0.05 | +0.06 | −0.27 | +0.21 |
| Betting | losing / distress | −0.07 | +0.03 | **+0.24** | +0.18 | +0.35 |
| Betting | colour-matched (green/yellow) | −0.13 | −0.03 | −0.00 | +0.14 | +0.08 |
| Control | winning | −0.00 | +0.02 | −0.08 | −0.24 | +0.21 |
| Control | losing / distress | +0.43 | +0.02 | −0.06 | −0.20 | +0.22 |
| Control | social drinking | +0.08 | +0.05 | −0.04 | −0.41 | +0.21 |

Bold = the content-specific effects that move in the direction human priming would predict.

Reading:

- **Beer responds to meaning, in the predicted directions.** After pub and beer-garden
  images, the beer ad looks more normal and less risky. After drink-driving images it looks
  pushier and less normal. Amber look-alikes move little. That is the semantic-over-surface
  pattern the design was built to detect.
- **Betting barely moves.** Risk is pinned at about 4.9–5 in every condition (ceiling).
  Only "losing" images nudge pushiness up. The model's prior on gambling is strong enough
  that a few images don't shift it.
- **Appeal rises by about +0.2 after any non-neutral images, including for Fanta and Nike.**
  That is a generic "busier, more emotional feed" effect, not priming of the product.
- **Behaviour questions are dead.** P(spend €10) exceeded 0.1 in only 6.5% of feeds;
  P(agent shows the ad) in 0.5%. Qwen almost never recommends spending or showing any ad,
  even Fanta.

## 3. Trails

The trails track the primes explicitly. Same Heineken ad:

- After neutral images: "a crafted moment designed to feel like a welcome break in the feed."
- After pub images: "a digital intermission… oddly satisfying as a break from the
  real-world chaos."
- After drink-driving images: "jarringly out of place and deeply concerning… a cynical,
  irresponsible punchline."

For betting ads, nearly every trail calls the ad "jarring" or an "interruption" whatever
came before. Notably, trails after "losing" images mention them only 10–20% of the time
(keyword check), while trails after other sets mention them 60–100%: a candidate case of
influence without mention, worth hand-checking.

## 4. Fixes before batch 2

1. Drop label-reversed scales. Counterbalance with **reversed option order on choice
   questions** and **two wordings per scale** (e.g. "how risky" / "how safe") instead.
2. Rerun the ad-alone baselines on the normal scale.
3. Replace the dead behaviour questions with graded choices (e.g. a 5-option willingness
   question, or a price list), and test them in a short pilot first.
4. Betting needs outcomes that aren't at ceiling: e.g. "how much would a typical person be
   tempted?", or comparisons between two betting ads.


## 5. Clean batch 1 (normal scale only, all 568 feeds)

Merged: batch-1 normal-scale feeds + `runs/batch1-rerun-normal-scale-311cfa8d08-20261021T182547Z/`
(276 feeds rerun with identical images and feed ids). Every rating below is on 1 = low, 5 = high.
Effects are vs the same ad after 5 neutral images; 90% bootstrap intervals over feeds within ad
(rough: they ignore images shared across draws). Sections 1–2 above are superseded by this.

### 5a. Effects of the preceding images (ad last, k = 1, 3, 5 pooled)

| Ad | Images before | Better off | Risk | Pushiness | Normal | Appeal |
|---|---|---|---|---|---|---|
| Beer | pubs, beer gardens | +0.45* | **−0.29*** | +0.06 | **+0.54*** | +0.10 |
| Beer | drink-driving, crashes | +0.49* | **+0.39*** | **+1.45*** | **−0.76*** | −0.04 |
| Beer | amber look-alikes | +0.41* | +0.22* | +0.01 | +0.16* | +0.03 |
| Betting | winning | +0.05* | −0.04* | +0.14* | −0.38* | +0.10* |
| Betting | losing, distress | +0.13* | +0.02* | **+0.32*** | +0.06 | +0.22* |
| Betting | green/yellow look-alikes | +0.06* | −0.03* | +0.07 | +0.08 | −0.06* |
| Fanta/Nike | winning | +0.13* | 0.00 | −0.01* | −0.17* | +0.10* |
| Fanta/Nike | losing | +0.39* | −0.01 | 0.00 | −0.18* | +0.07 |
| Fanta/Nike | pubs | +0.15* | +0.03* | +0.02* | −0.35* | +0.06 |

\* 90% interval excludes zero. Bold = content-specific shifts in the predicted direction.

### 5b. Dose and position (beer, difference vs neutral feed)

| Images before | Position | Risk | Pushiness | Normal | Appeal |
|---|---|---|---|---|---|
| Drink-driving | 1 before ad | −0.16 | +0.30 | −0.31 | +0.06 |
| | 3 before | +0.30 | +1.35 | −0.87 | +0.05 |
| | 5 before | +1.04 | +2.69 | −1.11 | −0.22 |
| | ad first, 5 after | +0.66 | +2.70 | −1.21 | −0.82 |
| Pubs | 1 before | −0.14 | +0.05 | +0.30 | +0.03 |
| | 3 before | −0.28 | −0.02 | +0.57 | +0.11 |
| | 5 before | −0.45 | +0.14 | +0.75 | +0.17 |
| | ad first, 5 after | +0.39 | +0.81 | +0.51 | −0.31 |

### 5c. Reading

1. **Content-specific, graded effects for beer.** Drink-driving images raise pushiness by up to
   +2.7 and lower normality by about −1.1, growing steadily with the number of images (1 → 3 → 5).
   Pub images lower risk and raise normality, also in a dose–response pattern. Amber look-alikes
   move little. This is the cleanest result so far.
2. **Images *after* the ad matter as much as images before it.** With the ad first, drink-driving
   images still raise pushiness by +2.7. There is no primacy or encoding asymmetry: the model
   judges the whole feed at once, as a set, not as a sequence. Humans reading a feed would not
   behave this way, so this is a candidate human–LLM difference in its own right. Pub images
   after the ad *reverse* direction (risk +0.39, pushiness +0.81), which suggests contrast rather
   than assimilation when the context comes second.
3. **Betting moves little.** Risk stays at about 4.9–5 whatever comes before. "Losing" images raise
   pushiness by +0.3 to +0.6, and that rises with dose.
4. **Two outcomes are contaminated by wording, not priming.**
   - "Normal for *people like those in this feed*" points the model at the primes, so it changes
     who the reference group is. That explains why Fanta/Nike "normality" drops after pub or
     celebration images. Reword to "for a typical adult".
   - "Better off" rises after *any* themed images, including drink-driving and losing, and
     for Fanta/Nike too. It looks like a generic response to a non-neutral feed, not a belief.
5. **Correction to the earlier read.** With clean scales, the ad-alone vs neutral-feed gap is
   smaller and less uniform than reported in §2: mainly lower appeal for betting ads
   (≈ 3.6–3.8 alone → 2.2–2.7 in a feed) and lower pushiness for Heineken glass (4.3 → 1.1).
