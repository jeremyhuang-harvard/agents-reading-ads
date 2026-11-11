"""Directed celebrity-brand association measures.

The package turns public data into *directed* association strengths between a set of
celebrities C and a set of brands B:

    forward  P(b | cue = c)   "when people think of Tate McRae, how much do they think of Adidas?"
    backward P(c | cue = b)   "when people think of Adidas, how much do they think of Tate McRae?"

and the asymmetry  A(c, b) = log P(b | c) - log P(c | b).

Every measure is computed over the same frozen candidate sets (config/assoc/ambassadors.json),
so the denominators that create asymmetry are explicit. See docs/assoc-design.md.

Modules
-------
config      load and validate the entity/pair frame
measures    pure functions (retrieval shares, counts, ranks, asymmetry decomposition)
sources/    cached collectors: Wikipedia, GDELT, Google Trends related queries, Wikimedia clickstream
embed       Sarkar-style coverage representations (mean of document embeddings per entity)
llm         directed retrieval probabilities from a local language model (MLX Qwen)
analyze     pair panel, size/interference regressions, figures
"""
