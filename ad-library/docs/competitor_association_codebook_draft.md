# Competitor ad association codebook: discovery draft (v0.1, not frozen)

Derived from the open-ended discovery pass `data/processed/competitor_discovery_v1/` (100 unique creatives, 20 per firm, seed 2026102101, Sonnet via Claude Code, prompt `competitor_discovery_prompt_v1.0.0`, 100/100 parsed). Firm identities were hidden from the model. Videos were coded from three still frames without audio, so video labels are incomplete.

Discovery labels are exploratory. Categories become measurements only after review, freezing, and human spot-checks.

## A. Context cues attached to the brand (multi-select, with names)

- Sport: football, horse racing, tennis, basketball, motorsport, combat sports, cycling, poker/casino.
- Competition level: national team or major tournament, European club competition, domestic league, single named fixture, racing event, poker tournament.
- Named entities: fixture, teams, athletes, celebrities, events, dates.
- Occasion: match day or live, weekend, holiday or festive, summer leisure, none.

## B. Borrowed meaning (each coded present/absent, prominence 0-3, quoted evidence)

| # | Category | Typical discovery evidence |
|---|---|---|
| 1 | Club fandom and rivalry | team shirts, "PSG vs OM", club identity |
| 2 | National pride | "TOUS BLEUS", national shirts, World Cup |
| 3 | Big-event prestige and spectacle | Champions League final, Arc de Triomphe, stadium lights |
| 4 | Star-athlete glamour | named strikers, drivers, NBA stars |
| 5 | Expertise and informed prediction | tips, stats, pundits, ready-made combos |
| 6 | Humour and wordplay | "DEMBOUZINHO", puns on club names |
| 7 | Street or youth culture | graffiti, colloquial French, urban styling |
| 8 | Creator or influencer authenticity | person speaking to camera, creator format |
| 9 | Sociability and community | friends, watching together, belonging |
| 10 | Safety and risk reduction | "remboursé", "garanti", cashback, abandonment protection |
| 11 | Money, wealth, and jackpot | 3D "100€", "200 000 €", gold, luxury |
| 12 | Official legitimacy and sponsorship | official partner, stadium boards, trusted operator |
| 13 | Tradition and heritage | horse-racing heritage, legendary races |
| 14 | Play, games, and collectibles | trading-card frames, video-game style, prediction contests |
| 15 | Product features and convenience | cash out, fast withdrawal, bet builder |
| 16 | Leisure occasion | summer, holidays, festive celebration |
| 17 | Strength and masculinity | fight night, power imagery |

## C. Primary framing of betting (single choice)

Companion to watching sport; skill or prediction contest; low-risk trial or deal; reward or money-making; social or community activity; product or service utility; competition entry; not shown.

## D. Offer, payoff, and risk

- Offer type: first-bet refund or guarantee, cash bonus, boosted odds, no-deposit bonus, prize pool or jackpot, product feature, none.
- Amount, prominence 0-3, deadline or urgency.
- How payoffs are depicted; whether a winning scenario is shown.
- Risk or probability information; "guaranteed" or "risk-free" language.

## E. Prominence and execution

- Most prominent element and first-noticed element: offer amount, match or teams, person, headline, odds, logo, product interface, scene.
- Template: match card, offer banner, person to camera, scenic photograph, app screenshot, poster.
- Tone, brand prominence, visual density.

## F. Regulatory cues

The 16 regulatory fields from the validation codebook (`config/snap_validation_codebook_v1.json`) are reused unchanged so the full run can be checked against the human-coding pilot.

## Firm patterns in the discovery sample (descriptive, n=20 per firm, not estimates)

- **bet365:** national team and World Cup cues, "premier pari garanti" risk-free offers, boosted odds, sponsorship legitimacy; a highly uniform template.
- **Betsson:** European club match cards with odds, "100€ remboursés" refunds, low-risk framing.
- **Unibet/Kindred:** mostly video; collectible-card match cards and creator or pundit videos; first-bet refunds.
- **PMU:** large "100€ bonus en cash" visuals; horse-racing prestige and tradition, poker tournaments, jackpots, and payout reliability; the broadest sport mix.
- **Winamax:** humour and wordplay, street culture, expertise and player-prop picks across football, NBA, F1, and tennis; offers in fewer ads.

Only 9/100 creatives depict a winning scenario, and sociability cues are rare.
