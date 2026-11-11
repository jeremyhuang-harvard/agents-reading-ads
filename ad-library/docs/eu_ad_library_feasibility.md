# Feasibility of an EU advertising-library pilot

**Assessment date:** October 8, 2026  
**Target:** A reproducible corpus of approximately 2,000–2,500 advertisements for GABRIEL-based image, video, text, and metadata analysis

## Executive verdict

**The pilot is feasible, but there is no single general-purpose “EU Ad Library.”** The Digital Services Act requires covered very large platforms and search engines to operate their own advertising repositories. The European Commission's DSA Transparency Database is a different system concerned with platforms' content-moderation decisions, not a central archive of commercial advertisements.[1][3]

The recommended sequence is:

1. **Begin immediately with Microsoft/Bing** for a 100-ad image/text technical pilot. Its public API worked without authentication in a live test on October 8, 2026 and returned structured ad records plus direct image URLs.[12]
2. **Apply immediately for TikTok Commercial Content API access.**
   TikTok is the strongest documented source for a later video-rich corpus and supplies creative URLs, targeting, reach, advertiser, payer, and destination fields.[4][5][16]
   Access is gated through an application process.[13]
3. **Use Meta as a metadata/text comparison source, not the sole multimodal source.** Meta supports ordinary EU commercial-ad queries, but its documented API supplies an ad snapshot URL rather than direct original image/video download fields.[8][19][20]
4. Treat Google as a parallel contingency after validating its access and media-download workflow; its transparency system is broad, but the immediate collection path is less straightforward than the Bing endpoint.[10]

The full 2,000–2,500-ad pull should begin only after a 100-ad shakedown establishes media-download success, query reproducibility, deduplication behavior, metadata completeness, and acceptable source terms.

## 1. What “EU ad library” actually means

Article 39 of the DSA creates a **provider-by-provider system**. Covered platforms must make advertisements searchable and provide information including the advertisement itself, payer and beneficiary, delivery period, major targeting criteria, and aggregate recipient information. Records must remain available for one year after the advertisement was last shown.[1]

The European Commission has also adopted harmonized repository templates and API expectations intended to make cross-platform research more comparable. Platform implementations still differ substantially in authentication, searchable fields, media access, pagination, and completeness, and the Commission has continued to negotiate platform-specific compliance commitments.[2][3][9]

This distinction matters for the research design. A corpus from Microsoft is a **Microsoft/Bing EU advertising corpus**, and a corpus from TikTok is a **TikTok EU commercial-content corpus**. Neither should be described as a representative census of all EU advertising.

## 2. Ranked source assessment

### A. Microsoft/Bing — recommended first pilot

**Verdict: GO for an immediate creative-focused pilot.**

Microsoft operates a Bing advertising library for EU advertisements and exposes a public API.[11][12] A live anonymous request to the official endpoint on October 8, 2026 returned HTTP 200 and structured JSON records containing:

- ad and advertiser IDs;
- advertiser name;
- title and description;
- display and destination URLs;
- an `AssetJson` field containing direct image URLs, dimensions, and asset type.

The live probe confirms that a collector can retrieve real creative assets without first completing an account or token-approval process. This makes Bing the fastest way to establish the raw-media → GABRIEL → analysis pipeline.

Important limitations:

- One record can contain many assets, so “advertisement,” “creative bundle,” and “asset” must remain separate units.
- The tested listing representation did not expose the full set of Article 39 targeting, payer, country-reach, or exposure fields alongside the creative.
- Broad pagination appears constrained, so the sample should be assembled from multiple declared query strata rather than one unfiltered walk.
- Bing inventory and format mix are not representative of the entire EU advertising market.

**Recommended use:** prove image download, hashing, bundling, OCR, GABRIEL measurements, deduplication, and plotting. Do not yet make strong claims about targeting or population exposure.

### B. TikTok — best documented multimodal production candidate

**Verdict: CONDITIONAL GO, pending approved credentials and a live test.**

TikTok's Commercial Content API is specifically designed to expose EU paid-ad data to outside users. Its query and detail endpoints document direct video and image URLs, caption and call-to-action fields, advertiser and payer identity, landing destinations, campaign objective, delivery dates, targeting criteria, and reach breakdowns.[4][5][6]

The API is highly suitable for the substantive project because it supports the relationship between creative content, intended audience, geography, and observed reach. It is also the strongest source for native short-form video.

Operational constraints include:

- an application and approval process;[13][14]
- client-credentials authentication and expiring access tokens;[15]
- a maximum of 10 paid ads per query response;[5]
- one-ad-at-a-time detail retrieval;[16]
- no documented gambling-category or random-sampling filter;
- no published Commercial Content API quota;
- potentially temporary signed media URLs that should be downloaded immediately.

At the documented page sizes, 2,000 ads require at least about 200 query calls plus 2,000 detail calls; 2,500 require about 250 query calls plus 2,500 detail calls, before retries and media downloads.

**Recommended use:** apply now, then run a 100-ad credentialed pilot. Promote TikTok to the principal source if media retrieval and throttling are acceptable.

### C. Meta — feasible for breadth and metadata, weaker for direct media

**Verdict: CONDITIONAL GO for metadata/text; not recommended as the sole multimodal source.**

Meta's Ad Library API can query ordinary commercial ads delivered in EU countries and provides creative text, advertiser/Page identity, dates, delivery information, demographics or regional information where available, payer/beneficiary fields, media type, and an `ad_snapshot_url`.[7][8][19]

Access requires Meta identity/location verification, a developer account/application, and an access token.[20] The documented API field surface does not supply stable direct image/video file URLs. Automated extraction from snapshot pages is not the normal documented API route and must be considered against Meta's automated-collection terms.[19][21]

**Recommended use:** cross-platform advertiser matching, ad text, delivery metadata, and comparison samples after API access is approved. Make stable, authorized creative acquisition a separate go/no-go test.

### D. Google and other repositories

Google's Ads Transparency Center covers ads from verified advertisers and provides geographic and advertiser-centered search.[10] It should be investigated in parallel as a potentially broad production source, but its account, API, download, quota, and dynamic-creative behavior should be tested on 100 ads before inclusion.

Snap is promising where a known advertiser list exists. X and AliExpress provide public-facing repositories, but no comparably clear bulk research API was verified during this audit. They should not be the first implementation target.

## 3. Recommended 2,000–2,500-ad design

### Stage 0: Define the unit of analysis

Store and distinguish:

- `repository_ad_id`: the platform's ad record;
- `creative_version_id`: the immutable bundle of copy and media assets;
- `asset_id`: SHA-256 of exact image, video, audio, or document bytes;
- `advertiser_id`: source-native plus canonical research entity;
- `query_stratum_id`: the exact inclusion rule that found the ad.

A responsive ad with 12 images is one repository record, one or more possible creative bundles, and 12 assets—not simply “one image ad.”

### Stage 1: 100-ad Bing shakedown

Collect 100 records across several EU countries, advertisers, dates, and search terms. Acceptance gates:

- at least 95% successful permitted media downloads;
- stable source IDs and reproducible requests;
- complete request and cursor logging;
- exact media hashes and MIME validation;
- understood handling of records with several assets;
- documented metadata coverage and missingness;
- successful GABRIEL processing for image/text bundles;
- no dependence on browser scraping or bypassing technical controls.

### Stage 2: Source-specific full sample

If Bing passes, collect 2,000–2,500 unique records using predeclared country × date × advertiser/keyword strata. Pull more candidate records than the target because duplicates, missing assets, and overlapping queries will reduce the usable sample. For TikTok expansion, explicitly restrict collection to the supported EU member-state codes rather than assuming that the broader regional list is EU-only.[18]

Use two arms:

- **Vice-enriched arm:** gambling, sportsbook, casino, poker, slots, lottery, alcohol, nicotine, and relevant advertiser/domain terms in local languages.
- **Background arm:** a broad non-vice comparison sample from the same platform, countries, dates, and media formats.

Cap the contribution from dominant advertisers and preserve inclusion weights or stratum shares. Classify gambling/vice status after collection using advertiser identity, destination domain, copy, OCR, ASR, and visual content; keyword hits are candidate generation, not ground truth.

### Stage 3: TikTok modality expansion

After approval, repeat the shakedown with 100 TikTok ads. Download video/image assets immediately and preserve the query JSON, detail JSON, source URL, retrieval time, HTTP response, MIME type, byte count, and SHA-256. Use TikTok's reach and targeting data for richer descriptive analyses.[5][16][17]

### Stage 4: GABRIEL measurement and validation

Freeze approximately 30 attributes after reviewing a stratified development sample. Use low-cost multimodal models for screening and routine measurement; route conflicts, missing evidence, and high-stakes cases to a stronger model or human review.

Before interpreting the full corpus:

- double-code a blinded human validation sample;
- retain per-run model outputs;
- estimate binary classification error, rating reliability, and evidence support;
- audit errors by country, language, advertiser, and media format;
- distinguish missingness from observable absence;
- publish descriptive findings with source-specific sampling limitations.

## 4. Main feasibility risks

1. **Access is not a copyright licence.** Keep raw creatives access-controlled and avoid redistributing them without review.
2. **Platform terms differ.** Prefer explicitly documented APIs; do not bypass login, CAPTCHAs, rate limits, or technical restrictions.
3. **One-year retention creates urgency.** Preserve lawful raw records and assets promptly because ordinary ad records may roll out of the repositories.[1]
4. **Media links may expire.** Download during ingestion and retain checksums and provenance.
5. **Dynamic ads complicate measurement.** Decide whether the analytic object is the repository record, asset, possible rendering, or campaign.
6. **The sample is platform-specific.** Results should not be generalized to “EU advertising” without additional platforms or explicit reweighting assumptions.
7. **Gambling recall is not automatic.** Keyword sampling will miss brand-only and visually coded ads and will include false positives.
8. **Exposure is not individual treatment.** Repository reach or targeting fields do not identify which specific user saw an advertisement.
9. **Personal-data and ethics review may apply.** Faces, handles, advertiser identities, targeting descriptions, and first-party joins require minimization and controlled access.

## Decision

**Proceed.** The EU repository concept is sufficiently real and technically accessible to support the proposed pilot, but the implementation should not begin by trying to integrate every platform.

The concrete path is:

1. implement a Bing collector and 100-ad validation run now;
2. submit the TikTok Commercial Content API application now;
3. scale Bing to 2,000–2,500 records only if the shakedown passes;
4. use TikTok as the preferred video/targeting expansion after approval;
5. defer Meta multimodal ingestion until direct, authorized creative acquisition is validated.

## Sources

[1] https://digital-strategy.ec.europa.eu/en/policies/dsa-brings-transparency — DSA brings transparency
[2] https://digital-strategy.ec.europa.eu/en/news/commission-harmonises-templates-advertising-transparency-very-large-online-platforms-under-digital — Commission harmonises templates for advertising transparency
[3] https://digital-strategy.ec.europa.eu/en/library/study-development-ad-repositories-online-platforms — Study on the development of ad repositories
[4] https://developers.tiktok.com/products/commercial-content-api — TikTok Commercial Content API
[5] https://developers.tiktok.com/doc/commercial-content-api-query-ads — TikTok Query Ads
[6] https://developers.tiktok.com/doc/commercial-content-api-query-ad-details — TikTok Query Ad Details
[7] https://www.facebook.com/ads/library — Meta Ad Library
[8] https://www.facebook.com/ads/library/api — Meta Ad Library API
[9] https://digital-strategy.ec.europa.eu/en/news/commission-accepts-tiktoks-commitments-advertising-transparency-under-digital-services-act — Commission accepts TikTok advertising transparency commitments
[10] https://support.google.com/adspolicy/answer/10350337?hl=en — Google Ads Transparency
[11] https://www.about.ads.microsoft.com/en/blog/post/june-2023/making-microsoft-advertising-safer-with-advertiser-identity-verification — Microsoft Advertising: Bing EU Ad Library
[12] https://adlibrary.api.bingads.microsoft.com/api/v1/Ads — Microsoft/Bing Ad Library API
[13] https://developers.tiktok.com/application/commercial-content-api — TikTok Commercial Content API application
[14] https://developers.tiktok.com/docs/en/commercial-content-api-getting-started — TikTok Commercial Content API getting started
[15] https://developers.tiktok.com/docs/en/client-access-token-management — TikTok client access token management
[16] https://developers.tiktok.com/docs/en/commercial-content-api-get-ad-details — TikTok get ad details
[17] https://developers.tiktok.com/docs/en/commercial-content-api-get-ad-report — TikTok get ad report
[18] https://developers.tiktok.com/docs/en/commercial-content-api-supported-countries — TikTok supported countries
[19] https://www.facebook.com/ads/library/api/fields — Meta Ad Library API fields
[20] https://www.facebook.com/ads/library/api/get-started — Meta Ad Library API getting started
[21] https://www.facebook.com/legal/automated_data_collection_terms — Meta automated data collection terms
