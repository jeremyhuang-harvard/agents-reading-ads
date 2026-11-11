# Feasibility memo: Meta EU Ad Library/API pilot

**Verdict — conditional GO for metadata/text collection; NO-GO as the sole source for automated multimodal assets.** Meta’s API can query ordinary commercial ads delivered in EU countries by using `ad_type=ALL`, so collecting 2,000–2,500 unique ad records is practical after authorization.[1][2] The API returns creative text, delivery metadata and an `ad_snapshot_url`, but its documented fields do **not** expose direct image/video files or stable media-download URLs.[3] A GABRIEL-style image/video pipeline therefore needs a separately approved/validated asset-acquisition method; scraping media from snapshot/UI pages is not an officially supported API workflow, and Meta’s Automated Data Collection Terms require express written permission.[3][7]

## What is available

- **Public UI:** The Ad Library website supports viewing/searching ads. For ads about social issues, elections or politics, coverage is global and includes inactive ads for seven years. For other ads, the special archive/API coverage is ads delivered in the EU, available for one year.[1][6]
- **API:** `GET /{version}/ads_archive` supports `ad_type=ALL` for ads delivered to EU countries. `ad_reached_countries` is required and uses ISO country codes. Search can be constrained by keyword/phrase (`search_terms`), Page IDs (`search_page_ids`), delivery dates, active status, media type and publisher platform.[1][2]
- **Returned data:** Documented fields include `id`, `page_id`, `page_name`, `ad_creation_time`, delivery start/stop times, creative body/caption/description/link title, `ad_snapshot_url`, `media_type`, publisher platforms, languages, EU reach, age/gender and regional delivery, beneficiary/payer, and spend/impression-related fields where applicable.[3]
- **Retention:** Meta states that ads delivered in the EU on or after **August 21, 2023** are stored in the Ad Library for one year.[2][6]

## Authorization and operational constraints

1. Use a Facebook account and complete Meta’s identity/location verification for Ad Library API access.[4]
2. Create a Meta developer account/app, accept the platform/API terms, and generate a Facebook Developer access token; Meta’s official sample CLI requires that token.[4][5]
3. Query `ads_archive`, explicitly request fields, and follow cursor pagination. Meta’s official sample code follows `paging.next` and defaults to `limit=500`; treat 500 as sample-code behavior, not a guaranteed current service limit.[5]
4. At least one search path is needed in Meta’s sample tooling: a search term or Page ID.[5] There is no documented gambling/vice category filter, random-sample endpoint, bulk export, or stable total-count endpoint in the reviewed parameter documentation.[2]
5. The official Ad Library documentation reviewed does not publish a numeric API quota/rate-limit for this endpoint. Do not infer unlimited access; measure throttling and response headers with the authorized pilot token before scheduling the full pull.[1][4]

An unauthenticated empirical request to `graph.facebook.com/v21.0/ads_archive` on **October 8, 2026** returned an `OAuthException`, confirming directly that this request did not work anonymously. The public UI was also not reliably automatable from the test environment (bot/interstitial response), reinforcing that the API—not UI automation—should be the collection path.

## Creative-asset feasibility

- **Usable directly:** creative text fields, metadata, and the archived-ad link (`ad_snapshot_url`).[3]
- **Not documented as retrievable:** original image files, video files, thumbnails, CDN URLs, or a media-download endpoint. `media_type` identifies format but does not supply the bytes.[3]
- **Implication:** multimodal analysis is the main blocker because the documented field surface stops at metadata, text and the snapshot link.[3] A small, manual validation can test whether authenticated snapshot pages consistently render creatives and whether research use/download can be approved. Do not design production ingestion around reverse-engineering snapshot HTML/CDN requests: it is brittle, outside the documented API surface, and automated collection requires Meta’s express written permission.[7]

## Sampling plan for 2,000–2,500 ads

1. **Pilot 100–200 records first:** 3–5 countries, 2–4 recent weeks, and 10–15 local-language gambling terms. Validate token lifetime, pagination, duplicates, field completeness, snapshot accessibility and observed throttling against the documented parameters/fields and official pagination pattern.[2][3][5]
2. **Create query cells:** country × week × multilingual keyword. Include casino, betting, sportsbook, poker, bingo, lottery and bonus/free-bet variants in the relevant languages. Use `ad_type=ALL`, `ad_reached_countries`, delivery-date bounds and `ad_active_status=ALL`; page through each cell.[2]
3. **Expand by advertiser:** extract `page_id` from keyword hits, then query those Pages to capture creatives whose text lacks seed words.[2][3] This reduces keyword-only recall bias.
4. **Deduplicate by ad `id`**, retain query provenance, and stratify the final sample by country, week, advertiser and media type using the API’s documented ID, Page, delivery and media fields.[3] Cap any one Page/advertiser so major operators do not dominate.
5. **Oversample metadata records** (for example, 3,500–5,000 candidates) and select 2,000–2,500 only after removing duplicates and records with missing/unusable snapshots. If the end goal requires downloadable image/video bytes, make asset validation a hard gate before scaling beyond the pilot.

## Bottom line

The EU API is practically usable for a **2,000–2,500-record commercial/gambling metadata and text corpus**. It is not, on its documented surface, a complete multimodal dataset API. Proceed only with a staged pilot and treat lawful, stable image/video acquisition as the go/no-go criterion for the later GABRIEL analysis.

## Sources

[1] Meta, “Ad Library API”: https://www.facebook.com/ads/library/api/

[2] Meta, “Ad Library API parameters”: https://www.facebook.com/ads/library/api/parameters/

[3] Meta, “Ad Library API fields”: https://www.facebook.com/ads/library/api/fields/

[4] Meta, “Ad Library API — get started”: https://www.facebook.com/ads/library/api/get-started/

[5] Meta/Facebook Research, official Ad Library API sample scripts: https://github.com/facebookresearch/Ad-Library-API-Script-Repository

[6] Meta Privacy Center, “Advertising information with respect to the EU”: https://www.facebook.com/privacy/dialog/advertising-information-with-respect-to-eu

[7] Meta, “Automated Data Collection Terms”: https://www.facebook.com/legal/automated_data_collection_terms
