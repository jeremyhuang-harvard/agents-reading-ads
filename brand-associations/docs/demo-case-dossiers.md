# Demo case dossiers: end-to-end celebrity-product chains

**Status:** source-audited demo set, November 9, 2026. Reported company figures are labeled `reported`; data we retrieved ourselves are labeled `observed`.

## Selected cases

1. **Taylor Swift × New Balance 550 `BB550SE1`.** Organic-looking appearance with company, marketplace and specialist evidence. This is the anchor case.
2. **Kanye West × Adidas Energy Boost ESM `B44283`.** The appearance came from an existing ambassador relationship. It has pre-event stock evidence, a reported sellout, and unsold asking prices that show resale hype without a resale premium.
3. **Meghan Markle × Outland Denim Harriet jeans.** The brand had seeded product to her representative but there was no paid placement. It has the richest chain of brand-reported traffic, sales and operations evidence plus an archived size-level stockout.

Benchmarks kept separate: the Kanye × UltraBoost `S77416` episode, whose release was already scheduled, and Justin Bieber × Crocs, a preannounced collaboration.

## Case 1: Taylor Swift × New Balance 550 `BB550SE1`

**Relationship.** No located New Balance contract, campaign or ambassador listing before the appearance. Swift's earlier formal footwear partnership was with Keds.[1] New Balance declined to comment on the appearance.[2]

**Appearance.** Chiefs–Bears game, Arrowhead Stadium, September 24, 2023, kickoff 3:25 p.m. CDT.[3] The clearest full-body footage is Jarrett Payton's postgame video, posted about 7:47 p.m. CDT according to its X post ID.[4]

**Identification.**
- An outfit-tracker entry appeared September 24–25.
- On September 25, The Hollywood Reporter displayed an offer labeled `BB550SE1`.[5]
- Complex named the style code on October 3.[2]

**Amplification.** The Payton video was reported at 2.4M views on the night of the game and 15.8M by the next morning. Retailers bought ads, New Balance sent an email blast, and StockX later ran a Swift-themed activation.[6][7]

**Reported response, week after the appearance** (internal New Balance deck seen by Complex, plus StockX):[2]
- 550 revenue +25%
- units +22%
- traffic +30%
- internal searches for "550" +73%
- StockX trades of `BB550SE1` more than 100 on September 25, against an August average of 18 per day
- StockX week-over-week trade volume +347% and price +8%

**Observed:**
- Archived New Balance product page, Sept 26–Oct 1: list price $109.99, schema `InStock`, 18–19 of 20 sizes selectable. This is consistent with a post-sellout restock rather than a stockout.
- Google Trends for "Taylor Swift New Balance" peaked on day 2.

**Gaps.** No absolute units, baseline-week definition, restock quantity or hourly series. No archived product-page capture survives from before the event.

## Case 2: Kanye West × Adidas Energy Boost ESM `B44283`

**Relationship.** Adidas had announced its partnership with West in December 2013.[8] This is an ambassador off-campaign appearance, not an organic one.

**Appearances.** Wango Tango on May 9, 2015, then the Bulls–Cavaliers game on May 10, wearing the same pair.[9]

**Identification.**
- Complex named the Energy Boost ESM in white on May 10 and noted a full size run was still available.[9]
- WearTesters reported continued availability on May 12.[10]

**Response, reported:**
- Nice Kicks and Complex reported a sellout by May 13.[11][12]
- eBay asking prices reached $1,000–$1,150, but Complex found none had sold. The highest completed auction was $153, below the $160 retail price.[12]

**Observed:**
- 11 archived Adidas captures from January 24 to May 4, 2015 (day −105 to day −5) all show the shoe in stock.
- No post-event capture exists.
- Google Trends for "Ultra Boost" peaked around the following weekend, which reflects the UltraBoost episode rather than the ESM.

**UltraBoost benchmark.** Archived Adidas pages for `S77416` on May 17–18 show "Coming Soon" with a 15- and then 14-day countdown. A launch around June 1 was already planned, so the Billboard Music Awards appearance cannot cleanly explain the release or sellout.

**Gaps.** No units, inventory or post-event page capture. Retail depletion is reported, not observed.

## Case 3: Meghan Markle × Outland Denim Harriet jeans

**Relationship.** A modest product selection had been given to her representative, and the brand did not know she would wear the jeans. Royal rules preclude paid endorsement.[13]

**Appearance.** Arrival in Dubbo, Australia, October 17, 2018.

**Identification.** Outland confirmed the jeans with the photo credit within about 20 minutes, then issued a prepared press release. Its Instagram following reportedly doubled within 10 hours.[13][14]

**Response, reported:**
- traffic +3,000% on the Australian site and +948% globally
- sales +640% in the following week
- sold out in Australia and the US within 24–48 hours, then backordered twice
- 16-day global online sales +2,374%
- 46 additional seamstresses hired[13][14]

**Observed:** archived Shopify product page, size-level variant availability.

| Date | Day | Sizes available |
|---|---|---|
| 2018-10-18 | +1 | 5 of 26 |
| 2018-10-21 | +4 | 26 of 26 |
| 2018-10-31 | +14 | 26 of 26 |
| 2018-11-01 | +15 | 26 of 26 |
| 2018-12-11 to 2018-12-13 | +55 to +57 | 24 of 24 |

The storefront ran a preorder app, so "available" after day 1 most likely reflects preorder or backorder, consistent with the reported backorders.

**Gaps.** No pre-event capture of the Harriet page survives. Absolute units and the baseline period are not public.

## Coverage of the chain

| Link | Taylor / NB 550 | Kanye / ESM | Meghan / Outland |
|---|---|---|---|
| Relationship evidence | none found (Keds prior) | announced Adidas partner | seeded, unpaid |
| Dated appearance | yes, to the minute | yes, to the day | yes, to the day |
| Exact SKU | `BB550SE1` | `B44283` | Harriet in black |
| Identification timing | about 18 hours | 1 day | about 20 minutes |
| Amplification evidence | rich: views, retailer ads, email | specialist coverage | press release, Instagram |
| Brand traffic or sales | reported | none | reported |
| Marketplace response | StockX trades and price | unsold eBay asks; one completed sale | none located |
| Observed inventory | post-restock size grid | pre-event in-stock series | day-1 size-level stockout |
| Google Trends | spike on day 2 | not available for ESM | not yet pulled |

## Reproducible demo artifacts

Run `make demo` (see [`demo-pipeline.md`](demo-pipeline.md)). First full run on November 9, 2026, all `observed`:

- **Kanye / Energy Boost ESM `B44283`:** Adidas page `InStock` in all 11 captures from January 24 to May 14 (day −105 to +5), then `OutOfStock` with Add to Bag disabled on May 15, 16, 18 and 19 (days +6 to +10). Specialist identification began day +1; 18 of 18 relevant articles were sneaker specialists.
- **Kanye / Ultra Boost `S77416` benchmark:** "Coming Soon" countdown on May 17–18 (15, then 14 days), then `OutOfStock` from May 20.
- **Taylor / New Balance 550:** 8 archived product URLs carry affiliate tracking (New York Post Network, Penske Media, Skimbit, Sneaker News) and 2 carry New Balance email tracking. Google Trends for "Taylor Swift New Balance" rose from a pre-period mean of 1.1 to 100 on day +2. "New Balance 550" rose only modestly (79 vs 59.5), and Adidas Samba also peaked on day 0, so day-of-week and category controls matter.
- **Meghan / Outland Harriet:** brand- and exact-level identification in Australian press on day 0. Australian Google Trends for "Outland Denim" went from 0 to 100 on day 0, and US Trends peaked on day +11. The archived product page shows 5 of 26 sizes available on day +1.

Outputs: `output/demo/<case>_chain.png`, `output/demo/timelines.csv`, `output/demo/summary.md`.

## Next build steps

1. Add Trends series for the Meghan case and the ESM product name.
2. Build an amplification ledger for each case: article URL, publisher, timestamp, actor type, identification level and commerce link.
3. Draw one timeline figure per case, with every point labeled observed or reported.
4. Pull controls: archived pages and Trends for sibling colorways or adjacent products, such as other 550 colorways, other Energy Boost colors and other Outland styles.
5. Package the dossiers, figures and coverage table as a short deck.

## Sources

[1] https://www.prnewswire.com/news-releases/keds-announces-multi-year-partnership-with-taylor-swift-173682701.html
[2] https://www.complex.com/sneakers/a/brendan-dunne/taylor-swift-new-balance-550-sneakers-boost-sales
[3] https://static.www.nfl.com/gamecenter/b07d2237-f053-11ed-b4a7-bab79e4492fa.pdf
[4] https://x.com/paytonsun/status/1706108185029845125
[5] https://www.hollywoodreporter.com/lifestyle/shopping/taylor-swift-travis-kelce-new-balance-shoes-sneakers-1235598735/
[6] https://wgntv.com/news/deans-list/travis-kelce-taylor-swift-spotted-leaving-arrowhead-stadium-after-sundays-game/
[7] https://www.actionnetwork.com/nfl/how-taylor-swift-travis-kelce-partnership-has-affected-sports-business
[8] https://www.adidas-group.com/en/media/press-releases/adidas-confirms-new-partnership-with-kanye-west
[9] https://www.complex.com/sneakers/a/rajah-allarey/kanye-takes-wango-tango-stage-not-wearing-his-yeezy-boosts
[10] https://weartesters.com/the-all-white-adidas-energy-boost-esm-that-kanye-west-wore-over-the-weekend-is-available-now
[11] https://www.nicekicks.com/kanye-wore-this-adidas-energy-boost-esm-on-sunday-and-now-theyre-sold-out
[12] https://www.complex.com/sneakers/a/matt-welty/white-adidas-esm-boost-ebay-prices
[13] https://fashionmagazine.com/flare/celebrity/meghan-markle-effect-outland-denim
[14] https://www.townandcountrymag.com/style/fashion-trends/a28198319/meghan-markle-outland-denim-jeans-interview
