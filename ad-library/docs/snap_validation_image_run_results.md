# Snapchat still-image validation run

## Status

The frozen Snapchat still-image arm completed successfully on 2026-10-15. This is a model-measurement output awaiting comparison with independent human coding; it is not prevalence evidence or a causal result.

## Run identity

- Packet specification: `snap_validation_sample_v1.0.0`
- Codebook specification: `snap_validation_codebook_v1.0.0`
- Arm: `image_only`
- Provider: `openai-codex`
- Model: `gpt-5.6-sol`
- Run fingerprint: `5edc6a0718446281044810d4fb1fd7089c2d1c7b1456df1d141036b3680b90a2`
- Completed at: `2026-10-15T18:34:00.751248+00:00`
- Packet manifest SHA-256: `7790445b9ea798693ac86cff7c91ccfafbd4b55ea977a301b1864af314410fd7`
- Codebook SHA-256: `53383396ef4ab86893d4698f015a4ab420d243e57aa9dcae2cc9f7e43fd7db2a`
- Prompt SHA-256: `0a5ea7a0258bab2f6cc7868a91d03dfdd609893d778f3b27e223e459b9649b34`
- `model_codes.csv` SHA-256: `8b6ecd62eab4660bb27a1f985cd8916c3fb0d14f8b5fff9e2dbeb9183d7f222d`
- Final run manifest SHA-256: `2b32725dad3a72ac11e560a646c56be84ad9eea434ccb0c68cf94338800d9e3f`

Generated outputs remain outside Git under the ignored `data/processed/snap_validation_v1/gabriel_image_arm/` directory.

## Verification

- 30 expected still-image creatives
- 30 returned model rows
- 30 unique coding IDs
- Exact equality between expected and returned coding-ID sets
- Exact frozen output-column schema
- 30 raw response rows
- 30 runtime media hashes recorded
- Zero media checksum mismatches
- Final manifest matches the pre-run fingerprint, packet, media, prompt, codebook, provider, and model identity
- Process exited normally with status code 0
- No reported timeout, rate-limit, connection, or JSON-parsing errors

The production runner rejected stale output reuse and supplied the exact verified image bytes to GABRIEL in memory.

## Interpretation and next step

These 30 rows constitute the completed model side of the still-image validation exercise. They should remain blinded from human coders until independent coding is complete. The next analytical step is to collect at least two independent human judgments where feasible, then compute human–human and human–GABRIEL agreement by field and inspect systematic disagreements before revising the codebook or scaling model coding.

The 30-video arm remains out of scope until a separate protocol freezes how full motion, frames, on-screen text, speech, music, and other audio will be represented consistently to both human and model coders.
