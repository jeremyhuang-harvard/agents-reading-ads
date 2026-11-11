# Raw source README template

Create one completed copy of this document for each external data source or source family.

## Source identity

- Source/platform:
- Repository or API name:
- Official documentation:
- Data owner:
- Access classification: public / account-gated / approved research / restricted
- Redistribution restrictions:

## Retrieval

- Collector program and version/commit:
- Versioned configuration or roster:
- Retrieval dates and timezone:
- API routes or source pages:
- Authentication method, if any (never include secrets):
- Rate limits and retry policy:
- Geographic or temporal filters:
- Known sampling-frame limitations:

## Local layout

- Immutable run directory pattern:
- `orig/` or raw-response location:
- Lightly processed data location:
- Media location:
- Manifest location:
- Failure/retry log location:

## Integrity and provenance

- Stable source identifier:
- Local primary key:
- Retrieval timestamp field:
- Source URL field:
- Checksum algorithm:
- Deduplication rule:
- Expected manifest fields:

## Schema

Document every retained field, its type, source, meaning, missingness convention, and whether it comes from search, detail, media inspection, or a derived transformation.

## Processing

List each transformation from the original response to lightly processed data. Link to the producing script and identify all inputs and outputs. Do not modify files in an immutable raw run.

## Validation

- Expected row-count or quota checks:
- Unique/non-missing key checks:
- Checksum checks:
- Schema/domain checks:
- Missing-media accounting:
- Known unresolved errors:

## Usage and citation

- Permitted research uses:
- Citation requirements:
- Required acknowledgments:
- Contact or approval record location:
- Date this README was last verified:
