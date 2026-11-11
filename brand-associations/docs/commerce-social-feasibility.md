# Commerce and social-amplification feasibility

**Assessment date:** November 6, 2026. This is an operational reading of published access routes and terms, not legal advice.

## Steering conclusion

A combined commerce–social study is feasible, but the initial interpretation needs tightening:

1. **StockX and ordinary eBay APIs do not currently give us platform-wide completed-purchase counts.** StockX exposes current market quotes and an authenticated seller's own orders.[1][2][3]
   eBay Browse exposes active listings and auction engagement, while eBay's sold-data Marketplace Insights API is restricted and not open to new users.[4]
2. **Posting volume is feasible and theoretically valuable as the amplification mechanism.** TikTok Research API and Meta Content Library are the strongest research-grade routes; YouTube is the strongest route that can be deployed without academic platform approval.[5][6][7]
3. The first compliant pilot should therefore measure **social resolution and amplification plus active-market demand pressure**, not call those outcomes purchases.
4. A full purchase study requires a separate agreement with StockX/eBay, a cooperating seller or retailer, an affiliate platform, or licensed transaction/receipt data.

## The three-clock design

The central empirical object should separate:

1. **Appearance (`T_A`)** — the product first becomes publicly visible.
2. **Identification (`T_I`)** — the first verified public exact-SKU identification.
3. **Amplification (`T_M`)** — exact identification spreads beyond the original identifier according to a frozen threshold.

The distinctive prediction is:

- generic celebrity/product discussion may respond at appearance;
- brand and exact-SKU posting should rise at identification;
- active-market demand pressure should concentrate after identification and grow with amplification;
- matched competitor products should respond less when the focal association is selective.

This sequence is more informative than a single post-campaign event study because it distinguishes visibility, information resolution, and diffusion.

## Commerce feasibility

### StockX: conditional, not an immediate longitudinal panel

The standard developer API supports:

- catalog and variant identifiers;
- current highest bids and lowest asks;
- seller listing management;
- the authenticated seller's active and historical orders.

It does **not** provide a standard route to platform-wide completed-sale counts, transaction histories, full order-book depth, or historical bid/ask series. Historical orders belong to the authenticated seller and cover only six months.[1][2]

The standard developer license prohibits archiving StockX Data and treats StockX data and derivatives as confidential. Therefore, technically polling quotes does not by itself make a longitudinal research panel permissible. Before collection, a written research agreement would need to cover snapshot retention, derived statistics, publication, collaborators, and deletion.[3]

**Verdict:**

- Product identity crosswalk: feasible after developer approval.
- Current bid/ask snapshots: technically feasible but longitudinal retention requires written permission.
- Market-wide completed purchases: unavailable through the standard API.
- Seller-specific purchases: possible only with a cooperating seller and represent only that seller.

### eBay Browse: feasible active-market measurement

The Browse API can support:

- current matching-listing counts;
- asking-price distributions;
- listing creation and end dates;
- fixed-price versus auction composition;
- auction bid counts and current bids;
- seller, condition, location, GTIN/ePID and other matching fields.

It does not return sold/completed listings. Listing disappearance is ambiguous: the item may have sold, expired, been withdrawn, been revised, or fallen outside the matching rule.[4]

Production Buy API use requires additional partner review and licensing beyond simply having a developer key. The exact granted quota and allowed derived measures must be read from the approved keyset and agreement.[4]

**Verdict:**

- Active supply and asking prices: feasible after production approval.
- Auction engagement: feasible for returned auction listings.
- Completed purchases: not available through Browse.
- Listing disappearance: usable only as an ambiguous turnover outcome, never labeled a sale.

### eBay Marketplace Insights: strong but currently blocked

Marketplace Insights is the relevant API for sold-item data. The specification includes rolling 90-day sold data such as total sold quantity, last sold date and last sold price, but the product is restricted and not open to new users.[4]

**Verdict:** a direct partnership or inherited entitlement would make eBay one of the strongest sources; it is not a critical-path source for the initial pilot.

### Commerce outcomes we can honestly use now

If access is approved, define active-market outcomes such as:

- new listings per hour/day;
- active listing inventory;
- median and quantile asking prices;
- share of auctions receiving a bid;
- bid-count increments;
- current-bid changes;
- seller entry;
- focal-product activity relative to sibling colorways and rival SKUs.

Call these **active-market demand and supply responses**, not purchases.

For actual purchases, pursue one of:

- eBay Marketplace Insights partnership;
- StockX research license or cooperating seller;
- retailer product-page/add-to-cart/sales partnership;
- affiliate-platform clicks and conversions;
- licensed card, receipt, loyalty or SKU transaction panel.

## Social posting feasibility

### TikTok Research API: strong and application-dependent

For approved academic research, TikTok supports historical public-video searches by creator, keyword, hashtag, date, region and other fields, plus engagement counts and comment text/metadata. Stable video and comment IDs make event linkage feasible. The current documented ceiling is 1,000 requests and up to 100,000 video/comment records per day, while new content and engagement metrics can arrive with delays.[5]

The API does not grant a blanket right to download and archive video binaries. The durable design should retain controlled IDs, canonical URLs, returned text/metadata, repeated engagement observations, and coded visual features under the approved terms.

**Verdict:** apply immediately; make it central only after approval.

### Meta Content Library/API: strongest Instagram/Facebook route

Meta Content Library is the correct research route for public Facebook and Instagram content. It supports producer- and keyword-based search, comments and engagement fields over included public surfaces. Analysis occurs in an approved secure environment and raw data generally cannot be exported. Exportable outputs are reviewed aggregate research products.[6]

Ordinary Instagram APIs are not a substitute: they are primarily for authorized professional or managed accounts, not arbitrary public celebrity monitoring.

**Verdict:** apply immediately; plan the analysis so row-level data and media coding remain inside the enclave while event-level aggregates are exported.

### YouTube Data API: immediate backbone

YouTube supports public video discovery, known-channel upload enumeration, metadata, statistics and public comments where enabled. Broad search is quota-expensive and not guaranteed exhaustive, so a verified channel roster is preferable for celebrity and brand accounts.[7]

YouTube policies require periodic refresh/deletion of non-authorized API data and prohibit downloading audiovisual content without approval. Store stable IDs, URLs, observation timestamps and permitted metadata; embed rather than archive videos.

**Verdict:** strongest immediate route for a small pilot and method validation.

### Other platforms

- **X:** full-archive search and counts are technically valuable but paid, policy-sensitive, and potentially problematic for cross-platform benchmarking. Use counts first and retrieve only a stratified post sample.
- **Reddit for Researchers:** useful for discussion and interpretation, but the approved dataset is delayed and project/subreddit-scoped. Treat it as a lagged amplification layer.
- **Snapchat Public Profile API:** account-roster monitoring only; not a platform-wide keyword corpus.
- **Pinterest standard API:** not a viable arbitrary public-post search route; useful only for authorized accounts or separate research access.

## Social outcomes

Posting volume should not be a single count. Preserve the resolution and provenance of each post:

1. **Generic event posting** — celebrity/event discussion with no product identification.
2. **Category posting** — mentions shoes, watch, dress, bag, sportsbook, etc.
3. **Brand identification** — names the focal brand.
4. **Exact-SKU identification** — names or links the exact model/colorway/product.
5. **Commerce-linked amplification** — contains a retailer, resale or affiliate link.

Primary social outcomes:

- unique independent posts per event-hour;
- brand-identification share of product-related posts;
- exact-SKU share of identified posts;
- time from appearance to brand and SKU identification;
- unique posters rather than raw repost count;
- repost-inclusive volume as a separate amplification measure;
- number of affiliate/commerce-linked posts;
- focal versus competitor identification share;
- specialist, editorial, affiliate, brand-owned, fan and general-news amplifier types.

Keep engagement measures native to each platform. Views, likes, comments and shares are defined differently and should not be summed directly across platforms.

## Product and control construction

For each focal appearance, freeze before examining post-event outcomes:

- exact focal SKU/model/colorway;
- two or three sibling products, preferably other colorways of the same model;
- two or three competitor SKUs matched on category, price, release cohort, baseline liquidity and visual similarity;
- a broader leave-one-out category index;
- event, product, celebrity and brand aliases.

Sibling controls address model-level demand shocks. Competitor controls test whether attention is focal or spills into the category.

## Recommended pilot

### Phase 1: access and technical calibration

In parallel:

- apply for TikTok Research API;
- apply for Meta Content Library;
- request StockX developer access plus written research/archival permission;
- apply for eBay production Buy API access and separately inquire about Marketplace Insights/research access;
- establish YouTube collection immediately.

Build a calibration sample of roughly 20–30 events to test:

- event timestamp recovery;
- exact-SKU mapping reliability;
- control-product availability;
- social search recall;
- identification timing;
- repeated engagement snapshots;
- eBay matching precision and listing coverage;
- ability to observe sufficient pre-event active-market variation.

### Phase 2: study sample

Scale only if the calibration shows:

- most events have confirmed exact SKUs;
- appearance and identification timestamps are recoverable;
- a meaningful share has identification delays long enough to separate the clocks;
- social posts can be classified reliably;
- focal and control products have nontrivial baseline marketplace activity;
- at least one commerce route permits repeated compliant snapshots.

### Main figures

1. **Social resolution:** generic → category → brand → exact-SKU posting around appearance, identification and amplification.
2. **Commerce response:** focal product minus sibling/competitor controls around the same clocks.
3. **Timing comparison:** commerce aligned once on appearance and once on identification.
4. **Competitive capture:** focal share of social and marketplace activity versus matched rivals.

The most distinctive result would be a diffuse or absent market response around appearance, followed by a sharp exact-SKU social and commerce response around public identification, with no analogous movement for incorrect colorways or matched rival products.

## Interpretation limits

The design observes aggregate public posting and market activity, not which individuals saw an appearance or whether they purchased because of it. Identification and amplification are endogenous to recognizability and early buzz. The safe claim is:

> Product-specific social and market activity changes differentially after appearance, identification and amplification, with timing and product-placebo patterns consistent with an information-resolution and diffusion mechanism.

Do not claim individual persuasion, formal causal mediation, or platform-wide sales unless the required exposure or completed-transaction data are obtained.

## Sources

[1] https://developer.stockx.com/portal/api-reference
[2] https://developer.stockx.com/portal/api-introduction
[3] https://developer.stockx.com/portal/license-agreement
[4] https://developer.ebay.com/api-docs/buy/static/buy-requirements.html
[5] https://developers.tiktok.com/products/research-api/
[6] https://developers.facebook.com/docs/content-library-and-api
[7] https://developers.google.com/youtube/v3/docs/search/list
