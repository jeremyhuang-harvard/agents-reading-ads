# “Ads as Cues”: deep dive and literature map

## 1. Verified paper identity and version

**Verified title:** *Ads as Cues*.

**Authors, in the paper’s order:** Pedro Bordalo, Giovanni Burro, Nicola Gennaioli, Gad Nacamulli, and Andrei Shleifer.

**Version checked:** NBER Working Paper **No. 34387**, issue date **October 2025**, DOI **10.3386/w34387**. The author-hosted PDF is dated **October 10, 2025**, runs 106 PDF pages including appendices, and is labeled by Shleifer’s publication page as the current version. I found no later author- or NBER-hosted version as of **October 8, 2026**. The paper remains a working paper, not a peer-reviewed journal article.[1][2]

**Canonical links:** NBER landing page: https://www.nber.org/papers/w34387 ; author PDF: https://shleifer.scholars.harvard.edu/sites/g/files/omnuum10626/files/2025-10/Ads.October_FINAL-1.pdf ; DOI: https://doi.org/10.3386/w34387 .

## 2. The mechanism in one sentence

Advertising can raise demand without conveying information or changing experienced utility: it changes **which past consumption experiences are retrieved**, and therefore which wants and brands are mentally available when a consumer chooses.[2]

This is not merely “brand awareness.” A cue’s effect is consumer-specific because recall depends on the consumer’s own history. The same Pepsi ad can retrieve Pepsi for a habitual Pepsi buyer, Coke for a habitual Coke buyer, other drinks for consumers with related consumption memories, and suppress unrelated wants through interference.[2]

## 3. Model anatomy

### Objects

- Goods are brands nested in product categories: e.g., Coke and Pepsi within cola.
- A consumer has intrinsic consumption pleasure or taste, `q_g`, and price `p_g` for good `g`.
- Memory contains relative frequencies `f_x` of past experiences with each good and a large residual category of neutral/nonbrand experiences.
- Current context contains cues `c`: physiological states, environments, and advertisements.
- `S(c,x)` measures feature similarity between cue `c` and remembered experience `x`.[2]

### Retrieval technology

For one cue, the probability of recalling experience `x` is

`r_x(c,f) = S(c,x) f_x / Σ_y S(c,y) f_y`.

The numerator captures **associativity × repetition**. The denominator captures **interference**: frequent or cue-similar rival memories compete for retrieval. With a vector of weekly cue exposures, recall is the exposure-share-weighted average of cue-specific recall probabilities.[2]

### Choice

Remembering a good retrieves/simulates its pleasure. In the paper’s reduced form,

`d_g(e,f) = q_g r_g(e,f) − θ p_g`.

Thus price and intrinsic pleasure still matter, but demand is also gated by recall. A consumer optimizes conditional on what comes to mind; the deviation from the benchmark is incomplete, cue-dependent retrieval, not irrational choice after retrieval.[2]

### Why habits emerge

Past consumption raises `f_g`, making the good easier to retrieve in future contexts. This creates state dependence even if intrinsic tastes do not change. Stable tastes can also generate high past frequency, so the main empirical proxy mixes “many memories” and “better memories”; the model predicts the ad–habit interaction under both, but only the frequency channel produces the specific concavity result.[2]

### Why ads work

An ad reallocates the cue mix toward features associated with the advertised brand and its consumption context. This raises retrieval of the brand’s pleasure, but—because retrieval is competitive—also raises recall of similar goods and inhibits dissimilar goods. Ads therefore operate as involuntary “memory spotlights,” not simply as messages about attributes.[2]

## 4. Main empirical predictions

1. **Habit/state dependence:** current demand rises with past purchase frequency, holding prices and observed covariates fixed.
2. **Own-ad effect:** exposure to a brand’s ad raises demand for that brand even when the ad is effectively uninformative.
3. **Habit × own-ad complementarity:** the ad effect is stronger for consumers with more past purchases or higher taste, but becomes concave in purchase frequency because the most habitual buyers already retrieve the brand readily.
4. **Within-category positive spillovers:** an ad for one brand raises demand for a similar rival. A Pepsi ad can increase Coke demand.
5. **Spillover × target habit:** that rival spillover is strongest for habitual buyers of the *target* brand, because the cue retrieves their own dominant memories.
6. **Category expansion:** brand advertising raises total demand for the category, not merely business stealing.
7. **Similarity gradient:** spillovers are more positive as cue and target ads/products become more similar.
8. **Interference:** sufficiently dissimilar ads reduce target demand by crowding its memories out of retrieval; negative cross-category effects should be stronger for habitual target consumers.
9. **Dynamic maintenance:** advertising may have low measured short-run lift yet preserve loyalty by rehearsing and re-encoding the brand. Turning advertising off should therefore cause gradual erosion, not necessarily an immediate discrete collapse.
10. **Content prediction:** ads tied to consumption occasions and pleasurable contexts should have durable effects when those contexts later recur; distinctive content should reduce leakage to competitors.[2]

## 5. Empirical design and findings

The authors combine NielsenIQ Homescan purchases for more than 60,000 U.S. households with Nielsen Ad Intel occurrences and audience impressions. The main period is January 2016–December 2019. They study the top two brands in 20 low-differentiation, advertising-intensive categories (40 brands), including cola, beer, cereal, diapers, detergent, pain remedies, pizza, tissue, and yogurt.[2]

- **Habit proxy:** number of shopping trips in the previous calendar year on which the household bought the brand.
- **Ad exposure:** expected household seconds of exposure, built from ad duration, channel, DMA, time, and age/gender-specific audience impressions, then aggregated weekly.
- **Similarity:** cosine similarity between stemmed word-frequency vectors formed from Nielsen’s short ad descriptions.
- **Controls/identification:** own/rival prices, household demographics, product/geography/time fixed effects, increasingly saturated DMA-season controls, local aggregate demand, and household fixed effects. The design adapts the quasi-random timing/geographic strategy of Shapiro, Hitsch, and Tuchman rather than using randomized ad assignment.[2][17]

### Findings

- In the pooled sample, own-ad exposure is positively associated with own demand; the own-ad × own-frequency interaction is positive and its squared-frequency interaction negative.
- Rival-brand exposure has a positive spillover for sufficiently habitual buyers of the target brand.
- Ads raise total category demand.
- Across separate brand estimates, the own-ad effect is stronger for more frequent buyers for 80% of brands; habit-amplified spillovers appear for 63%.
- For cola, the estimated exposure needed to induce one extra 12-ounce Coke falls from about 166 seconds for the average Coke buyer to 44 seconds at the 95th percentile of Coke purchase frequency; for Pepsi-ad spillovers onto Coke, it falls from 362 to 53 seconds.
- Measured ad similarity predicts stronger positive spillovers. For cross-category tests, cola/beer advertising raises demand for other drinks but lowers demand for dissimilar non-drinks; the same sign pattern appears when all other categories are pooled as cues.[2]

### What the evidence does—and does not—establish

The evidence is unusually aligned with the model’s cross-equation restrictions: consumer history, cue exposure, and cue–target similarity jointly predict demand. The positive competitor spillover and negative dissimilar-product interference are harder to rationalize with simple informative advertising or a brand-specific utility shifter.[2]

But the paper is not a randomized advertising experiment. Exposure is predicted rather than observed at the individual viewing level; residual targeting and correlated local demand may remain; ad-text cosine similarity is a noisy proxy for psychological similarity; and annual purchase frequency mixes stable taste, household need, and memory stock. The large sample makes estimates precise but does not itself eliminate these identification and measurement issues. The strongest causal next step would randomize ad content/exposure and preregister heterogeneous effects by prior consumption and semantic similarity.

## 6. Intellectual lineage

Bagwell’s survey organizes economic theories of advertising into **persuasive**, **informative**, and **complementary** views. *Ads as Cues* is closest to persuasion in its positive prediction that nominally uninformative ads alter demand, but its microfoundation is different: ads need not alter deep tastes, fool consumers about attributes, or directly enter utility.

- **Habit/utility capital:** Becker and Murphy model consumption capital and advertising as a good or bad complementary with consumption. *Ads as Cues* replaces a reduced-form utility complement with retrieval, producing consumer-history-dependent spillovers and interference.[4]
- **Information/search/signaling:** Stigler, Nelson, Grossman–Shapiro, and Milgrom–Roberts explain ads through lower search costs, awareness, product information, or costly quality signals. Those channels matter most for unknown products, uncertain quality, or prices; the cue mechanism is designed for famous, frequently purchased, intrinsically similar brands.[5][6][7][8]
- **Cue-triggered preferences:** Laibson’s cue theory lets learned cues change marginal utility. The new paper instead makes cues change recall of past utility and thereby derives habits plus similarity-structured cross-good effects.[9]
- **Associative memory and salience:** Bordalo–Gennaioli–Shleifer’s memory model supplies frequency, similarity, and interference; salience theory supplies the broader idea that context changes representation and choice.[10][11]
- **Behavioral persuasion:** coarse-thinking persuasion shows how messages move judgments through categorical representations. *Ads as Cues* shifts the object from belief distortion to retrieval of consumption experiences.[12]
- **Marketing memory:** Keller’s retrieval-cue experiments and Alba–Chattopadhyay’s recall-inhibition experiments are direct psychological ancestors: retrieval cues affect evaluation, and making one brand salient suppresses competitors in unaided recall.[13][14]
- **Closest empirical precursors:** Sahni’s restaurant experiments show positive spillovers to similar competitors; He–Klein identify reminder effects; Lewis–Nguyen find display ads stimulate searches for both advertisers and rivals; Shapiro finds positive rival spillovers in antidepressants.[15][16][22][26]
- **Closest prior formal mechanism:** Jesse Shapiro’s “memory-jamming” paper models advertising that selectively reminds consumers of favorable experiences or alters their valence. *Ads as Cues* generalizes toward frequency, similarity, interference, and cross-product spillovers.[28]

## 7. Structured literature map

**Legend:** **F** = foundational/conceptual; **A** = directly actionable for testing, campaign design, measurement, or policy. Some papers are both.

### A. Canonical economic views of advertising

| Status | Paper | Connection | URL / DOI |
|---|---|---|---|
| **F** | Bagwell (2007), “The Economic Analysis of Advertising” | Definitive map of persuasive, informative, complementary, signaling, entry, and welfare theories. | https://doi.org/10.1016/S1573-448X(06)03028-7 |
| **F** | Becker & Murphy (1993), “A Simple Theory of Advertising as a Good or Bad” | Advertising directly complements consumption in utility; the main reduced-form benchmark challenged by *Ads as Cues*. | https://doi.org/10.2307/2118455 |
| **F** | Stigler (1961), “The Economics of Information” | Search-cost foundation for informative advertising. | https://doi.org/10.1086/258464 |
| **F** | Nelson (1974), “Advertising as Information” | Advertising informs or signals in experience-good markets. | https://doi.org/10.1086/260231 |
| **F** | Grossman & Shapiro (1984), “Informative Advertising with Differentiated Products” | Awareness, differentiation, price competition, and equilibrium ad reach. | https://doi.org/10.2307/2297705 |
| **F/A** | Milgrom & Roberts (1986), “Price and Advertising Signals of Product Quality” | Separates cue effects from signaling: ad disclosure/expense should matter most under quality uncertainty. | https://doi.org/10.1086/261235 |
| **F/A** | Sahni & Nair (2020), “Does Advertising Serve as a Signal?” | Randomized sponsorship disclosure isolates a pure signaling channel. | https://doi.org/10.1093/restud/rdz053 |

### B. Persuasion, salience, and cue-triggered demand

| Status | Paper | Connection | URL / DOI |
|---|---|---|---|
| **F** | Mullainathan, Schwartzstein & Shleifer (2008), “Coarse Thinking and Persuasion” | Persuasion through categorical/associative representation rather than Bayesian information. | https://doi.org/10.1162/qjec.2008.123.2.577 |
| **F** | Bordalo, Gennaioli & Shleifer (2013), “Salience and Consumer Choice” | Context changes attention weights; useful contrast with retrieval-based context effects. | https://doi.org/10.1086/673885 |
| **F** | Laibson (2001), “A Cue-Theory of Consumption” | Learned cues trigger state-dependent demand; especially relevant to temptation and harmful goods. | https://doi.org/10.1162/003355301556356 |
| **A** | Goldfarb & Tucker (2011), “Online Display Advertising: Targeting and Obtrusiveness” | Targeting and visual salience can help separately but backfire jointly through privacy/reactance. | https://doi.org/10.1287/mksc.1100.0583 |

### C. Memory, associative cues, brand recall, and interference

| Status | Paper | Connection | URL / DOI |
|---|---|---|---|
| **F** | Bordalo, Gennaioli & Shleifer (2020), “Memory, Attention, and Choice” | Core economic memory architecture: similarity-based retrieval and context-dependent valuation. | https://doi.org/10.1093/qje/qjaa007 |
| **F/A** | Keller (1987), “Memory Factors in Advertising” | Ad retrieval cues causally change which ad claims are recalled and how brands are evaluated. | https://doi.org/10.1086/209116 |
| **F/A** | Alba & Chattopadhyay (1986), “Salience Effects in Brand Recall” | Making one brand salient inhibits recall of competing brands—the marketing analogue of interference. | https://doi.org/10.1177/002224378602300406 |
| **F/A** | Keller (1993), “Conceptualizing, Measuring, and Managing Customer-Based Brand Equity” | Brand knowledge as memory-node accessibility and associative structure; operational bridge to brand tracking. | https://doi.org/10.1177/002224299305700101 |
| **A** | Stayman & Batra (1991), “Encoding and Retrieval of Ad Affect in Memory” | Match between encoding and retrieval context determines whether ad-created affect enters evaluation. | https://doi.org/10.1177/002224379102800211 |
| **F/A** | Shapiro (2006), “A ‘Memory-Jamming’ Theory of Advertising” | Closest earlier formal advertising-memory paper; selective reminder and memory manipulation. | https://doi.org/10.2139/ssrn.903474 |

### D. Reminder effects and cross-brand/category spillovers

| Status | Paper | Connection | URL / DOI |
|---|---|---|---|
| **A** | Sahni (2016), “Advertising Spillovers” | Randomized restaurant ads increase sales leads for similar, high-quality nonadvertised rivals; closest causal evidence for cue spillovers. | https://doi.org/10.1509/jmr.14.0274 |
| **A** | He & Klein (2023), “Advertising as a Reminder” | Lottery advertising primarily reminds prior/latent customers rather than informing them. | https://doi.org/10.1287/mksc.2022.1405 |
| **A** | Lewis & Nguyen (2015), “Display Advertising’s Competitive Spillovers to Consumer Search” | Randomized display exposure increases advertiser-branded and competitor-branded search, often more in aggregate for competitors. | https://doi.org/10.1007/s11129-015-9155-0 |
| **A** | Shapiro (2018), “Positive Spillovers and Free Riding in Advertising of Prescription Pharmaceuticals” | Antidepressant ads expand rivals’ demand; directly relevant to category-level cueing and free riding. | https://doi.org/10.1086/695475 |
| **A** | Lodish et al. (1995), “How T.V. Advertising Works” | 389 split-cable experiments document weak average lift and heterogeneity, motivating reminder/maintenance mechanisms. | https://doi.org/10.2307/3152042 |

### E. Targeting, incrementality, and empirical design

| Status | Paper | Connection | URL / DOI |
|---|---|---|---|
| **A** | Shapiro, Hitsch & Tuchman (2021), “TV Advertising Effectiveness and Profitability” | 288-brand benchmark and the quasi-random TV exposure design adapted by *Ads as Cues*. | https://doi.org/10.3982/ecta17674 |
| **A** | Blake, Nosko & Tadelis (2015), “Consumer Heterogeneity and Paid Search Effectiveness” | Large-scale experiments show selection makes observational ROI too high and that effects concentrate among new/infrequent users—a useful boundary condition versus cue effects among habitual users. | https://doi.org/10.3982/ECTA12423 |
| **A** | Johnson, Lewis & Nubbemeyer (2017), “Ghost Ads” | Practical experimental method for measuring incremental ad effects under optimized delivery. | https://doi.org/10.1509/jmr.15.0297 |
| **A** | Goldfarb & Tucker (2011) | Content-context match is a direct way to manipulate cue similarity, but privacy concerns can moderate targeting effects. | https://doi.org/10.1287/mksc.1100.0583 |

### F. Harmful products, health, and welfare

| Status | Paper | Connection | URL / DOI |
|---|---|---|---|
| **A/policy** | Saffer & Chaloupka (2000), “The Effect of Tobacco Advertising Bans on Tobacco Consumption” | Comprehensive bans reduce consumption more reliably than partial bans; category-wide restrictions matter when substitution across channels/brands is strong. | https://doi.org/10.1016/S0167-6296(00)00054-0 |
| **A/policy** | Saffer & Dave (2006), “Alcohol Advertising and Alcohol Consumption by Adolescents” | Links market-level ad exposure to youth participation and binge drinking; relevant to cue-amplified habits and vulnerable populations. | https://doi.org/10.1002/hec.1091 |
| **A/policy** | Dubois, Griffith & O’Connell (2018), “The Effects of Banning Advertising in Junk Food Markets” | Structural counterfactual includes brand spillovers, dynamic advertising, firm repricing, healthfulness, and welfare; closest policy complement. | https://doi.org/10.1093/restud/rdx025 |
| **A/policy** | Avery, Kenkel, Lillard & Mathios (2007), “Private Profits and Public Health” | Smoking-cessation ads increase quitting, including quitting without the advertised product—beneficial behavioral spillovers. | https://doi.org/10.1086/520065 |
| **A/policy** | Shapiro (2018), antidepressants | Shows that regulated/health-product ads can expand an entire treatment category, not only the advertised drug. | https://doi.org/10.1086/695475 |

## 8. Practical research agenda implied by the paper

The most discriminating experiment is a factorial design crossing: (i) prior target-brand consumption, (ii) randomized ad exposure, and (iii) randomized semantic/context similarity between the ad and target/rival consumption occasions. Measure own-brand sales, rival sales, category sales, dissimilar-category sales, unaided recall, and delayed effects. The signature of the cue model is not simply positive ad lift; it is a positive `exposure × target habit × similarity` effect plus negative effects on sufficiently dissimilar wants.

For campaign design, the paper predicts: use category-generic imagery to expand the category but expect leakage; use distinctive brand assets to capture retrieval and reduce competitor spillovers; target habitual customers when the objective is maintenance or consumption frequency; target light/nonusers when information or trial is the likely bottleneck; and test “dark periods” over long horizons because weekly sales lift can miss memory maintenance.

For harmful products, brand-level restrictions may be weak if surviving ads cue the entire category, surrogate/alibi brands preserve associative links, or consumers substitute toward similar harmful products. Policy evaluation should therefore measure category demand and cross-product spillovers—not only the advertised SKU—and should randomize or exploit variation in cue content as well as gross ad volume.[2][24]

## 9. Bottom line

*Ads as Cues* contributes a specific, falsifiable bridge between economics and marketing memory research. Its novelty is not the broad claim that ads remind consumers; it is the joint structure: **frequency × similarity × interference**. That structure predicts who responds, which competitors benefit, which unrelated goods lose demand, why famous brands keep advertising, and why welfare cannot be inferred from own-brand lift alone. The empirical evidence is broad and pattern-rich, though still quasi-experimental; the next decisive evidence should directly randomize cue similarity and exposure while observing individual consumption histories.

## Sources

[1] https://www.nber.org/papers/w34387
[2] https://shleifer.scholars.harvard.edu/sites/g/files/omnuum10626/files/2025-10/Ads.October_FINAL-1.pdf
[4] https://doi.org/10.2307/2118455
[5] https://doi.org/10.1086/258464
[6] https://doi.org/10.1086/260231
[7] https://doi.org/10.2307/2297705
[8] https://doi.org/10.1086/261235
[9] https://doi.org/10.1162/003355301556356
[10] https://doi.org/10.1093/qje/qjaa007
[11] https://doi.org/10.1086/673885
[12] https://doi.org/10.1162/qjec.2008.123.2.577
[13] https://doi.org/10.1086/209116
[14] https://doi.org/10.1177/002224378602300406
[15] https://doi.org/10.1509/jmr.14.0274
[16] https://doi.org/10.1287/mksc.2022.1405
[17] https://doi.org/10.3982/ecta17674
[22] https://doi.org/10.1086/695475
[24] https://doi.org/10.1093/restud/rdx025
[26] https://doi.org/10.1007/s11129-015-9155-0
[28] https://doi.org/10.2139/ssrn.903474
