# Large-batch canonical ingestion orchestration

Use this reference when an approved immutable-source queue is promoted in large atomic batches with parallel read-only analysis and one serialized writer.

## Batch lifecycle

1. Freeze exact queue ordinals, source paths, IDs, byte counts, and SHA-256 values outside the knowledge root.
2. Partition analysis by total bytes, not only item count. Keep an oversized source as a singleton slice and require bounded pagination or deterministic structural parsing so the full source is inspected without truncation.
3. Run semantic slices read-only. Each slice writes one external `results.json` under `0700`/`0600` permissions.
4. Deterministically reconcile all slice outputs against frozen inputs before starting a writer: exact coverage, ordering, IDs, filenames, hashes, safe routes, target existence, locators, classification consistency, uniqueness, and permissions.
5. Give one writer the immutable input and reconciled-analysis hashes. The writer must create verified rollback copies before moving payloads and roll back the entire batch on any transaction failure.
6. Independently rerun tests, strict lint, migration links, exhaustive read-back, scope comparison, and final-root manifest verification. Only then mark the batch complete or obey a pause boundary.

## Input and output schema discipline

- Use one canonical field name for slice identity, such as `analysis_slice`; do not emit informal aliases such as `slice` when the contract names another field.
- Optional summary metadata (`ordinal_range`, `ordinals`, `queue_ordinals`) must never override the actual item list. Derive authoritative ordinals from items and reject only genuine contradictions.
- If a non-semantic metadata field is malformed, preserve the original manifest, write a byte-exact pre-repair copy, repair only that field, prove item-list identity, and record pre/post hashes in external evidence.
- Never silently repair a semantic contradiction. For example, `unclassified` with a non-null formal target requires a bounded re-review and separate correction evidence.

## Provider failure after artifact creation

A provider may return HTTP 429 or fail while sending its final report after a complete result file was already written. Do not assume either success or failure from the envelope alone:

1. Inspect the actual artifact.
2. Run deterministic full reconciliation against the frozen manifest.
3. If every item, source hash, route, locator, target, schema, and permission passes, accept the artifact and record that the provider failure occurred after artifact creation.
4. If reconciliation fails or coverage is partial, quarantine or overwrite only through a fresh bounded retry; never promote partial analysis.

## Legitimate concurrent knowledge-root changes

An older final-root manifest can fail because a user or another governed workflow legitimately added an unrelated file after the prior batch. Treat this as baseline evolution, not automatic corruption:

1. Identify the exact unexpected path without reading private body content unnecessarily.
2. Verify it is absent from the frozen queue.
3. Record path, size, mode, and SHA-256 in external evidence.
4. Add it to the next writer's protected baseline: preserve byte-for-byte, do not ingest it, and do not delete it as drift.
5. Build the new pre-manifest from the current root and require the next final scope comparison to prove that protected file stayed unchanged.

Never restore an old manifest or stale backup over a legitimate concurrent addition.

## Pause and resume boundaries

Interpret “finish this round, then pause” as finishing the active batch through semantic reconciliation, atomic writer transaction, and independent verification. Pause before preparing the next batch. Persist:

- completed batch and ordinal range
- completed and remaining counts
- final manifest path and verification result
- next resume ordinal
- explicit confirmation that the next batch was not created or started

If the user later resumes, supersede the pause in the plan/state record, re-baseline the live root, and continue from the frozen next ordinal without repeating completed items.

## Final-manifest ordering

Finalize every knowledge-root run record and append-only maintenance entry before generating the final-root manifest. Verify it externally and do not mutate the knowledge root afterward. A producer exit code is not acceptance; parent-level verification remains mandatory.
