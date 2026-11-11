# Project vision: directional celebrity–brand associations

## Status

This document preserves the user's initial theory and proposed research program. Named campaigns, commercial relationships, papers, and data-access claims are **leads requiring verification**, not established facts in this repository.

## Core idea

Advertising can work by linking products to familiar concepts, memories, emotions, people, and mental models. The proposed mechanism combines three ideas:

1. **Ads as associative cues.** An ad activates a representation that can retrieve memories and meanings related to the advertised product.
2. **Competitive interference.** If the activated representation is a shared product category—such as sportswear or sportsbooks—the cue may also retrieve rival brands, weakening the advertiser's exclusive claim on attention and memory.
3. **Directional representativeness.** Associations between a celebrity and a brand need not be symmetric. A celebrity may strongly retrieve a brand, while the brand does not strongly retrieve that celebrity.

The central conjecture is that an advertiser can reduce competitive interference by attaching itself to a distinctive person, scene, or cultural topic that competitors do not already “own.” A generic sportswear execution may activate sportswear and therefore Nike as well as Adidas. A Tate McRae execution may create a more exclusive route from Tate McRae to Adidas because Nike has little claim on Tate McRae. The reverse route—Adidas to Tate McRae—may remain weak.

This yields a proposed distinction:

- **Category route:** ad → product category → advertiser and competitors.
- **Distinctive-association route:** ad or celebrity → distinctive person/topic → advertiser, with less retrieval of competitors.

The theory is not that all celebrity advertising avoids interference. It predicts that avoidance depends on how distinctive, asymmetric, and uncontested the celebrity–brand link is. LeBron–Nike is proposed as relatively symmetric and category-congruent; Tate McRae–Adidas is proposed as more asymmetric and profession-orthogonal. A provocative campaign, such as the user's Sweeney/Novig example, may also move the brand into cultural or sexual-attention topics that are distant from the conventional sportsbook representation.

## User-supplied examples to investigate

### Public or declared relationships

- Tate McRae / Adidas
- Lady Gaga / Polaroid
- LeBron James / Nike
- Sweeney / Novig

### Implicit or private appearances

- Leonardo DiCaprio wearing Rolex or other luxury watches
- Celebrities photographed or posted wearing identifiable clothing, jewelry, watches, accessories, or other consumer goods without an immediately visible advertisement or disclosure

These examples must be classified by evidence rather than assumption: formal ambassador relationship, disclosed paid partnership, gifted product, affiliate relationship, editorial styling, self-purchase, incidental appearance, or unknown.

## Long-run data asset

The proposed corpus joins four linked objects:

1. **Appearance ledger** — literal celebrity, product, logo, object, scene, date, source, geometry/prominence, duration, text/audio evidence, and media provenance.
2. **Relationship ledger** — dated evidence of ambassador, sponsorship, gifting, affiliate, ownership, styling, or other material connection; `unknown` remains distinct from organic.
3. **Amplification graph** — links from an original appearance to paparazzi coverage, tabloids, fan accounts, reviewers, shopping-identification posts, brand reposts, and other downstream identification.
4. **Exposure or response data** — served/viewed/attended exposure, search, memory, attribution, choice, or sales outcomes only where actually observable.

Potential source families include official campaign materials, brand and celebrity social accounts, platform disclosures, tabloids, paparazzi archives, entertainment and fashion coverage, fan accounts, “what they wore” identification sites, and repost networks. Collection must be evaluated source by source for legality, terms, licensing, retention, and reproducible access.

## Representation and measurement program

Build separate representations for:

- celebrities or influencers;
- brands;
- product categories;
- campaign creative and surrounding topics;
- public memories, traits, occupations, values, emotions, and contexts associated with each entity.

The user proposes adapting ideas from a Suproteem Sarkar paper on representing companies; the exact paper and applicable method must be identified and verified.

A useful representation should support more than a symmetric embedding distance. The mechanism is directional, so the project should measure quantities such as:

- probability or rank of retrieving brand `B` given celebrity `C`;
- probability or rank of retrieving celebrity `C` given brand `B`;
- category and competitor retrieval given a creative or cue;
- uniqueness of the celebrity/topic to the focal brand relative to rivals;
- change in directional retrieval before and after a campaign;
- congruence between the celebrity's prior representation and the product category;
- distance from the category's dominant or incumbent-associated topics.

Possible instruments include search and co-mention patterns, temporal text corpora, knowledge graphs, directed language-model elicitation, associative human surveys, recognition and recall experiments, and versioned multimodal embeddings. Embedding geometry alone cannot establish a directed association or a causal campaign effect.

## Main hypotheses

1. **Association asymmetry:** Campaigns can increase `celebrity → brand` retrieval much more than `brand → celebrity` retrieval.
2. **Interference reduction:** A distinctive celebrity or cultural cue produces less rival retrieval than a generic category cue.
3. **Congruence gradient:** Highly category-congruent ambassadors create stronger two-way links but may also activate competitors; orthogonal ambassadors create weaker category activation and potentially more exclusive one-way links.
4. **Distinctiveness:** The interference advantage is larger when rivals have little prior association with the celebrity or topic.
5. **Amplification:** Tabloid, paparazzi, fan, reviewer, and shopping-identification coverage can transform an initially implicit appearance into an explicit informational treatment.
6. **Provenance heterogeneity:** Declared sponsorship, undisclosed material connections, and genuinely organic use may have different credibility, memory, and spillover effects.

## Distinctive empirical signature

Evidence for the focal mechanism requires more than showing that celebrities and brands co-occur. The sharp pattern is:

- a campaign or appearance strengthens directional retrieval from the celebrity/topic to the focal brand;
- the reverse link remains materially weaker;
- focal-brand retrieval rises without an equivalent increase in category or competitor retrieval;
- generic category-focused creatives produce more competitor retrieval than matched distinctive-celebrity creatives;
- these differences are strongest where the celebrity/topic was initially distinctive to the focal brand.

## Causal and descriptive boundaries

The observational corpus can establish appearances, documented relationships, amplification paths, association dynamics, and descriptive sequencing. It cannot by itself show what a viewer saw, noticed, remembered, or purchased, nor that the celebrity caused a change in demand.

A later causal program could use matched creative experiments that vary only the cue:

- generic product/category execution;
- focal celebrity execution;
- category-congruent celebrity;
- profession-orthogonal celebrity;
- focal celebrity with and without relationship disclosure;
- original implicit appearance versus later explicit identification.

Outcomes would include focal-brand retrieval, rival retrieval, category retrieval, delayed memory, attribution, liking, choice, and willingness to pay.

## Immediate open decisions

1. Identify and verify the exact Shleifer et al., Sahni et al., and Sarkar papers and extract their mechanisms and measures.
2. Choose a bounded first market or product class rather than scraping all celebrity–product appearances at once.
3. Decide whether the first pilot begins with declared campaigns, implicit appearances, or a matched sample of both.
4. Define the observation unit and stable identifiers for celebrities, brands, appearances, relationships, media assets, and amplification events.
5. Select legally accessible sources and test whether their media, metadata, and historical coverage can be retained reproducibly.
6. Predefine a directed-association measure that is not merely symmetric embedding similarity.
7. Specify a small human or model validation exercise before scaling collection.
