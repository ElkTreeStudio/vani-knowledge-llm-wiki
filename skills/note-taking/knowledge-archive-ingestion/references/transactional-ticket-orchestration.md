# Transactional ticket orchestration for archive ingestion

Use this reference when several model-driven tickets update schema-driven wikis.

## Preflight contract

For each ticket record:

- authoritative approved IDs and source file
- live target classification: new / update / link-only / drop
- exact existing-file backup set
- exact new-target allowlist
- baseline hashes and expected live-count delta
- one writer for every shared index/log/canonical

Before model launch, assert existing files equal backup and new targets are absent. If a supposedly new target exists, stop and reclassify it as an update with a new backup.

## Producer wrapper states

Parse the JSON envelope into distinct states:

- `completed + VERDICT: PASS`: provisional producer PASS; run deterministic acceptance
- `completed + VERDICT: FAIL`: semantic/source precondition failure; inspect findings, do not quota-retry
- `max_turns`: preserve session ID and drafts; rollback promotion; resume the same session
- `api_error_status == 429`: rollback and schedule only at the provider's reset window
- timeout/auth/permission failure: rollback and report immediately

Never infer quota from free-text substring matching. In particular, `session_id` can make a naive `"session" in envelope` test return true.

## Partial transaction rollback

On non-success:

1. Move every new allowed target to a restricted attempt-specific quarantine.
2. Save partial copies of each edited existing file.
3. Restore existing files from the ticket's current verified backup.
4. Assert restored bytes match and allowed targets are absent.
5. Retain the producer envelope, session ID, quarantine manifest, hashes, and modes.

Resume from the session plus quarantine drafts instead of repeating full source exploration.

## Independent acceptance after producer PASS

Do not trust the producer's first line. Recompute with deterministic tools:

- raw body hashes using the target wiki's executable validator convention
- required frontmatter/taxonomy
- actual filesystem and index counts
- target registrations and link resolution
- append-only log byte prefix
- sensitive-pattern scan
- changed-file allowlist

Path discovery must account for the actual ingestion date written by the producer; do not hard-code an older draft date and mistake correctly dated files for absence.

## Stale baseline handling

If a legitimate concurrent ticket changed the wiki after backup:

- identify the exact diff and provenance
- run the wiki's authoritative linter
- do not restore the old backup
- create a new exact-file backup and manifest
- recalculate expected counts and protected pages
- rerun preflight

## Final manifest ordering pitfall

- Finalize every knowledge-root run record (`run.md`, internal manifest, validation record, maintenance append) **before** building the external finalized-root manifest.
- Build and verify that manifest only after the last knowledge-root write. Do not edit the knowledge root afterward.
- Store final manifest verification output in external evidence, not in a knowledge-root file that the manifest itself covers; otherwise recording PASS mutates the root and immediately makes the manifest stale.
- Independently rerun `verify_manifest.py` after the producer finishes. A producer may have verified an intermediate manifest that becomes stale when it finalizes its own run records.

## Staging-analysis validator pitfall

- Validate fields against the actual staging schema and analysis contract; do not invent stronger requirements during the write phase.
- In particular, an `inference` list may legitimately be empty when no inference is needed. An empty inference is not a malformed record if observation, uncertainty, target handling, and source locator satisfy the contract.
- Run structural analysis validation before any knowledge-root write so a validator correction cannot leave partial state.

## Large-batch read/converge/write pattern

For archive-ingestion batches large enough that full semantic reading could overrun one worker's context:

1. Freeze the batch's exact input set, ordinal range, source hashes, and byte counts before analysis.
2. Partition inputs by **balanced total bytes**, not merely equal item count. Use several read-only analysis slices; splitting analysis does not change the user's requested transaction batch size.
3. Each analyst must read its assigned sources fully, write only an external result artifact, and reconcile every result one-to-one by ordinal, stable source key, source ID, filename, and SHA-256. Analysts must not modify the knowledge root.
4. Before any knowledge write, independently combine all slice outputs and verify full coverage, uniqueness, schema, safe source routes, existing suggested targets, source locators, file permissions, and current source hashes. Re-verify the previous finalized-root manifest to prove the read-only phase caused no knowledge drift.
5. Hand the reconciled combined analysis to **one writer**. The writer performs the entire user-visible batch as one atomic transaction with one rollback boundary, even if analysis used multiple workers or multiple waves.
6. Do not run concurrent knowledge-root writers. Read fan-out may be parallel; convergence and write must be serialized.

### Mid-flight batch-size and quota corrections

- A new batch-size instruction applies to the next unopened transaction. Do not interrupt an already-running atomic writer merely to resize it; finish and verify that batch, then use the new size.
- If a large requested batch needs smaller internal analysis slices, report those as implementation detail while preserving the requested external batch size.
- Treat a user's later explicit instruction to continue or ignore a prior quota pause as an authority update. Record the actual producer route and remove the quota stop condition from the active plan/state; do not keep re-pausing on a superseded threshold.
- Quota routing never relaxes integrity gates: exact scope, one writer, backups, tests, strict lint, finalized-root manifest, read-back, and rollback remain mandatory.

## Batch metadata compatibility pitfall

- Treat the frozen item list and its exact ordinal set as authoritative. Optional summary aliases such as `ordinal_range`, `ordinals`, or `queue_ordinals` must not become undeclared hard requirements.
- If an executor expects a batch-range summary field, either emit the agreed field during preparation or accept equivalent aliases after verifying they exactly match the item ordinals.
- Run this compatibility check before any knowledge-root write; a missing non-required summary field must not trigger a partial transaction.

## Analysis-artifact convergence and correction evidence

When combining parallel read-only analyses:

- Preserve each analyst's original result artifact byte-for-byte. Corrections and normalizations belong in separate evidence files or the combined artifact's provenance, never as silent edits to the original.
- Distinguish semantic contradictions from administrative metadata defects. A record marked `unclassified` with a non-null formal target is semantic and must be re-read/re-decided before writing. A null slice number is administrative when the assigned input path uniquely proves the slice; it may be normalized during convergence with explicit provenance.
- Reject a conflicting non-null slice number, duplicate ordinal, missing item, source-key/ID/filename/hash mismatch, unsafe route, missing target, or invalid source locator. Do not infer through these failures.
- Apply any single-item correction by ordinal only after rechecking the frozen source hash and full source content. Record the correction path and preserve the superseded analyst output.
- The combined artifact should report classification counts, route counts, correction count, metadata-normalization count, and a whole-file SHA-256 consumed by the writer contract.
- Prefer deterministic preparation and convergence helpers for repeated batches. Their outputs must include exact input hashes, ordinal bounds, byte-balanced slice manifests, permissions, and machine-readable PASS/failure evidence; helpers do not replace independent final acceptance.

## Python dynamic-import probe pitfall

- When a preflight test harness loads an executor module with `importlib.util.spec_from_file_location`, register the module in `sys.modules[spec.name]` before calling `exec_module`; dataclasses and other runtime introspection may otherwise fail even though the executor itself is valid.
- Prefer invoking the deterministic executor as a subprocess for smoke tests when module introspection is unnecessary.
- Keep loader/probe failures before any knowledge-root write and distinguish them from transaction failures in evidence.

## Progress reporting

Track three separate facts:

- scheduler/timer is waiting
- model child is actively running
- terminal envelope has completed

A live parent/timer is not evidence of active model work. Notify the user immediately on terminal failure and before any delayed retry window.
