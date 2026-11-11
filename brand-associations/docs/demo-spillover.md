# Demo spillover analysis: focal versus sibling versus competitor

Every number below is `observed` output from `make demo` (stage `spillover`, run on November 9, 2026). Nothing here is a causal estimate: there are four to five events, no matched control events and no unit sales.

## How the spillover measures are built

The comparison sets for siblings and competitors are written in `config/demo_cases.json` (`trends`, `roles`, `mentions`). Each product gets one of these roles:

- `focal`: the product the celebrity wore.
- `sibling`: another product from the same brand.
- `competitor`: a product from a rival brand.
- `category`: a generic category search term.
- `*_link`: a celebrity-plus-brand search term.

These sets were chosen after the first look at the data. They are therefore illustrative, not pre-registered. A real study must freeze them before outcomes are pulled.

The analysis measures four channels.

1. **Search attention (Google Trends).**
   - Each term gets a day-of-week baseline from days −28 to −1.
   - The headline number is the mean excess over that baseline on days 0–3, divided by the standard deviation of the pre-period residuals (`z_0_3`).
   - The same quantity is also reported for days 0–7 and days 8–21.
   - Terms are comparable only within one query payload, so each payload holds the focal product with its siblings or competitors.
2. **Encyclopedic attention:** Wikipedia pageviews for the brand pages, measured the same way.
3. **Inventory:** archived brand product pages. For the focal colorway and for other colorways of the same model, the question is whether the page went out of stock or lost sizes.
4. **Coverage co-mentions.** The set is on-topic, post-event articles, keeping one copy per headline. Each article is checked for other products named within 400 characters of the celebrity or focal-product mention.
   - Newsletter, tag and category boilerplate is removed first.
   - The output is `spillover_mentions.csv`.
   - Qwen's open-ended list of other products is stored separately as `model_predicted` (`spillover_llm_products.csv`).

Outputs:

- `data/derived/demo/spillover_attention.csv`
- `data/derived/demo/spillover_inventory.csv`
- `data/derived/demo/spillover_mentions.csv`
- `output/demo/spillover_overview.png`
- `output/demo/<case>_spillover.png`

## What the four cases show

### Taylor Swift × New Balance 550: attention concentrated on the celebrity–brand link

| Measure (days 0–3) | z |
|---|---|
| "Taylor Swift New Balance" | 11.6 |
| "Taylor Swift Nike" (rival link) | 2.7 |
| "New Balance 550" (focal model) | 1.1 |
| New Balance 327 / 9060 / 530 / 990 (siblings) | 2.2 / 0.7 / −0.8 / −1.0 |
| Samba / Dunk Low / Air Force 1 / Chuck Taylor (competitors) | 0.7 / 0.0 / −0.6 / −0.9 |
| Wikipedia: New Balance | −1.1 |

- Generic searches for "New Balance 550" rose only on the Monday and Tuesday after the game (86 and 83, against roughly 60 the week before). They then returned to baseline.
- Only the 327 among the siblings cleared 2 SD. There was no competitor movement.
- **Inventory.** The focal `BB550SE1` page shows 19 of 20 sizes on day +2 and 18 of 20 on days +3 to +7. The press had reported a sellout and restock, and we have no page capture before the game. Other 550 colorways, men's and women's, show full or near-full size runs on days 0–10. The two depleted pages are hard to read:
  - `BB550LSB` had 11 of 22 sizes on day −2 and 3 of 22 on day +10, but it was already half depleted before the game.
  - `GSB550TA` (grade school) had 1 of 8 sizes on day +4, with no capture before the event.
- **Coverage.** Of 14 on-topic articles, 2 also name the NB 1906 and 1 each names Nike or Keds.

### Kanye × Adidas Energy Boost ESM: the stockout was confined to the worn colorway

| Measure | days 0–3 | days 0–7 | days 8–21 |
|---|---|---|---|
| "Energy Boost" (focal) | 2.6 | 3.8 | −0.2 |
| "Ultra Boost" (Boost sibling) | 0.6 | 3.1 | 7.7 |
| "Pure Boost" (Boost sibling) | −1.5 | 0.6 | 0.1 |
| Superstar / Stan Smith (heritage siblings) | −0.3 / 0.0 | −0.5 / −0.5 | — |
| Nike Free / Flyknit / Roshe / Asics Gel | −0.5 / 0.7 / 0.4 / −1.7 | all within ±0.7 | — |

- **Inventory.** The worn colorway `B44283` was in stock on day +5 and out of stock with Add to Bag disabled on days +6, +7, +9 and +10. Four other Energy Boost colorway pages archived in the same window stayed in stock:
  - `B40904` on day +6;
  - `B44280` on days +6 and +13;
  - `B44281` on day +7;
  - `B44285` on days +15 and +17.

  This is the cleanest observed evidence that demand concentrated on the exact product rather than the model.
- **Search spillover within the brand** went to the Ultra Boost, another shoe on the same Boost cushioning platform, not to heritage lines. That signal is confounded on three counts:
  - Kanye wore the Ultra Boost himself on May 16–17 (day +7 and day +8).
  - Adidas showed a "Coming Soon" countdown on the Ultra Boost page.
  - The Ultra Boost launched on June 1.
- **Coverage.** Hypebeast asked directly whether "associated colorways of the same model" would get the same reception. That is a spillover question raised by the specialist press itself. Nike mentions near Kanye are mostly about his departure from Nike. One reader comment compared the ESM and Ultra Boost to the Nike Free and Flyknit.

### Meghan × Outland Denim: a jump from zero search, shared mostly with other items in the outfit

- **Search in Australia.** "Outland Denim" went from 0 to 100 on day 0 and took 87% of attention in its competitor payload over days 0–7.
  - Australian competitors stayed flat: Nobody Denim 0.7, Levi's −0.2, Nudie −0.4, Ksubi −0.5 (all low-volume series).
  - The category term "black jeans" scored 1.3.
- **Search in the US.** "Outland Denim" barely registered on days 0–7, with an index of at most 1 against Madewell. Everlane, another ethical-fashion brand, scored 1.9, below the 2 SD line.
- **Coverage.** There were 93 on-topic articles but only 12 distinct headlines, because News Corp regional mastheads syndicated the same stories. Of those 12, 9 also name the Serena Williams jacket and 2 name Martin Grant. The other products sharing coverage were the rest of her outfit, not competing jeans.
- **Inventory.** Only the focal product page is archived. It showed 5 of 26 sizes on day +1 and 26 of 26 by day +4, with preorder enabled.

### Bieber × Crocs (preannounced collaboration benchmark)

- "Justin Bieber Crocs" reached z = 11.2. The generic "Crocs" search did not move (0.1), but the Crocs Wikipedia page did (2.0).
- Searches for earlier celebrity Crocs collaborations fell: Bad Bunny −0.5, Post Malone −0.4.
- Competitors moved little: Ugg 1.6 (seasonal) and Vans 1.0.

## Working pattern

In all four cases, the search spike was in the celebrity-plus-brand term rather than in generic searches for the model or brand. No competitor product search cleared 2 SD, and competitors were rarely named in on-topic coverage. The one rival term that moved was the celebrity search "Taylor Swift Nike" (2.7), which looks like people checking what else she wears rather than demand for Nike products. Same-brand spillover, where it appears, went to the closest sibling: the Ultra Boost for Kanye and the NB 327 for Taylor. The one inventory comparison we have (Kanye) shows the stockout limited to the exact colorway he wore.

This fits the low-interference reading: rapid exact identification concentrates the response on the focal product. With five events, it is a hypothesis to test on the 30-appearance sample, not a finding.

## Article-coding validation

The gold labels were hand-coded by the assistant from keyword-in-context excerpts. They need a human spot-check before any claim rests on them.

- **Tuning set:** 33 articles. It was coded while diagnosing errors, and the proximity rule was revised on it, so scores on it are in-sample.
- **Held-out set:** 32 articles, drawn after the rule change.

Scores on the held-out set (the question is whether the article is about the focal appearance):

| Coder | Precision | Recall | Accuracy | ID level agrees on true positives |
|---|---|---|---|---|
| Rule v1: whole-page co-occurrence | 0.75 | 1.00 | 0.81 | 14/18 |
| Rule v2: celebrity within 500 characters of product | 0.89 | 0.94 | 0.91 | 13/17 |
| Qwen3-8B, prompt v2 (excerpts) | 1.00 | 0.72 | 0.84 | 7/13 |

Why the rules and prompts changed:

- **Rule v1 failures.** Kanye and Adidas co-occur on almost every sneaker-site page. Related-story sidebars produced false hits. The regex `outland` matched *Outlander*.
- **Qwen prompt v1** sent the first 3,500 characters of page text, which are mostly navigation menus. It agreed with the rules on only 17 of 94 articles.
- **Qwen prompt v2** sends only excerpts around the mentions. It has no false positives but misses about a quarter of true articles, and it is unreliable on identification level.

Rule v2 is the primary coder. Qwen v2 is a high-precision filter and an open-ended product extractor. All local Qwen labeling ran in about 8 minutes for 243 articles.
