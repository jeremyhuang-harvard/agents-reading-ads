# Feasibility memo: TikTok EU Commercial Content API

**Assessment date:** October 8, 2026  
**Pilot target:** 2,000–2,500 EU paid ads, preferably gambling/vice, with downstream multimodal analysis

## Verdict

**Conditionally feasible and worth piloting.** Once access is approved, TikTok’s Commercial Content API exposes paid-ad records, direct video/image URLs, captions, advertiser identity, reach, delivery breakdowns, and unusually detailed targeting metadata. That is enough to construct a 2,000–2,500-ad multimodal corpus.[1][5][6]

The material qualifications are: access is application-gated; paid-ad search returns only **10 ads per request**; and ad detail accepts only **one `ad_id` per request**.[2][5][6] The official documentation does not publish Commercial Content API request-rate quotas, and search has no documented category, gambling, random-sample, sort, or “return total count” control.[5][10] The current Query Ads documentation also says the minimum publication date must be within one year.[5] The pilot should therefore be framed as a reproducible, stratified recent-ad sample—not a complete census or statistically uniform sample of all EU TikTok gambling advertising.

**Go/no-go recommendation:** **GO for a credentialed technical pilot**, conditional on (1) approval and working production credentials, (2) a small live test showing media URLs can be fetched reliably before expiry, and (3) observed throttling allowing roughly 2,200–2,750 API calls plus media downloads in the project window. Do not promise historical coverage beyond the rolling availability window or a representative EU-wide gambling prevalence estimate.

## 1. What is actually accessible

TikTok describes this product as an ad-transparency API containing paid ads, advertiser metadata, targeting information, reach, and selected information about rejected ads. TikTok says records remain accessible while an ad runs and until one year after it was last shown.[1]

### Paid ads

`POST /v2/research/adlib/ad/query/` with scope `research.adlib.basic` queries paid ads. It can return ad ID, first/last shown date, status/status statement, video URLs, image URLs, reach, advertiser business ID/name, and funding source (`paid_for_by`).[5]

The search body supports:

- required publication-date range;
- optional targeted-country list;
- ad type: `VIDEO`, `IMAGES`, or `TEXT`;
- status: `ACTIVE` or `INACTIVE`;
- reach bands: `0-10K`, `10K-100K`, `100K+`, or `all`;
- targeted age bands;
- targeted gender;
- optional search term of at most 50 characters, with `exact_phrase` or `fuzzy_phrase` matching.[5]

### Media assets

The ad-query and ad-detail responses expose `ad.videos[].url` and `ad.image_urls[]`; the examples show MP4-style CDN URLs and signed image URLs containing `x-expires` and `x-signature` parameters.[5][6] Thus the API does expose asset locations suitable for collection, but the documentation does **not** define a separate bulk media-download endpoint, URL lifetime, guaranteed format, or archival guarantee. The correct operational assumption is to fetch media immediately when each record is received, retain the source URL and retrieval timestamp, validate MIME/type and HTTP status, and checksum the bytes. A live credentialed test is still required before asserting download success rates.

Do not confuse `ad.download_url` with a creative download URL: TikTok defines it as the app-store download page linked from the ad. The actual creative locations are `ad.videos[].url` and `ad.image_urls[]`.[6]

For creator-labelled “commercial content” (for example paid partnerships), a separate endpoint returns the public TikTok video page and cover image rather than a documented raw video file. That endpoint is useful for a secondary branded-content sample, but paid ads are the better primary source for downloadable multimodal creatives and targeting/reach fields.

## 2. Credentials and application path

Official access steps are:

1. Create a TikTok for Developers account using an official email address.[1]
2. Log in and submit the Commercial Content API application at the official application URL.[1][2]
3. TikTok states that a complete application should receive a response within two working days; clarification may come from `commercial-research-questions@tiktok.com`. Applicants may be located anywhere, although the product currently begins with EU ad data.[1]
4. After approval, open the approved research project and reveal its **Client key** and **Client secret**.[3]
5. Exchange those credentials at `POST https://open.tiktokapis.com/v2/oauth/token/` using `grant_type=client_credentials` and `Content-Type: application/x-www-form-urlencoded`.[4]
6. Use the returned bearer token in API requests. Tokens are valid for 7,200 seconds (two hours), so the collector must refresh them automatically.[4]

**Application-form caveat:** the application URL is login-gated and, when accessed without an authenticated developer account, displays “No access / You need to login.” TikTok’s public overview says to provide all requested information so it can validate authentic applications, but it does not publish a stable field-by-field schema outside the authenticated form.[1][2] Therefore the exact current form fields cannot be responsibly enumerated from public official documentation. Before submission, prepare at minimum an institutional identity, official email, project purpose, requested use, collection scope, security/storage plan, and publication/output description, but treat that list as application preparation—not a claim about the form’s exact fields.

## 3. Search, pagination, and quota constraints

### Paid-ad query constraints

- Maximum `max_count`: **10 ads per response**; default 10.[5]
- Pagination: omit `search_id` on the first request, then submit the returned `search_id` for each sequential page while `has_more` is true.[3][5]
- Changing the search term or filters requires removing `search_id` and starting a new search, because it identifies a cached result set.[5]
- Search term: optional, ≤50 characters; one exact or fuzzy phrase per query.[5]
- Required date range: the current page says `min` must be within one year.[5]
- No documented sort order, randomization, offset/page number, total-result count, gambling/industry category, language filter, advertiser-ID filter on the ad-query endpoint, or batch ad-detail endpoint.[5][6]

### Supporting endpoints

- `ad/detail` returns one ad per `ad_id` and supplies the richest metadata.[6]
- `advertiser/query` searches advertiser names, returns up to 50 records, and exposes business ID/name/country; no pagination field is documented on that endpoint.[7]
- `ad/report` returns daily ad counts by country and can optionally filter by advertiser business IDs. It is useful for sizing date/country strata before downloading creatives.[8]

### Quotas

TikTok’s generic rate-limit page documents 600 requests per minute for several user/video endpoints and says API limits are set separately, but it does **not** list any Commercial Content API endpoint.[10] The Commercial Content API reference pages also omit a request-per-minute/day quota.[5][6] Consequently, **no official numeric Commercial Content API quota should be assumed**. Implement exponential backoff for HTTP 429, log TikTok `log_id` values, cap concurrency conservatively, and ask TikTok support for the assigned quota during approval.

At the documented maxima, 2,000 ads require at least 200 query pages and 2,000 detail calls; 2,500 require at least 250 query pages and 2,500 detail calls. The minimum metadata workload is therefore approximately **2,200–2,750 API calls**, excluding token refreshes, retries, report/advertiser discovery, and media HTTP requests.

## 4. Geography, reach, targeting, and analytic fields

TikTok’s supported-country page lists all 27 EU member states and additionally Norway, Iceland, Liechtenstein, the United Kingdom, and Switzerland.[9] For this project, explicitly restrict `country_code_list` to the 27 EU codes rather than relying on a default or the broader supported-country list.

The ad detail response can supply:

- **Advertiser:** business ID/name, advertiser country, funding source, profile/avatar URL, follower count.[6]
- **Creative and destination:** caption/title, video URLs, image URLs, external landing page, app-store page, call-to-action, advertising objective, first/last shown date, status, status statement, and rejection information.[6]
- **Targeting:** estimated users targeted; countries; age flags; gender flags; uploaded/custom-audience inclusion and exclusion; video-interaction categories; creator-interaction categories; interests; provinces; cities; languages; device models; operating systems; and high-spending-power targeting.[6]
- **Observed reach:** total unique users seen, reach by delivered region, and age-by-gender reach breakdowns within region. TikTok marks `unique_users_seen_by_country` deprecated in favor of `unique_users_seen_breakdowns`.[6]

The values are often bucketed strings such as `10K`, `0-1K`, or age bands rather than exact counts. The schema should preserve original strings and separately derive normalized lower/upper bounds for analysis.[5][6]

## 5. Realistic 2,000–2,500-ad collection design

### Recommended design: vice-enriched, reproducible sample with a control stratum

1. **Run a 100-ad credentialed shakedown first.** Use two EU countries, one recent week, `VIDEO`, both active and inactive ads, and a small multilingual vice keyword set. Confirm pagination continuity, duplicate behavior, media HTTP success, URL lifetime, file sizes/codecs, null-field rates, and actual throttling.

2. **Define fixed strata before full collection.** Use country × calendar week/month × search strategy. Oversample larger ad markets but reserve coverage for multiple EU regions. Record every request body, response, timestamp, token-refresh event, and returned `search_id`.

3. **Use two sampling arms.**
   - **Vice/gambling-enriched arm: 1,800–2,100 unique ads.** Run exact and fuzzy searches using a versioned multilingual lexicon covering betting, casino, slots, poker, sportsbook, jackpot, lottery, bingo, odds, bonus, and locally relevant terms/brand names. Because one search term is allowed per query and category filtering is absent, deduplicate globally by `ad.id` and classify candidates after retrieval.
   - **Background/control arm: 300–400 unique ads.** Omit `search_term` in selected country/date/type strata and page sequentially. This supplies non-vice comparisons and permits measurement of keyword-selection error.

4. **Use `ad/report` before each broad stratum.** Daily country counts help choose windows small enough to paginate and balance, although they do not provide gambling-specific counts.[8]

5. **Request rich query fields immediately.** Include ID, dates, status, videos, image URLs, reach, business name/ID, and payer in the query response.[5] Download media as soon as the response arrives rather than deferring URL resolution.

6. **Fetch detail for every deduplicated retained ad.** This adds caption, destination, objective, full targeting, regional reach breakdowns, and rejection fields. Since detail is one ad per call, checkpoint completion per `ad_id` and make retries idempotent.[6]

7. **Store an auditable corpus.** Recommended objects: raw query JSON, raw detail JSON, normalized ad/advertiser/targeting/reach tables, creative bytes, SHA-256, MIME/type, HTTP status, retrieval timestamp, source URL, query-stratum ID, and lexicon/version. Keep failed-media records rather than silently dropping them.

8. **Stop at 2,500 unique ads, not 2,500 hits.** Search overlap across countries, terms, and dates will be substantial. Budget more than 2,500 candidate hits, then deduplicate and retain according to predeclared stratum quotas.

9. **Perform multimodal classification after collection.** Use caption, landing URL/domain, advertiser/payer, OCR, ASR, frames, and visual brand cues to determine gambling/vice status. The API’s keyword search should be treated as candidate generation, not ground truth.

### Collection risks and mitigations

- **Unknown completeness/order:** no documented random or exhaustive ordering. Mitigate with small fixed strata, full `has_more` traversal where feasible, and transparent inclusion rules.[5]
- **Rolling retention:** collect promptly and timestamp snapshots; do not assume old creatives will remain available after the stated window.[1]
- **Expiring media URLs:** fetch immediately, retry promptly, and retain checksums and retrieval logs.[5][6]
- **Unknown quota:** throttle conservatively and benchmark during the 100-ad shakedown; obtain a written quota from support if possible.[10]
- **Application uncertainty:** submit early; exact authenticated form fields and assigned access conditions remain a pre-pilot blocker.[1][2]
- **Category validity:** validate a stratified sample manually and report precision/recall of the post-collection gambling classifier rather than labeling all keyword hits as gambling ads.

## Bottom line

The API is technically sufficient for a 2,000–2,500-ad EU multimodal pilot and is the strongest official TikTok source for paid-ad creatives plus targeting/reach metadata. Its practical weaknesses are operational rather than fatal: gated credentials, 10-result paid-ad pages, one-at-a-time details, signed/possibly temporary asset URLs, a rolling historical window, missing category/random sampling controls, and undocumented Commercial API quotas. Approve a pilot, but make the first milestone a 100-ad end-to-end retrieval test and condition the full run on measured media and throttling performance.

## Sources

[1] https://developers.tiktok.com/products/commercial-content-api — Commercial Content API
[2] https://developers.tiktok.com/application/commercial-content-api — Commercial Content API application
[3] https://developers.tiktok.com/docs/en/commercial-content-api-getting-started — Getting Started - Commercial Content API
[4] https://developers.tiktok.com/docs/en/client-access-token-management — Client Access Token Management
[5] https://developers.tiktok.com/docs/en/commercial-content-api-query-ads — Query Ads
[6] https://developers.tiktok.com/docs/en/commercial-content-api-get-ad-details — Get Ad Details
[7] https://developers.tiktok.com/docs/en/commercial-content-api-query-advertisers — Query Advertisers
[8] https://developers.tiktok.com/docs/en/commercial-content-api-get-ad-report — Get Ad Report
[9] https://developers.tiktok.com/docs/en/commercial-content-api-supported-countries — Supported Countries
[10] https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit — Rate Limits
