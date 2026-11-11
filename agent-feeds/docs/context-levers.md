# Context levers: what counts as "context" for an LLM reading an ad

Status: design memo, pre-pilot. Nothing here has been tested on Qwen yet.

## 1. The core point

A person sees an ad on a screen, while in a mood, with a history in memory. Those
are different channels.

An LLM gets one token sequence. Its "persona history", the "article next to the
ad", the "Sponsored" label and the instruction are all just text, in some order,
in the context window. So "should we put the ad near other things, or load the
agent with a history?" is not really a choice between two kinds of context. The
real question is **which part of the input the cue sits in, and whether the model
treats it as relevant evidence or as incidental background**.

That matters for the claim we want to make. If we *tell* the model "you are in
recovery from gambling" and it then rates a betting ad negatively, that is
instruction-following (and probably stereotype reproduction), not priming. The
human phenomenon we care about, salience in the Bordalo–Gennaioli–Shleifer sense,
is about **logically irrelevant or incidental cues changing what is attended to
and how it is interpreted**. So the cleanest test is:

> Does an incidental cue that should not matter (an adjacent article, a recent
> event, a label) shift the agent's interpretation of a fixed ad, and does that
> shift depend on the agent's history the way human cue-reactivity does?

## 2. Taxonomy of levers

Each lever is defined by where it sits in the prompt and how relevant it is to
the decision.

| # | Lever | Where it sits | Example (gambling app / light beer) | Human evidence | LLM evidence |
|---|---|---|---|---|---|
| L1 | **Adjacent media content** (placement) | Feed items before/after the ad | Match recap vs. article on gambling harms vs. neutral recipe | Media-context effects are real but small; congruence r ≈ .11, larger when shown simultaneously ([Kwon et al. 2021](https://doi.org/10.1080/00913367.2021.1895920)). Sports programming did *not* make teen boys more receptive to beer ads ([Slater et al. 1996](https://doi.org/10.15288/jsa.1996.57.425)). | LLMs are easily swayed by irrelevant context in reasoning tasks ([Shi et al. 2023](https://proceedings.mlr.press/v202/shi23a.html)). |
| L2 | **Competing items / choice set** | Other ads or offers on the same page | Betting ad next to a responsible-gambling PSA, or next to a rival app with a bigger bonus | Classic anchoring/decoy effects | Shopping agents shift choices with position, ratings, "sponsored"/endorsement tags, and the shift differs across models ([Allouah et al. 2025](https://arxiv.org/abs/2508.02630)). Inserted text can push a product up LLM recommendations ([Kumar & Lakkaraju 2024](https://arxiv.org/abs/2404.07981)). |
| L3 | **Endowed history (trait)** | Persona card / memory | Recreational bettor vs. heavy bettor vs. person who quit | Ad effects are concentrated among at-risk people: problem gamblers show cue-driven urges ([Kushner et al. 2007](https://doi.org/10.1007/s10899-006-9050-4)); preference-matched alcohol ads raised craving only among risky drinkers ([PMC11730253](https://pmc.ncbi.nlm.nih.gov/articles/PMC11730253/)). | Persona prompts can reproduce stereotypes rather than people; validity varies by task (see `docs/literature-map.md`). |
| L4 | **Recent state / episode** | Last few turns or "today" log | Just lost £80, just got paid, team just won, hungover morning | Situational state moderates ad response (time of day mattered for alcohol craving in PMC11730253) | Earlier turns can carry over into later answers; structural priming exists in LMs ([Jumelet et al. 2024](https://arxiv.org/abs/2406.04847)). |
| L5 | **Source, label and disclosure** | Around the ad | "Sponsored", platform name, "18+ / gamble responsibly", regulator warning | Recognizing persuasion intent changes how people process ads ([Friestad & Wright 1994](https://doi.org/10.1086/209380)) | Labels move agent choices (Allouah et al.). |
| L6 | **Agent role / task frame** | System prompt or instruction | "You are this person, scrolling" vs. "You act for this person; decide whether to flag/click/buy" vs. "Evaluate this ad" | n/a (no human analogue; this is the delegation question) | Assistants bend toward what the user seems to want (sycophancy; [Sharma et al. 2024](https://arxiv.org/abs/2310.13548)). |
| L7 | **Format mechanics (nuisance)** | Position, length, order | Ad first vs. middle of long feed | n/a | Information in the middle of long contexts is used less ([Liu et al. 2024](https://doi.org/10.1162/tacl_a_00638)). |

L1–L6 are substantive levers. L7 is a confound to hold fixed or randomize, never
a treatment.

## 3. The design choices that matter most

### 3a. Show vs. tell the history

Two ways to give an agent a gambling history:

- **Told:** "You are a 34-year-old who has struggled with sports betting."
- **Shown:** a short, neutral activity log: bank lines with three deposits to a
  betting site, a missed bill, a search for "how to self-exclude".

Told histories invite the model to act out a label. Shown histories make the model
*infer* the state, which is closer to how context works for people and to how a
real delegated agent sees a user (through records, not self-descriptions). We
should run both and treat the gap between them as a measure of label-acting.

### 3b. A relevance gradient for context cues

Within L1/L4, vary how relevant the cue is:

1. **Placebo:** length-matched neutral content (recipe, weather).
2. **Incidental, related:** match recap, no mention of betting.
3. **Incidental, valenced:** story about someone's big win, or about gambling debt.
4. **Explicit and relevant:** the agent is told the odds, or told about a harm.

Effects at 4 are just conditioning. Effects at 2–3 are the priming-like result.
Effects at 1 are a measure of noise and nonsense sensitivity.

### 3c. Separate the model's own stance from the persona's

RLHF-tuned models have their own views on gambling and alcohol and may moralize
whatever the persona says. Every design needs:

- a **no-persona baseline** (the model's default reading of the ad); and
- a **persona-only baseline** with no extra context.

Then context effects are measured *within* persona, and persona effects are
compared to the model's own baseline.

### 3d. Measure interpretation before evaluation

Order the outcomes so the agent reports what it saw before it judges:

1. What did you notice first? (unaided, free text)
2. What is this ad offering or claiming?
3. Who is this ad for?
4. Odds, risk and cost: what does it cost and what can you lose?
5. How does it make you feel / how appealing is it?
6. Intent: click, ignore, hide, report, or (as delegate) act or flag.

With local Qwen we can also read **token probabilities** for the closed-ended
answers. That gives the full response distribution per cell without sampling
noise, which suits our distribution-level estimands.

### 3e. Image vs. text

Real ads are images. Qwen3-8B (installed) is text-only. Options:

- **Transcribe** each ad into a fixed text description. Cheap, but our wording then
  decides what is salient, which is the very thing we want to measure.
- **Use a vision model**, e.g. Qwen3-VL-8B-Instruct (4-bit MLX build exists:
  [model card](https://huggingface.co/mlx-community/Qwen3-VL-8B-Instruct-4bit)).
  The ad stays as pixels; context goes in as text or as a rendered feed screenshot.

Recommendation: the vision model as the primary condition, with transcription as
a secondary condition. The gap between them is itself informative.

## 4. What would count as "human-like"?

Human priming evidence is uneven. Many behavioural priming results have failed to
replicate ([Doyen et al. 2012](https://doi.org/10.1371/journal.pone.0029081)). We
should benchmark against the robust patterns:

- **Moderation by risk:** ad and context effects concentrated among at-risk
  profiles, near zero for low-risk ones.
- **Small congruence effects:** placement effects of modest size, not large swings.
- **Persuasion knowledge:** disclosure labels increasing scepticism.

An LLM that shows huge placement effects for *everyone* is not human-like; it is
over-sensitive. That over-sensitivity is a finding in its own right for the
delegation story: it means an agent's reading of an ad can be steered by what sits
next to it.

## 5. Candidate first batch (to finalize once ads arrive)

- **Ads:** 2 gambling, 2 light beer, 2 neutral controls of the same format.
- **History (L3, shown):** none, low-risk user, at-risk user, quit/self-excluded
  user. Add a *told* version of the at-risk profile.
- **Placement (L1):** placebo, incidental-related, valenced-win, valenced-harm.
- **Role (L6):** first-person consumer vs. delegate agent.
- **Held fixed or randomized:** ad position, feed length, item order (L7).

That is 6 ads × 5 histories × 4 placements × 2 roles = 240 cells. With 10 persona
draws per cell this is 2,400 local calls, feasible on the Mac mini. Labels (L5)
and recent state (L4) come in the second batch, once we know which channels move
anything at all.

## 6. Open questions for the PI

1. Is the main claim about **LLMs as models of people** (do they react like humans?)
   or about **LLMs as delegates** (what happens to ad exposure when an agent reads
   for you)? The answer decides how much weight the delegate role gets.
2. Do we want a matched human sample for at least one ad, so the at-risk
   moderation pattern has a real comparison?
3. Which jurisdiction's ads and warnings (UK, EU, US state)? That fixes the L5
   label wording.
