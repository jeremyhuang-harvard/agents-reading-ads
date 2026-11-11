# Acute celebrity-product shock design

**Steering decision:** make accessible footwear the primary empirical vertical; treat watches as a high-attention, low-conversion comparison rather than the first main outcome study.

## Research question

The project should estimate the **distribution of event-level celebrity-product shocks**, not only an average celebrity effect:

> Why do a small number of appearances create enormous, exact-product demand shocks while most create diffuse attention or no measurable response? Does rapid exact-product identification concentrate the response on the focal product rather than activate substitutes and competitors?

This reframing preserves the directional-association and competitive-interference theory while moving the main outcome toward behavior that can change within hours or days.

## Motivating cases

### Kanye West and the Triple White UltraBoost

GQ reports that Kanye West wore white Adidas Energy Boost and Triple White UltraBoost products in May 2015; within days, both were unavailable through ordinary retail and appeared on eBay and Flight Club for as much as $600.[1] The Triple White UltraBoost has a stable style code, `S77416`, making it possible to distinguish the focal colorway from sibling UltraBoost products.

The case is not a clean natural experiment. West already had an Adidas relationship, the product was scarce, and the appearance occurred near a release cycle. It nevertheless illustrates the focal sequence:

1. appearance;
2. exact-colorway identification;
3. specialist amplification;
4. retail depletion;
5. resale-market response;
6. potential halo or spillover to sibling and competitor products.

### Taylor Swift and the New Balance 550

Taylor Swift wore the white/red/black New Balance 550, style code `BB550SE1`, to a Kansas City Chiefs game on September 24, 2023. Complex reports that an internal New Balance presentation showed, in the following week, a 30% increase in product traffic, a 22% increase in units sold and a 25% increase in revenue for the 550.[2]

This is an unusually useful benchmark because it links a dated public appearance and exact product identifier to actual traffic, units and revenue rather than only searches or publicity.

### Justin Bieber and Crocs

Justin Bieber's yellow Crocs reportedly sold out in about 90 minutes and generated enough demand to disrupt the website.[3] Crocs had formally announced the collaboration on October 7, 2020 for an October 13 launch.[4]

This is an explicit, supply-planned collaboration rather than an implicit appearance. It should define the upper-bound benchmark arm, not be pooled with plausibly organic events.

## Distribution of responses

Classify each event into an outcome pattern without selecting the sample on that pattern:

1. **No measurable response** — no clear social or market movement.
2. **Attention only** — coverage and identification increase, but shopping behavior does not.
3. **Brand/category halo** — the focal brand and substitutes rise together.
4. **Exact-product demand** — focal SKU activity rises relative to sibling and competitor products.
5. **Sellout/resale shock** — focal inventory disappears and secondary-market pressure rises.

The empirical target is the distribution of event-specific focal effects and competitive selectivity, plus the observable event characteristics that predict the upper tail.

## Event taxonomy

Preserve these groups separately:

- **A. Plausibly organic:** no documented material relationship; existing product.
- **B. Ambassador off-campaign:** known relationship, but no documented campaign for the specific appearance.
- **C. Gifted/stylist placement:** evidence of product provision without an explicit consumer-facing campaign.
- **D. Explicit collaboration/campaign:** announced launch, signature product, paid creative or capsule collection.
- **E. Unknown:** insufficient evidence; never infer organicity from missing disclosure.

Types A–C are the primary substantive sample. Type D is an upper-bound benchmark. Unknown remains a separate status.

## Mechanism and clocks

An event can fail at several stages:

1. product is displayed;
2. viewers notice it;
3. brand is identified;
4. exact SKU/colorway is identified;
5. specialist accounts amplify it;
6. a commerce link or retailer becomes available;
7. people click, save, bid, add to cart or purchase.

Record separate timestamps:

- `T_A`: original public appearance;
- `T_B`: first credible brand identification;
- `T_S`: first exact-SKU/colorway identification;
- `T_M`: prespecified amplification threshold;
- `T_C`: first commerce-linked amplification.

Specialist recap accounts are part of the mechanism, not merely a data source. They transform an ambiguous visual cue into an explicit, searchable and purchasable product treatment.

## Predicted heterogeneity

Pre-register a compact set of event-level moderators:

### Identification resolution

Generic category or brand coverage should create more diffuse responses than exact style-code/colorway identification.

### Amplification velocity

Measure time to first exact identification, unique independent identifiers, commerce-linked posts, time to peak and concentration among large accounts.

### Celebrity–product fit

Code expected fit, distinctive-but-plausible fit and implausible fit. A distinctive but credible pairing may be more memorable than either a routine pairing or an incoherent one.

### Product accessibility

Price, ordinary retail availability, number of sellers, size availability and baseline resale liquidity determine whether attention can convert to behavior.

### Prior association

A novel celebrity–brand pairing may create a larger short-run spike. A mature association may create recognition with little marginal surprise.

### Competitive specificity

Track whether movement occurs in the focal SKU, sibling colorways, same-brand adjacent products or matched rival products.

## Primary empirical objects

For event `e`, estimate a focal response relative to frozen controls:

```text
focal response_e = post/pre change for focal SKU
                 - post/pre change for sibling and competitor SKUs
```

Define competitive selectivity as the focal product's share of total focal-plus-substitute movement. Report the component outcomes rather than relying only on a composite index.

Interpretation:

- large focal response and high selectivity: product-specific, low-interference shock;
- large focal response and low selectivity: broad category activation;
- high attention and little market response: publicity without conversion;
- little attention and little market response: cue failed to propagate.

## Recommended contained sample

Collect **30 consecutive eligible footwear appearances** from a frozen discovery roster. Do not handpick known viral successes.

### Discovery roster

- Sneaker News `Celebrity Feet` archive;[5]
- Spotern product-identification records;[6]
- one or more cooperating sneaker or celebrity-style identification accounts;
- original photographs, video or reporting used to establish `T_A`.

### Eligibility

- exact SKU/style code and colorway can be established;
- product existed before the appearance;
- appearance and first identification timestamps are recoverable;
- product is ordinarily purchasable rather than a one-off sample or custom item;
- release, restock and formal campaign timing can be recorded;
- include the event regardless of later response.

Use a prespecified accessible-price band for the primary sample, with more expensive products retained as a heterogeneity or comparison arm. Freeze the numerical threshold after inspecting product coverage but before outcome collection.

### Controls

For every focal SKU:

1. same model, different colorway;
2. same brand, adjacent model;
3. competitor product matched on price, category, release cohort and baseline liquidity;
4. leave-one-out category basket when coverage permits.

## Outcome hierarchy

### Preferred partner outcomes

The strongest initial partner may be a product-identification or celebrity-style account using ShopMy, LTK, Amazon Associates or retailer affiliate links. Request all consecutive eligible posts over a fixed period, including zeros:

- impressions/reach;
- exact product and post timestamp;
- outbound clicks;
- add-to-cart or checkout events where available;
- conversions, units and revenue;
- audience geography;
- commission or affiliate revenue;
- stockout indication.

A retailer or small brand with Shopify-style event data could provide hourly product-page views, referrers, carts, checkouts, units and inventory around appearances.

### Public behavioral fallback

The eBay Browse API exposes active listings and auction activity but not a generally available completed-sales panel.[7] Public outcomes can include:

- auction bid counts and current bids;
- new listings;
- active listing inventory;
- asking-price distribution;
- listing disappearance, explicitly not labeled a sale;
- retailer size availability and stock status where collection is permitted;
- exact-product shopping/search measures as mechanism checks;
- social identification and commerce-link creation.

StockX should remain a conditional source: standard access does not provide platform-wide completed purchases, and longitudinal retention requires appropriate permission.[8]

## Why watches move to the comparison arm

The 98th Academy Awards occurred on March 15, 2026.[9]

The surrounding window is crowded. BAFTA occurred on February 22 and the Actor Awards on March 1.[10][11]

Paris Fashion Week continued through March 10, while Watches and Wonders began April 14.[12][13]

Rolex was also an official Oscars sponsor, increasing commercial-placement concerns.[14]

Specialist Oscars-watch recaps appeared the night of March 15 and on March 16, compressing appearance, identification and amplification into less than a day for many pieces.[15][16]

This makes the Oscars useful for an attention and identification case study, but weak for a clean price event study. Ten rare watch events are enough to test reference matching and detect a very large, consistently signed attention response; they are not enough to identify modest price or sales effects from slow, thinly traded outcomes.

Use watches later to test a valuable boundary condition:

> Specialist attention and exact identification can be high while immediate purchase conversion remains low because price, scarcity and liquidity create substantial friction.

## Alternatives and extensions

Ranked for acute product-specific responses:

1. **Sneakers and accessible footwear** — clean style codes, frequent events, fast specialist amplification and strong sibling controls.
2. **Consumer headphones/electronics** — excellent model identifiers and retail availability, but fewer celebrity identification events.
3. **Beauty/cosmetics** — potentially very high-volume with a retailer or TikTok Shop partner; exact product often becomes known only after a makeup artist disclosure.
4. **Sports equipment** — abundant exact-product identification, but sponsorship, repeated exposure and performance confounds are substantial.
5. **Music gear** — useful specialist identification and active-market data; slower purchases than footwear.
6. **Luxury handbags and watches** — strong identification ecosystems but higher price, lower velocity and weaker public transaction access.

## Timeline for the contained footwear pilot

### Public-data calibration

Approximately **two working weeks**:

- freeze roster, rules and schemas;
- collect 30 consecutive events;
- verify timestamps and exact products;
- freeze controls;
- probe eBay and public retailer coverage;
- construct social-amplification traces;
- report matching, missingness and outcome feasibility.

### Partner-enriched calibration

Approximately **three to five working weeks after access**, depending on partner export and documentation:

- ingest post-level impressions/clicks/conversions;
- align appearance and recap clocks;
- validate all zero and nonzero events;
- construct focal and substitute responses;
- produce event traces and the distributional readout.

Do not scale to causal claims until the public or partner outcomes provide meaningful pre-period denominators and the sample includes both high- and low-response events by construction.

## Immediate next gate

Before building collectors, identify and approach:

1. two sneaker or celebrity-style identification accounts with affiliate links;
2. one accessible-footwear retailer or small brand able to export product-level traffic, inventory and sales;
3. the public discovery roster for 30 consecutive events.

The first go/no-go question is whether a single account or retailer can provide the zeros, impressions and downstream clicks/conversions needed to estimate the response distribution rather than only document famous sellouts.

## Sources

[1] https://www.gq.com/story/adidas-boost-history-yeezy-sneakers
[2] https://www.complex.com/sneakers/a/brendan-dunne/taylor-swift-new-balance-550-sneakers-boost-sales
[3] https://abc7ny.com/post/justin-bieber-crocs-shoes-fashion-launches-design/7018173
[4] https://investors.crocs.com/news-and-events/press-releases/press-release-details/2020/Just-Drop-It-Already-Crocs-and-Justin-Bieber-Turn-Up-for-the-Biggest-Croctober-Launch-to-Date/default.aspx
[5] https://sneakernews.com/category/celebrity-feet/
[6] https://www.spotern.com/en
[7] https://developer.ebay.com/api-docs/buy/browse/overview.html
[8] https://developer.stockx.com/portal/api-reference
[9] https://www.oscars.org/oscars/ceremonies/2026
[10] https://bafta.org/media-centre/press-releases/2026-ee-bafta-film-awards-date
[11] https://www.sagawards.org/media/news/releases/screen-actors-guild-awards-sets-date-2026
[12] https://www.fhcm.paris/en/node/7829
[13] https://www.watchesandwonders.com/en/geneva-2026/practical-info
[14] https://newsroom.rolex.com/world-of-rolex/perpetuating-arts-and-culture/rolex-and-cinema/rolex-and-cinema-2026/news-3/the-oscars
[15] https://www.insidehook.com/watches/best-watches-oscars-red-carpet-2026
[16] https://www.gq.com/gallery/2026-oscars-best-watches
