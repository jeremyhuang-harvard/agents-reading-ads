# Data-source map for implicit brand exposure in social video and images

**Assessment date:** October 15, 2026  
**Scope:** background logos/signage, celebrity- or athlete-worn products, product placement, ambassador content, sports clips, and other brand appearances that are not necessarily official paid ads.

## Bottom line

No official platform interface provides all four things needed for this project: broad discovery, lawful downloadable media, public exposure/impression counts, and a reliable sponsorship flag. The feasible design is a **linked-source system**:

1. use native platform APIs/research archives to discover public posts and obtain identifiers, dates, creators and public engagement/view metrics;
2. acquire media only through an expressly permitted route (controlled research environment, licensed archive/feed, creator/rights-holder permission, or a vendor contract);
3. run frame-level logo/product detection and human validation;
4. use partnership databases and disclosure signals to separate known paid relationships from incidental or undisclosed exposure; and
5. retain official ad libraries only as a paid-ad benchmark, not as the sampling frame for implicit exposure.

A post's cumulative views are an **opportunity-to-see proxy**, not a count of people who saw the logo. The defensible measurement unit is the detected appearance within a post/clip—brand, bounding box, timestamp interval, size, clarity, placement and duration—joined to the post's metric snapshot and source provenance.

## Source map

**Risk legend:** Low = licensed/official use within stated scope; Medium = contract/access limitations or unclear media-export rights; High = scraping/downloading/reuse outside an official or licensed route.

| Source | Unit and discoverability | Media access | Views/impressions | Sponsorship/disclosure signal | API/archive limits | Historical sampling | Lawful/terms risk | Best use |
|---|---|---|---|---|---|---|---|---|
| **TikTok Research API** | Public TikTok video and account. Query by keyword, hashtag, creator, region and date; returns description, create time, engagement, voice-to-text and other metadata.[1][3] | API returns metadata/IDs, not a documented bulk archive of reusable video files. Public page playback is not equivalent to permission to download/store media. | Public `view_count`, likes, comments, shares and favorites; cumulative platform counts, not logo-level impressions.[1][3] | No dependable field for whether a visible product/logo was sponsored. Caption/hashtags and visible native disclosure must be coded separately. | Eligible researchers only. Query windows are at most 30 days; up to 100 records/request; default limits are 1,000 requests and 100,000 records/day. Creator-video lookup is capped at the 100 most recent matching videos.[1][2] | **Yes, but constrained.** Date-bounded search can reach older content, while creator enumeration is not a complete account archive. Snapshot metrics because counts change. | **Medium.** Strong official discovery route; media copying and redistribution require separate review/permission. | Best official TikTok sampling frame for public implicit exposures and view-weighted prevalence after research approval. |
| **TikTok Commercial Content API / Library** | Paid ads plus creator-labelled commercial content. Commercial-content records can include the public video URL, creator, label type, advertiser and dates.[4][5] | Paid-ad endpoints can expose creative URLs; creator-commercial-content queries generally point to public TikTok pages/cover images rather than a guaranteed raw video archive. | Paid-ad reach is available in the ad library; creator-post public engagement can be linked where exposed. | Strong positive signal for content that used TikTok's commercial-content disclosure, but it cannot identify undisclosed sponsorships or incidental exposure. | Gated access; EU-first ad coverage; paid-ad retention is rolling. Existing project memo documents 10 ads/query, one-ad detail calls and a one-year date/retention constraint. | **Recent only for ads; partial for labelled creator content.** | **Low–Medium** within API terms; do not treat absence from the library as proof that a post was unpaid. | Gold-standard positive set for validating disclosure detection and distinguishing official ads from implicit appearances. |
| **Meta Content Library and API (Instagram/Facebook)** | Public posts, Reels and account content in a controlled research product. Search public content and retrieve engagement/creator/time variables.[6][7] | Content is available in Meta's controlled research environment; export and media handling are governed by the product's approved workflow, not open scraping. | Public engagement is available; public organic reach/impressions are generally not available for arbitrary third-party posts. | Captions, hashtags, tags and visible paid-partnership presentation can be coded; no assumption that all sponsorships are labelled. | Access is limited to qualified academic/nonprofit researchers through Meta's application/secure-environment process. Interface details and export controls can change. | **Yes.** This is the strongest official path to a historical public Instagram/Reels archive, subject to approval and controlled access. | **Low** inside the approved environment; **High** for independent automated scraping under Meta's Automated Data Collection Terms.[10] | Priority source for Instagram/Reels historical sampling and for estimating prevalence by creator/topic, even when reach is unavailable. |
| **Instagram Graph API / Insights** | Media belonging to professional accounts that authorize the application; not a general public-content discovery API. | Media URLs/metadata are available for authorized accounts under the API's permissions and expiry rules. | Media insights include views and interactions; metrics are organic for the documented media-insights fields and require account authorization.[8] | Account owners may expose branded-content/partnership workflow data, but the API is not a census of third-party ambassador posts. | Permission review, tokens and owned/authorized-account scope. Reels insights are not a substitute for public archive access. | **Yes for participating accounts**, bounded by the metrics' retention and authorization. | **Low** with creator/brand consent. | Best source for a recruited creator/ambassador panel with true account-side reach/view metrics. |
| **Meta Ad Library/API** | Official ads; keyword/Page/date/country searches. Ordinary commercial-ad API coverage is principally EU/UK, while political/social-issue coverage is broader.[9] | Text/metadata and an ad snapshot link; the documented API does not provide a stable bulk media-download endpoint. | Reach/impression ranges where applicable, not organic-post exposure. | Definitive that the item is an ad; no coverage of merely visible background brands in organic content. | Search-based, authorization required, rolling retention for ordinary EU commercial ads; not a random sample. | **Limited/rolling for ordinary ads.** | **Low** through API; **High** for scraping snapshot media without written permission.[10] | Negative/positive benchmark: remove known official ads or compare their creative treatment with implicit exposures. |
| **YouTube Data API (videos, including Shorts)** | Public video/Short. Search by keyword, channel, date, region and other filters; channel upload playlists allow efficient creator enumeration.[11][12] | Thumbnails and embeddable playback are supported. YouTube's developer policies prohibit downloading/storing audiovisual content without prior written approval.[14] | Public `viewCount`, likes and comments where available. A video's `hasPaidProductPlacement` field is documented in the video resource; it is creator-supplied and not a complete detector of sponsorship.[12] | Strongest native public disclosure variable among the major platforms, plus on-video disclosure and description/hashtag coding.[12][15] | Default quota is 10,000 units/day; `search.list` costs 100 units/call and returns at most 50 results, while `videos.list` costs 1 unit. Search pagination has practical caps for some channel/type combinations.[11] | **Yes—strong.** Public videos are date searchable and channel uploads can be enumerated; metric snapshots must be timestamped. | **Low for metadata/embeds; High for unapproved audiovisual downloads or offline frame archives.** | Best immediate, reproducible discovery pilot, especially for Shorts, athletes, celebrities and brand-relationship validation. Use manual/embedded review or licensed media for CV. |
| **YouTube Analytics API** | Video/channel reports only for an authenticated channel/content owner. | Does not itself grant rights to third-party video files. | Rich first-party views, engaged views, watch time, geography, traffic and audience dimensions.[13] | Can be joined to a creator's paid-placement declarations and campaign records. | Requires channel/content-owner authorization; not public competitor data. | **Yes for consenting channels.** | **Low** with consent. | Recruit a small ambassador/creator panel to calibrate public view counts against reach/watch-time and logo screen time. |
| **X API** | Post and media. Recent search covers seven days; full-archive search covers posts since 2006 with paid/approved access and advanced operators.[16] | Media entities/variants may be returned according to endpoint and access tier; storage, redistribution and display remain governed by X's developer agreement.[19] | Post public metrics include impression count and engagement; media metrics can include video views.[17] | X requires paid-partnership disclosure, but the documented search/metrics interfaces do not provide a reliable universal sponsorship classifier; use label/caption/UI coding.[18] | Access and cost are tier-dependent; recent search is seven days, full archive is a paid product, and API policies constrain redistribution/retention. | **Yes, excellent if full-archive access is purchased; otherwise prospective seven-day capture.** | **Medium.** Official API is feasible, but commercial pricing and content-display/retention rules need contract review. | Strong for athlete/celebrity posts, real-time sports moments and public impression weighting. |
| **Licensed sports/broadcast feeds + Relo Metrics** | Frame/segment within broadcast, stream or social sports content. Relo describes computer-vision measurement across broadcast, streaming and social, including exposure quality, duration and asset-level valuation.[20] | Contracted/licensed feed or vendor-hosted analysis. | Can combine detected logo exposure with audience/viewership datasets; methodology is vendor-defined rather than a platform raw metric. | Sponsorship roster/asset mappings help distinguish contracted inventory from incidental brands. | Commercial contract; coverage, exports, model auditability and underlying audience data must be negotiated. | **Yes if the vendor/feed license includes archive coverage.** | **Low–Medium** under contract. | Best turnkey route for background signage, uniforms, press backdrops and sports clips; request event-level detections, not only aggregate valuation. |
| **SponsorUnited** | Sponsorship deal, property, brand, asset and activation across teams, leagues, athletes, events and media.[21] | Usually metadata, examples and commercial intelligence—not a general raw-media archive. | Provides sponsorship/activation intelligence; do not assume platform-verified post impressions unless specifically included in the contract. | High-value ground truth for known brand-property/athlete relationships. | Commercial access; methodology, universe and historical depth are proprietary. | **Yes, contract-dependent.** | **Low–Medium** under license. | Partnership-label layer: identify likely ambassador/sponsor relationships and evaluate false negatives in native disclosure. |
| **Tubular DealMaker / social-video intelligence** | Creator, video, audience and inferred sponsorship relationship across major social-video platforms. DealMaker advertises sponsored-video search, sponsor/creator relationships and performance metrics.[22] | Platform/vendor interface; raw media and API export rights depend on contract. | Cross-platform public performance estimates/metrics; validate definitions against native counts. | Useful inferred/observed sponsorship graph, broader than explicit native labels. | Commercial, proprietary coverage and inference; request platform-by-platform history, update frequency and API fields. | **Yes, vendor-dependent.** | **Low–Medium** under contract. | Best single commercial discovery layer for creator-brand partnership candidates across YouTube, TikTok and Instagram. |
| **CreatorIQ** | Creator/account, campaign, post and relationship within an enterprise creator-marketing platform.[23] | First-party connected content and campaign assets for participating brands/creators; broader discovery data are vendor-controlled. | Strong campaign/owned-program measurement; public competitive metrics may be estimated or limited. | Direct campaign/creator relationship ground truth for customers; not a universal market archive. | Commercial access and customer-specific data permissions. | **Yes for customer campaigns; broader history contract-dependent.** | **Low** for consented campaign data. | Partner with a brand/agency to obtain verified ambassador rosters, contracts/disclosures and post-level campaign outcomes. |
| **Modash Discovery + Collaborations APIs** | Creator profiles and posts on Instagram, TikTok and YouTube; collaboration API is designed to find sponsored posts and brand/creator collaborations.[24][25] | Metadata/content references through commercial API; verify whether raw media bytes may be stored or processed. | Public post/follower/engagement data; not first-party impressions unless a creator authorizes them. | Explicit vendor product for collaboration/sponsored-post detection; remains an inference unless backed by native label or contract. | Commercial API, platform/plan coverage and historical depth must be tested in a sample export. | **Yes, contract-dependent.** | **Low–Medium** under license. | Lower-cost candidate for building an ambassador/post universe before native validation. |
| **Meltwater / Brandwatch-class social listening** | Mention/post/video indexed by keyword, account or brand across TikTok, Instagram, X, YouTube and other networks. Meltwater advertises speech-to-text for Instagram/TikTok and broad network coverage.[26] | Vendor-indexed media/transcripts/links; export and retention vary by platform contract. | Public engagement/view fields where licensed; usually not actual reach for arbitrary Instagram/TikTok posts. | Text/audio brand mention detection; weak for silent background logos unless visual analytics are explicitly included. | Proprietary firehose/partner coverage, query caps and export restrictions; exact completeness must be audited. | **Usually yes, with vendor-specific lookback.** | **Low–Medium** under contract. | Useful for candidate recall and spoken-brand mentions; not sufficient alone for visual background exposure. |
| **Hive Logo Detection API** | Image or sampled video frame; returns detected logo class, confidence and bounding region. Hive documents thousands of logo classes.[27] | Researcher supplies lawfully acquired media/frames; Hive is a detector, not a social-content source. | None; join detections to native/vendor view metrics. | None intrinsically. | Per-image/video pricing and model coverage; betting/prediction-market logos may need custom classes or validation. | **Yes for media the project can lawfully retain.** | **Low for the API; upstream media rights determine overall risk.** | Fast build-vs-buy benchmark for background logos, signage and apparel; validate on small/blurred/occluded marks. |
| **Getty Images API / AP Media API** | Licensed editorial photo/video item covering sports, entertainment, red carpets and public appearances.[28][29] | High-quality licensed media and metadata; AP states 30 days are available by API with deeper archives available separately.[28] | No social-platform impression count; use event/media reach proxies only if separately licensed. | Captions/credits identify subjects/events, not sponsorship; join to SponsorUnited/creator databases and visually code products. | Subscription/license, usage and retention terms; archive access differs from recent API access. | **Yes, especially via archive products.** | **Low** under an appropriate research/content license. | Best source for celebrity-worn products, press conferences, sideline apparel and high-resolution logo validation independent of social-platform scraping. |

## What each source can and cannot estimate

### Feasible outcomes

- **Appearance prevalence:** share of sampled posts/clips containing each brand.
- **Screen-time-weighted exposure:** visible seconds × post views, reported as an opportunity-to-see index rather than actual impressions.
- **Quality-adjusted exposure:** views × visible duration × logo area/clarity/centrality, with sensitivity analyses rather than a single opaque valuation.
- **Relationship-conditioned exposure:** prevalence and view-weighted exposure among known ambassadors/sponsored properties versus creators with no known relationship.
- **Disclosure gap:** detected brand appearances with native/hashtag disclosure, known partnership but no observed disclosure, and no known partnership.
- **Historical/event panels:** brand appearance around games, trades, launches, controversies or regulatory changes, provided discovery and media rights cover the period.

### Generally not feasible from public data alone

- exact unique people who saw a background logo;
- dwell time on the logo within an algorithmic feed;
- causal effect of the implicit appearance on betting/trading without experimental or first-party exposure data;
- proof that an unlabelled appearance was paid;
- a complete census of Instagram/TikTok content through ordinary public APIs;
- lawful bulk downloading merely because a video is publicly viewable.

The FTC expects material connections to be disclosed clearly and conspicuously, but disclosure presence is not a complete sponsorship ground truth: creators can omit it, relationships can be non-cash, and incidental background exposure may have no material connection.[30][31]

## Ranked pilot recommendation

### 1. Launch now: YouTube/Shorts metadata-first pilot

**Why first:** strongest combination of reproducible public discovery, deep historical sampling, stable IDs, public view counts, creator/channel enumeration and a native `hasPaidProductPlacement` field. It also provides a clean way to separate discovery from media rights.

**Pilot design (4–6 weeks):**

1. Define 100–200 seed entities: Kalshi, Polymarket, sportsbooks/casinos, relevant teams/leagues, athletes, celebrities and known ambassadors.
2. Pull a stratified sample of **3,000–5,000 public videos/Shorts** by creator, keyword and event/date; timestamp all metric snapshots.
3. Code a **500-item validation set** through embedded playback/manual frame review—do not download audiovisual content under the standard YouTube API terms.[14]
4. Record frame intervals, logo/product class, bounding box, prominence, apparel/signage/background role, spoken mention, description mention, `hasPaidProductPlacement`, #ad/#sponsored language and known partnership status.
5. Use SponsorUnited, Tubular DealMaker, Modash or a cooperating agency/brand to add a partnership graph for the same creators.[21][22][25]
6. Report unweighted prevalence and view-weighted opportunity-to-see separately. Cap/winsorize extreme view counts and preserve observation dates.
7. Seek YouTube written approval, creator permission or a licensed/vendor media route before scaling automated frame extraction.

### 2. Apply in parallel: TikTok Research API + Meta Content Library/API

These are the strongest official paths to TikTok and Instagram/Reels public-content research, but approval time and controlled-media rules make them slower than YouTube. Pre-register date/query/creator strata, because neither interface should be treated as a simple-random sample of the whole platform.[1][2][6][7]

- **TikTok target:** 5,000–10,000 video metadata records, stratified by 30-day windows and creator/keyword/hashtag; 500 manually reviewed items until a permitted media-processing route is confirmed.
- **Instagram target:** use Meta Content Library to reproduce the same creator/event strata and estimate appearance prevalence; use a recruited professional-account panel for actual Reels reach/views through Instagram Insights.[8]

### 3. Buy one narrow vendor proof of concept, not an enterprise suite immediately

Request the same **200 sports/athlete clips/posts** from Relo Metrics and one detector/provider (Hive or an in-house baseline). Require row-level outputs: source ID, frame timestamps, bounding boxes, confidence, duration, visibility/quality features, audience metric source and version. Compare precision/recall against blinded human coding before buying broad coverage.[20][27]

For relationship discovery, test **one** of Tubular DealMaker, Modash or SponsorUnited on the same seed list. The acceptance test is not dashboard polish; it is recall of known deals, post-level evidence, historical depth, exact export/API fields and permission to retain research extracts.[21][22][25]

### 4. Add X for event studies and Getty/AP for celebrity-worn products

Purchase X full-archive access only if the project has a defined historical event design; otherwise begin prospective seven-day capture now.[16] License a small Getty/AP sample for high-resolution sports/celebrity images to validate apparel and small-logo detection without relying on social-video downloading.[28][29]

### 5. Keep ad libraries as benchmarks

TikTok Commercial Content and Meta Ad Library are valuable for labelled/official paid-ad comparison sets, disclosure validation and advertiser dictionaries. They should not define the implicit-exposure universe because the target phenomenon often occurs outside official ad repositories.[4][5][9]

## Minimum procurement and access questions

For every commercial vendor or platform application, obtain written answers to:

1. Which platforms, countries and media types are included as of **October 15, 2026**?
2. Is the unit a post, video, frame, exposure event, deal or aggregate dashboard metric?
3. What exact historical start date and deletion/update policy apply?
4. Can the project export native post IDs, creator IDs, timestamps, URLs, frame timestamps, bounding boxes and confidence scores?
5. Are view/impression fields native, estimated or licensed from a third party, and at what observation time?
6. Does the contract permit academic retention, reproducibility, derived features, screenshots/keyframes and publication of aggregate results?
7. How are deleted/private posts handled?
8. Is sponsorship status observed from a native label/contract, inferred, or manually researched?
9. Can betting/prediction-market logos be added as custom classes, including wordmarks and on-screen UI?
10. Will the vendor provide a fixed 200-item evaluation export before a longer contract?

## Source dates and exact URLs

Pages without a stable published/updated date are marked with the exact access date rather than an invented publication date.

- TikTok Query Videos — updated **September 1, 2026**: https://developers.tiktok.com/docs/en/research-api-specs-query-videos
- TikTok Research API FAQ — updated **September 1, 2026**: https://developers.tiktok.com/docs/en/research-api-faq
- TikTok Research API Codebook — updated **September 1, 2026**: https://developers.tiktok.com/docs/en/research-api-codebook
- TikTok Commercial Content API — accessed **October 15, 2026**: https://developers.tiktok.com/products/commercial-content-api
- TikTok Query Commercial Content — accessed **October 15, 2026**: https://developers.tiktok.com/doc/commercial-content-api-query-commercial-content?enter_method=left_navigation
- Meta Content Library and API overview — accessed **October 15, 2026**: https://transparency.meta.com/researchtools/meta-content-library/
- Meta Content Library developer documentation — accessed **October 15, 2026**: https://developers.facebook.com/docs/content-library-and-api/
- Instagram Media Insights — accessed **October 15, 2026**: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-media/insights
- Meta Ad Library API — accessed **October 15, 2026**: https://www.facebook.com/ads/library/api/
- Meta Automated Data Collection Terms — effective **January 1, 2025**: https://www.facebook.com/legal/automated_data_collection_terms
- YouTube `search.list` — updated **August 28, 2025**: https://developers.google.com/youtube/data/reference/rest/v3/search/list
- YouTube Video resource — updated **October 8, 2026**: https://developers.google.com/youtube/data/reference/rest/v3/videos
- YouTube Analytics API reference — updated **August 28, 2025**: https://developers.google.com/youtube/analytics/reference/
- YouTube API Services Developer Policies — updated **September 24, 2025**: https://developers.google.com/youtube/terms/developer-policies
- YouTube paid product placements/help — accessed **October 15, 2026**: https://support.google.com/youtube/answer/154235
- X Search Posts introduction — accessed **October 15, 2026**: https://docs.x.com/x-api/posts/search/introduction
- X Metrics — accessed **October 15, 2026**: https://docs.x.com/x-api/fundamentals/metrics
- X Paid Partnerships Policy — accessed **October 15, 2026**: https://help.x.com/en/rules-and-policies/paid-partnerships-policy
- X Developer Agreement and Policy — effective **May 15, 2026**: https://developer.x.com/en/developer-terms/agreement-and-policy
- Relo Metrics — accessed **October 15, 2026**: https://relometrics.com/
- SponsorUnited Platform — accessed **October 15, 2026**: https://www.sponsorunited.com/platform
- Tubular DealMaker — accessed **October 15, 2026**: https://tubularlabs.com/products/dealmaker/
- CreatorIQ — accessed **October 15, 2026**: https://www.creatoriq.com/
- Modash Influencer Marketing API — accessed **October 15, 2026**: https://www.modash.io/influencer-marketing-api
- Modash Collaborations API — accessed **October 15, 2026**: https://www.modash.io/influencer-marketing-api/collaborations-api
- Meltwater global content coverage — accessed **October 15, 2026**: https://www.meltwater.com/en/platform/global-content-coverage
- Hive Logo Detection — accessed **October 15, 2026**: https://docs.thehive.ai/docs/logo-detection
- AP Media API — accessed **October 15, 2026**: https://developer.ap.org/ap-media-api/
- Getty Images API — accessed **October 15, 2026**: https://www.gettyimages.com/api
- FTC Disclosures 101 for Social Media Influencers — published **November 5, 2019**: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- FTC Advertisement Endorsements — updated **June 20, 2024**: https://www.ftc.gov/news-events/topics/truth-advertising/advertisement-endorsements

## Sources

[1] https://developers.tiktok.com/docs/en/research-api-specs-query-videos
[2] https://developers.tiktok.com/docs/en/research-api-faq
[3] https://developers.tiktok.com/docs/en/research-api-codebook
[4] https://developers.tiktok.com/products/commercial-content-api
[5] https://developers.tiktok.com/doc/commercial-content-api-query-commercial-content?enter_method=left_navigation
[6] https://transparency.meta.com/researchtools/meta-content-library
[7] https://developers.facebook.com/docs/content-library-and-api
[8] https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-media/insights
[9] https://www.facebook.com/ads/library/api
[10] https://www.facebook.com/legal/automated_data_collection_terms
[11] https://developers.google.com/youtube/data/reference/rest/v3/search/list
[12] https://developers.google.com/youtube/data/reference/rest/v3/videos
[13] https://developers.google.com/youtube/analytics/reference
[14] https://developers.google.com/youtube/terms/developer-policies
[15] https://support.google.com/youtube/answer/154235
[16] https://docs.x.com/x-api/posts/search/introduction
[17] https://docs.x.com/x-api/fundamentals/metrics
[18] https://help.x.com/en/rules-and-policies/paid-partnerships-policy
[19] https://developer.x.com/en/developer-terms/agreement-and-policy
[20] https://relometrics.com
[21] https://www.sponsorunited.com/platform
[22] https://tubularlabs.com/products/dealmaker
[23] https://www.creatoriq.com
[24] https://www.modash.io/influencer-marketing-api
[25] https://www.modash.io/influencer-marketing-api/collaborations-api
[26] https://www.meltwater.com/en/platform/global-content-coverage
[27] https://docs.thehive.ai/docs/logo-detection
[28] https://developer.ap.org/ap-media-api
[29] https://www.gettyimages.com/api
[30] https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
[31] https://www.ftc.gov/news-events/topics/truth-advertising/advertisement-endorsements
