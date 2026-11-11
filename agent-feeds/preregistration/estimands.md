# Initial estimands and contrasts

Let `Y(i, j, c, a)` be the response vector for frozen profile `i`, model–prompt system `j`, randomized context `c`, and fixed ad `a`.

## 1. System-specific context effect

For contexts `c` and `c'`:

`tau_j(c, c') = E_i[Y(i,j,c,a) - Y(i,j,c',a)]`

Estimate separately for first notice, inferred claim, price and quality evaluation, choice, and purchase probability.

## 2. Induced-state moderation

Estimate context × preference × history interactions. These are effects for induced profile states, not demographic subgroup effects.

## 3. Human–LLM context-effect gap

For profile stratum `z`:

`Gamma_j(c,c',z) = tau_j(c,c' | z) - tau_human(c,c' | z)`

Preregister equivalence bounds before opening the human holdout.

## 4. Distributional fidelity

Compare complete conditional distributions rather than means alone. Planned summaries include variance, endpoint shares, categorical total variation or Jensen–Shannon distance, scalar Wasserstein distance, and outcome covariance.

## 5. Deployment sensitivity

Treat model family, snapshot, prompt variant, persona card, collection date, and completion randomness as distinct sources of variation. Repeated completions are nested samples from one conditional policy.

## Primary pilot tests

- average marginal effect of favorable price context on first noticing price;
- average marginal effect of favorable quality context on first noticing quality;
- context interaction indicating reinforcement or attentional crowd-out;
- moderation by stated preference and recent history;
- robustness to option order, scale direction, prompt paraphrase, and model family.
