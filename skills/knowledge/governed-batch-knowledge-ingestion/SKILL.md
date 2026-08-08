---
name: governed-batch-knowledge-ingestion
description: "Use when ingesting a large queue into a governed wiki."
version: 1.3.1
---

# Governed Batch Knowledge Ingestion

Use for Roy-authorized, multi-batch ingestion of a finite Inbox/source queue into the knowledge base.

## Operating contract

1. Determine the complete queue and batch size before dispatch.
2. Treat user authorization to process the remainder as authorization to continue automatically across batches.
3. For each full batch: run the required read-only planning role, validate the entire batch mapping, run the required writer role, then verify the actual artifact/read-back results.
4. After every batch, query the configured quota. If the user’s stop threshold has not been reached and no real blocker exists, start the next batch immediately. Do not wait for a reply after reporting.
5. Report only at the requested batch cadence. A report is status visibility, not a confirmation gate.
6. On a retryable failure, inspect concrete evidence, repair the deterministic workflow, and retry immediately. Never claim that a repair is underway unless a process has actually been started.

## Scope, intent, and proportionality gate

Before reading deeply, dispatching a worker, or creating any artifact, classify the user's latest instruction by side-effect class. The latest correction overrides earlier goals:

1. **Read-only lookup/audit/history request** (for example, “先查紀錄”, “只列模型”, or “不要寫東西”) means no move, delete, patch, write, rule cleanup, writer dispatch, or new knowledge-root evidence. Read the existing records only; report exact model IDs, session IDs, usage fields, paths, and missing fields without guessing. A late async result is historical evidence, not permission to resume the superseded workflow.
2. **Bounded source write** means the user explicitly asks to copy/move/capture a small, named set. Use the smallest sufficient path: exact inventory, collision check, byte-preserving write/move, and direct read-back. Do not automatically expand it into multi-batch freeze, semantic planning, role-worker fan-out, global rollback, or full-root acceptance unless the user asks for those controls or the live source contract makes one mandatory.
3. **High-risk or broad promotion** (large queue, formal domain/project publication, destructive cleanup, protected archives, or ambiguous ownership) may use the full governed transaction below. State why the extra controls are necessary before dispatch.
4. When scope is ambiguous, ask one focused question before any side effect. Never treat a request to inspect records as approval to modify the rules, schema, tests, or audit history.

For a simple bounded move, keep the evidence proportional and local to the exact delta. Preserve a concise audit record outside the knowledge root when one is requested, but do not manufacture a durable governance layer for a one-time operation.

### Method authorization checkpoint

The user's authorization of an outcome is not authorization for an implementation method. Before any worker, planner, model, rule, schema, test, or audit artifact is created:

1. Write a one-line interpretation of the requested outcome, source scope, allowed mutations, forbidden/unknown mutations, and required evidence level.
2. If the request names a bounded Inbox folder or file set and does not explicitly name an archive/export workflow, classify it as an ordinary bounded source operation. Do not route it through `knowledge-archive-ingestion` or a ChatGPT/export profile. A folder name or body text mentioning ChatGPT is a data label, not an archive trigger.
3. Use the smallest sufficient path: exact in-scope listing, collision check, byte-preserving copy/move if authorized, and direct read-back. Do not create a frozen queue, semantic planner packet, role-worker fan-out, global rollback plan, full-root baseline, or multi-model review unless Roy asks for that control or the live source contract makes it unavoidable. If a stronger control changes scope, side effects, or model usage, ask before dispatch.
4. Model dispatch requires an explicit task need, not merely worker availability or the existence of a governance skill. Never call Sol, Luna, or Terra for a bounded move solely to classify, validate, or write ordinary source records.
5. Do not create durable ChatGPT-specific rules for one-time work. Keep one-time audit and usage evidence outside the knowledge root; historical records are not active policy. If Roy later asks to remove such rules, inventory and remove only policy/implementation/test clauses, preserving source data and historical audit unless deletion is separately explicit.
6. If Roy says only inspect records, list models, or do not write, halt all mutations even when an earlier request authorized ingestion; the latest correction wins.

## Pre-write root baseline gate

Before dispatching any writer that may touch the formal knowledge root:

1. Define the exact opaque no-touch paths and the fixed control/metadata marker policy before traversal.
2. Build a fresh whole-root manifest outside the knowledge root using one shared iterator for manifest, lint, link, and scope checks. Inventory only non-excluded regular files and sort by root-relative path; record path, root-relative path, byte count, SHA-256, and mode.
3. Compare each lexical absolute path against the opaque set before `lstat`, `open`, hash, parse, index, symlink checks, or recursion. An entry name may be observed solely to perform the exact comparison; never descend into an excluded directory or inspect an excluded file.
4. Keep opaque exclusions exact-path only. If the contract excludes `README.md`, `.DS_Store`, or other control artifacts from the payload baseline, apply that fixed marker policy before metadata/content probes and record every marker in protected-set evidence instead of hashing it.
5. Fail closed on symlinks, special files, permission/read errors, or source changes. Preserve raw errors externally and set the evidence status to `blocked`.
6. Write the manifest, protected set, and summary only to an external `0700` worker directory; keep JSON artifacts `0600`. The summary must assert zero knowledge-root writes, no opaque probes, and no semantic judgment.
7. After provisional evidence is written, read it back once and reconcile ordered manifest equality, counts, source byte counts, modes, SHA-256 values, and protected-set equality. A single mismatch prevents `PASS`.

### Opaque-folder count reporting without violating no-touch boundaries

When a read-only freeze report asks for file counts for an exact opaque directory while also forbidding inspection:

1. Observe only the immediate parent entry name and compare its lexical absolute path against the exact opaque set. Do this before any `lstat`, `open`, hash, parse, symlink check, or recursion.
2. If the exact opaque directory entry is absent, `file_count: 0` is a permitted absence-derived fact; record that it came from parent-entry observation and that the target was not probed.
3. If the exact entry is present, do not enumerate or count descendants. Record `file_count: null` (or an equivalent not-probed value) and an explicit policy status. Never trade the no-touch contract for a requested numeric count.
4. Distinguish protected-folder counts from eligible-folder counts. Derive counts for non-opaque payload folders from the frozen manifest itself, not from a second unrestricted root walk.
5. For fixed control markers such as `README.md` and `.DS_Store`, metadata-only `lstat` is acceptable when the policy allows it; never open, hash, parse, or semantically inspect marker content. Record `content_opened: false` and `hashed: false`.

If the scanner or report generator is patched after a run, the previous run is stale: create a new unique external producer run, regenerate all evidence, rerun read-back/source reconciliation, recompute artifact hashes, and select only the final run as authoritative.

See `references/knowledge-root-baseline-evidence.md` for the reusable evidence shape and reconciliation checklist.

## Batch integrity

- Preserve a deterministic source mapping from queue ordinal to source path, filename, and hash.
- Let model workers supply semantic classification/planning only; generate or re-attach deterministic source identity fields from the validated input mapping when safe to do so.
- Reject malformed, duplicate, missing, or unaligned model results.
- Before writer dispatch, validate all planned source hashes and complete batch coverage.
- For partial final batches, derive expected count and ordinal bounds from `inputs.json`; never assume 100.
- Build writer task packets from explicit batch metadata (batch number, start/end, count, input hash, analysis hash, unique run ID), not brittle copied-string replacements.

## Read-only semantic planner mode

When the task stops at a proposal and authorizes exactly one artifact outside the knowledge root, keep the planner and writer scopes separate:

1. Read the packet first and obey its exact read allowlist. Read every frozen queue source completely, then read the live source/schema contract and the explicitly named project examples before choosing classifications or destinations.
2. Parse the frozen manifest as the authority. Reconcile each queue item by exact absolute path, root-relative path, byte count, mode, and whole-file SHA-256. Distinguish the manifest file's own SHA-256 from the manifest's `queue_sha256` field; the proposal carries the latter unless the packet explicitly asks for both.
3. Check protected paths before any `lstat`, open, hash, parse, index, or recursion. To test target availability, probe only the exact proposed destination paths; never broaden this into a scan of the knowledge root.
4. Prefer the live canonical-source contract over inferred project conventions. For Markdown article captures, use a deterministic dated snapshot label supplied by the packet, normalized category paths, immutable payload bytes, and `sidecar_path = payload_path + '.source.md'`. Do not invent dates from document bodies.
5. Emit exactly one operation per queue ordinal. Use low confidence for draft/planning material, keep source identities and hashes verbatim, and use deterministic catalog/navigation targets rather than generated factual synthesis. A source-level disagreement can live in `conflicts` without a staging target when no overlap, duplicate identity, provenance gap, or model-derived claim is being promoted; reserve `staging_targets` for those concrete review records.
6. Before writing, verify every proposed destination is absent or record a collision. Write only the explicitly permitted external proposal. Read it back, parse it as JSON, re-check operation coverage/source hashes/formal-target equality, and hash the exact proposal bytes with a system checksum tool.
7. If parallel file reads make result ordering or labels ambiguous, do not infer identity from display order. Re-run a manifest-driven exact-path verification and normalize manifest `sha256` to proposal `source_sha256` explicitly before accepting the plan.
8. Honor a strict report contract when the packet gives one: return only proposal path, proposal SHA-256, coverage, conflicts, and the blocker with its raw error. Never call the read-only proposal canonical ingestion or claim that a writer ran.

See `references/read-only-planner-verification.md` for the reusable manifest-driven validation pattern and report boundary.

## User-directed ordinary article-source capture

When Roy explicitly says that a named Inbox folder contains curated articles and that those files should be treated as ordinary newly delivered articles, that statement is a classification override for that bounded folder. Do not reclassify the files as a ChatGPT/export archive, demand upstream archive IDs or external-archive provenance, or apply a conversation-specific profile merely because filenames or body metadata mention ChatGPT. Re-plan the affected queue before writing, preserve the raw bytes, and record Roy's exact authority in the plan and import-run evidence.

For this mode:

1. Treat each eligible file as one ordinary article source capture. Use the live canonical source contract and an exact deterministic target map, normally `sources/articles/<stable-name>.md` plus `sidecar_path = payload_path + '.source.md'`.
2. Preserve the payload byte-for-byte. The sidecar may record the original Inbox path as historical `source_uri`, the capture timestamp, payload path, payload SHA-256, immutable status, and the ordinary article-source record kind. Do not infer conversation identity or fabricate archive provenance.
3. Keep this bounded source-layer operation separate from formal promotion: unless explicitly authorized, set formal, staging, index, and map targets to empty. Create only the required import-run and append-only maintenance evidence.
4. If a prior plan classified the folder as an archive and blocked it for missing archive provenance, discard that semantic blocker after the explicit correction and generate a fresh plan; preserve the old plan as audit history, record any deterministic path-only normalization, and do not ask Roy to provide provenance that he explicitly waived by this classification.
5. Keep unrelated queue items on their own gates. A mixed-source item outside the explicitly overridden folder may remain blocked for a source-boundary defect; never broaden the article override to it silently.
6. A full-root strict-lint failure on paths outside the exact delta is a pre-existing governance blocker, not permission to repair unrelated files in this transaction. Run targeted lint/read-back on changed paths, report the unchanged full-root errors plainly, and do not call the whole knowledge root green.

See `references/ordinary-article-source-promotion.md` for the decision matrix, deterministic normalization record, sidecar contract, and acceptance evidence pattern.

## Inbox promotion transaction gate

For an authorized Inbox-to-wiki promotion where the user names exact no-touch folders or frozen artifacts, serialize the run as:

`freeze → read-only semantic plan → commander policy gate → one writer → independent verifier → quota boundary`.

- Freeze a canonical queue with stable ordinals, source paths, byte counts, modes, whole-file SHA-256, queue hash, and an exact protected set. Never let concurrent workers write the authoritative manifest names; use unique producer names, read back the chosen manifest, then lock authoritative planning artifacts read-only (`0400`) before dispatch.
- Compare exact protected paths before `lstat`, `open`, hash, parse, or recursion. The two no-touch ChatGPT folders and a frozen ZIP are opaque policy boundaries; observing a parent entry for exact comparison is not permission to inspect descendants. Treat control/system artifacts such as `.DS_Store` with an explicit, separately recorded marker policy rather than accidentally mixing them into the content queue.
- Have the semantic planner produce mappings and conflicts only. A commander may normalize target extensions or schema details only after reading the live README/schema; record the original plan, normalized plan, reason, and one-to-one mapping. For the repository staging contract, Markdown frontmatter plus Observation/Inference/Uncertainty/Recommendation is the safe default; do not blindly materialize a model-proposed `.yaml` suffix when the live records use `.md`.
- Keep unresolved duplicate URLs, overlap, provenance uncertainty, and model-derived claims in `staging/unclassified/`; set formal targets to an empty list. User delegation can authorize this bounded source/staging transaction, but must not erase conflict evidence or silently promote formal domain/entity pages.
- Before a high-capability writer starts, make its packet satisfy both semantic governance and runner preflight. Include literal, machine-detectable declarations for `effective Luna plan`, `Roy gate`, `write allowlist`, and `stop conditions` when the role runner requires them; then list the exact source moves, extension-preserving `.source.md` sidecars, staging records, rollback location, and zero-formal-write rule.
- The writer must make verified external rollback copies first, refuse target collisions, preserve source bytes, use one serialized writer, and abort/rollback on hash drift, secrets, schema failure, or scope expansion. A producer's `committed` status or exit `0` is not acceptance.
- The independent verifier must derive its expected path set from the frozen baseline plus the exact delta: source removals plus canonical payloads, sidecars, and staging records. Re-read every new artifact, compare unchanged baseline hashes/modes, validate sidecar path formula and staging linkage, verify rollback copies, and assert formal/index paths are unchanged. Normalize verifier records before comparison (including deterministic ordinals and nested `formal_targets` fields) so a verifier schema bug does not masquerade as data drift.

See `references/inbox-promotion-transaction-evidence.md` for the reusable packet markers, normalization record, and independent acceptance checklist.

## Independent verifier normalization and completion visibility

A producer result can be correct while an independent verifier reports a false failure. Before treating verifier output as a data defect:

1. Normalize file modes to one representation on both sides. If one record stores full `st_mode` (`0o100600`) and another stores permission bits (`0o600`), parse both and compare the canonical file-type-plus-permission value; never compare the raw strings.
2. Apply the frozen control-marker policy to the verifier, not only the producer. For `.DS_Store`, `README.md`, and other excluded markers, make the lexical/basename decision before metadata or content access, omit them from the content expected-path map, and report their count separately. Do not turn pre-existing markers into unallowlisted deltas.
3. Derive the expected path set mechanically from the baseline minus exact source removals plus exact payloads, sidecars, staging records, and explicitly enumerated run-evidence files. Treat an amended maintenance log as a replacement, not a new path.
4. Verify sidecars and rollback copies against actual bytes, hashes, canonical modes, and path formulas; separately assert that formal targets, indexes, and maps remain unchanged.
5. If a verifier fails on mode representation, marker policy, field naming, or schema normalization, stop acceptance, repair only the verifier logic, and rerun read-only. Never rewrite content or mark a transaction accepted to silence a verifier defect.
6. After `producer_committed`, report that state promptly and start independent acceptance in the same turn. If no worker is active, say so plainly instead of implying that work is still running. Update the validation artifact to `accepted` only after the corrected verifier passes and the read-back confirms the status; preserve the producer terminal state in the immutable run evidence.

See `references/independent-verifier-normalization.md` for the mode/marker normalization pattern and the bounded post-commit checklist.

## Deterministic writer contract self-check

Before dispatching a generated writer, inspect the queue/plan/writer/verifier field contracts independently and run an explicit mapping check. Never rely on same-name lookups: for example, a frozen queue may expose `sha256` while the normalized operation exposes `source_sha256`. Require an explicit safe conflict policy when `conflicts` is non-empty; source disagreements are evidence to preserve, not an automatic execution blocker. Generate snapshot-manifest sidecar hashes only after the actual sidecars are installed, and make hash helpers handle verified external rollback paths without forcing them through root-relative conversion.

If a writer stops before root mutation, preserve the failed result under a unique external name, reconcile the root to the pre-write baseline, patch only the deterministic runner defect, compile/recheck plan and queue hashes, and retry with one replacement writer. After a commit, require the independent verifier plus a separate direct smoke check over payloads, sidecars, rollback backups, exact delta paths, source cleanup, and temporary artifacts. See `references/writer-preflight-corrections.md` for the reusable correction checklist.

## Verification and cleanup

- Completion means direct evidence: actual written/read-back counts, writer model identity, tests/lint/link/manifest results, scope check, and quota output.
- If generated report metadata disagrees with direct read-back evidence, report the discrepancy plainly and repair the reporting generator before relying on it again.
- When Roy directs Inbox cleanup, delete only source artifacts whose identity has been independently verified to have an expected formal payload and staging/provenance record. Do not delete unverified, unrelated, pending, or abandoned Inbox content.
- Remove explicitly designated one-time batch work directories only after required evidence has been preserved in the knowledge root.

## Reporting template

Use Roy’s requested model/role report format. Include actual model IDs, verification status, actual batch count (including a partial last batch), verdict, quota percentage, and either automatic continuation or the exact stop reason.

## Pitfalls

- Do not mistake preparation files for a running worker.
- Do not require a fresh user prompt between authorized batches.
- Do not stop after announcing an error; take the corrective action in the same turn.
- Do not use an old batch executor without regenerating all explicit metadata and verification expectations.
- Do not exclude only the known Inbox copies when the payload contract excludes `README.md`/`.DS_Store` generally; otherwise control artifacts elsewhere in the root can silently enter the baseline. Keep this marker policy separate from the opaque exact-path denylist.
- Do not call a baseline complete from in-memory scan results alone: persist external evidence, perform the single read-back/count/hash reconciliation, and report `blocked` with raw errors on any mismatch.
