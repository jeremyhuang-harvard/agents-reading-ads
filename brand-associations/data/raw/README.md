# Raw data provenance

Raw data are immutable external inputs. Do not commit raw, restricted, personal, licensed, or large files to Git.

Create one subdirectory per source and document:

- source name and owner;
- exact URL, API endpoint, archive, or transfer mechanism;
- access date and collection window;
- license, terms, consent, and retention constraints;
- unit of observation and stable identifiers;
- original filenames and formats;
- collection query or request manifest;
- row/file counts;
- SHA-256 checksum for every file;
- any transformation between the received original and the stored raw file;
- known selection, missingness, and measurement limitations.

Never overwrite a raw capture. Add a new dated or run-identified capture instead.
