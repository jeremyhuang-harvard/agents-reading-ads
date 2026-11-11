# Reproducibility and repository architecture

This project follows the principles in Gentzkow and Shapiro's *Code and Data for the Social Sciences* and the current JMSLab research template without reorganizing working code solely for cosmetic conformity.

## Operating principles

1. **Automate repeated work.** A clean checkout uses `make check` for the canonical local verification path.
2. **Separate inputs from outputs.** Code, tests, configuration, and documentation are versioned; external captures and generated artifacts are not.
3. **Preserve raw inputs.** Collection runs are immutable and carry provenance, timestamps, request metadata, failure records, and checksums.
4. **Keep data normalized until analysis.** Derived tables should use explicit, stable, non-missing keys. Wide analysis tables are produced late in the pipeline.
5. **Separate slow from fast stages.** Network collection, creative downloads, and model calls are not required for ordinary tests or transformations.
6. **Prefer readable code over premature abstraction.** Shared libraries are introduced only when repeated use justifies their maintenance and testing cost.

## Directory contract

| Path | Role | Git policy |
|---|---|---|
| `src/` | Collection, validation, transformation, and analysis programs | Tracked |
| `tests/` | Offline behavioral tests and small synthetic fixtures | Tracked |
| `config/` | Sampling rosters, codebooks, and run specifications | Tracked |
| `docs/` | Research design, source documentation, methods, and aggregate reports | Tracked |
| `data/raw/` | Immutable source responses and downloaded creatives | Ignored except `.gitkeep` |
| `data/processed/` | Generated databases, panels, model outputs, tables, and previews | Ignored except `.gitkeep` |
| `datastore/` | Future external location or local link for large/restricted shared data | Never tracked |
| `temp/` | Disposable intermediate files | Never tracked |
| `log/` | Generated execution logs | Never tracked |

The current `src/` and `data/` names are retained because they already encode the source/output distinction and are used by tested collectors. A disruptive rename to `source/` and `output/` would add migration risk without improving identification or reproducibility.

## Canonical commands

```bash
make setup       # install the locked environment
make dev         # fast local test run
make boundaries  # verify Git/data/secret boundaries
make check       # boundary checks plus the complete offline test suite
```

Collection remains explicit rather than part of `make check`: it uses live platform repositories, can download media, and may produce immutable raw runs. Each collector's command and run configuration must be documented and versioned separately.

## Dependency graph strategy

The project will adopt explicit dependencies incrementally:

- **Now:** Python entrypoints, versioned configuration, immutable run manifests, `uv.lock`, tests, and top-level `make` commands.
- **Next:** declare inputs and outputs for normalized datasets and publication figures/tables once those artifacts stabilize.
- **Later:** introduce SCons if the project develops a multi-stage paper build where dependency-aware partial reconstruction is materially useful.

This preserves the central JMSLab objective—a reproducible dependency graph—without replacing working collection code prematurely.

## Data validation expectations

Each normalized or analytical table should eventually assert:

- the documented key is non-missing and unique;
- row counts and merge cardinalities meet declared expectations;
- category and date fields use documented domains;
- raw-source and run identifiers remain traceable;
- checksums match downloaded files where media are available;
- missingness is reported rather than silently imputed.

## External data and redistribution

Open API access does not imply permission to redistribute creatives. Raw ad JSON, images, video, signed URLs, first-party identifiers, and generated model tables stay outside Git. Public replication artifacts should contain code, versioned sampling specifications, checksums, schemas, aggregate results, and instructions for authorized reconstruction.

Use [`raw_directory_readme_template.md`](raw_directory_readme_template.md) for every new external source.
