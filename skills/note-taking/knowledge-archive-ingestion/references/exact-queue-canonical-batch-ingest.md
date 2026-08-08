# Exact-queue canonical-source batch ingest

Use this pattern when authority approves one fixed queue slice of deterministic per-item Markdown and forbids touching later ordinals, disposition directories, or the external archive.

## Preflight evidence

Before any knowledge-root write:

1. Verify the batch descriptor's whole-file hash and assert the ordinal list is exactly the approved contiguous slice, not merely a count or range label.
2. Verify every source path, byte count, SHA-256, conversation/source key uniqueness, global record-ID uniqueness, and absence of payload/sidecar/staging targets. Reconcile analysis structure without inventing stricter content requirements: a verified bounded section such as `inference` may intentionally be an empty list. Preserve it as an empty labeled section rather than rejecting it or fabricating filler; enforce only the live analysis contract's actual required fields and bounds.
3. Build and verify a fresh whole-root manifest outside the knowledge root.
4. From that manifest, snapshot three protected sets into external evidence:
   - every later queue item as `root-relative path -> present record or null`, so both presence and absence are compared after the batch;
   - abandon/pending plus formal domain/project/entity/archive files;
   - all pre-existing canonical conversation payloads outside the batch.
5. Read every approved conversation fully before classification. Existing source buckets are conservative hints; use `unclassified/` when no reliable existing bucket matches.

## Transaction

- Set external backup directories to `0700` and create a verified `0600` byte-exact backup immediately before each move.
- Move payload bytes atomically and preserve `0600`; never rewrite canonical Markdown.
- Create the exact `payload_path + '.source.md'` sidecar with complete external-archive provenance, converter mapping, equal payload/source-Markdown hashes, and authority decision.
- Create exactly one staging record per source. Separate observation, inference, uncertainty, recommendation, and exact source locator. Keep assistant claims explicitly unverified.
- Keep one writer for the maintenance log and one import run for the full batch. A partial outcome is failure and triggers verified rollback.

## Mid-run batch-size changes

- Treat the active batch descriptor and aggregate-analysis hash as immutable once the writer starts.
- If authority changes batch size while a writer is active, finish or roll back that transaction at its original size; apply the new size only to the next unprocessed ordinal.
- Re-cut only future boundaries. Never renumber the frozen queue, duplicate completed ordinals, or absorb already-ingested records into the new batch.
- For larger batches, use read-only fan-out → deterministic aggregate reconciliation → one writer. The aggregate batch remains one all-or-nothing transaction even though semantic analysis used several slices.
- Update the external plan/state evidence with the effective batch number, ordinal range, old/new size, and authority decision before launching the next writer.

## Finalization and verification ordering

1. Complete all knowledge-root run records and the append-only maintenance entry.
2. Run unit tests, strict lint, strict migration-link checks, and full read-back with bytecode writes disabled.
3. Read back every payload, sidecar, staging record, and backup. Validate sidecar field values and converter parameters, not just file existence.
4. Compare the protected-set snapshots exactly. Confirm later ordinals, abandon/pending, formal layers, and prior payloads have zero drift; confirm no archive appeared in the root.
5. Build the external finalized-root manifest only after the last knowledge-root write.
6. Verify it, then verify it again after producing all external comparison evidence. Never write verification PASS back into the knowledge root afterward.

Store final test/lint/link/read-back/scope-comparison outputs outside the knowledge root to avoid self-referential manifest drift.

## External analysis-manifest repair boundary

A malformed read-only slice manifest is not a reason to weaken the validator or infer metadata from directory names. Before re-dispatch:

1. Preserve every malformed manifest byte-for-byte outside the knowledge root.
2. Record pre/post hashes, counts, and a digest of the ordered item allowlist.
3. Repair only the contract field—for example, emit canonical `analysis_slice` instead of an unsupported `slice` alias—and prove the item list is unchanged.
4. Rerun slices that stopped before semantic output. Reuse an already-completed slice only after validating its output against the repaired manifest and recording the metadata-only normalization in aggregate provenance.
5. Fix the reusable batch-preparation helper and exercise it against the governed validator before preparing the next batch.

Never classify such a pre-write schema stop as a knowledge rollback, and never hide it as a silent normalization.

## Pitfalls

- Put descriptor loading, analysis-shape validation, and all other preflight checks inside the same top-level failure-reporting boundary as the transaction. A failure before the first knowledge-root write needs no rollback, but it should still emit the raw error externally; after the first write, the same boundary must trigger verified rollback.
- A post-manifest built before final `run.md`, validation, or maintenance bytes is stale even if it once verified.
- Do not infer later-queue protection from checking only the next ordinal; compare the entire frozen later-queue state.
- Do not invent a manifest result enum in an ad-hoc checker. Validate the result value defined by the live manifest contract or authoritative linter.
- A final scope diff should equal the exact allowlist: removed Inbox paths, moved payload targets, sidecars, staging records, run files, and the single maintenance modification—nothing else.
- Do not compare `operations_count` directly with the whole-root changed-path count. A single `move` is one manifest operation but changes two root paths (source removal plus target creation), while finalized run-record files and the maintenance append may be tracked as audit evidence rather than content operations. Derive and record both expected formulas from the live contract; for a typical 100-item batch with one move, one sidecar create, and one staging create per item, the operation count is 300, while the root diff additionally includes 100 removed source paths plus run/log evidence. Validate the operation result set and exact changed-path allowlist independently.
- When adapting a previously verified batch runner, keep batch constants together and exercise its pure reconciliation loader before the transaction. Invoke that loader inside the same top-level failure boundary as setup and writes, so malformed descriptors still produce external failure evidence without triggering an unnecessary rollback.
- Validate descriptor metadata against the live batch contract, not the previous batch's incidental JSON shape. The exact ordered ordinal list plus the approved descriptor hash can establish the slice even when a convenience field such as `ordinal_range` is absent. Never require an optional field merely because an earlier batch emitted it; probe the loader against the next immutable descriptor before enabling writes.
- If that pre-write probe fails, preserve a small external failure record with the raw error and explicit `rolled_back` or `no knowledge-root writes occurred` status. After correcting only the contract mismatch, rerun the full preflight and transaction from the unchanged source descriptor; do not treat the earlier transient shape mismatch as a durable tool limitation.
