# Contained watch-data pilot

**Status:** retained as a secondary attention/measurement calibration, not the primary pilot. The current primary direction is the accessible-footwear design in [`acute-product-shock-design.md`](acute-product-shock-design.md).

**Purpose:** prove the event → identification/amplification → reference-level market-data pipeline and study a high-attention, low-immediate-conversion boundary condition.

## Recommendation

Use a **10-appearance watch pilot drawn from one bounded event: the 2026 Academy Awards**.

This is deliberately a technical and measurement calibration, not the final causal sample. A single event gives us:

- one known appearance window;
- multiple celebrity–watch pairs;
- concentrated specialist coverage;
- exact model/reference identifications;
- common calendar and macro conditions;
- enough variation in brands, prices and relationship status to expose data problems.

GQ and several watch-specialist/retailer publications published 2026 Oscars watch roundups with named celebrities and watches, creating a bounded discovery frame.[1] The pilot should freeze the first 10 eligible pairs in the primary roundup rather than selecting the cases with the largest subsequent response.

## Pilot unit and scale

### Focal sample

- 10 celebrity–watch appearances;
- one exact reference per appearance where possible;
- preserve `unknown` when the article identifies only a collection or prototype;
- include known ambassador or placement events, but label them and do not call them implicit/organic.

### Controls

For each focal reference, select before looking at market outcomes:

1. one sibling reference from the same collection and similar material/price;
2. one competitor reference with similar price, function, age and baseline liquidity.

This produces approximately:

- 10 event rows;
- 30 product/reference rows;
- roughly 10,950 product-day rows for a one-year daily panel;
- 50–200 amplification records, depending on source coverage.

The small size keeps exact-reference verification and manual quality control feasible.

## Data objects to collect

### 1. Appearance ledger

One row per celebrity–watch appearance:

- `event_id`;
- celebrity;
- event and location;
- appearance date and best available time;
- original photo/video/article URL;
- source publication time;
- brand, collection, model and reference;
- case material, dial and configuration;
- identification confidence;
- evidence text and visual coordinates where permitted;
- visible branding;
- disclosed or documented ambassador/sponsorship relationship;
- relationship status: `confirmed`, `plausible`, `none_found`, or `unknown`;
- unreleased/prototype flag;
- concurrent product launch or announcement.

Do not download or commit copyrighted event photography by default. Preserve canonical URLs, metadata, hashes of any legally retained derivative, and the evidence needed to reproduce the identification.

### 2. Identification and amplification ledger

One row per relevant article, video or public post:

- source/platform and stable ID;
- canonical URL;
- publication timestamp and observation timestamp;
- author/account;
- actor type: specialist editorial, general media, retailer/dealer, affiliate, brand-owned, celebrity-owned, fan, or other;
- generic watch mention;
- brand identification;
- collection/model identification;
- exact-reference identification;
- price or purchase link;
- affiliate or commercial link;
- relationship disclosure;
- engagement counts at the observation time;
- quoted evidence span;
- correction or conflicting-identification flag.

For this contained pilot, use a frozen source roster rather than trying to census all Instagram and TikTok posts:

- the primary GQ roundup;
- two watch-specialist roundups;
- two dealer/retailer or trade roundups;
- YouTube search results for the event and exact watches;
- brand/celebrity-owned posts only when a canonical public URL is discoverable.

TikTok and Meta research APIs can be added later. They should not block the pilot.

### 3. Product/reference table

- canonical brand;
- collection, model and exact reference;
- WatchCharts UUID;
- manufacturer product URL where available;
- retail price;
- current secondary-market estimate;
- production status;
- release year;
- complications, material, size and dial;
- focal/sibling/competitor role;
- matching rationale frozen before outcome inspection.

### 4. Market panel

The immediate source is the official WatchCharts API. Its documented endpoints support reference search, watch information and daily one-year price history. Search costs 1 credit, watch information 3 credits and one-year price history 3 credits.[2]

For 30 references, the bounded request budget is approximately:

- search: `30 × 1 = 30` credits;
- watch information: `30 × 3 = 90` credits;
- one-year price history: `30 × 3 = 90` credits;
- **total: about 210 credits**, plus a small retry/matching allowance.

WatchCharts advertises 500 starting data credits for its pay-as-you-go route, so this pilot is intentionally sized below that threshold.[3] API access requires a key; a live unauthenticated probe of the brand endpoint returned HTTP 401, confirming that credentials are necessary.

Store:

- date;
- WatchCharts price estimate;
- volatility;
- observation/retrieval timestamp;
- API response checksum;
- focal/control role;
- event-relative day.

The price estimate is a market measurement rather than a completed transaction. Its construction is smoothed, so it may be too slow-moving for a sharp daily event effect. The pilot's purpose is partly to measure that limitation.

### 5. Partnership-only market outcomes

Chrono24's Market Scanner, launched October 5, 2026 for professional dealers, reports reference/configuration-level:

- average completed-sale price and trend;
- average listing price and trend;
- average time-to-sell;
- listing views;
- purchase requests;
- listing supply relative to requests;
- recent sales;
- geographic demand and supply where data are sufficient.[4][5]

These are much closer to the desired behavioral outcomes than a smoothed price index. However, Market Scanner is a dealer tool rather than a documented research API. The project should request either:

1. a research agreement with Chrono24; or
2. a collaboration with a professional dealer, with separate written permission covering extraction, retention, analysis and publication.

Chrono24 access is an extension, not a prerequisite for the contained pilot.

## Immediate estimands

The pilot can produce descriptive event-time quantities:

### Social identification

- hours from appearance to first brand identification;
- hours from appearance to first exact-reference identification;
- number of independent exact-reference sources;
- exact-reference share of watch-related coverage;
- specialist-to-general-media diffusion sequence.

### Market response

For each focal reference and event-relative day:

- change in estimated market price;
- change relative to its sibling reference;
- change relative to its matched competitor;
- change in volatility;
- persistence over 7-, 14- and 30-day windows.

These are diagnostic plots, not causal estimates. A null or visibly over-smoothed price response is useful evidence that the full study needs Chrono24 views/requests/sales or another higher-frequency demand measure.

## Feasibility assessment

### Feasible now

- bounded event discovery from public watch coverage;
- exact-reference and relationship coding;
- a frozen amplification-source roster;
- WatchCharts catalog matching and historical daily price series after receiving an API key;
- sibling and competitor matching;
- a reproducible 10-event panel and descriptive figures.

### Feasible but manual

- confirming original appearance times;
- resolving conflicting watch identifications;
- checking brand-ambassador or stylist relationships;
- identifying prototypes and unreleased references;
- coding public Instagram/TikTok URLs found through the web without claiming exhaustive platform coverage.

### Gated

- Chrono24 Market Scanner data;
- reference-level purchase requests, views and completed-sale counts;
- comprehensive Instagram and TikTok posting volumes;
- copyrighted image retention and automated visual re-identification at scale.

## Time estimate

Assuming WatchCharts trial/API access is granted promptly:

### Day 1

- freeze the Oscars source frame and eligibility rule;
- create the event, product, amplification and market schemas;
- select the first 10 eligible appearances.

### Days 2–3

- verify exact references;
- record relationship/prototype/launch status;
- preserve evidence and disagreements.

### Day 4

- select and freeze two controls per focal reference;
- validate WatchCharts catalog coverage.

### Days 5–6

- run the WatchCharts collector;
- collect the frozen public coverage and YouTube layer;
- normalize timestamps and identifiers.

### Day 7

- quality assurance;
- produce missingness, matching and provenance reports;
- generate initial event-time figures.

### Days 8–9, if needed

- resolve ambiguous references and controls;
- rerun bounded collections;
- write the feasibility readout and scale/no-scale recommendation.

**Expected duration:** about **7 working days**, or **1–2 calendar weeks**, once the WatchCharts key is available.

A public-web-only version can be completed in approximately **3–4 working days**, but it would validate event and amplification coding rather than market outcomes. Chrono24 or Meta/TikTok access can take an uncertain number of weeks and should run in parallel.

## Go/no-go gates

Scale beyond 10 events only if:

- at least 8 of 10 focal appearances resolve to an exact reference;
- at least 24 of 30 focal/control references match confidently to WatchCharts;
- original appearance timing is recoverable to the day for all events and preferably to the hour for most;
- relationship status can be evidenced or preserved as `unknown` without forced classification;
- the market series has enough pre-event coverage and variation to be informative;
- exact-reference amplification can be recovered from more than one independent source for a meaningful share of events;
- collection and publication are permitted under the relevant data licenses.

If the WatchCharts series is too smooth or references too illiquid, do not enlarge the sample. Pivot effort toward a Chrono24 partnership or test the same pipeline on sneakers with a marketplace partner.

## Sources

[1] https://www.gq.com/gallery/2026-oscars-best-watches
[2] https://watchcharts.com/api/documentation
[3] https://watchcharts.com/api
[4] https://update.chrono24.com/market-scanner/
[5] https://about.chrono24.com/en/press/chrono24-launches-market-scanner-direct-access-to-marketplace-data-for-professional-dealers
