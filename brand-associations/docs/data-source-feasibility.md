# Celebrity–brand appearance, relationship, amplification, and outcome panels

**Current assessment: November 2026.** This is an engineering and published-terms assessment, not a legal opinion. “Retain” below means the source’s published access/licensing model supports research retention under the stated conditions; copyright, privacy, publicity-right, and contract review is still needed. Preserve `unknown` when a commercial relationship is not affirmatively evidenced.

## Bottom line

A 100–500-event panel is feasible without a platform partnership if the core is **official YouTube posts + Wikidata/Wikipedia + GDELT/Media Cloud/Guardian + Common Crawl + manually verified disclosures**, with media stored only when openly licensed or separately licensed.[1][4][6]
Common Crawl supplies a separate historical-web layer.[7]
Add **Meta Content Library, TikTok Research API, and Reddit for Researchers** only as approved extensions; none should be on the critical path.[10][12][15]
Google Trends is useful but its official API remains application-only alpha.[9]

Build four linked tables rather than one ad/non-ad label:

1. `appearance`: literal person–brand–asset episode, timestamp, geometry/duration, source and evidence;
2. `relationship`: sponsorship, ambassadorship, gifting, affiliate, ownership, or explicit disclosure evidence;
3. `amplification`: reposts, comments, news, fashion-ID, affiliate, and brand follow-on links;
4. `outcomes`: platform engagement snapshots, Wikipedia pageviews, search interest when available, news volume, and product price/availability.

## Source feasibility matrix

| Source / route | Panel role and concrete route | Retention and reproducibility | Stable IDs / linkage | Quota / access | Main blocker |
|---|---|---|---|---|---|
| **YouTube Data API v3** | Best public official-post backbone. Enumerate known celebrity/brand channels; retrieve uploads, video metadata, descriptions, captions where authorized, comments, and repeated engagement snapshots. `videos.list` exposes `paidProductPlacementDetails.hasPaidProductPlacement`, view/like/comment counts, channel ID, and video ID.[1] | Retain IDs, request manifests, coded features, and refreshed metadata. API policy generally requires non-authorized data to be deleted or refreshed within 30 days; do not archive video files via the API—embed or separately license them.[3] | Strong: video ID, channel ID, comment/thread IDs. | Default allocation is 10,000 units/day for most endpoints; current quota documentation separately limits `search.list` to 100 calls/day. `videos.list` is cheap; search is the bottleneck.[2] | Discovery by broad search is quota-constrained; deleted/private videos; policy limits on long-lived raw API data and derived metrics. |
| **Official X posts / X API** | Useful for official celebrity and brand announcements, quote posts, repost chains, and timestamps. Use known account IDs and post lookup/timelines rather than broad scraping. | Keep post/user IDs, URLs, timestamps, and compliant snapshots; media retention needs the content owner’s license and deletion handling. Avoid browser scraping as a reproducible primary route. | Strong post and user IDs. | Developer account; read access is paid and pricing/limits have changed repeatedly.[27] | Cost and policy volatility; historical/full-archive search tiering; deleted posts and media rights. |
| **Instagram standard API** | Only for accounts that authorize the app and are Business/Creator accounts; useful for a cooperating brand/celebrity, not general public-account collection.[18] | Retention governed by Meta Platform terms; safest durable layer is IDs, URLs, timestamps, disclosure flags, coded features, and periodic refresh—not downloaded media. | IG media ID and professional account ID, but some identifiers are app-scoped. | App review, permissions, account authorization, Business Use Case rate limits. | Cannot provide general access to arbitrary celebrity personal accounts. |
| **Meta Content Library/API** | Strongest research route for public Facebook/Instagram content, account/post search, engagement, comments, and multimedia inspection.[15] | Controlled environment. API data cannot be exported from the secure research environment; a defined public-data subset can be downloaded through the UI only with ICPSR/CASD approval and contract. Snapshot Mode can preserve certain statistical results for up to one year.[30] | Meta post/account IDs and URLs; suitable for linkage inside the environment. | Application and independent review. 60 synchronous calls/minute, 1 async call/minute, and 500,000 retrieved records per rolling 7 days per researcher.[16] | Approval time, secure-environment/export restrictions, eligibility, and incomplete coverage of smaller/nonpublic accounts. |
| **TikTok Research API** | Public videos/accounts, captions/descriptions, hashtags, voice-to-text, `video_label`, repost/pinned/liked lists, and view/like/comment/share counts. Query by username, keyword, hashtag, or video ID.[12][29] | Retain only as permitted by the approved research terms; the API provides metadata rather than a blanket license to archive videos. Store video IDs, URLs, returned fields, manifests, and derived coding; treat media as controlled/temporary unless separately licensed. | Strong numeric video ID, username, music/effect/playlist IDs. | Vetted academic/nonprofit research, application and ethics evidence. 1,000 requests/day and up to 100,000 records/day; reset at 00:00 UTC.[13] | Approval/eligibility, noncommercial research limitation, deleted content, and no general media-archive license. |
| **Reddit for Researchers (RFR)** | Amplification and identification discussions, e.g. brand/fashion identification and reaction threads. Use RFR, not the ordinary Data API, for academic research.[10] | Secure, privacy-first access; no deanonymization. Retain/export only as approved. Ordinary Data API terms give a limited, revocable license and require removals; user content remains owned by users.[11] | Submission, comment, subreddit, and account IDs. | Accredited-university affiliation, PI/application, explicit approval. | The normal developer API is not an authorized academic-research workaround; approval and privacy/output controls. |
| **Wikidata + MediaWiki APIs/dumps** | Canonical celebrity/brand entity table: QIDs, aliases, occupations, brand ownership, official websites, social identifiers, and article mappings. Live probe mapped Taylor Swift page ID `5422144` to Wikidata `Q26876`. | Metadata is reproducibly retainable under Wikimedia licenses; keep dump date and revision ID. | Excellent: Wikidata QID, page ID, revision ID. | Public; identify the client and use polite batching. Full dumps are large but available with checksums. | Entity-resolution errors, incomplete qualifiers/dates, and community-edited claims. |
| **Wikimedia Commons** | Openly licensed portraits, logos, event photography, and product/brand images for legally retainable media exemplars.[5] | Yes, file-by-file subject to the stated license, attribution, share-alike, personality/privacy, and trademark constraints. Save file page, license, author, revision, and checksum. | Commons file title, page ID, revision ID, SHA1. | Public API/dumps. | Coverage is selective; license and personality-right review is still per asset. |
| **Wikimedia Analytics/Pageviews API** | Low-cost daily outcome panel for celebrity and brand attention. Live probe returned daily Taylor Swift article views for October 1–7, 2026.[4] | Aggregate metrics can be retained with query manifests. | Article title/project/time; link through page ID/QID while handling page moves. | Public; no key for the REST route used in the probe. | Page-title moves, language fragmentation, bots/automated-agent definitions, and attention is not sales. |
| **GDELT 2.0 / DOC / Events / Mentions / GKG** | News discovery, volume, geography, tone, organization/person co-mentions, and article URLs. Use DOC for bounded discovery and raw 15-minute files/BigQuery for reproducible bulk work.[6] | GDELT metadata is free/open; underlying publisher article text/images are not relicensed. Retain GDELT records, URLs, dates, query manifests, and coded features—not copied publisher media. | `GLOBALEVENTID` for event records; article URL and GKG record identifiers for mentions. | Public/free, but operational rate limits are not clearly documented. A live DOC probe received HTTP 429. | Duplicate/syndicated stories, noisy entity matching, changing article URLs, undocumented throttling, and no article-content license. |
| **Media Cloud** | Research-friendly news index for story URLs, dates, source IDs, and attention/word aggregates; useful independent check on GDELT. | Story text is searchable internally but explicitly unavailable for download because of copyright; metadata/URLs are downloadable.[20] | Story ID is a hash of normalized URL; source ID/domain. | Public research service/API; practical rate limits may require coordination. | Source coverage starts when feeds/sitemaps were ingested; no downloadable full text. |
| **Guardian Open Platform** | Concrete licensed news/archive route for celebrity/fashion coverage and amplification. Search by query/date/tag; optionally request article body. | Developer key allows noncommercial use and article text subject to terms; commercial/text-mining uses require a commercial license.[21] | Guardian content ID and canonical URL. | Free noncommercial: 1 request/sec, 500/day; commercial custom quota/pricing.[21] | Single-publisher selection and license boundary for commercial work. |
| **NewsAPI** | Fast current-news discovery across many sources; use as URL lead generator, not the archive of record. | Retain returned metadata under plan terms; article content is usually truncated/linked and publisher rights remain. | Source ID plus URL; no universal cross-publisher content ID. | Free developer tier: 100 requests/day, 24-hour delay, only one month of history, development/testing only; production starts paid.[28] | Expensive production plans, shallow history on free tier, deduplication, and no media license. |
| **Common Crawl WARC + CDXJ/URL Index** | Historical recovery of official websites, press releases, fashion pages, disclosure text, deleted landing pages, and affiliate pages. Public collection index reported `CC-MAIN-2026-43` for October 2026 in a live probe.[7] | Reproducibly retain WARC coordinates, payload digest, crawl ID, headers, and derived text. Common Crawl access does not erase underlying copyright/privacy restrictions; raw republishing requires separate justification.[8] | Crawl ID + WARC filename/offset/length + payload digest + URL/timestamp. | Free; no normal per-request quota, but wildcard index queries can be computationally heavy. Live exact/domain queries timed out with HTTP 504. | Sparse/uneven captures, robots/opt-outs, dynamic/social pages, duplicate content, and underlying rights. |
| **Google Trends** | Outcome series for celebrity, brand, and product search interest, ideally by geography and event window. | Official API output should be versioned and retained under alpha terms; avoid relying on undocumented web endpoints or `pytrends` for a reproducible long-run panel. | Google Knowledge Graph topic IDs where available; query strings otherwise unstable/ambiguous. | Official API is still alpha and application-only; public docs do not provide a general quota.[9] | Access uncertainty, sampling/scaling changes, low-volume zeros, geography/topic ambiguity. |
| **Getty Images API / licensed editorial archives** | High-quality paparazzi/red-carpet/editorial appearance discovery with photographer, event, caption, date, and image IDs.[22] | Metadata under contract; image/video only after licensing. Preserve license receipt/allowed use and asset ID. | Strong Getty asset IDs. | API key and commercial relationship; Getty directs users to an account representative for access/licensing.[22] | Payment, rights-managed restrictions, no blanket research redistribution, and editorial-caption error. Shutterstock/AP editorial routes are similar partnership/licensing products. |
| **Fashion identification sites: WornOnTV, Spotern, ShopYourTV, Steal Her Style** | Secondary identification/amplification layer: celebrity/show/person, episode/post, garment brand/model, retailer and affiliate link. Use targeted manual coding or obtain permission/data partnership. | Retain citations, URLs, claimed identification, retrieval time, and your verification outcome. Do not mirror screenshots/text/products: site materials are copyrighted and no stable public research API is offered.[23] | Usually page URL/slug only; retailer SKU/GTIN/MPN when present. | Public web pages, but no documented bulk API; crawling must respect terms/robots and server load. | Copyright/ToS, affiliate-link churn, unverified crowd identifications, redesigns, and weak IDs. |
| **Direct paparazzi/tabloid sites** | Discovery of candid appearances and dates through RSS/sitemaps, publisher search, GDELT/Media Cloud, or Common Crawl; use canonical URL as evidence. | Retain metadata, quoted facts within fair-use limits, and hashes/manifests. Do not retain/republish full photos without a license; license from Getty/AP/Shutterstock/agency when needed. | Canonical URL, publisher article ID when exposed, image agency/asset ID when captioned. | Site-specific; often paywalls, anti-bot controls, no API. | Highest legal and reproducibility risk: copyright, publicity/privacy, robots/WAF, changing pages, and syndication. |
| **eBay Browse API** | Outcome/commerce layer for product availability, asking price, condition, seller geography, image search, and affiliate URL. Good for discontinued fashion items.[24] | Retain item IDs and timestamped price/availability facts; refresh active listings and follow eBay API/affiliate display and caching terms. Do not treat seller images as freely reusable. | eBay REST item ID, legacy item ID, GTIN/EPID where present. | Developer key/OAuth; production access and call limits are app-specific. Affiliate commission requires eBay Partner Network links.[24] | Listing turnover, selection into resale, counterfeit/misidentified goods, and caching/display constraints. |
| **Amazon Creators/PA API** | Product metadata, ASIN, price/availability, images, and affiliate links when products can be matched. | Highly constrained: Program Content is licensed only under Associates/API specifications; scraping/data mining is prohibited and content must be refreshed as required.[25] | ASIN is strong within Amazon marketplace. | Associates enrollment and API eligibility; call capacity depends partly on qualifying shipped revenue. | Not a neutral research API, strict display/caching terms, sales-performance gating, and no historical price archive. |
| **Meta Ad Library API** | Relationship/amplification check for paid campaigns and partnership ads. Search by advertiser/page and creative text; capture Library ID, page ID, dates, platforms, and creative link. | Retain API metadata and IDs under platform terms; creative retention/republication remains subject to terms/copyright. | Ad Library ID, Page ID, beneficiary/payer fields. | Developer account/app. Coverage: political/issue ads worldwide for seven years; all ad types delivered in UK/EU for the past year.[17] | Not a complete global commercial-ad archive; ranges rather than exact spend/impressions in many cases; creative URLs may expire/change. |
| **TikTok Commercial Content API** | Search ads and other commercial content by advertiser/keyword; captures advertiser, targeting and ad metadata.[14] | Metadata retention under approved API terms; do not assume a license to archive creatives. | Ad/commercial-content and advertiser IDs. | Application/client credentials. TikTok states ads remain available while running and for one year after last shown; query endpoints page at up to 50 records. | Geographic/field coverage varies (many detailed routes focus on EEA), approval, one-year retention horizon, and media rights. |
| **Snap Ads Gallery API** | Particularly feasible ad-transparency source: EU ads from the last 12 months plus currently live organic commercial content; search by paying advertiser, dates, country and status.[31] | Retain returned metadata/IDs and manifests; creative media still needs terms/licensing review. | Ad/advertiser IDs from API response. | Public endpoints are documented as open to third parties and do not require OAuth.[32] | EU/12-month scope, repository is not proof of individual exposure, and creative-link durability. |
| **Google Ads Transparency Center** | Manual advertiser/creative confirmation across Search, Display, Gmail and YouTube; political archive is also searchable.[26] | Retain identifiers, URLs, dates and coded attributes under Center terms; do not bulk-copy creatives without permission. | Advertiser/creative IDs visible in URLs. | Public UI. Google states API access exists for EEA-served ads, but general public API documentation/access is not comparable to Snap’s open route.[26] | No robust general-purpose public API, UI automation fragility, regional restrictions, and terms. |
| **FTC/platform disclosures** | Relationship evidence: `#ad`, “paid partnership,” TikTok content-disclosure labels, YouTube paid-promotion flag, affiliate statements, and contract/press-release evidence. FTC guidance defines material connections broadly, including payment, free products, employment and family relationships.[19] | Retain disclosure text, location, timestamp, screenshot only where justified, and source URL; separately code “disclosure observed” from “relationship exists.” | Link to source post/video/ad IDs. | Public guidance; disclosure observations come from the underlying platform routes. | Under-disclosure, edited captions, labels not exposed in every API, and absence is not evidence of organic use. |

## Minimal feasible stack for 100–500 events

### A. No-approval MVP (recommended starting point)

1. **Event seed and official evidence:** 100–300 YouTube videos from a fixed list of verified celebrity and brand channels; add official press releases/web posts. Use `videos.list` for metadata, paid-placement flag and engagement snapshots; minimize `search.list` by using known channel upload playlists.[1][2]
2. **Entity backbone:** Wikidata QIDs for every celebrity, brand, product and parent company; store aliases and date-qualified relationships. Use Wikimedia page IDs/revisions for reproducibility.
3. **Appearance coding:** Store source IDs/URLs and deterministic media derivatives only when allowed. For durable raw media, use Wikimedia Commons or licensed Getty/AP/Shutterstock assets. Otherwise embed the source and retain frame/time coordinates, human labels, model version and cryptographic hashes rather than redistributing the file.[5][22]
4. **Relationship ledger:** YouTube paid-product-placement field, on-post disclosure language, brand/celebrity press releases, affiliate links, and Ad Library matches. Code `confirmed_paid`, `confirmed_gifted`, `affiliate`, `ambassador`, `ownership`, `no_disclosure_observed`, and `unknown` separately.[1][17][19]
5. **Amplification:** GDELT raw/BigQuery records plus Media Cloud URLs and Guardian API for a licensed full-text slice.[6][20][21]
   Use YouTube comments and brand follow-on videos plus Common Crawl for historical/deleted web pages.[1][7]
6. **Outcomes:** daily Wikipedia pageviews and repeated YouTube statistics at fixed lags (for example +1, +3, +7, +30 days), plus news counts.[1][4]
   Add eBay item count/median asking price/availability for matchable products and Google Trends only after alpha acceptance.[9][24]
7. **Ad transparency:** use Snap’s unauthenticated Ads Gallery API immediately and Meta Ad Library for its defined political and UK/EU coverage.[17][31][32]
   Treat Google’s UI as manual confirmation rather than a bulk collector.[26]

This supports 100–500 carefully verified events with roughly 1–5 official source assets per event, daily/weekly outcome snapshots, and an auditable evidence trail. The labor bottleneck will be appearance/product verification, not API volume.

### B. Approval-dependent extension

Apply in parallel for Meta Content Library, TikTok Research API and Reddit for Researchers.[10][12][15]
They materially improve Instagram/TikTok/Reddit coverage but should remain optional because application decisions, secure-environment rules and export constraints can delay or prevent collection.[30]

### C. Paid extension

License Getty/AP/Shutterstock editorial stills for durable visual measurement, and add a commercial news archive/API only if full-text scale is necessary. Do not buy this before the 100-event pilot demonstrates that the visual/product coding is reliable.[21][22]

## Recommended event schema

Minimum keys:

- `event_id` (project UUID), `celebrity_qid`, `brand_qid`, `product_id_type/value`;
- `platform`, `source_account_id`, `source_content_id`, `canonical_url`, `published_at`, `captured_at`;
- `appearance_start/end`, `brand_visible`, `product_visible`, `spoken/text mention`, `evidence_coordinates`;
- `relationship_type`, `relationship_status`, `disclosure_text`, `disclosure_surface`, `relationship_source_id`;
- `parent_event_id`, `amplifier_type`, `amplifier_source_id`, `amplified_at`;
- repeated outcomes keyed by `metric_name`, `metric_time`, `metric_value`, `retrieval_request_hash`;
- `media_rights_basis`, `retention_deadline`, `deletion_checked_at`, `source_checksum`, `model/prompt/codebook_version`.

## Verified interface notes

- On November 3, 2026 UTC, the Wikimedia Pageviews API returned seven daily observations for both `Tate_McRae` and `Adidas` for October 1–7, 2026.
- The Common Crawl collection endpoint returned `CC-MAIN-2026-43` as the latest collection; historical index queries may still require retries, narrower prefixes and backoff.
- An unauthenticated Snap Ads Gallery search for Adidas in France over October 1–November 3, 2026 returned HTTP 200 and ten ad-preview records in the first page.
- Prior exploratory GDELT DOC requests encountered HTTP 429; use backoff and prefer raw files/BigQuery for production reproducibility.

## Sources

[1] https://developers.google.com/youtube/v3/docs/videos
[2] https://developers.google.com/youtube/v3/determine_quota_cost
[3] https://developers.google.com/youtube/terms/developer-policies
[4] https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/examples/page-metrics.html
[5] https://commons.wikimedia.org/wiki/Commons:Reuse
[6] https://gdeltproject.org/data.html
[7] https://commoncrawl.org/get-started
[8] https://www.commoncrawl.org/terms-of-use
[9] https://developers.google.com/search/apis/trends
[10] https://support.reddithelp.com/hc/en-us/articles/49381918834964-Reddit-for-Researchers-Program
[11] https://redditinc.com/policies/data-api-terms
[12] https://developers.tiktok.com/products/research-api
[13] https://developers.tiktok.com/docs/en/research-api-faq
[14] https://developers.tiktok.com/products/commercial-content-api
[15] https://transparency.meta.com/researchtools/meta-content-library
[16] https://developers.facebook.com/docs/content-library-and-api/support/faqs
[17] https://www.facebook.com/ads/library/api
[18] https://developers.facebook.com/docs/instagram-platform
[19] https://www.ftc.gov/system/files/documents/plain-language/1001a-influencer-guide-508_1.pdf
[20] https://www.mediacloud.org/documentation/story-guide
[21] https://open-platform.theguardian.com/access
[22] https://developer.gettyimages.com/docs
[23] https://wornontv.net/terms
[24] https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search.html
[25] https://affiliate-program.amazon.com/help/operating/policies
[26] https://support.google.com/adspolicy/answer/13733850
[27] https://developer.x.com/en/products/twitter-api
[28] https://newsapi.org/pricing
[29] https://developers.tiktok.com/docs/en/research-api-codebook
[30] https://developers.facebook.com/docs/content-library-and-api
[31] https://developers.snap.com/marketing-api/Ads-Gallery-Api/Introduction
[32] https://developers.snap.com/marketing-api/Ads-Gallery-Api/using-the-api
