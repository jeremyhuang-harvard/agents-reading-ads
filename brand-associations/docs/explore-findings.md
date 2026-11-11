# Overnight exploration: public-data evidence on cues and interference

Date: 2026-11-09. Status: exploratory. All results are descriptive, come from one celebrity, and were found after looking at the data. None are pre-registered. Each claim is labeled **observed** (we computed it from public data) or **reported** (a source says it).

Code: `scripts/explore/`. Raw caches: `data/raw/explore/`. Tables: `output/explore/study_*/`. Figures: `output/explore/figures/`.

## Why these studies

*Ads as Cues* (Bordalo, Burro, Coffman, Gennaioli & Shleifer, NBER w34387) treats an ad as a cue. The cue retrieves goods in proportion to similarity × experience, and the retrieved goods compete for recall (interference). The paper does not say when interference is larger or smaller. A celebrity's outfit is a natural setting for that question:

- One appearance shows several products at once.
- Some products are new to the audience and some are household names.
- Coverage picks which item to name first.

Each look is therefore a single cue with several candidate goods competing for the same retrieval.

## Study C — items in the same look compete for attention (strongest result)

Data: Page Six's list of every brand in Taylor Swift's Chiefs game-day looks, Sep 2023 to Feb 2025. That is 73 brand mentions in 20 looks (`config/explore/taylor_gameday_looks.json`). For each brand we took Google Trends (US, daily). Lift is the mean over days 0–3 relative to the same-weekday mean over days −28..−1. Days within 2 days of another game are excluded from the baseline. 61 brands had measurable search.

**Observed**
- Lift falls as the number of identified brands in the look rises.
  - 1 brand: ×28. 2–3 brands: ×3.3. 4–6 brands: ×1.5. 7–9 brands: ×1.1.
  - Pooled regression slope on log(number of brands): −0.80 (t −2.2) with tier controls. With the 12 no-data items counted as zero lift: −0.67 (t −2.1).
- Within a look (look fixed effects), the item coverage names first gets +0.96 log points more lift than the other items in that look (t 2.7). That is about 2.6×.
  - Means relative to the look's average: +0.72 for the first-named item, −0.26 for the rest.
  - The result holds when no-data items are counted as zero: +1.08 (t 3.1).
- Small, unknown makers respond most and established luxury houses barely move.
  - Indie brands: lift ×13–60 when the look is small. Luxury (Louis Vuitton, Chanel, Cartier): about ×1.
  - This matches the paper's experience term. A brand with no stored memories has the most to gain from a cue, and a top-of-mind brand gains little.

**Caveats**
- Look size is confounded with time and tier. Early looks (2023) had few items and many indie makers. Later looks (2024–25) are luxury-heavy and came after the relationship was no longer novel.
- Among indie brands only, lift still falls with look size (+3.3, +2.6, +0.9, +0.1 log points), but the cells are small.
- "First named" may reflect attention rather than cause it, because editors lead with the item already drawing buzz.
- Google Trends values are scaled within each request. Log lift does not depend on that scale, but sparse series hit a privacy floor.

## Study A — regions more exposed to the event searched the exact model more (fragile)

Data: Google Trends interest by metro area (DMA). We used two-term requests against a common anchor (Converse), so regional shares are comparable across windows. Exposure is the change in log Taylor Swift search share in Sep 24–30 relative to Aug 27–Sep 23.

**Observed**
- In weeks 2–3 after the game (Oct 1–14), metros with more exposure moved search toward the 550 relative to New Balance overall. Regression coefficient +0.11 per SD of exposure; permutation p = 0.0002; n = 63.
- Rank correlation +0.27 (p = 0.025).
- Placebo windows: none (p = 0.97).
- **The result is not robust.** It disappears when we drop the three most-exposed metros: Kansas City, Wichita and New Orleans (ρ +0.16, p = 0.23). Kansas City is the Chiefs' home market, which is the most plausibly treated place. So the pattern is suggestive but rests on a handful of markets.
- Rival Nike Dunk: exposure × prior Dunk familiarity was negative (p = 0.004 by permutation; placebo null). That is, in metros where Dunks were habitual, Dunk search fell more where exposure was high. The figure shows only a weak slope, so we do not treat this as established.

## Study B — archived StockX pages (resale burst on the exact colorway)

**Observed** (Wayback copies of StockX product pages; no requests were sent to stockx.com)
- Worn 550 White/Red: 136 sales in the prior 72 hours on day +2, and 30 on day +10.
  - A Dec 2022 capture shows 109.
  - Day +2 last sale: $95. Day +10 last sale: $77. Both are below $110 retail.
- The sibling 550 White/Green moved from 183 to 170 to 138 over the same span, a steady decline with no burst.
- **Interpretation:** the exact colorway got a short burst of resale trades at falling prices, which is consistent with a restock (**reported** by Complex: +25% NB revenue). The sibling shows no matching burst.
- Coverage is thin: one or two captures per product.

**Clearance needed:** StockX's terms restrict using its data. These are third-party archive copies, but before any figure goes in a paper or deck please confirm, or let me check with StockX or the IRB/counsel, that using them is acceptable.

## Study D — later appearances did not re-cue the New Balance link

**Observed** (Google Trends US, game days with a weekday-adjusted baseline over 21 non-game days)
- "Taylor Swift New Balance": z = 5.0 on Sep 24, then roughly 0 at every later game, including Oct 22 when she wore Nike AF1s. The shared context (Chiefs game, Taylor) did not re-retrieve the earlier product.
- On Oct 22, "Taylor Swift Nike" rose (z 2.3), but national Nike Air Force 1 search did not (z −0.5). For comparison, NB 550 was +1.6 on Sep 24.
  - In ×-lift terms this matches Study C: a staple, non-headline item in a multi-item look produces almost nothing.
- "Taylor Swift Nike" also rose on Sep 24 (z 3.6), when she wore New Balance. People may have searched the rival brand together with the celebrity, but the series is sparse.

## What this suggests about interference

1. **Within-cue competition.** When one cue shows more goods, each good gains less. A lead item takes a disproportionate share. This is a measurable version of the paper's interference term, and the setting varies it naturally.
2. **The experience term.** Lift is largest for unfamiliar brands and near zero for top-of-mind brands. This fits the inverted-U the paper implies: an unknown brand gains from a cue, while a staple is already recalled.
3. **Persistence.** One acute cue (NB 550) did not create a celebrity–product association that later appearances re-activated.

## Next steps (proposed)

- **Look size → attention:** scale Study C to more celebrities with itemized outfit lists (WhoWhatWear, Page Six, Footwear News), preregister look size × tier, and add time controls.
- **Region test:** extend Study A to many events and pool them. One event with 63 metros is too few.
- **Purchases:** pursue Wayback inventory or stockouts for indie brands with Shopify stores. They have the largest lifts and public `/products.json`.
