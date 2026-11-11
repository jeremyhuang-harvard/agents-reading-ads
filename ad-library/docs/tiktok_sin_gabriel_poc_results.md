# TikTok sin-product ads → GABRIEL salience proof of concept

**Source manifest:** `data/raw/tiktok_sin_poc/run_id=2026-10-08T203658Z/manifest.json`
**Ads analyzed:** 5
**Transport model:** `gpt-5.6-sol` via Hermes OAuth
**Status:** Exploratory feature discovery; not a validated codebook or causal result.

## Candidate features

### Human figure prominence

- **Definition:** Extent to which a clearly visible human figure or face occupies the ad, measured by the approximate percentage of image area occupied by the largest person.
- **Potential pathway:** Large faces and bodies may attract attention and support person-centered memory encoding.
- **Example ads:** 1875911993674481, 1875988017549681
- **Suggested measure:** 0-100 rating

### Product or interface prominence

- **Definition:** Extent to which a product, device, or consumption interface is centrally placed, visually large, and unobscured.
- **Potential pathway:** A prominent product or interface may focus attention on the advertised action and make its use more mentally accessible.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730
- **Suggested measure:** 0-100 rating

### Visual dynamism

- **Definition:** Presence and intensity of compositional cues associated with movement or action, such as rotation, motion blur, floating objects, combat, or partial reveal.
- **Potential pathway:** Implied motion and action may capture attention and increase arousal.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730
- **Suggested measure:** 0-100 rating

### Color and luminance contrast

- **Definition:** Degree of visual separation produced by saturated colors, light-dark differences, or contrasting foreground and background elements.
- **Potential pathway:** High contrast may guide gaze toward specific objects, text, branding, or warnings.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730, 1875911993674481, 1875988017549681
- **Suggested measure:** 0-100 rating

### Distinctive object or texture density

- **Definition:** Number of visually distinctive objects, symbols, clothing patterns, or textures that could serve as separately recognizable details.
- **Potential pathway:** Repeated or unusual visual details may attract scrutiny and provide retrieval cues in memory.
- **Example ads:** 1875142511830242, 1876356852465730, 1875988017549681
- **Suggested measure:** count

### Partial concealment or ambiguity

- **Definition:** Presence of obscured eyes, cropped subjects, occluded objects, indistinct backgrounds, or other incomplete visual information.
- **Potential pathway:** Incomplete information may create uncertainty, invite closer inspection, or activate familiar interpretive schemas.
- **Example ads:** 1877909455644690, 1875911993674481, 1875988017549681
- **Suggested measure:** 0-100 rating

### Emotionally toned atmosphere

- **Definition:** Dominant affective presentation created by lighting, color, setting, facial presentation, or depicted action, coded into categories such as arousing, intimate, tense, celebratory, or neutral.
- **Potential pathway:** An emotionally toned atmosphere may influence arousal, mood, and affect-linked memory encoding.
- **Example ads:** 1875142511830242, 1875911993674481, 1875988017549681
- **Suggested measure:** category

### Short slogan prominence

- **Definition:** Presence of a concise slogan displayed or supplied as a primary message, with prominence assessed from text size, placement, contrast, and verbal brevity.
- **Potential pathway:** Short, distinctive phrasing may be easy to parse, rehearse, recognize, and retrieve.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730, 1875911993674481, 1875988017549681
- **Suggested measure:** 0-100 rating

### Direct viewer address

- **Definition:** Use of second-person pronouns, possessives, commands, or action statements that explicitly frame the viewer as the actor, owner, or beneficiary.
- **Potential pathway:** Direct address may increase self-relevance and connect the message to the viewer's identity or possible behavior.
- **Example ads:** 1875142511830242, 1877909455644690, 1875911993674481, 1875988017549681
- **Suggested measure:** boolean

### Reward or value claim

- **Definition:** Presence of an explicit or implied benefit involving payout speed, favorable odds, comparative value, winnings, or another desirable consumption outcome.
- **Potential pathway:** Concrete benefits may focus attention on anticipated rewards and make value comparison more accessible.
- **Example ads:** 1877909455644690, 1876356852465730
- **Suggested measure:** category

### Numeric offer or product information

- **Definition:** Count of visible numbers directly relevant to the advertised activity, such as betting odds, alcohol strength, prices, percentages, or quantities.
- **Potential pathway:** Specific numbers may provide concrete anchors for reward evaluation, product interpretation, or risk assessment.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730, 1875911993674481, 1875988017549681
- **Suggested measure:** count

### Immediacy or live-status cue

- **Definition:** Presence of words or symbols indicating that an event, offer, or outcome is live, current, hot, instant, direct, or otherwise time-sensitive.
- **Potential pathway:** Time-sensitive framing may create urgency and make immediate action or gratification more cognitively accessible.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730
- **Suggested measure:** category

### Identity and schema cue

- **Definition:** Presence of recognizable names, national flags, sports competitions, fashion styles, brand identifiers, or other symbols associated with a social identity, lifestyle, community, or cultural schema.
- **Potential pathway:** Identity-linked cues may activate existing knowledge, affiliations, aspirations, and category-based memories.
- **Example ads:** 1875142511830242, 1876356852465730, 1875911993674481, 1875988017549681
- **Suggested measure:** count

### Brand identifier repetition

- **Definition:** Number of distinct visible placements of the advertiser's name, logo, hashtag, branded color mark, or other recognizable brand identifier.
- **Potential pathway:** Repeated identifiers may strengthen brand recognition and provide multiple opportunities for visual encoding.
- **Example ads:** 1875142511830242, 1876356852465730
- **Suggested measure:** count

### Risk and regulatory disclosure prominence

- **Definition:** Visual prominence of warnings, responsible-use language, age restrictions, product-strength information, official marks, help resources, or descriptions of possible harms, considering size, contrast, placement, and specificity.
- **Potential pathway:** Prominent disclosures may cue risk, restricted participation, regulation, and concrete financial, social, health, or addiction harms.
- **Example ads:** 1875142511830242, 1877909455644690, 1876356852465730, 1875911993674481, 1875988017549681
- **Suggested measure:** 0-100 rating

## Sample limitations

- The proof of concept contains only five ads from two advertisers and two product categories, so it cannot establish the prevalence or generality of any feature.
- Three observations are Winamax betting ads and two appear to be closely related executions of the same Pernod Ricard campaign, limiting creative independence.
- The two alcohol analyses may describe the same or highly similar underlying visual, so treating them as independent evidence would overstate replication.
- All betting examples come from one advertiser, making it difficult to distinguish category-level features from Winamax-specific creative conventions.
- The ads span French and Spanish language contexts, but the sample is too small to separate linguistic, cultural, regulatory, and product-category differences.
- Some evidence comes from supplied titles or descriptions rather than visible image content, so image-level and metadata-level measures should be stored separately.
- The GABRIEL outputs use inconsistent family assignments for similar features, including concealed gaze and direct address, indicating a need for clearer coding rules.
- Several proposed constructs overlap, such as color contrast, visual dynamism, object prominence, and emotional atmosphere, and may require empirical tests of coder discrimination.
- The analyses identify plausible salience pathways but provide no gaze, recall, emotional-response, behavioral, or causal evidence.
- Disclosure prominence differs substantially across examples, but the current evidence does not include exact pixel area, legibility, exposure duration, or device context.

## Next validation steps

- Write a codebook specifying inclusion, exclusion, and boundary rules for each feature, with positive and negative examples.
- Separate features observable in the creative image from claims available only in titles, descriptions, landing pages, or platform metadata.
- Apply the taxonomy to a larger pilot containing multiple advertisers, campaigns, formats, languages, and both regulated and non-regulated product categories.
- Deduplicate near-identical creatives and preserve campaign identifiers so that reliability and prevalence are not inflated by repeated executions.
- Have at least two independent human coders annotate a stratified subset without seeing the GABRIEL labels.
- Estimate inter-coder reliability using an appropriate statistic for each measurement type, including agreement for booleans and categories and intraclass correlation for ratings.
- Review features with low reliability, merge constructs that coders cannot distinguish, and split constructs that repeatedly combine multiple observable dimensions.
- Test 0-100 ratings against simpler ordinal scales to determine whether fine-grained scores add reliable information.
- Add automated measurements where feasible, including text area, warning area, face area, object area, logo count, numerical-token count, color contrast, and centrality.
- Compare automated measurements, human annotations, and repeated GABRIEL calls to assess convergent validity and model-output stability.
- Evaluate whether the taxonomy covers held-out ads without frequently requiring new features, and record an explicit other or uncodable category.
- Only after measurement reliability is established, test associations with separate salience outcomes such as gaze allocation, unaided recall, recognition, perceived urgency, perceived reward, and perceived risk.

## Per-ad exploratory outputs

### 1875142511830242 — Les meilleures cotes sur Winamax

**Advertiser:** WINAMAX
**Category:** betting
**Summary:** A high-contrast Winamax betting ad centers a live-looking UFC matchup and visible odds within a composition of oversized combat-sport and broadcast cues.

- **Central smartphone focal point:** A large, tilted smartphone occupies the center and displays a UFC fight interface. — Central placement, scale, and rotation could draw attention toward the depicted betting interface.
- **Combat imagery:** Two fighters appear inside an octagon on the phone, while large black boxing gloves flank the foreground. — Physical confrontation and implied action could evoke arousal and cue memories associated with combat sports.
- **High-contrast brand palette:** Saturated red panels, black objects, and bold white lettering contrast with a pale gray background; the Winamax W logo appears at the upper right. — Strong color contrast and repeated red branding could attract gaze and support brand recognition.
- **Colloquial command-like slogan:** The large central red banner reads “BON GAMIN” in uppercase white type. — The short, unusual, prominently displayed phrase could be easy to encode and retrieve as a verbal cue.
- **Visible betting odds:** Decimal odds including 1,86 and 2,75 are shown beneath the fighters on the phone screen. — Specific numerical odds could focus attention on potential betting outcomes and cue reward-oriented comparison.
- **Live-broadcast cue:** A bright red “ON AIR” sign appears near the top, alongside a play-button icon and a red megaphone. — Broadcast and announcement symbols could cue immediacy, active coverage, or a time-sensitive event.
- **Named fighter matchup:** The phone interface shows Cyril Gane and Alex Pereira with French and Brazilian flags. — Recognizable names, national flags, and matchup framing could activate fighter, sport, or national-identity associations.
- **Prominent gambling-risk disclosure:** A yellow warning strip states that gambling can be dangerous and lists risks including debt, isolation, and addiction; an “-18” symbol appears above it. — The bright warning block and age restriction could cue risk, regulation, and restricted participation.

### 1877909455644690 — Les meilleures cotes sur Winamax

**Advertiser:** WINAMAX
**Category:** betting
**Summary:** The ad combines saturated green motion-like imagery, a partially revealed betting interface, and a large red-and-white instant-payment message with prominent gambling-risk warnings.

- **saturated color contrast:** A bright green background dominates the image, while the main message appears in white inside a vivid red outlined box. — Strong red-green-white contrast could draw visual attention toward the central promotional message.
- **dynamic reveal imagery:** Blurred green curtain-like forms and a red vertical shape partially obscure a tilted smartphone screen. — Partial occlusion and motion-like blur could create visual tension and direct attention toward the revealed betting interface.
- **instant payout claim:** The largest text reads "ON PAYE TON PARI DIRECT !" in bold uppercase lettering. — The explicit promise of immediate bet payment could cue reward availability and rapid gratification.
- **odds and betting interface:** A smartphone displays a betting interface with labels including "Buteurs," "Titulaires," and visible odds of "2,75." — Recognizable betting controls and numerical odds could cue gambling-related memories and action possibilities.
- **hotness cue:** A red badge labeled "HOT" appears beside the central payment message. — The "HOT" label could signal heightened immediacy, importance, or timeliness.
- **direct second-person address:** The phrase "TON PARI" addresses the viewer using the informal French second-person possessive "ton." — Direct personal address could increase perceived self-relevance by framing the bet as belonging to the viewer.
- **responsible-gambling warning:** A yellow footer states that gambling can be dangerous and lists risks including loss of money, family conflicts, and addiction; an "-18" icon and French government branding are also visible. — The contrasting warning panel, concrete harms, age restriction, and official branding could cue risk awareness and regulatory associations.

### 1876356852465730 — Les meilleures cotes sur Winamax

**Advertiser:** WINAMAX
**Category:** betting
**Summary:** The ad uses vivid tennis imagery, a prominent smartphone betting interface, live-broadcast cues, and high-contrast Winamax branding to make sports wagering visually central.

- **Oversized tournament headline:** The white text "LES MASTERS 1000" appears in very large type inside a bright red, outlined panel near the center-bottom. — Large typography and strong red-white contrast could capture attention and create a compact verbal cue for later recognition.
- **Floating tennis iconography:** Multiple fluorescent yellow tennis balls surround the phone, including balls marked "WTA," "ATP," and "ROLAND GARROS." — Repeated, brightly colored sport objects could quickly establish the tennis context and cue memories associated with major competitions.
- **Betting interface demonstration:** A large tilted smartphone displays a live tennis court, player names, match controls, and selectable numerical odds. — Showing concrete odds and betting controls could make the wagering action and its potential rewards more mentally accessible.
- **Live-broadcast cue:** A raised red sign reading "ON AIR" and a nearby play-button icon appear above the phone. — Broadcast and live-status symbols could emphasize immediacy and cue time-sensitive sports-viewing routines.
- **High-contrast action palette:** Saturated red panels, fluorescent yellow-green balls, dark phone graphics, and white text are set against a pale background. — Strong color contrast and isolated saturated elements could guide visual attention toward the headline, sports objects, and betting screen.
- **Repeated advertiser branding:** The Winamax "W" logo appears in a red square at the upper right, and "#WINAMAX" is printed vertically along the left edge. — Repeated brand identifiers in separate locations could support advertiser recognition and retrieval.
- **Best-odds value claim:** The supplied title and description both state "Les meilleures cotes sur Winamax" (the best odds on Winamax). — A comparative odds claim could cue value-seeking and make favorable potential returns more cognitively prominent.
- **Gambling-risk warning block:** A bright yellow footer contains a warning that gambling can be dangerous, mentions losses, family conflict, and addiction, provides the joueurs-info-service.fr resource and phone number, and is accompanied by an "-18" symbol. — The contrasting warning strip and age restriction could cue awareness of financial, social, addiction, and eligibility risks.

### 1875911993674481 — No hay un por qué. Ni falta que hace. Lo haces: Porque Sí.

**Advertiser:** PERNOD RICARD ESPAÑA SA
**Category:** alcohol
**Summary:** The ad combines a tightly cropped, fashion-styled male-presenting figure in a dark cinematic setting with a concise Spanish slogan centered on spontaneous action.

- **Close-up human figure:** A male-presenting person fills most of the vertically framed image, with the face and upper torso shown at close range. — The large human figure and face provide a prominent focal point that could capture attention and support person-based memory encoding.
- **Obscured gaze:** The person wears narrow dark sunglasses and looks downward, leaving the eyes and immediate object of attention unclear. — Concealed eyes and an ambiguous downward gaze could create visual uncertainty that encourages closer inspection.
- **Distinctive formal styling:** The figure wears a checked blazer, light collared shirt, dark tie, patterned tie section, and metal-framed sunglasses. — The coordinated and visually distinctive clothing can cue fashion, sophistication, or occasion-related schemas in memory.
- **Warm low-key lighting:** The scene uses dim illumination, deep shadows, and warm brown and amber tones. — The warm, shadowed palette could cue intimate, nocturnal, or cinematic associations and establish an emotionally toned context.
- **Tight partial cropping:** Parts of the person's head, body, and surrounding scene extend beyond the frame, while the background remains indistinct. — Incomplete visual information can concentrate attention on selected details and invite viewers to mentally complete the scene.
- **Reason-rejecting slogan:** The supplied title and description state: "No hay un por qué. Ni falta que hace. Lo haces: Porque Sí." — The explicit dismissal of a reason followed by "Porque Sí" creates a simple contrast that may be easy to rehearse and retrieve.
- **Second-person action language:** The slogan directly addresses the viewer through the second-person phrase "Lo haces" and uses short, punctuated sentences. — Direct address can increase perceived self-relevance, while the brief sentence structure may make the message easier to parse and remember.
- **Alcohol responsibility disclaimer:** Small white text at the bottom reads "Disfruta de un consumo responsable. 40º", states that the content is for adults and should not be forwarded to minors under 18, and labels it "Ficción publicitaria." — The alcohol-strength, adult-only, and responsible-consumption language can cue product-risk and age-restriction categories, although its small size reduces its visual prominence.

### 1875988017549681 — No hay un por qué. Ni falta que hace. Lo haces: Porque Sí.

**Advertiser:** PERNOD RICARD ESPAÑA SA
**Category:** alcohol
**Summary:** A tightly framed, low-light portrait combines a stylish male figure, warm nightlife-like tones, patterned formalwear, sunglasses, and a terse Spanish slogan centered on spontaneous action.

- **Tight face-and-torso framing:** The vertically cropped image is dominated by a close view of one man's face, shoulders, jacket, shirt, and tie. — A large human figure and partially visible face could concentrate visual attention and support person-centered encoding.
- **Concealed gaze:** The man wears dark, narrow sunglasses that obscure his eyes while his head is angled downward. — The hidden gaze and incomplete facial information could create visual ambiguity that invites closer inspection or retrieval of familiar style archetypes.
- **Retro formal styling:** The figure wears a checked suit jacket, wide-collared cream shirt, patterned tie, facial hair, and tinted glasses. — The coordinated, distinctive clothing could cue memories or schemas associated with retro fashion, nightlife, sophistication, or performative self-presentation.
- **Warm low-key lighting:** The scene uses dim illumination, deep shadows, and predominantly amber-brown tones. — Warm color and darkness could establish an intimate or nocturnal emotional tone and make illuminated facial and clothing details more conspicuous.
- **Dense pattern contrast:** Fine checks on the jacket contrast with the cream shirt, dark tie section, and ornate patterned tie section. — Multiple adjacent textures and high-frequency patterns could attract scrutiny and provide distinctive details for visual memory.
- **Reason-free action slogan:** The supplied title and description state: "No hay un por qué. Ni falta que hace. Lo haces: Porque Sí." — The short clauses, repetition of "por qué/porque," and justification-free action framing could make the phrase easy to rehearse while cueing spontaneity.
- **Alcohol responsibility disclaimer:** Small white text at the bottom includes "Disfruta de un consumo responsable," "40º," an adults-only notice, a warning not to forward to minors under 18, and "Ficción publicitaria." — The explicit alcohol-strength, age, and responsibility language could cue alcohol-related risk and regulatory associations, although its small size makes it visually subordinate.
