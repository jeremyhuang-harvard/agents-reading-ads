# Exact papers underlying the “Implicit Ads” idea

## Bottom line

The three intended papers are almost certainly: **(1) “Ads as Cues,” (2) “Consumer Memory and Competitive Interference: The Case of Auto Insurance Advertising,” and (3) “Economic Representations.”** They play different roles. *Ads as Cues* supplies the cue-similarity/habit theory and household-purchase outcomes; Sahni–Yang supplies direct field evidence that brands compete for retrieval from memory; Sarkar supplies a scalable embedding method for measuring how an economic object is represented, but not a memory-interference or celebrity-endorsement design.[2][4][7]

## 1) Ads as Cues

- **Exact title:** *Ads as Cues*[2]
- **Authors:** Pedro Bordalo, Giovanni Burro, Nicola Gennaioli, Gad Nacamulli, and Andrei Shleifer.[2]
- **Status:** NBER Working Paper No. 34387, October 2025; explicitly not peer reviewed. DOI: **10.3386/w34387**.[1][2]
- **Canonical URLs:**[2]
  - https://www.nber.org/papers/w34387
  - https://www.nber.org/system/files/working_papers/w34387/w34387.pdf
  - https://doi.org/10.3386/w34387

### Construct and directional-association mapping

The model is explicitly directional: an ad or other cue **c** changes retrieval of memories of a good **g**. Recall rises with (i) the consumer’s past frequency of experiencing the good and (ii) similarity between the cue and the good, but falls through interference from other frequent or cue-similar experiences. Demand then rises when the consumer retrieves the pleasure associated with the brand.[2]

For a celebrity–brand project, the closest mapping is:

- celebrity appearance/persona = **cue**;[2]
- remembered brand/consumption episode = **retrieved object**;[2]
- celebrity→brand association strength = cue–brand similarity or retrieval probability;[2]
- competing celebrity→other-brand links = interference terms;[2]
- cue distinctiveness = high similarity to the focal brand and low similarity to rival brands.[2]

The paper does **not** measure celebrities. Its empirical similarity measure is symmetric cosine similarity between short textual descriptions of brands’ ads. Therefore, it supports the mechanism that a distinctive cue could make recall more brand-selective, but it does not itself establish a directional celebrity→brand link.[2]

### Outcomes / dependent variables

1. **Brand-level weekly household demand:** quantity of the target brand purchased by household *j* in week *t*.[2]
2. **Category-level weekly demand:** summed quantity of the two leading brands in a product category.[2]
3. **Direct advertising effect:** target-brand demand as a function of exposure to that brand’s ads.[2]
4. **Within-category spillover:** target-brand demand as a function of exposure to the competing brand’s ads.[2]
5. **Cross-category spillover/interference:** category demand as a function of exposure to ads for other categories, interacted with ad-content similarity.[2]
6. **Mechanism interactions:** ad exposure × prior purchase frequency, including a quadratic frequency term to test the predicted concavity.[2]

These are behavioral purchase outcomes, not direct recall, recognition, attribution, or association measures.[2]

### Design and required data

- Observational household-by-brand-by-week panel, 2016–2019.[2]
- NielsenIQ Homescan purchases for more than 60,000 U.S. households.[2]
- Nielsen Ad Intel ad occurrences and audience impressions by DMA, channel, date/time, age, and gender.[2]
- Expected household exposure constructed from ad duration and demographic/DMA viewership probabilities.[2]
- Prior-year number of shopping trips containing the brand as the main habit/experience proxy.[2]
- Short, 4–6-word Nielsen descriptions of each ad; stem-count vectors and cosine similarity measure ad similarity.[2]
- Prices, discounts, household demographics, product/brand, geography, and detailed time controls; the authors also use the Shapiro et al. strategy to isolate quasi-random supply-side variation in TV advertising.[2]

### Main limitations for Implicit Ads

- **Not directly scrapable:** the key purchase panel, impression data, and ad descriptions are licensed Nielsen products.[2]
- **Exposure is expected, not observed individual exposure:** it is inferred from DMA-demographic viewership probabilities.[2]
- **No direct memory measure:** purchase is interpreted through the memory model; recall and celebrity→brand attribution are latent.[2]
- **Frequency is initially composite:** prior purchases combine stable taste and memory strength, although household fixed-effect analyses partially address this.[2]
- **Similarity is crude and symmetric:** cosine similarity of very short ad descriptions can combine category similarity and creative-context similarity; it does not measure directional retrieval.[2]
- **Selected setting:** top two brands in 20 highly advertised, weakly differentiated packaged-goods categories, limiting generalization to durable goods, services, influencers, or new brands.[2]

## 2) Consumer Memory and Competitive Interference: The Case of Auto Insurance Advertising

- **Exact title:** *Consumer Memory and Competitive Interference: The Case of Auto Insurance Advertising*[4]
- **Authors:** Navdeep S. Sahni and Yifan Yang.[4]
- **Status:** Working paper. Stanford lists it as Working Paper No. 4302; the latest primary PDF located is dated **March 11, 2026**. SSRN DOI: **10.2139/ssrn.4968643**.[3][4][5]
- **Canonical URLs:**[4]
  - https://www.gsb.stanford.edu/faculty-research/working-papers/consumer-memory-competitive-interference-case-auto-insurance
  - https://bfi.uchicago.edu/wp-content/uploads/2026/03/SahniYang2026_Auto_insurance_advertising.pdf
  - https://doi.org/10.2139/ssrn.4968643

### Construct and directional-association mapping

This is the cleanest foundation for **competitive memory interference**. The consumer has an associative network linking an “auto-insurance purchase context” to brands. Advertising jointly activates the category context and advertised brand, strengthens that directional category→brand link, and makes a rival less likely to be retrieved because brands compete for limited recall slots.[4]

For Implicit Ads:

- purchase/category context→brand retrieval is directly modeled;[4]
- a celebrity could be added as another cue node that activates the brand;[4]
- a distinctive celebrity cue should help if it strengthens focal-brand retrieval without also activating competitors;[4]
- the strongest test would measure whether celebrity exposure raises focal-brand consideration and lowers rival recall/consideration, especially after rival advertising.[4]

The paper uses a brand character/mascot in the focal banner, but does not separately randomize or estimate the character’s contribution. It therefore validates interference, not celebrity distinctiveness.[4]

### Outcomes / dependent variables

1. **Primary outcome—consideration proxy:** whether, or on how many unique days, an individual visits the focal insurer’s website.[4]
2. **Competitor consideration:** number of competitor-insurer websites visited, especially on the treatment day and next day.[4]
3. **Category activation:** visits to any auto-insurance website.[4]
4. **Customer-status proxies:** indicators inferred from browsing behavior for being a focal or competitor customer post-treatment.[4]
5. **Dynamic treatment effects:** focal and competitor visits by day/week/month, including carryover for several months.[4]
6. **Treatment heterogeneity/interactions:** treatment × prior local TV advertising by the focal firm; treatment × competitor TV advertising; treatment effects before/after the start of the MLB season; heterogeneity by age and prior browsing.[4]
7. **Structural-model outcomes:** joint probabilities of visits to the focal and competitor sites on treatment day and next day; log likelihood and six in-/out-of-sample moments used to compare the memory model with ad-stock models.[4]

### Design and required data

- Large randomized field experiment conducted for one day in March 2015 on the homepage of a top-five global website.[4]
- 326,952 users who both visited the site that day and had the platform’s browser extension installed.[4]
- Random assignment: 75% saw the insurer’s banner whenever they visited that day; 25% saw an unrelated public-service announcement.[4]
- Browser-level persistent IDs linked assignment to clickstream behavior from February–June 2015.[4]
- Subdomain-level browsing histories for focal and rival insurers.[4]
- DMA location; self-reported age for a subset.[4]
- Nielsen Ad Intel local TV GRPs for ten insurers, merged by DMA and time.[4]
- Auxiliary comScore browsing data, Google Trends, MLB timing/popularity, and inferred customer-status rules.[4]

### Main limitations for Implicit Ads

- **Partnership-only core data:** randomized ad assignment linked to persistent individual clickstreams is not obtainable by ordinary scraping.[4]
- **Website visits are a proxy:** they are closer to consideration than sales, but are not direct unaided recall, explicit celebrity→brand association, or final purchase.[4]
- **One campaign, day, platform, advertiser, and category:** strong internal validity for that intervention, narrower external validity.[4]
- **Creative mechanism is bundled:** brand name, standard character, savings claim, and “get a quote” call-to-action move together.[4]
- **Competitive-ad interactions are less clean than the randomized main effect:** local TV GRPs are DMA-level exposure proxies, and the MLB analysis uses natural variation rather than randomized rival advertising.[4]
- **Selected users:** the analysis requires visiting the partner site and installing its extension; behavior may differ from the general population.[4]

## 3) Economic Representations

- **Exact title:** *Economic Representations*[7]
- **Author:** Suproteem K. Sarkar.[7]
- **Status:** Standalone working paper/manuscript; first version October 2024, current primary PDF dated **June 25, 2026**. It is also related to the first essay of Sarkar’s Harvard dissertation. No DOI was located for the standalone paper.[6][7]
- **Canonical URLs:**[7]
  - https://suproteem.is
  - https://suproteem.is/assets/files/representations.pdf

### Construct and directional-association mapping

Sarkar learns a vector representation for each firm-year from the language used in financial-news coverage. Directions in the embedding correspond to economic features such as “software,” “platform economy,” or “upmarket”; geometric proximity captures how similarly firms are represented.[7]

This is useful for **measurement engineering**, but its core association object is not the same as celebrity→brand recall:

- measured object: firm→feature representation in news language;[7]
- similarity measure: mostly symmetric geometric proximity between representations;[7]
- behavioral interpretation: a proxy for how “the market” perceives a firm’s business model;[7]
- not measured: whether seeing celebrity X causes a person to retrieve brand Y rather than brand Z.[7]

For Implicit Ads, the transferable method is to learn time-indexed embeddings from ads, captions, news, and social text, then construct celebrity and brand vectors or directional retrieval scores. A separate human or behavioral outcome is still needed to establish directional celebrity→brand association and interference.[7]

### Outcomes / dependent variables

1. **Representation-validation outcomes:** pairwise daily stock-return correlation, shared analyst coverage, and common institutional ownership.[7]
2. **Valuation/forecast outcomes:** log price-to-book, log price-to-earnings, and median IBES long-term growth forecast.[7]
3. **Price-change outcomes:** annual log stock returns and the share explained by representation levels, changes in representation, and traditional characteristics/industries.[7]
4. **Representation dynamics:** cosine-based reversion of a firm’s representation after deviation from its recent historical mean.[7]
5. **Forecasting/mispricing outcomes:** future monthly stock returns in Fama–MacBeth regressions; long–short portfolio alphas based on priced representation deviations.[7]
6. **Attention-feature outcomes:** future returns after a firm’s representation shifts toward features associated with trending news coverage, extreme profitability, or extreme past returns.[7]
7. **Communication outcomes:** reversion in earnings-call speech embeddings and the association between priced deviations in managerial communication and priced deviations in news-based market representations.[7]

### Design and required data

- 6,560,329 Dow Jones Newswires articles covering 12,661 firms, January 1980–December 2023.[7]
- Firm-year representations built from articles coded to a single stock; at least ten articles per firm-year.[7]
- Time-indexed language models trained on historical corpora to avoid look-ahead contamination; financial-news contrastive learning places articles about the same firm closer than articles about different firms.[7]
- Matched U.S. common-stock panel: 95,165 firm-year observations, 1983–2022.[7]
- CRSP returns; firm/accounting characteristics; SIC/Fama–French industries; IBES forecasts; analyst coverage; 13F ownership; and StreetEvents earnings calls for 2003–2021.[7]
- Split-sample ridge regressions for explanatory tests and out-of-sample return-forecasting tests.[7]

### Main limitations for Implicit Ads

- **Mostly licensed data:** Dow Jones Newswires, CRSP, IBES, 13F processing, and StreetEvents make exact replication expensive; public substitutes would change the measurement universe.[7]
- **Representation is a proxy:** press language is assumed to be informative about market perception, but the latent perception itself is not observed.[7]
- **Association is not causal:** news language, fundamentals, prices, management communication, and investor attention can move together.[7]
- **Geometry is not inherently directional:** cosine similarity does not by itself distinguish celebrity→brand from brand→celebrity association.[7]
- **Firm-level annual aggregation is far from ad-level memory:** the unit, timescale, population, and outcomes differ sharply from consumer cue retrieval.[7]
- **Return predictability does not uniquely prove misperception:** the paper supplies robustness tests, but risk, omitted information, endogenous media coverage, and changing fundamentals remain alternative concerns.[7]

## Implication for the Implicit Ads design

Use the papers as a three-layer stack rather than treating them as one design:

1. **Mechanism:** Sahni–Yang—cues strengthen one association and suppress competing retrieval.[2][4][7]
2. **Comparative statics:** Bordalo et al.—effects depend on prior experience and cue–object similarity; similar cues create spillovers, while dissimilar cues interfere.[2][4][7]
3. **Scalable measurement:** Sarkar—learn representations from language without imposing a small, fixed feature taxonomy.[2][4][7]

The key missing outcome in all three is a direct **directional celebrity→brand measure**. The minimum clean outcome battery would therefore include: unaided brand recall after a celebrity cue; focal-versus-rival brand attribution; response latency; confidence; delayed recall; and choice/consideration. To test distinctiveness, randomize whether the celebrity cue is uniquely linked to the focal brand, shared with/category-similar to rivals, or absent, and measure both focal recall gains and rival recall losses. Scraped ads/news can construct the stimulus and historical-association ledger, but credible interference outcomes require an experiment, survey panel, search/clickstream partnership, or another person-level behavioral source.[2][4][7]

## Sources

[1] https://www.nber.org/papers/w34387 — Ads as Cues | NBER
[2] https://www.nber.org/system/files/working_papers/w34387/w34387.pdf — Ads as Cues (PDF)
[3] https://www.gsb.stanford.edu/faculty-research/working-papers/consumer-memory-competitive-interference-case-auto-insurance — Consumer Memory and Competitive Interference | Stanford GSB
[4] https://bfi.uchicago.edu/wp-content/uploads/2026/03/SahniYang2026_Auto_insurance_advertising.pdf — Consumer Memory and Competitive Interference (March 2026 PDF)
[5] https://doi.org/10.2139/ssrn.4968643 — SSRN DOI: Consumer Memory and Competitive Interference
[6] https://suproteem.is — Suproteem Sarkar research page
[7] https://suproteem.is/assets/files/representations.pdf — Economic Representations (PDF)
