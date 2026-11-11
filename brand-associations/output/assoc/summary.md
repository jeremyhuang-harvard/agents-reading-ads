# Directed association: pilot summary (frame 2026-11-10, window 2025-11-01 to 2026-10-31)

Asymmetry = log P(brand | celebrity cue) - log P(celebrity | brand cue). Positive = the celebrity retrieves the brand more strongly than the brand retrieves the celebrity.

| measure | pairs with both directions > 0 | share asym > 0 | median asym (pairs) | slope on size ratio: news coverage | slope: Wikipedia pageviews | n cells |
|---|---|---|---|---|---|---|
| embed_st-baai-bge-base-en-v1-5 | 23/23 | 35% | -0.14 |  | +0.16 (se 0.02) | 660 |
| embed_st-suproteem-representlm-v2 | 23/23 | 48% | -0.22 |  | +0.23 (se 0.04) | 660 |
| llm_qwen3-8b-4bit | 23/23 | 57% | +1.11 |  | +2.08 (se 0.11) | 660 |

Size ratio = log(brand) - log(celebrity) of English-language GDELT article counts (news coverage) or Wikipedia pageviews over the window. Pageviews understate brands (people visit brand sites, not brand Wikipedia pages), so coverage is the primary size measure.
For `gdelt_conditional` the asymmetry equals log N(brand) - log N(celebrity) by construction (a pure size effect); competition-normalized measures (`gdelt_share`, `trends_related`, `embed_*`, `llm_*`) instead reflect crowding at each cue.
