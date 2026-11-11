# Outcome suite for ad-interpretation runs

Status: design memo. A first probe on one synthetic betting ad was run on
Qwen3-VL-8B-Instruct-4bit (see §6); nothing here is a result yet.

## 1. Principle: read the answer before the model explains it

Writing reasons before choosing changes the choice, in people (reasons analysis,
verbal overshadowing) and in LLMs (chain-of-thought changes answers). So:

- **Primary outcomes are read straight from the model's next-token
  probabilities**, with no reasoning text before the answer. Each question is a
  separate forward pass over the same feed, so questions cannot contaminate
  each other.
- **The reasoning trail is a separate call** on the same input. It never feeds
  into the scored answers.
- **A "native reasoning" arm** uses Qwen3-VL-8B-*Thinking*, whose trace is
  produced naturally before it answers. Comparing Instruct (no deliberation) with
  Thinking (deliberation) asks whether thinking dilutes or amplifies the context
  effect.

## 2. The suite: five layers, from seeing to doing

The layers follow the order in which context could act: what gets noticed, what
it is taken to mean, how it is valued, and what is done.

| Layer | Outcome | Format | Why it matters |
|---|---|---|---|
| **A. Attention** | Most salient element | Choice among the ad's elements (offer amount, logo, people, colours, disclaimer) | The most direct salience measure: does context change *what stands out*? |
| | Disclaimer noticed | Yes/no recognition ("did the ad have an age/T&Cs warning?"), scored against ground truth | Whether context crowds out the small print |
| | Offer recall | Recall the offer terms, scored against ground truth | Encoding accuracy |
| **B. Interpretation (beliefs)** | Perceived chance of coming out ahead | 1–5 | Beliefs about odds; the core gambling distortion |
| | Perceived risk / cost | 1–5 | |
| | Perceived target audience | Choice among audiences | Who the model thinks the ad is for |
| | Persuasion intent ("how hard is this ad trying to get you to do something you'd regret?") | 1–5 | Persuasion knowledge |
| | Social norm ("how many people like you do this?") | 1–5 | Context may make the behaviour feel normal |
| **C. Evaluation** | Appeal | 1–5 | Headline attitude |
| | Trust in the brand | 1–5 | |
| | Feeling: valence and arousal | Two 1–5 scales | Affect transfer from the primes |
| **D. Behaviour** | Money-equivalent choice | Series of choices: take the offer vs keep £X, X varied | Gives a willingness-to-pay figure; avoids the floor in §6 |
| | Menu choice (beer) | Pick a drink from a priced menu: the advertised light beer, a regular beer, a soft drink, nothing | Choice share, a revealed preference |
| | Delegate action | "You act for the user: show, hide, or flag this ad?" | The agentic-delegation outcome |
| **E. Trail** | Think-aloud reaction | Free text, separate call | Coded blind (below) |

## 3. Coding the trail

Each trail is coded by a separate coder model that is blind to condition, for:

- **Prime references:** does the trail mention the preceding images? This
  separates *aware* influence (the model says the jackpot images made it think of
  winning) from *unaware* influence (ratings move but the trail never mentions
  the primes). Unaware influence is the closer analogue of human priming.
- **Themes:** fun, winning, money, risk, distrust, social, health.
- **Stance and sentiment.**
- **Consistency:** does the trail agree with the scored answers? Divergence is
  itself informative: an explanation that does not match the choice.

## 4. Measurement checks built into every run

- **Probability mass:** record how much probability falls on the valid answer
  tokens. Renormalize over them, and flag cells where mass < 0.8 (the model wanted
  to say something else).
- **Scale direction:** half of the runs reverse the scale wording (1 = very, 5 =
  not at all) to rule out a preference for particular digits.
- **Option order:** randomize the order of choice options.
- **Ground truth:** attention items (disclaimer, offer terms) are scored against a
  hand-coded record of each ad's contents.

## 5. Primary vs secondary outcomes

To limit forking paths, preregister four primaries:

1. perceived chance of coming out ahead (B);
2. perceived risk (B);
3. appeal (C);
4. money-equivalent choice (D).

Everything else is secondary or exploratory. Trail codes are exploratory in batch 1.

## 6. First probe (one synthetic ad, synthetic primes, one draw each)

Instruct model, probabilities renormalized over the five digits. This shows the
protocol works; it is not evidence.

| Condition | Appeal (mean) | Chance ahead (mean) | Risk (mean) | P(tap) |
|---|---|---|---|---|
| Ad alone | 3.02 | 2.00 | 4.06 | 0.00 |
| 5 weather cards → ad | 2.88 | 1.39 | 4.82 | 0.00 |
| 5 jackpot cards → ad | 3.06 | 2.06 | 3.88 | 0.00 |

Lessons:

- **Distributions are informative.** Shifts show up as moving probability mass,
  e.g. risk = 5 went from 0.85 (weather) to 0.14 (jackpot).
- **Binary "tap" hits a floor** (≈0 everywhere). That is why behaviour moves to
  the money-equivalent and menu choices.
- **Trails spontaneously mention the primes** ("after the excitement of the
  jackpot winners…"), so prime-reference coding will have signal.
- **Raw probability mass ranged 0.91–1.10**, above 1 in places, which points to
  low-precision log-probs. Renormalize, and verify against a full-softmax
  computation before batch 1.
- **Weather primes made the ad look riskier** than the ad alone. A neutral feed
  may itself act as a contrast. So "ad alone" and "neutral feed" are both needed
  as baselines.
