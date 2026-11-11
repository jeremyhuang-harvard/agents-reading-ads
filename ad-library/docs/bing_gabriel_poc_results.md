# Bing → GABRIEL salience-feature proof of concept

**Source manifest:** `data/raw/bing_poc/run_id=2026-10-08T195020.951683+0000/manifest.json`
**Ads analyzed:** 5
**Transport model:** `gpt-5.6-sol` via Hermes OAuth
**Status:** Exploratory feature discovery; not a validated codebook or causal result.

## Candidate features

### Destination or category identity cues

- **Definition:** Presence of recognizable objects, architecture, clothing, symbols, settings, or transaction artifacts that visually indicate the advertised destination, product category, or service category.
- **Potential pathway:** Concrete identity cues may support rapid categorization, recognition, and retrieval of associated knowledge or memories.
- **Example ads:** 71056221548107, 71674697305347, 80127133828226, 71743416592197
- **Suggested measure:** 0-100 rating

### Explicit category or destination naming

- **Definition:** The title, description, or image text explicitly names the advertised destination, product category, or service category; record whether present and how many times it appears.
- **Potential pathway:** Repeated or explicit labels may reinforce category recognition and make related concepts easier to encode and retrieve.
- **Example ads:** 71056221548107, 71674697305347, 80127133828226
- **Suggested measure:** count

### Saturated or category-congruent color palette

- **Definition:** The creative uses highly saturated colors or a coherent palette conventionally associated with the depicted category or destination, such as blue-white coastal imagery or gold-orange desert imagery.
- **Potential pathway:** Color saturation and category-congruent color patterns may capture attention, create visual distinctiveness, and reinforce associative encoding.
- **Example ads:** 71056221548107, 71674697305347, 71743416592197
- **Suggested measure:** 0-100 rating

### Figure-ground contrast

- **Definition:** Key people, objects, text, or offer elements are visually separated from their background through differences in brightness, color, sharpness, or bounded panels.
- **Potential pathway:** Strong figure-ground separation may direct attention toward focal content and reduce competition from surrounding details.
- **Example ads:** 71056221548107, 79989681308796, 71674697305347, 80127133828226
- **Suggested measure:** 0-100 rating

### Compositional attention guidance

- **Definition:** Visible lines, paths, gaze directions, hand positions, shadows, or perspective cues converge on or lead toward a focal object, person, or region.
- **Potential pathway:** Directional composition may guide visual attention and establish a clear sequence for scanning the ad.
- **Example ads:** 71056221548107, 79989681308796, 71674697305347, 80127133828226
- **Suggested measure:** 0-100 rating

### Expansive scenic imagery

- **Definition:** A large portion of the creative depicts an open landscape, coastal panorama, distant horizon, or elevated overview rather than a tightly cropped scene.
- **Potential pathway:** Visual scale and spatial openness may encourage exploration, increase scene distinctiveness, and support mental simulation of being in the depicted environment.
- **Example ads:** 71056221548107, 71674697305347, 71743416592197
- **Suggested measure:** 0-100 rating

### Positive experiential imagery

- **Definition:** The ad visibly depicts or textually invokes pleasurable experiences such as sunshine, relaxation, scenic beauty, recreation, satisfaction, adventure, or freedom.
- **Potential pathway:** Positive experiential cues may evoke emotion and make anticipated benefits or desired future states more accessible.
- **Example ads:** 71056221548107, 79989681308796, 71674697305347, 71743416592197
- **Suggested measure:** category

### Positive human affect

- **Definition:** One or more visible people display smiles, relaxed expressions, or other clearly positive facial or bodily affect.
- **Potential pathway:** Positive expressions may provide an immediate emotional cue and associate the depicted product or activity with satisfaction or reassurance.
- **Example ads:** 79989681308796
- **Suggested measure:** 0-100 rating

### Social interaction or joint activity

- **Definition:** Two or more people visibly coordinate attention, exchange an object, travel together, or participate in a shared activity.
- **Potential pathway:** Social interaction may activate schemas involving trust, collaboration, household decisions, service encounters, or shared experiences.
- **Example ads:** 79989681308796, 80127133828226, 71743416592197
- **Suggested measure:** category

### Everyday-life relevance cues

- **Definition:** The creative places the advertised product or service within a familiar domestic, purchasing, payment, work, or household-decision context.
- **Potential pathway:** Familiar settings and actions may increase perceived personal relevance and cue memories of routine decisions or responsibilities.
- **Example ads:** 79989681308796, 80127133828226
- **Suggested measure:** 0-100 rating

### Concrete monetary or price benefit

- **Definition:** The ad presents a specific monetary amount, low-price claim, discount, savings claim, free-product claim, or other explicit price advantage.
- **Potential pathway:** Concrete financial benefits may attract attention, activate reward or savings goals, and provide a simple numeric or verbal memory cue.
- **Example ads:** 71056221548107, 80127133828226
- **Suggested measure:** category

### Bundled convenience proposition

- **Definition:** The offer combines multiple components or services into one package, such as flight plus hotel, or explicitly describes the offer as all-inclusive.
- **Potential pathway:** Bundling may foreground convenience, reduced planning effort, and perceived package value.
- **Example ads:** 71056221548107, 71674697305347
- **Suggested measure:** boolean

### Choice range or quality-tier framing

- **Definition:** The ad explicitly presents multiple product levels, quality tiers, rankings, or comparison options, such as a star-rating range or a top-N list.
- **Potential pathway:** An explicit range or ranking may cue comparison, broaden perceived relevance, and signal that the viewer can select among alternatives.
- **Example ads:** 80127133828226, 71743416592197
- **Suggested measure:** category

### Direct action language

- **Definition:** The ad addresses the viewer with an imperative, direct question, exclamation, or explicit invitation to perform an action or imagine a desired experience.
- **Potential pathway:** Direct language may orient attention toward a behavior, goal, or self-relevant question and increase the prominence of the requested action.
- **Example ads:** 80127133828226, 71743416592197
- **Suggested measure:** category

### Qualification or conditions disclosure

- **Definition:** The creative contains text indicating conditions, eligibility requirements, limits, exclusions, or a need to consult additional terms.
- **Potential pathway:** Qualification language may activate risk or restriction considerations, although its practical prominence depends on size, contrast, and placement.
- **Example ads:** 80127133828226
- **Suggested measure:** 0-100 rating

## Sample limitations

- The sample contains only five ads, so feature prevalence, co-occurrence, and category boundaries cannot be estimated reliably.
- The ads come from only two advertiser names and are concentrated in travel and financial-service categories.
- Three of the five ads are travel creatives from the same advertiser, making repeated destination imagery and package language partly advertiser- and category-specific.
- The input consists of prior model-generated analyses rather than independent coding of the original creatives, so the taxonomy may inherit model omissions, interpretation errors, or inconsistent granularity.
- Some evidence comes from titles and descriptions while other evidence comes from image content; these modalities were not consistently separated in the source labels.
- Features that appear only once, including positive facial affect and conditions disclosure, are provisional and may not generalize.
- The examples do not include video, animation, audio, carousel structure, landing pages, or temporal presentation features.
- The sample provides no exposure, attention, recall, emotion, click, conversion, or audience-response data, so salience pathways remain hypotheses rather than validated effects.
- The creatives are French-language ads, and some textual features may depend on language, market, or cultural context.
- Several proposed features overlap conceptually, such as positive experiential imagery, destination identity cues, and saturated color palettes; discriminant validity has not been established.

## Next validation steps

- Develop a codebook with inclusion and exclusion rules, modality labels, and positive and negative examples for every candidate feature.
- Separate image-derived, embedded-text, title, description, and metadata measurements so modality-specific effects can be examined.
- Apply the taxonomy to a larger and more diverse sample spanning advertisers, product categories, countries, languages, and creative formats.
- Use at least two independent human coders on a stratified subset and assess inter-rater reliability for boolean, categorical, count, and rating measures.
- Compare human annotations with fresh blinded GABRIEL annotations to identify systematic model disagreement and revise ambiguous definitions.
- Test whether closely related features can be coded independently or should be merged, split, or organized into higher-order dimensions.
- Record objective companion measures where feasible, including color saturation, luminance contrast, face count, text area, font-size ratios, monetary-value count, and disclosure-area share.
- Measure feature prevalence and co-occurrence before using the taxonomy in predictive or experimental analyses.
- Oversample underrepresented creative types, including risk-focused ads, urgency claims, negative affect, testimonials, scarcity, social proof, and text-only designs.
- Validate candidate salience measures against independent outcomes such as gaze allocation, viewing time, unaided recall, recognition, emotional ratings, and perceived personal relevance.
- Treat advertiser, category, country, language, and format as contextual variables to distinguish reusable features from campaign-specific creative conventions.
- Pre-register any later confirmatory coding or experiments after refining the taxonomy on a separate exploratory sample.

## Per-ad exploratory outputs

### 71056221548107 — La Grèce À Petit Prix

**Advertiser:** Karavel Comptabilité Fournisseurs
**Summary:** The advertisement combines an iconic, brightly lit Greek island scene with low-price and all-inclusive travel language to make the destination and bundled offer visually and conceptually prominent.

- **Iconic Greek destination cues:** Whitewashed hillside buildings, blue doors, the Aegean-like sea, and several visible Greek flags. — These recognizable national and architectural cues could rapidly activate stored associations with Greece and Greek-island tourism.
- **Blue-white color coding:** The image is dominated by deep blue sky and sea set against bright white buildings, with a vivid blue door on the right. — Strong color contrast could attract attention while reinforcing a visually distinctive Greece-related schema.
- **Vivid floral foreground:** Large clusters of saturated pink, purple, red, and white flowers occupy the immediate foreground. — The saturated colors and near-field placement could draw the eye first and create a memorable visual anchor.
- **Sunny coastal leisure imagery:** The scene shows clear blue skies, bright sunlight, calm water, and a scenic coastal settlement. — These visible vacation cues could evoke positive leisure, warmth, escape, or relaxation associations.
- **Immersive pathway perspective:** A stone walkway begins in the lower-right foreground and recedes between the buildings toward the center of the scene. — The converging path could guide visual attention into the image and support mental simulation of moving through the destination.
- **Low-price framing:** The title states "La Grèce À Petit Prix," explicitly presenting Greece as available at a low price. — Explicit affordability language could cue value-seeking goals and make potential monetary savings more cognitively accessible.
- **All-inclusive bundle:** The description states "offres tout compris" and specifies "Vol + Hôtel inclus !" — Combining flight and hotel into one inclusive offer could make convenience and package value especially easy to notice and remember.

### 79989681308796 — Comparateur Assurance de Prêt

**Advertiser:** SAS MEILLEURTAUX
**Summary:** A warmly lit domestic scene centers on a smiling adult pair jointly viewing a laptop, visually framing online comparison as a calm, collaborative household activity.

- **Joint screen attention:** Both adults lean toward the open laptop and direct their gaze toward its screen. — Converging gaze and body orientation could guide viewers' attention toward the laptop as the scene's focal object.
- **Positive facial affect:** The woman is broadly smiling, while the man has a slight relaxed smile. — Visible positive expressions could provide an emotionally pleasant cue and make the depicted activity easier to associate with satisfaction.
- **Collaborative decision context:** Two adults sit closely together and appear to examine the same laptop content. — The shared activity could cue memories or schemas involving joint household research and decision-making.
- **Domestic setting:** The pair is seated at a table in a bright home interior with bowls, jars, chairs, shelving, and plants. — Familiar household objects could increase perceived personal relevance by linking the advertised service to everyday home life.
- **Adult life-stage representation:** The image features two adults, including a gray-haired man wearing glasses and a younger-looking woman. — Visible age and life-stage cues could prompt self-recognition or retrieval of memories involving adult financial and household responsibilities.
- **Warm coordinated color palette:** The subjects wear orange and muted reddish-brown tops against a softly lit, neutral interior. — Warm clothing colors contrast with the pale background and could draw attention to the people while supporting a visually cohesive scene.
- **Shallow-focus human emphasis:** The two adults and laptop are relatively sharp, while foreground containers and background furnishings are blurred. — Selective focus could reduce competing detail and concentrate attention on the people and their interaction with the device.

### 71674697305347 — Le Maroc All Inclusive

**Advertiser:** Karavel Comptabilité Fournisseurs
**Summary:** A warm, expansive desert scene with camels and traditionally dressed guides visually frames Morocco as a distinctive travel experience, while the metadata emphasizes an all-inclusive flight-and-hotel package.

- **Expansive desert landscape:** The image is dominated by broad, rolling sand dunes extending toward the horizon. — The large open setting could attract attention through visual scale and cue stored associations with deserts, travel, and Morocco.
- **Camel caravan cue:** Two loaded camels are prominently positioned in the lower center of the image. — Camels provide a concrete destination-associated cue that could facilitate recognition and retrieval of Morocco or desert-tourism memories.
- **Traditional dress cue:** Two people walking beside the camels wear long robes, and one has a white head covering. — Visible clothing associated with the depicted setting could make the destination feel culturally specific and personally relevant to viewers interested in cultural travel.
- **Warm golden palette:** Golden sunlight and orange-brown sand dominate nearly the entire image. — The warm color palette could evoke associations with sunlight, warmth, relaxation, or adventure and make the scene visually cohesive.
- **Dramatic directional lighting:** Low-angle sunlight creates strong highlights across the dunes and long, dark shadows from the people and camels. — High light-dark contrast and elongated shadows could guide attention toward the caravan and strengthen the scene's visual distinctiveness.
- **All-inclusive bundle framing:** The title states "Le Maroc All Inclusive," and the description says "Vol + Hôtel inclus !" — Combining flight and hotel into one explicitly inclusive offer could cue convenience, package value, and reduced planning effort.
- **Explicit Morocco destination label:** Both the title and description explicitly name "Le Maroc." — Repeated destination naming could reinforce category recognition and retrieve existing knowledge, preferences, or memories associated with Morocco.

### 80127133828226 — Top 10 Banques en Ligne 2026

**Advertiser:** SAS MEILLEURTAUX
**Summary:** The ad combines a prominent bank-switching command, a large monetary incentive, and a familiar card-payment scene to make the financial offer visually immediate and easy to encode.

- **Direct switching command:** The upper-left headline reads “Changez Votre banque !” in large white text on red and black blocks. — The imperative phrasing and exclamation mark could orient attention toward a specific action and cue thoughts about changing banks.
- **Large monetary reward:** The central offer prominently states “Jusqu’à 280€ Offerts,” with “280€” and “Offerts” highlighted in reddish-brown type. — A concrete euro amount and the promise of something offered could attract attention and support memory for the financial benefit.
- **Free-product cue:** The main text includes “une carte bancaire Gratuite,” with “Gratuite” capitalized and displayed in large bold type. — The explicit zero-price cue could activate reward or savings associations distinct from the cash incentive.
- **Payment-action imagery:** Two hands exchange or present a bank card directly above a payment terminal. — The recognizable transaction scene could rapidly cue memories and schemas related to card payments, banking, and everyday purchases.
- **Human hand interaction:** The image centers on two people’s hands reaching toward each other with the card between them. — The implied interpersonal exchange and converging hand positions could guide visual attention toward the card and transaction.
- **High-contrast text panels:** White lettering appears on red and black headline blocks, while the main offer is placed inside a large white rectangle over the photographic background. — Strong figure-ground contrast and boxed text could increase visual prominence and make the key claims easier to scan and encode.
- **Prominent brand signature:** The white Meilleurtaux name and geometric logo occupy the lower-right corner against the darker tabletop and background. — The large, isolated brand mark could facilitate advertiser recognition and link the offer to the Meilleurtaux identity.
- **Conditional-offer disclosure:** Small text in the lower-left corner reads “*Voir conditions sur le site.” — The conditions notice could cue qualification or restriction, although its small size makes it less visually prominent than the reward claims.

### 71743416592197 — Hôtels et Resorts 3* à 5*

**Advertiser:** Karavel Comptabilité Fournisseurs
**Summary:** The advertisement combines a vivid Mediterranean coastal panorama with Tunisian architectural cues and travel language emphasizing sunshine, freedom, and varied hotel quality.

- **Saturated sea-and-sky palette:** Bright turquoise water and a large expanse of clear blue sky dominate the image. — The saturated blue field and strong color coherence could capture attention and cue memories associated with coastal travel.
- **Scenic elevated viewpoint:** The scene is photographed from above, revealing white buildings, a marina, open water, and the distant horizon. — The expansive overview could encourage visual exploration and make the destination scene easier to encode as a coherent spatial image.
- **Distinctive white-and-blue architecture:** Whitewashed buildings feature vivid blue doors, windows, gates, railings, and domed roofs. — The repeated architectural color pattern could function as a recognizable destination cue and support place-related memory retrieval.
- **Warm-weather nature cues:** The image includes bright sunlight, dense green vegetation, a palm tree, calm water, and a largely clear sky. — These visible cues could evoke pleasant warm-weather associations and reinforce the description's references to sea and sun.
- **Visible human presence:** A small group of pedestrians is shown walking together along the foreground street. — The people provide a social and human-scale element that could help viewers imagine activity within the destination.
- **Maritime leisure cues:** A marina with numerous small boats is visible beside the turquoise sea. — Boats and waterfront access could cue recreational travel possibilities and anticipated leisure.
- **Freedom-oriented travel language:** The supplied description asks, "Envie de mer, soleil et liberté ?" and invites the viewer to head to Tunisia. — The direct question and the words for sea, sun, and freedom could activate desired vacation experiences and personal travel goals.
- **Broad hotel-quality range:** The supplied title advertises hotels and resorts rated from three to five stars. — The explicit quality range could increase perceived relevance across different accommodation preferences and cue comparison of comfort levels.
