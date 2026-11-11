# Reproducibility standard

The repository adapts Gentzkow and Shapiro's recommendations: automate the complete workflow, make execution order explicit, separate inputs from outputs, use portable paths, test restrictions in code, and successfully run the project before publishing changes.[1]

## Rules

- `make reproduce CONFIG=...` is the authoritative entry point.
- `data/raw/` is immutable; every input requires provenance and SHA-256.
- `data/interim/`, `data/processed/`, `artifacts/`, `runs/`, and `tmp/` are generated.
- Generated files are never manually corrected.
- Every research-relevant choice belongs in versioned configuration or a versioned prompt.
- Each run records Git commit, dirty-tree state, runtime, input checksums, counts, and output checksums.
- Expensive inference output is preserved separately from inexpensive analysis and reporting.
- Notebooks may explore but are never the sole authority for a reported result.
- CI runs tests and a miniature end-to-end reproduction.

The modern additions—dependency lockfiles, machine-readable manifests, cryptographic hashes, CI, append-only model requests, and exact model snapshots—extend the guide's fixed-input and full-run principles to stochastic external model systems.

## Sources

[1] https://web.stanford.edu/~gentzkow/research/CodeAndData.pdf — Code and Data for the Social Sciences
