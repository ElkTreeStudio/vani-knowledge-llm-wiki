# Deterministic writer preflight corrections

Use this reference when a governed Inbox promotion uses a generated or scripted single writer. It records reusable correction patterns from a real promotion run; it is not a replacement for the main transaction gate.

## Contract checks before root mutation

1. Read the queue, normalized plan, writer validator, and verifier as separate schemas. Do not assume a field has the same name in every artifact.
2. Build an explicit field map and test it before dispatch. A common mapping is:
   - queue `source_path` → operation `source_path`
   - queue `root_relative_path` → operation `source_root_relative_path`
   - queue `sha256` → operation `source_sha256`
   - queue `byte_count` → operation `byte_count`
   - queue `mode` → operation `mode`
   - queue `source_file_name` → operation `source_file_name`
3. Recompute the queue hash with the same canonical projection used to create the frozen manifest. Confirm the commander plan hash with a system checksum tool and pass that exact value to the writer.
4. Keep source-content conflicts separate from execution blockers. A non-empty `conflicts` list is safe only when the plan carries an explicit policy to preserve identities, expose the disagreement, avoid deduplication/fact-checking, and avoid promoting claims. Do not let a writer use `if plan.conflicts: block` as a blanket rule.
5. Validate all exact target paths, not only target roots. Reject collisions, symlinks, special files, scope expansion, and protected-path encounters before the first mutation.

## Manifest and provenance ordering

- Create and hash the immutable payloads and `.source.md` sidecars first; then generate the snapshot manifest from the actual installed sidecar bytes. Never write a placeholder sidecar hash into a manifest that is later treated as authoritative.
- A hash helper must support both paths inside the knowledge root and verified external rollback copies. Do not unconditionally convert every path to a root-relative path before hashing an external backup.
- Keep external rollback copies and result artifacts outside the knowledge root. Record their whole-file hashes and read the records back before accepting a producer commit.

## Repair-and-retry protocol

If a writer fails before root mutation:

1. Preserve the failed result under a unique external filename before the next attempt; do not overwrite the failure evidence.
2. Confirm the formal root is still equal to the pre-write baseline and the exact source queue is still present.
3. Patch only the deterministic validator/runner defect, compile or syntax-check it, and rerun the plan/queue/hash preflight. The commander plan and queue hashes must remain unchanged.
4. Dispatch one replacement writer. Do not claim success from the original failure or from a producer `committed` status alone.
5. After the replacement commits, run an independent verifier and a second direct smoke check over the TSV, payload bytes, sidecars, rollback backups, expected path set, source cleanup, and temporary-artifact absence.

## Evidence boundary

A producer result proves only that the writer believes its transaction committed. Acceptance requires independent read-back of every new artifact, exact unchanged-baseline hashes/modes, exact delta path set, sidecar-to-payload links, staging linkage, and verified rollback evidence. Keep the first failed attempt, correction note, final writer result, verifier result, and post-root manifest together in the external audit directory.
