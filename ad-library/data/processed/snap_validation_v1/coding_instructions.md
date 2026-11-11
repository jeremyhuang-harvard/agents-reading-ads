# Blinded Snapchat validation coding instructions

Code only what is observable in the supplied creative. Do not use the filename to infer category, advertiser, exposure, country, or campaign metadata.

- Boolean values: `1` present, `0` observably absent, blank only when genuinely unobservable.
- Ratings: integer 0–100 using the field anchors. Zero means observable absence, not missingness.
- For blanks, complete the corresponding `__unknown_reason` field.
- Positive booleans and ratings of 80 or above require concise visible/audible evidence.
- Watch complete videos with sound when available. Do not code from thumbnails alone.
- Code each creative independently before consulting another coder.

## Fields

### `gambling_ad_present` — boolean

The creative promotes wagering, sportsbook, casino, lottery, poker, odds, prediction-market trading, or a gambling-linked offer.

### `financial_inducement_present` — boolean

A bonus, free bet, odds boost, cashback, matched deposit, bonus credit, prize, or similar wagering-linked incentive is visibly or audibly offered.

### `risk_minimization_claim` — boolean

The creative frames wagering or an offer as risk-free, no-sweat, protected, money-back, safe, or otherwise downplays potential loss.

### `social_normalization_present` — boolean

The creative explicitly presents gambling as common, routine, expected, socially approved, or integral to ordinary participation.

### `fandom_identity_present` — boolean

The creative links wagering to team loyalty, supporter identity, or fuller participation in a sporting event.

### `celebrity_endorsement_present` — boolean

A recognizable public figure endorses, recommends, demonstrates, narrates, or normalizes the promoted product. Mere appearance without an endorsing role is not enough.

### `urgency_scarcity` — rating_0_100

How strongly the creative pressures the viewer to act soon through deadlines, countdowns, live-event timing, scarcity, or loss of opportunity.

- **0:** No urgency or scarcity.
- **25:** Weak generic action prompt.
- **50:** Explicit time-limited or live-event framing, not dominant.
- **75:** Prominent or repeated deadline, countdown, or imminent-event pressure.
- **100:** The creative is organized around immediate action and loss of opportunity.

### `betting_actionability` — rating_0_100

How directly a viewer can translate the creative into a wager using visible selections, odds, promo code, direct CTA, or procedural clarity. For non-gambling ads, rate observable betting actionability as zero.

- **0:** No path to a wager.
- **25:** Brand or product shown with little procedural direction.
- **50:** Clear CTA or offer but limited wager detail.
- **75:** Direct CTA plus useful offer, odds, or selection information.
- **100:** A nearly complete, immediate path from creative to a specific wager.

### `sensory_salience` — rating_0_100

Visual and auditory intensity from contrast, motion, typography, editing pace, sound, repetition, and foreground prominence.

- **0:** Visually and aurally minimal.
- **25:** Some contrast or motion but subdued.
- **50:** Moderately attention-grabbing.
- **75:** Strong motion, contrast, sound, or emphatic typography.
- **100:** Extremely intense and continuously attention-demanding.

### `arousal_excitement` — rating_0_100

Suspense, celebration, crowd energy, rapid pacing, emphatic voice or music, and emotional intensity.

- **0:** No excitement or arousal.
- **25:** Mildly upbeat.
- **50:** Clearly energetic or suspenseful.
- **75:** Strong excitement, celebration, or rapid pacing.
- **100:** Extreme sustained arousal dominates the creative.

### `positive_affect` — rating_0_100

Joy, humor, triumph, anticipation, pleasure, or other positive feeling connected to the promoted product or action.

- **0:** No positive affect.
- **25:** Mild pleasant tone.
- **50:** Clearly positive or enjoyable.
- **75:** Strong joy, humor, triumph, or anticipation.
- **100:** Intense positive emotion dominates the creative.

### `social_proof_normalization` — rating_0_100

How strongly the creative portrays gambling as common, socially approved, routine, or integral to ordinary social participation. For non-gambling ads, rate gambling normalization as zero.

- **0:** No gambling normalization.
- **25:** Weak contextual suggestion of normality.
- **50:** Gambling is clearly presented as ordinary or socially embedded.
- **75:** Strong social approval or participation framing.
- **100:** The central message is that gambling is expected or universally shared.

### `sport_fandom_linkage` — rating_0_100

How strongly wagering is fused with team loyalty, supporter identity, event enjoyment, or being a real fan. For non-gambling ads, rate wagering–fandom linkage as zero.

- **0:** No wagering–fandom linkage.
- **25:** Sport appears but identity linkage is weak.
- **50:** Wagering is connected to following or enjoying sport.
- **75:** Strong fan-identity or team-loyalty framing.
- **100:** Wagering is portrayed as essential to authentic fandom.

### `responsible_gambling_prominence` — rating_0_100

Perceptual prominence and comprehensibility of safer-gambling messaging, considering size, contrast, duration, placement, and audibility. For creatives with no such message, rate zero.

- **0:** No observable safer-gambling message.
- **25:** Present but difficult to notice or understand.
- **50:** Noticeable with moderate clarity.
- **75:** Prominent, legible or audible, and easy to understand.
- **100:** Safer-gambling messaging is a dominant element.

### `terms_prominence` — rating_0_100

Perceptual prominence and comprehensibility of material offer terms, considering legibility, audibility, duration, contrast, placement, and speech speed. If no offer terms are relevant or observable, use zero and explain when needed.

- **0:** No observable material terms.
- **25:** Terms are present but difficult to notice or understand.
- **50:** Terms are moderately visible or audible.
- **75:** Terms are prominent and comprehensible.
- **100:** Material terms are a dominant element.

### `age_restriction_prominence` — rating_0_100

Perceptual prominence and comprehensibility of an age eligibility or exclusion message. If absent, rate zero.

- **0:** No observable age restriction.
- **25:** Present but difficult to notice.
- **50:** Moderately visible or audible.
- **75:** Prominent and clear.
- **100:** Age restriction is a dominant element.
