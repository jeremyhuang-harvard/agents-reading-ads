# Ads as Cues × the French betting competitor panel: research memory

Running memory for linking Bordalo, Burro, Gennaioli, Nacamulli and Shleifer, *Ads as Cues* (October 10, 2025; NBER w34387) to the five-firm Snapchat panel. The paper itself is summarized in `docs/ads_as_cues_literature_map.md`; this file records **how our data connects to it**, what we can and cannot claim, and which tests follow.

Status: exploratory. Labels are Sonnet codes (codebook `competitor_association_codebook_v1.0.0`) not yet validated against human coders. Metrics come from `src/ads_as_cues_metrics.py` → `data/processed/competitor_analysis_v1/ads_as_cues_metrics.json`.

## 1. The paper in five lines

- Demand is gated by recall. A consumer buys a good if she recalls the pleasure it gave her: `d_g = q_g · r_g(e,f) − θ p_g`.
- Recall: `r_x(c,f) = S(c,x) f_x / Σ_y S(c,y) f_y`. The numerator is **similarity × frequency (habit)**; the denominator is **interference**, including a large "fog" of neutral, non-branded experiences `f_n`.
- Ads are involuntary, bottom-up cues. They raise recall of the advertised brand, **and of similar brands**, and inhibit dissimilar wants.
- Predictions:
  - Ad effects are stronger for habitual consumers, concave in habit.
  - Positive within-category spillovers, strongest for habitual buyers of the *rival*.
  - Brand ads expand the category.
  - Cross-category effects are positive if similar and negative (interference) if dissimilar.
- Section 6 implications about ad content:
  - Entrants should **differentiate** to avoid spillovers onto the leader.
  - Ads should make the brand **distinctively encoded**.
  - Ads should **co-occur with consumption pleasure** so that recurring contexts later cue the brand (Corona and the beach).
  - Advertising maintains habits (Wrigley's "electric train").
  - Negative advertising is rare because it cues the category's downsides.

## 2. Mapping model objects to what we observe

| Model object | Meaning | Our measure | Coverage |
|---|---|---|---|
| Cue `c` | Ad content that triggers retrieval | 951 coded creatives: cues linked to brand, borrowed meanings, sport/event/team, offer, framing, prominence | **Strong.** Much richer than Nielsen's 4–6-word descriptions |
| Similarity `S(c,x)` | Feature overlap between cues and memories | Cosine similarity of (a) verbatim ad-text stems, as in the paper, and (b) coded cue features; visual embeddings planned | **Strong** for ad–ad similarity; no access to ad–memory similarity |
| Exposure `e` | Weekly cue exposure | Lifetime impressions by ad and by launch month; targeting (age, gender, OS) | **Partial.** No individual exposure, no end dates |
| Database `f` (habits) | Past consumption frequency | None at consumer level; firm-level proxies only (incumbency, evergreen creatives, targeting) | **Missing** |
| Neutral experiences `f_n` | Frequent non-branded activities | Football watching, match days, World Cup, as the contexts ads attach to | Observed only as ad content |
| Demand `d` | Choice | None yet | **Missing.** Needs outcome data |

**Bottom line:** we observe the *supply side of cues*: which retrieval contexts firms try to occupy, how similar competitors' cues are, and how that changes over time. We cannot yet test demand-side predictions. The paper predicts demand from cues and habits; our panel shows **how firms choose cues**, which the paper only discusses informally in Section 6.

## 3. Linkages, with current evidence

### L1. Betting ads attach brands to a frequent, recurring "neutral" experience
- **Mechanism.** In the model, neutral activities (`f_n` ≫ `f_g`) mostly interfere. A footnote notes that a neutral activity can be similar to a brand (jogging and Nike). Sports-betting ads systematically pair the brand with **watching football**: specific fixtures, match days, national-team games.
- **Evidence.**
  - 676/951 creatives (71%) tie the brand to a specific event cue; 492/951 (52%) to a sport cue.
  - Football appears in 51–95% of each firm's ads.
  - "Companion to watching sport" and match-card templates are common (Betsson: 53% of ads are match cards).
- **Implication.** If ads raise `S(football match, brand)`, every future match becomes a cue for the brand without any ad exposure. This is the paper's Corona-and-beach mechanism in its strongest form, because the context recurs on a fixed public schedule.
- **Test.** Brand-search and app-activity spikes on match days should be larger for brands whose ads are most tied to those matches or competitions, holding ad spend fixed.

### L2. Cue similarity is high within the category and peaks at the World Cup
- **Similarity levels.**
  - Text-stem cosine between firms ranges 0.36–0.70 (mean ≈ 0.45). The paper reports 0.46 for same-category brand pairs and 0.25 across categories. The corpora and methods differ, so treat this as a rough comparison only.
  - Coded-cue similarity is higher: 0.55–0.93. bet365–Betsson is 0.93; Unibet–Betsson 0.79.
- **Convergence.** Mean pairwise coded-cue similarity of ads *launched in the same month* peaks in **June 2026 (0.77)**, versus 0.35–0.64 in other 2026 months. Winamax–bet365 similarity is 0.73 that month.
- **Caveat.** The set of firms launching differs by month.
- **Implication.** When a shared event dominates attention, firms converge on the same cue. In the paper, highly similar cues produce **positive spillovers to the brand consumers already use**.

### L3. The spillover logic predicts that generic challenger ads help the incumbent
- **Mechanism.** By Proposition 2, a challenger's ad that is similar to the leader's cues retrieves the *leader* for the leader's habitual users. The effect is stronger the more habitual they are, up to concavity.
- **Incumbent.** Winamax has 57% of panel impressions and 183 creatives that have run since before 2025, which makes it the plausible owner of the largest memory database.
- **Least distinctive challengers.**
  - bet365's and Betsson's most representative features (firm share ÷ rival share) are only 2–5×: national-team football, refunds, low-risk framing.
  - These are generic category cues that Winamax users also associate with Winamax.
- **Prediction.** bet365's World Cup push may have raised betting on *Winamax* among Winamax users. That is the betting analogue of a Pepsi ad raising Coke demand among Coke drinkers.
- **Test.** A survey experiment (Section 5) or outcome data split by prior operator.

### L4. Differentiation follows the paper's advice, through verticals rather than tone
- **Mechanism.** Section 6 suggests entrants "differentiate sharply from the leader to avoid positive spillovers." Distinctive cues retrieve only the advertiser.
- **Most distinctive features by firm** (representativeness ratio):

| Firm | Features |
|---|---|
| PMU | racing events 18.7×, horse racing 11.8×, cash bonus 7× |
| Unibet | no-deposit bonus 46×, MMA 10× |
| Winamax | poker tournaments 5.6×, jackpots 5.4×, humour 4× |
| bet365 / Betsson | ≤ 5× |

- **Implication.** Firms that own a non-football vertical (racing, poker, MMA) occupy cues that rivals cannot retrieve. Firms competing only on football rely on brand prominence and offers.
- **BGS stereotypes link.** A brand's image is its *representative* features, not its most frequent ones (Bordalo, Coffman, Gennaioli & Shleifer 2016). The representativeness ratio is a direct operationalization.

### L5. Brand encoding: separate storage needs salient branding
- **Mechanism.** The model's key assumption is that intrinsically similar goods are stored separately because branding is salient during consumption. Without that, the category is encoded as one good and no brand is retrieved.
- **Evidence.**
  - Maximal brand prominence (3 on a 0–3 scale) appears in 99.9% of bet365 impressions, about 76% for Betsson and Unibet, 44% for PMU and 26% for Winamax.
  - 21% of PMU impressions are football ads with low brand prominence.
- **Implication.** By the paper's logic, those PMU ads are the most spillover-prone in the panel: they cue "betting on football" more than PMU. Winamax uses low maximal prominence but highly distinctive assets (cash, the red W, poker), consistent with an incumbent whose brand is already encoded.

### L6. Repetition and maintenance: the "electric train"
- **Mechanism.** One return to ads is maintaining and rehearsing existing habits, not acquisition. Ads matter most for habitual users, and brands that go dark lose demand slowly.
- **Evidence.**
  - Winamax: 8.6M impressions per creative and 183 evergreen creatives. This looks like maintenance.
  - Betsson: 0.3M impressions per creative and 5 ads per creative. This looks like acquisition and testing.
  - **Unibet launched nothing after 19 March 2026**: a potential natural "going dark" episode, if the archive is complete.
- **Test.** Compare Unibet's subsequent market share or app rank against rivals (ANJ quarterly data, app-store ranks), with care about Kindred's corporate events.

### L7. Targeting as investment in habit footholds
- **Mechanism.** The paper argues that once a habit foothold is established, for example through campaigns targeted at specific demographics, it persists with continued investment. Ads are most effective for habitual users.
- **Evidence.**
  - Winamax, Unibet and Betsson target **men only, mostly 18–45** on Snapchat.
  - PMU and bet365 target all genders, 18+.
- **Interpretation.** The incumbent and the established challengers concentrate cues on the demographic with the largest existing betting database. The relaunching PMU and the entrant bet365 cast wider nets.

### L8. Category expansion, no negative ads, and the welfare angle
- **Category expansion.** The model predicts brand ads expand the category, and that negative ads are rare because cueing costs recalls the category's downsides.
- **No negative ads.** The panel contains no comparative or negative ads; the closest is Winamax's implicit "cash, not freebets".
- **Possible exception.** Refund offers explicitly cue *losing* ("1er pari perdu remboursé"). Per footnote 26, cueing a cost could prompt recall of losses across the category. This is a hypothesis about why refunds are framed as safety.
- **Welfare.** Habit × ad complementarity implies that the most habitual bettors respond most to betting cues (subject to concavity). Category-wide spillovers imply that brand-level restrictions are weak. Ads also inhibit recall of non-betting uses of time and money (interference). This is the paper's welfare channel applied to a harmful-good market.

### L9. Salience layer: what is prominent
- **Mechanism.** BGS salience: the attended attribute is the one that contrasts with the context.
- **Evidence.** The coded "most prominent element" (impression-weighted) is the offer amount for 56–61% of PMU, Unibet, Betsson and bet365 impressions. For Winamax it is the headline (62%), with the offer amount at only 23%.
- **Implication.** Challengers make the deal salient; the incumbent makes its message salient. Salience determines what gets encoded; similarity determines what gets retrieved later.

## 4. What we can and cannot claim

- **Can claim:**
  - Descriptive facts about the cue supply: content, similarity, timing, repetition and targeting.
  - That firm behaviour is *consistent with* Section 6's content implications.
  - That the panel provides a richer similarity measure than the paper's.
- **Cannot claim:**
  - That ads changed recall or demand.
  - Who is habitual.
  - That spillovers exist in betting.
  - Anything about individual exposure.
- **Main threats:**
  - Model-coded labels are not yet validated.
  - Multi-image Story ads were coded from the first image only.
  - Winamax and Betsson are capped at 1,000 ads.
  - No end dates; impressions are lifetime.
  - The sports calendar drives all firms at once, which mimics strategic convergence.

## 5. Tests that would turn this into evidence on memory

1. **Survey experiment on habit-dependent spillovers (cleanest).**
   - Recruit French adult bettors.
   - Elicit their main operator (habit `f`).
   - Randomize exposure to:
     - (a) a challenger ad using the *incumbent-similar* World Cup cue;
     - (b) the same challenger with a *differentiated* cue (racing, MMA);
     - (c) a neutral non-betting ad.
   - Measure unaided brand recall, intended operator, and betting intent.
   - Prediction: (a) raises recall and intent for the respondent's *own* habitual brand, more for heavier bettors (concave). (b) leaks less. (c) interferes.
   - Real ads from the panel provide the stimuli. Restrict to adults, add responsible-gambling safeguards, and obtain ethics review.
2. **Match-day retrieval.** Weekly brand Google Trends or app ranks around fixtures that specific brands featured, versus fixtures they did not.
3. **Going dark.** Track Unibet after March 2026 against rivals, using ANJ quarterly market data.
4. **Measurement validation.** Compare text-stem, coded-cue and visual-embedding similarity with human pairwise similarity judgments on a sample of ad pairs.
