# Vertical selection: accessible footwear first

**Steering status:** updated after stress-testing watch-market timing, liquidity and alternative verticals. See [`acute-product-shock-design.md`](acute-product-shock-design.md) for the current primary design.

## Recommendation

Focus the first pilot on **reference-identifiable products with concentrated shopping and specialist-identification channels**, with this ordering:

1. **Sneakers and accessible footwear** — primary acute-shock domain and strongest style-code/colorway design.
2. **Luxury watches** — high-attention, low-immediate-conversion comparison and secondary marketplace-data path.
3. **High-end designer apparel/accessories** — later extension after product matching is proven.

The common research object is not “a celebrity wore a brand.” It is:

> A public appearance links a celebrity to an exact scarce product; specialist media identify and amplify that product; focal and substitute market activity then adjust.

This yields stable product identifiers, concentrated shopping venues, specialist media ecosystems, and matched product controls.

## Why sneakers remain an important replication domain

### Advantages

- Exact products usually have stable style codes, model names and colorways.
- Product drops, restocks and release calendars can be recorded explicitly.
- Secondary-market behavior can move rapidly after an appearance.
- Same-model colorways provide unusually close controls.
- Competitor products can be matched by silhouette, use case, price, release cohort and baseline liquidity.
- A dense specialist-media ecosystem exists across sneaker publications, YouTube, TikTok, Instagram and resale communities.
- Public appearances are frequent enough to create a prospective event panel.

### Motivating example: Kanye West and white Adidas Boost products

Contemporaneous and retrospective coverage describes a sequence in May 2015 in which Kanye West wore white Adidas Boost products, availability disappeared rapidly, and resale asking prices increased. GQ reports that the white Energy Boost ESM and Triple White Ultra Boost were gone from the market within days and were listed on eBay and Flight Club for as much as $600.[1] GOAT identifies the Triple White UltraBoost by SKU `S77416` and describes pre-orders selling out after West wore the shoe before its official release.[2]

This is a motivating case rather than a clean estimate. The product was close to release, supply was constrained, Adidas publicity and the broader Yeezy relationship were active, and historical platform data may be incomplete. But it illustrates the exact empirical sequence the project should test prospectively:

1. celebrity appearance;
2. specialist product identification;
3. social amplification;
4. focal-SKU sellout or marketplace pressure;
5. possible halo effects on sibling Adidas products;
6. comparison with Nike or other matched substitutes.

### Main limitation

The best sneaker marketplaces do not currently provide a straightforward public platform-wide transaction feed. StockX standard developer access does not supply market-wide completed-sale counts and restricts longitudinal archival use without separate permission. GOAT should be treated as a partnership or manual-validation source until a documented research/data route is obtained.

Therefore, the sneaker pilot requires two parallel tracks:

- social/event identification and product matching, which can begin immediately;
- commerce-data access, pursued through StockX, GOAT, eBay, retailers, sellers or licensed vendors.

## Why watches remain a useful comparison domain

### Advantages

- Watch reference numbers provide strong product identity.
- Watches are systematically identified at red carpets, tennis tournaments, Formula 1, film festivals, press events and public appearances.
- Specialist watch media often report celebrity, event, brand, model and exact reference.
- Authorized-dealer scarcity makes secondary-market behavior substantively important.
- Chrono24 reports more than 500,000 available watches and more than 1.6 million watches sold since 2003, making it an unusually concentrated market.[3]
- WatchCharts offers an official paid API with watch lookup by brand/reference, current prices, historical prices and historical listings. Its entry plan includes 500 free data credits; higher plans provide daily credits and more advanced endpoints.[4]
- In October 2026, Chrono24 launched Market Scanner for professional dealers. It distinguishes listing and completed-sale prices and reports reference-level time-to-sell, market saturation, listing views, requests, recent transactions and geography where data are sufficient.[7]

### Available market measures

WatchCharts publishes daily market prices for more than 28,000 watches and states that its prices use a weighted 30-day transaction window, supplementing with last asking prices or unsold listings when transaction evidence is sparse.[5]

Potential reference-level outcomes include:

- market-price changes;
- dealer-price changes;
- new listing volume;
- listing age and disappearance;
- spread between dealer and private-market estimates;
- number of active listings;
- changes relative to sibling references;
- changes relative to watches from competing brands in the same price/use segment.

Chrono24's public ChronoPulse index uses actual transaction data but covers aggregate market segments rather than supplying event-level transaction microdata.[6] Market Scanner demonstrates that Chrono24 already computes the outcomes this project needs at the reference level: views, requests, listing supply, time-to-sell and completed-sale prices.[7]

The immediate access path is therefore a research agreement with Chrono24 or a professional-dealer collaborator, with explicit permission for retention, analysis and publication. Dealer access alone should not be assumed to authorize academic extraction or publication.

### Main limitations

- Watches trade less frequently than hype sneakers, reducing high-frequency power.
- Public price series may be smoothed over windows too long for short event studies.
- Vintage condition, provenance, box/papers and production year create within-reference heterogeneity.
- Celebrity watch identification can be uncertain from photographs.
- Watch buyers may react over weeks rather than hours or days.
- An appearance can coincide with a brand ambassador contract or tournament sponsorship.

Watches may therefore work best with a platform/data-provider partnership that exposes requests, wishlist additions, listing views or transaction counts—not only price estimates.

## Why broad designer fashion should wait

Luxury apparel, jewelry, bags and accessories offer many appearances, but the initial measurement problem is harder:

- inconsistent or absent public style codes;
- seasonal naming and retailer-specific identifiers;
- counterfeit and near-duplicate products;
- fit, size, condition and customization heterogeneity;
- fragmented resale platforms;
- short product lifecycles;
- styling teams may select products, complicating relationship interpretation.

The later extension should begin with categories that retain strong identifiers, such as handbags, jewelry models or iconic outerwear, rather than unconstrained clothing.

## Core sneaker design

### Eligible event

- Celebrity is publicly visible wearing a commercially identifiable sneaker.
- Original appearance does not explicitly name or link the exact SKU in the primary implicit sample.
- Appearance time is recoverable.
- Exact style code and colorway are later confirmed by two sources or coders.
- The product existed before the event and has a measurable pre-period.
- No scheduled release, restock or major campaign contaminates the main window.

Keep explicit endorsements as a separate benchmark arm.

### Three clocks

- `T_A`: first public appearance.
- `T_B`: first brand-level identification.
- `T_S`: first exact style-code/colorway identification.
- `T_M`: prespecified social-amplification threshold.

Separating brand and exact-SKU identification is especially valuable. A viewer may recognize Adidas immediately but only later learn that the shoe is the Triple White UltraBoost `S77416`.

### Social outcomes

Track specialist and general accounts separately:

- generic celebrity-event posts;
- shoe/category posts;
- brand identifications;
- exact-SKU identifications;
- unique independent posters;
- repost-inclusive amplification;
- retailer/resale/affiliate links;
- purchase-intent language;
- incorrect model/colorway identifications;
- focal versus competitor recommendations.

The primary social outcome should be the **exact-SKU share of product-related posts**, not total celebrity engagement.

### Commerce outcomes

Preferred hierarchy:

1. completed units, if a partnership provides them;
2. auctions receiving new bids;
3. bid-count and current-bid changes;
4. best-bid/best-ask changes under approved retention terms;
5. new listings and seller entry;
6. active listing inventory;
7. asking-price distribution;
8. retailer size availability and stockouts where collection is permitted.

Never treat listing disappearance as a confirmed sale.

### Controls

For each focal shoe:

- same model, different colorways;
- same brand, adjacent models;
- competitor shoe matched on price, release cohort, category and baseline liquidity;
- leave-one-out category index.

The sharpest interference test is whether focal activity rises without analogous activity in rival hype products.

## Core watch design

### Eligible event

- Exact brand/model/reference can be identified from a public appearance.
- The reference has sufficient historical market coverage.
- No contemporaneous watch launch, auction record or brand announcement dominates the event window.
- Condition and configuration can be represented consistently.

### Controls

- same collection, adjacent references;
- same brand and price tier;
- competing sports/dress watch with similar secondary-market liquidity;
- broader brand and market indexes.

### Outcomes

- reference-level daily market value;
- listing volume and age;
- dealer versus private-market spread;
- marketplace request, wishlist or transaction measures if a partnership is obtained;
- exact-reference social identification and amplification.

## Feasibility tournament

Before committing the full project to one vertical, run a bounded comparison:

### Watch calibration

- 10–15 recent red-carpet/sports/public appearances;
- verify exact references and appearance/identification clocks;
- use WatchCharts API credits for price and listing history;
- seek a Chrono24 research agreement or professional-dealer collaboration for Market Scanner outcomes;
- measure social identification in specialist watch media and available platform data.

### Sneaker calibration

- 10–15 recent implicit appearances;
- verify exact SKU and clocks;
- measure social identification across YouTube and available TikTok/Instagram routes;
- test eBay and any approved marketplace coverage;
- evaluate control-product liquidity.

Select the first full study using predeclared gates:

- product identification accuracy;
- recoverable appearance/identification timestamps;
- event frequency;
- pre-period market liquidity;
- control-product quality;
- social coverage recall;
- legal and contractual retention;
- availability of behavior rather than only asking prices.

## Current steering recommendation

Begin with **sneakers and accessible footwear as the primary acute-shock domain**. They provide exact style codes, frequent appearances, rapid specialist identification, lower purchase friction and unusually clean same-model colorway controls. The first sample should contain consecutive eligible appearances rather than famous sellouts.

Retain **watches as a secondary comparison domain**. Watch references and specialist identification are unusually precise, while WatchCharts and Chrono24 demonstrate valuable market-data possibilities.[4][7] But sparse transactions, high prices, smoothed public price measures and dense sponsorship/launch calendars make watches better for studying attention without immediate conversion than for the first spike-based sales design.

## Sources

[1] https://www.gq.com/story/adidas-boost-history-yeezy-sneakers
[2] https://www.goat.com/sneakers/ultra-boost-triple-white-s77416
[3] https://about.chrono24.com/en/company
[4] https://watchcharts.com/api
[5] https://watchcharts.com/watches/about
[6] https://about.chrono24.com/en/press/luxury-watches-prices-remain-stable-in-2024
[7] https://about.chrono24.com/en/press/chrono24-launches-market-scanner-direct-access-to-marketplace-data-for-professional-dealers
