# Reproducibility standard

The project adapts Gentzkow and Shapiro's recommendations and the JMSLab research-repository template: automate the workflow, make execution order explicit, separate inputs from outputs, use portable paths, test restrictions in code, and successfully run the project before publishing changes.

## Rules

- `make reproduce` is the authoritative end-to-end entry point.
- `data/raw/` is immutable; every source requires provenance, access conditions, and SHA-256 checksums.
- `data/derived/`, `output/`, and `tmp/` are generated and are not manually edited.
- Every research-relevant choice belongs in versioned configuration, a versioned codebook, or a versioned prompt.
- Each substantive run must record the Git commit, dirty-tree state, runtime, input checksums, record counts, configuration, random seeds, and output checksums.
- Slow acquisition or model inference must be preserved separately from inexpensive analysis and reporting.
- Cleaned tables must have unique, non-missing keys and remain normalized until analysis requires otherwise.
- Notebooks may support exploration but cannot be the only implementation of a reported result.
- CI should run tests and a miniature end-to-end reproduction once the pipeline exists.
- Before publication, reproduce all reported outputs from a clean checkout using documented inputs.

## Source/output boundary

- Source-controlled inputs: code, configuration, schemas, codebooks, prompts, documentation, and small test fixtures.
- External inputs: immutable files under `data/raw/`, normally stored outside Git.
- Generated data: `data/derived/`.
- Generated deliverables: `output/`.
- Disposable intermediates: `tmp/`.

Generated files must be rebuildable from documented source inputs. If an external or stochastic step cannot be rerun exactly, preserve the original request, response, model/version information, timestamp, and checksum.

## References

- Gentzkow and Shapiro, *Code and Data for the Social Sciences: A Practitioner's Guide*: https://web.stanford.edu/~gentzkow/research/CodeAndData.pdf
- JMSLab research repository template: https://github.com/JMSLab/Template
