# Research design

## Claim

The project asks whether an LLM system conditioned on a specified profile can serve as a useful **research instrument** for screening hypotheses about contextual ad interpretation. It does not assume that prompted personas are people, representative consumers, or digital twins.

## Conceptual model

The initial mechanism is:

`contextual cues → comparison set → attribute salience / reference selection → ad interpretation → evaluation or choice`

The key design choice is to hold the target ad fixed while randomizing context. This turns “context” from narrative background into an experimentally controlled input.

## Experimental objects

1. **Immutable ad:** identical pixels and copy across conditions.
2. **Structured profile state:** stated preference and recent history, initially without demographic labels.
3. **Context:** surrounding price and quality benchmarks, later expanded to editorial, platform, social, task, and economic context.
4. **Model system:** provider, exact model/snapshot, system prompt, user prompt, decoding settings, tool access, and collection date.
5. **Response:** structured interpretation and choice fields collected before explanation.

Persona construction and response generation remain separate. The profile compiler cannot see the ad, randomized context, hypotheses, or outcomes.

## Minimal pilot

Use a novel ad with two similarly prominent attributes, such as price and battery life. Place it on a mock comparison page with a 2 × 2 manipulation:

| Factor | Near benchmark | Favorable contrast |
|---|---|---|
| Price | Target resembles contextual price | Target is notably cheaper |
| Quality | Target resembles contextual quality | Target is notably better |

Cross four induced profile states:

- price-first + recent budget pressure;
- price-first + recent product failure;
- performance-first + recent budget pressure;
- performance-first + recent product failure.

The baseline configuration creates 25 frozen cards per state and crosses them with four contexts, two prompt variants, and two model families: 1,600 calls. Before that run, execute a small sentinel batch and stop if schema, option-order, prompt-blinding, or modality checks fail.

## Outcome order

1. first attribute noticed;
2. unaided one-sentence takeaway;
3. perceived claim, intent, and intended audience;
4. price and quality attractiveness;
5. purchase probability;
6. target-versus-opt-out choice;
7. confidence;
8. explanation last.

Interpretation is primary. Purchase intent is downstream and should not be described as demand without incentives or market behavior.

## Validation path

Collect matched human responses under the same randomized contexts. Build model profiles only from pre-treatment human fields. Compare full distributions and the vector of context effects, including subgroup moderation. Use a development subset to freeze prompts and equivalence bounds, then evaluate on an untouched holdout.

## Advancement gates

Advance from mock plumbing to paid model inference only if:

- ad and contexts are immutable and hashed;
- context cells are unique and exactly balanced;
- every request and response is append-only and resumable;
- prompt and option-order permutations are defined;
- the runner records model snapshot, prompts, parameters, and timestamps.

Advance to claims about consumers only if matched human validation shows context-effect fidelity without collapsed variance or offsetting subgroup errors.
