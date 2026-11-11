# Prefix caching for batch runs: assessment

Status: **audit complete** (rerun 02:03–02:13, 22 Oct, alone on the GPU). The first attempt on
21 Oct crashed with a Metal out-of-memory error while three MLX processes shared 24 GB.

## Summary

1. **Speedup: 2.86× median** (18.5 s → 6.5 s per feed; range 1.7–3.4×), measured interleaved
   on the same 20 feeds.
2. **Projected hours:** batch 2 is already finished (A happened). For a batch-2-sized run
   (888 feeds) alone on the GPU: about 4.6 h uncached vs about 1.6 h cached.
3. **Risk numbers:** top-token agreement **98.1%** (3 flips in 160, all at exact ties); max |Δprob|
   **0.076**; median |Δ rating mean| 0.007, max 0.15; trail text differs in **42%** of feeds
   (wording-level). The old path is exactly deterministic: 0 differences vs stored rows (200 answers).
4. **Recommendation: do not adopt under the current rule.** It fails two thresholds:
   max |Δprob| ≤ 1e-2 and agreement ≥ 99%. The drift is small, unrelated to condition, and comes
   only from the cached path. Adopting it would be a judgement call, not a pass (see §Options).
5. **Need from you:** decide whether to (a) keep the uncached path, (b) adopt caching for whole
   new batches with the drift documented, or (c) let me spend about 1 h finding where the
   numerical difference comes from.

## Step 0: shared prefix. Confirmed

Token IDs from the actual chat template output, per question:

| Feed shape | Images | Shared prefix (tokens) | Last image token at | Question suffix (tokens) |
|---|---|---|---|---|
| ad alone | 1 | 356 | 339 | 18–54 |
| 5 primes, then ad | 6 | 1,102 | 1,063 | 18–54 |
| ad first, then 5 | 6 | 1,032 | 993 | 18–54 |

All images and the frame sentence sit inside the shared prefix. Nothing question-specific comes
before the question text.

## Step 1: profile (old path, quiet GPU)

| Feed | Total |
|---|---|
| betting, 5 before | 18.8 s |
| beer, 1 before | 18.5 s |
| control, ad first | 18.6 s |

About 95–98% of each prompt is the shared prefix, so most per-question time is repeated prefill.
The measured 2.9× is consistent with that.

## Step 3: equivalence audit (N = 20 feeds, stratified: 8 betting, 6 beer, 6 control)

Old and new paths were run interleaved on each feed, alternating which went first.

| Category | Scored answers | Top-token flips (95% UB) | Max \|Δprob\| | Mean \|Δprob\| | Max \|Δ mean\| | Trail mismatches (95% UB) |
|---|---|---|---|---|---|---|
| Betting | 64 | 2 (0.107) | 0.075 | 0.0071 | 0.076 | 8/16 (0.72) |
| Beer | 48 | 0 (0.074) | 0.076 | 0.0086 | 0.150 | 2/12 (0.45) |
| Control | 48 | 1 (0.109) | 0.057 | 0.0047 | 0.062 | 7/12 (0.81) |
| **All** | **160** | **3 (0.054)** | **0.076** | **0.0068** | **0.150** | **17/40 (0.58)** |

Diagnostics:

- **Where the drift comes from:** the first question in each feed (computed cold, nothing cached)
  matches the old path exactly (20/20, Δ = 0). All drift is in the 140 questions that reuse the
  cache; 48% of those differ by more than 0.01.
- **The flips are ties.** All 3 were near-exact two-way ties in the old path (0.404 vs 0.404,
  0.497 vs 0.497, 0.357 vs 0.357), so any tiny perturbation flips the reported top token.
- **Trails** diverge by a word or phrase, e.g. "the sudden appearance of the bright green Unibet
  ad" → "the sudden shift to this bright, green Unibet ad". The first differing token is at
  positions 1–73.
- **No category pattern:** mean |Δprob| is 0.005–0.009 in every category.
- **Old path determinism:** 0 differences against the stored batch-2 rows across 200 answers. The
  stored data are exactly reproducible from the uncached code.
- **Order check:** with the cached path, reversing question order changed 5/40 answers (max |Δprob|
  0.063). This is the same numerical drift (a different question is computed cold), not leakage
  of earlier answers: cold questions match exactly whatever their position.

**In scale:** median |Δ rating mean| is 0.007; p90 0.057; max 0.15. The main beer effects are
0.3–2.7. The subtlest effects we have reported (look-alike images, about 0.1–0.2) are within
reach of the max drift for a single answer, though averaged over 10+ feeds per cell the drift
should mostly cancel.

## Step 4: time

| Option | Quiet GPU | Shared with norms job |
|---|---|---|
| Batch-2-sized run (888 feeds), uncached | ~4.6 h | ~9 h, crash-prone |
| Same, cached | ~1.6 h | not tested |

Batch 2 itself finished uncached (A) at 23:58 on 21 Oct, so B and C no longer apply to it.

## Step 5: risk register

| # | Risk | Evidence | Probability | Consequence | Mitigation |
|---|---|---|---|---|---|
| 1 | Numeric drift | Max \|Δprob\| 0.076; median \|Δ mean\| 0.007 | Certain (measured) | Small noise per answer; flips at ties | Use only for whole batches; never mix paths within a comparison |
| 2 | Contamination across questions | Cold questions match exactly in any position; trims verified in code | Low | Would be a hidden order confound | Keep a fixed question order; log `cached_tokens` |
| 3 | Code path × category confound if resumed mid-run | Structural: feeds run grouped by ad | Certain if mixed | Uninterpretable | Never resume across code paths |
| 4 | Out-of-memory with other MLX jobs | **6 crashes** in batch 2 with the norms job running | High when shared | Lost time, not lost data | Run one MLX job at a time |
| 5 | Crash mid-run | Resume worked 6 times; duplicates bit-identical | Low impact | None observed | Keep resume, and dedupe on load |
| 6 | Silent fallback to uncached | mlx-vlm falls back with only a warning | Low | Mislabelled provenance | Record per-question `cached_tokens` |

## Options

- **(a) Keep uncached.** Exactly reproducible; 2.9× slower.
- **(b) Adopt caching per batch**, never mixed within a comparison. The drift is unrelated to
  condition, so treatment effects stay unbiased. Record the flag and the measured drift in the
  manifest. This misses the pre-set thresholds, so it is a deliberate change of rule.
- **(c) Find the source.** Likely suspects: chunked-prefill boundaries, or image features
  computed once vs per call. If the source is fixable, caching might meet the 1e-2 bar.

The `--prefix-cache` flag is still not implemented in `run_priming.py`; the audit used the
evaluation script (`scripts/eval_prefix_cache.py`). Data: `tmp/cache_eval/` (audit.jsonl,
order_check.jsonl, step0_prefix.json, step1_profile.json).
