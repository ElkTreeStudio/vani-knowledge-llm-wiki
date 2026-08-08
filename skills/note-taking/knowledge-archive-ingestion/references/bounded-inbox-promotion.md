# Bounded Inbox Promotion

Use this pattern for an explicitly approved, finite batch of Markdown intake files when the governed knowledge root already defines `sources/`, `staging/`, schemas, validators, and import-run records. This is promotion of known inputs, not open-ended archive discovery.

## Transaction shape

1. Freeze the exact input list and write allowlist. Treat all other Inbox files and frozen artifacts as out of scope.
2. Read root, Inbox, source, staging, schema, import-run, and domain contracts before choosing destinations.
3. Inspect only bounded adjacent canonical sources and formal pages. Reconcile every input to one terminal disposition: `create`, `update`, `link-only`, `hold`, or `drop`.
4. For each existing input, immediately before move/removal:
   - copy its exact bytes to an external backup preserving the relative path;
   - record byte count and whole-file SHA-256;
   - verify the backup;
   - record rollback instructions for both restoration and deletion of newly created paths.
5. Move source evidence byte-for-byte. Do not wrap or rewrite the payload to add metadata.
6. Create a sidecar at the exact path:

   ```text
   sidecar_path = payload_path + ".source.md"
   ```

   Preserve the payload's entire filename and every extension. Record `payload_path`, payload SHA-256, source URI, media type, immutable status, and stable source ID.
7. Write staging records separately from source payloads. Keep observation, inference, uncertainty, and recommendation distinct.
8. Modify formal knowledge only when the bounded review finds genuinely new durable synthesis within the write allowlist. Existing coverage should produce `link-only`, not cosmetic churn.
9. Remove successfully processed Inbox copies only after their canonical payload or duplicate target and rollback evidence have read back successfully.

## URL deduplication

Use a normalized canonical source URL as the primary collision key. When the same URL already has a canonical source:

- do not create a second payload or overwrite the existing source;
- back up the Inbox input, record both Inbox and existing-canonical hashes, and resolve it as `link-only` through a duplicate-group record;
- preserve differences as provenance in the run evidence rather than pretending they are independent sources.

A similar topic, title, or author is not enough for source-level deduplication. Those cases may still share a staging duplicate group while retaining distinct canonical captures.

## Holds after successful capture

A semantic hold does not automatically require retaining a second Inbox copy. If the byte-preserving payload and sidecar are complete, the source is no longer stranded in Inbox; keep the pending decision in the appropriate staging directory. Retain the Inbox original only when the governing Inbox contract explicitly requires it or canonical capture itself is blocked.

Typical holds include cross-domain ownership, unverifiable product/version claims, missing publication metadata, and overlap that needs a separate synthesis authority. Never guess missing author/date metadata merely to avoid a hold.

## Frozen artifact boundary

An exact frozen path must be excluded before file type detection, `stat`, hashing, parsing, moving, indexing, or archive entry listing. Verify the scanner's exact-path exclusion before the batch. Do not broaden the exclusion by basename or extension.

## Import-run evidence

Maintain four canonical records when the repository requires them:

- `run.md`: authority, scope, tools, commands, timestamps, warnings, result;
- `manifest.yaml`: every create/modify/move/archive with before/after paths, bytes, whole-file hashes, schema, approver, and result;
- `validation.json`: schema/hash/link/test/read-back checks and actual exit codes;
- `promotion.md`: reviewer, time, target groups, link-only decisions, holds, and formal writes.

Keep an external `SHA256SUMS`, rollback mapping, migration mapping, and post-run manifest in the work directory.

### Final-manifest immutability boundary

Determine whether `system/import-runs/` is excluded by the manifest scanner before sequencing final evidence:

- **If import-run records are excluded:** run the post-manifest build and verification, then finalize `validation.json` and `run.md` with the real final exit codes. Because the directory is excluded, this does not invalidate the verified snapshot.
- **If import-run records are included:** finalize all in-root records before building the post-manifest; place final build/verify receipts outside the root, and do not mutate the root afterward.

Do not leave planned final gates as `null` in the authoritative validation record when the scanner contract permits recording their real results. Never modify a manifest-covered file after successful verification without rebuilding and re-verifying.

### Post-review evidence repair

A fresh semantic reviewer may find that a completed `run.md` does not clearly point to the external final-manifest receipt. When `run.md` is manifest-covered:

1. back up `run.md` immediately before the small evidence-only edit;
2. add the external receipt path and terminal build/verify result;
3. create a **new** post-manifest snapshot rather than overwriting the prior immutable snapshot—manifest builders may intentionally reject an existing output path;
4. verify the new snapshot against the root;
5. update only the external receipt to reference the new snapshot, after backing up that receipt;
6. do not mutate the knowledge root afterward.

If a combined shell invocation prints a success marker but the wrapper reports a non-zero status, do not infer success from stdout. Re-run the final verifier as a standalone command, capture its explicit exit code, and use only that terminal result as evidence. Preserve the earlier snapshot and failed-attempt evidence; do not delete them to make the run look clean.

## Protected-path-aware verification

When an authority order contains an absolute denylist, it overrides any otherwise-standard root-wide validator. Before executing each checker, inspect its documented traversal scope and select only checks that can be confined to the explicit input/target mapping. In particular, do **not** run a root manifest, root lint, root link scan, or root verification command if it would open, hash, stat, parse, or otherwise traverse a denylisted path merely to complete the scan.

Use this bounded alternative instead:

1. Persist preflight evidence in an external work directory: the exact input list, whole-file input hashes/byte counts, mapping/dispositions, collision/duplicate decisions, baseline-manifest readability, and a prepared migration manifest.
2. Immediately before mutation, recompute every allowlisted input hash and re-check only its exact target, sidecar, staging, backup, and run-id collision paths. Stop on drift or collision.
3. After atomic writes, directly read back every payload, exact `payload_path + '.source.md'` sidecar required field, staging record, backup, and import-run file. Recompute hashes from bytes rather than accepting the writer's report.
4. Validate the import-run manifest itself: completed status, operation count, operation target allowlist, after hash/byte values, and required run files. Make completed run records read-only when the repository contract requires immutability.
5. Run fixture/unit suites only when they operate on isolated fixtures rather than the governed root. Record actual interpreter/command and exit code.
6. In `validation.json` and the final report, name every deliberately skipped root-wide checker and state the precise denylist conflict. This is a governed omission, not a silent missing gate.

A local baseline manifest may be verified as readable when the authority explicitly prohibits GCP/API probes; record the fixed generation and external manifest path without creating a new cloud backup or remote object probe.

## Deterministic acceptance

Run each required suite/gate exactly as governed, then read back:

- every expected payload and exact sidecar path;
- payload hash equality with the original input;
- staging frontmatter and directory/record-kind agreement;
- formal frontmatter and links for any actual formal write;
- absence of every successfully processed Inbox input;
- presence and hash equality of every backup;
- all required import-run files and terminal dispositions.

Report the 1:1 input-to-destination mapping, work directory, backup paths, commands with exit codes/key output, and every hold with its reason and Inbox-retention decision.
