---
name: knowledge-archive-ingestion
description: Safely ingest large personal conversation, chat, email, or assistant export archives into a schema-driven knowledge base using immutable staging, privacy gates, durable-value selection, atomic wiki tickets, provenance, backups, and fresh verification.
version: 1.2.15
---

# Knowledge Archive Ingestion

Use this skill when the user wants to turn a large exported archive—ChatGPT conversations, Slack/Discord history, email, notes, support chats, or similar personal records—into a durable, searchable knowledge base.

Treat the archive as sensitive evidence. **Source preservation and semantic promotion are separate layers:** first create a complete, readable, restricted raw corpus; only afterward run discovery, curation, or wiki promotion.

### Source-first raw-corpus rule

For an unclassified user archive, before any domain routing or durable-value selection:

1. Preserve the original archive byte-for-byte with size/hash/CRC evidence.
2. Deterministically flatten **every** conversation/item into one independent readable Markdown source record in a restricted intake corpus. Do not summarize, redact, classify, score, exclude, or omit an item because of topic or perceived value. Preserve exact message text and ordering; represent branches, roles, timestamps, attachment references, and unsupported content explicitly. Keep the original JSON/archive as the source of truth when Markdown cannot be byte-lossless.
3. Give every raw Markdown a stable provenance key (conversation/item ID may be metadata and collision-safe identity, but never a selection axis), source shard/member, timestamps, archive hash, rendering version, and body hash.
4. Prove one-to-one coverage mechanically: archive item count equals raw Markdown count; every source key appears exactly once; no unexpected raw; rerendering is idempotent. Maintain a disposition ledger for all raws.
5. Keep the complete raw corpus even when a later semantic pass marks an item `not-promoted`, private, duplicate, stale, or low-value. `Dropped` may mean excluded from curated/canonical knowledge; it must not mean deleting or failing to materialize the source raw unless the user explicitly authorizes deletion.
6. Store unrestricted full text under a restricted, non-embedded, non-public intake path with `0700` directories and `0600` files. Redacted synopsis/transcript packets are derivatives for reviewers, not substitutes for the raw corpus.
7. Only after the raw corpus passes coverage verification may open-world discovery propose existing-domain, cross-domain, new-domain, private/deferred, or excluded dispositions. Existing domain names must not constrain initial discovery.

Any prior workflow text about staging manifests, routing queues, selected transcripts, or raw captures is subordinate to this source-first rule. Those artifacts may optimize later review, but may not replace or precede complete raw materialization.

### Office-document project snapshots

When a user supplies a directory of DOCX/XLSX/XLSM/PPTX/PDF or similar office files as a named project cutoff, treat it as an immutable **source set**, not as a loose collection of articles. Capture the user-declared `snapshot_label` separately from the real UTC `ingested_at`, and make a machine-generated per-file SHA-256 manifest the comparison authority. Never report model-transcribed hash text as a drift result.

Before admitting office binaries, confirm that the target knowledge base has an approved document-source taxonomy, canonical path, extension-preserving sidecar contract, deterministic non-executing converter/projection profile, and dry-run/apply/import gate. The generic raw-source schema alone is insufficient to invent these. Do not put a Word workbook in an article path merely because no document taxonomy exists. If the contract is missing, stop before formal `sources/`, `staging/`, or `projects/` writes and obtain explicit authority to extend governance. Preserve macro-enabled files as opaque inputs; extraction must never execute macros.

Only publish concise project provenance/navigation after the binary source, sidecar, projection, import-run, privacy, and manifest gates pass. Mark draft material as unverified and compare all later submissions as new immutable manifests; never overwrite an earlier snapshot. Use `references/office-document-snapshot-contract.md` for the complete preflight, contract, and successor-diff rules.

#### User-run conversion handoff

If the user decides to convert the office files to Markdown themselves, treat that as an immediate stop to any converter, schema-extension, or ingestion producer. Confirm no worker remains active; do not create a project, source, staging, or migration artifact from unconverted inputs. Leave original files untouched except for individually named files the user explicitly authorized for deletion (prefer a recoverable removal). Tell the user only the minimal handoff: place the converted Markdown in the agreed Intake location, then the returned set is a **new source set** that must receive a fresh file count, per-file SHA-256 manifest, real `ingested_at`, and snapshot comparison before admission. Never reuse an unfinished converter's outputs, plan freshness, or hashes as evidence for user-converted Markdown.

## Core invariants

1. **Preserve the source.** Never rewrite, move, delete, or extract over the original archive. Record byte size and SHA-256; create an external recovery copy when the user authorizes it.
2. **Separate staging from formal knowledge.** Prefer a restricted work area outside the canonical knowledge root by default. If the user-approved architecture explicitly provides top-level `sources/` and `staging/` inside that root, use those governed layers instead: keep them outside `domains/`, `projects/`, `entities/`, and generated indexes; enforce privacy permissions and scan exclusions mechanically. Parsing workspaces, temporary reviews, caches, and debug logs still stay outside the active corpus or under an explicitly excluded runtime path.
3. **Fail closed on privacy.** Unknown or suspicious content is quarantined, not partially admitted. Public outputs contain only aggregates and schemas—never titles, message bodies, secrets, IDs, or private paths.
4. **Assistant output is not evidence.** Imported model responses remain `not fact-checked`, low confidence, and never count as independent authoritative sources merely because several conversations repeat them.
5. **Schema before content.** Read the target wiki's `SCHEMA.md`, `index.md`, and `log.md`. If a target domain is empty, bootstrap its schema/index/log as a separate prerequisite ticket.
6. **Raw and canonical are different.** Raw captures preserve provenance and declared omissions. Canonical pages synthesize reusable ideas, expose uncertainty, and link back to raw captures.
7. **One writer per shared index/log.** Parallelize independent queues and distinct wikis only. Serialize tickets that touch the same index, log, or existing canonical page.
8. **Back up immediately before editing existing files.** Preserve relative paths and write a manifest with source/backup hashes. Re-baseline before every later ticket that edits the same file.
9. **Terminal state or rollback.** If a producer times out, hits max turns, loses quota, or returns an error envelope, do not infer success from files on disk. Audit actual state; quarantine unregistered partials and restore index/log from the verified baseline.

## Workflow

### 1. Source reconnaissance

- Inspect archive members without unsafe bulk extraction.
- Reject Zip Slip paths, symlinks, decompression-bomb ratios, CRC failures, malformed shards, and unsupported structures.
- Parse incrementally by shard with standard libraries where possible.
- Record archive provenance and source hash.
- Do not read unrelated backups or network services during local ingestion.

#### Frozen artifacts deferred to a later migration

When the user freezes a specific archive or binary but authorizes sibling text records, treat the frozen artifact as outside the current inventory. Put its exact root-relative path in the shared scanner exclusion set and check that set before file-type, stat-derived metadata, open, hash, parse, move, or index logic. Never exclude by basename or extension. Test with synthetic ordinary files: exact path excluded; same basename elsewhere, near-match names, and other archives still included. If governance promises exclusion but the scanner still hashes the artifact, stop the ingestion, fix and test the scanner first, then resume the same ticket. See `references/frozen-artifact-scanner-exclusion.md`.

### 2. Restricted staging manifest

Produce a per-conversation manifest that contains identifiers, timestamps, counts, attachment flags, routing class, and sensitivity findings. Keep message bodies out of public reports.

Useful outputs:

- restricted conversation manifest
- attachment crosswalk
- public provenance summary
- routing/count summary
- sensitivity summary
- candidate queue summary

Set restricted directories to `0700` and files to `0600` unless the canonical wiki has an explicit different policy.

### 3. Privacy and residual gates

Use both named-secret redaction and residual detection. Cover at minimum:

- emails, phone numbers, identity numbers
- bearer/JWT/private-key markers
- provider-specific access keys, including separatorless formats
- private paths, endpoints, account/channel IDs
- mixed-alphanumeric opaque credentials below traditional 32-character thresholds
- copied third-party page bodies and attachment-derived content

Run synthetic boundary tests for every credential regex. A regex fix requires RED → GREEN evidence and a full-corpus rebuild.

### 4. Two-stage semantic selection

**Stage A — synopsis review**

Review only redacted title/user-intent synopsis. Select durable candidates; reject one-off debugging, translation, generic generation, administrative material, obsolete version trivia, and content easily recovered from first-party documentation.

**Stage B — restricted transcript review**

Generate transcripts only for approved IDs. Keep user/assistant plain text; omit thoughts, reasoning recaps, tools, metadata, branches not selected by the deterministic flattening rule, and attachment bytes. Review for:

- durable cross-project value
- natural-language privacy missed by regex
- factual or technical unreliability
- overlap with existing wiki pages
- create/update/link-only/drop disposition
- concept clusters rather than one page per conversation

### 5. Integration context packet

Before writing the wiki, normalize every approved conversation to:

- target wiki
- raw capture path
- canonical destination
- create/update/link-only/drop
- existing-file write allowlist
- new-file allowlist
- required backup set
- expected index counts
- append-only log rules
- atomic ticket and dependency

Cross-wiki deduplication happens here. Do not create near-duplicate canonical pages merely because reviewers used different labels.

#### Integration-plan reconciliation gate

Treat planner/Scout packets as proposals, never as source authority. Before launching any writer:

- join every planned conversation ID against the restricted selected-transcript manifest and the authoritative final-review approved collection
- verify the referenced review filename actually exists
- classify every destination as **new**, **existing update**, **link-only**, or **drop** by inspecting the live wiki; do not infer this from the proposed slug
- derive expected counts from the live filesystem/index plus the exact delta, not from a narrative plan
- detect cross-review/domain conflicts and resolve them schema-first; when the source is single-project, duplicate, or outside the target schema, record a drop rather than manufacturing quota-filling content
- produce a reconciliation table of approved IDs → already ingested / pending / intentionally excluded; only true pending IDs become tickets

If even one planned ID is absent, stop that ticket before model generation. Never substitute a thematically similar conversation or fabricate a raw capture to satisfy a planned count.

### 6. Raw capture contract

Always declare:

- `structured_extract`
- export-derived, not verbatim
- not fact-checked
- redacted
- conversation ID and source timestamps
- source archive SHA-256
- deterministic branch flattening
- retained roles/content types
- omitted thoughts/tools/metadata/attachments
- whether attachments were indicated but unread

Do not claim a structured extract is a complete transcript. When natural sensitive context exists, summarize or omit it and record the omission category without reproducing the value.

#### Metadata sidecar path contracts

When source payloads use metadata sidecars, define the sidecar path as an exact root-relative function of the payload path rather than a basename or stem convention. Preserve the payload's complete filename and extensions, compare the linter's current sidecar path to the computed expected path, and report both values on failure. Add fixture-based RED/GREEN tests for extension-preserving success plus wrong-stem, wrong-directory, and basename-only rejection; retain payload safety, existence, hash, and schema gates. See `references/raw-source-sidecar-contract.md` for the reusable implementation and verification pattern.

### 7. Body-only hash convention

Use the target schema's exact byte convention. Prefer one unambiguous cross-wiki rule:

- find the first two lines whose content is exactly `---`
- body starts after the closing delimiter line ending
- exclude the delimiter and its LF/CRLF
- include any additional blank line after it
- hash raw bytes through EOF, including final newline
- do not normalize Unicode, whitespace, or line endings

Before introducing a schema, test existing raw pages. If current schemas disagree, stop and obtain authorization for a cross-wiki governance correction; back up every affected schema, log, and metadata-only raw change.

**Validator pitfall:** some existing wikis under-specify the byte boundary in `SCHEMA.md` while their linter applies a legacy convention such as `text.split('---', 2)[2].lstrip('\n')`. Before computing or independently checking hashes, inspect the target wiki's actual validator and reproduce its established convention exactly. Do not report a mismatch produced only by using a different boundary rule; do not silently change the schema or validator during an ingestion ticket.

### 8. Atomic ingestion tickets

Keep each ticket small enough to verify independently. A typical ticket contains:

- a bounded set of raw captures
- one or two canonical clusters
- one index update
- one append-only log update

A ticket is complete only when:

- every raw hash matches
- required frontmatter and taxonomy pass
- links resolve
- sensitive patterns and manual privacy review pass
- index counts and registrations match the filesystem
- log retains the backup as an exact byte prefix
- scope equals the allowlist
- a fresh-context semantic reviewer returns PASS

#### Producer-envelope acceptance boundary

A producer's `VERDICT: PASS`, successful exit code, or `terminal_reason: completed` is only a **producer terminal state**, not ticket acceptance. Immediately run an independent deterministic acceptance gate against the files actually written. The gate must discover actual paths rather than assuming an old draft date, and must compare index/filesystem counts bidirectionally. Only then mark the producer stage PASS; semantic verification remains separate.

Before each run, baseline preflight must verify both sides of the write contract:

- every existing file in scope is byte-identical to the ticket backup
- every proposed new target is absent
- a destination thought to be new is not already an existing canonical page

If a legitimate ticket lands after an older backup, never restore the stale backup. Run the wiki's authoritative linter, create a fresh exact-file backup, recalculate counts, and re-baseline the pending ticket. On failed producers, quarantine new files and partial index/log, restore only from the ticket's current verified baseline, and prove rollback by byte comparison.

### 9. Model and quota handling

For external CLI agents:

- verify auth status and run a real one-turn inference probe before claiming work started
- inspect live CLI `--help` before using optional flags
- parse the JSON envelope, not only process exit code
- distinguish `max_turns`, timeout/aborted streaming, permission denial, auth failure, and quota 429
- preserve session IDs when continuation may be needed
- reserve stronger models for semantic verification; use a workhorse model for bounded production when quota is constrained
- never silently fall back to a provider the user asked to conserve
- keep model identity separate from reasoning effort. For Roy-authorized Hermes workers, prefer the real `gpt-5.6-luna` model with `reasoning_effort=max` when Luna Max is requested; set `delegation.reasoning_effort=max` for delegated workers when that scope is authorized. Verify the effective value with `hermes config get` and the installed Hermes venv's shared `resolve_reasoning_config()`; do not infer it from a model name, a CLI success message, or display-only reasoning visibility. If the resolver does not return enabled `max`, stop or use only an explicitly authorized fallback, never a silent role/model substitution.

For user-controlled batched promotion, first isolate `abandon` and `pending` dispositions into distinct restricted locations and freeze the promote-only queue. Record the exact batch size and active quota policy, including a comparator only when authority explicitly supplies one. Query live quota before the first batch and after every accepted batch for observability and routing; do not impose a fixed percentage threshold. If authority explicitly removes a percentage threshold as a pause condition, continue frozen batches after independent acceptance unless quota is unavailable, the provider returns a hard exhaustion/429, an integrity or safety blocker exists, or authority stops. If quota remains an active gate, apply its comparator literally and call out boundary risk. If quota lookup is unavailable or ambiguous while quota remains an active gate, pause rather than guessing.

Treat quota policy and data-integrity acceptance as separate controls. An explicit instruction to ignore a percentage threshold changes only the pause condition; preserve all hash, rollback, one-writer, and verification gates, record the authority change and actual producer route, and use only already-authorized workers. A real provider hard-quota failure remains a blocker unless authority explicitly authorizes an already-approved alternate route. Never interpret "ignore quota" as permission to weaken the transaction or silently change providers outside existing authority. See `references/quota-gated-batch-promotion.md`.

If a quota reset time is reported, either pause explicitly or run a controlled delayed continuation that rechecks auth and baseline hashes immediately before writing. A retry window is quota-eligible only from the parsed provider envelope (for example `api_error_status == 429` plus the provider reset message), never from substring matching over the whole envelope—fields such as `session_id` contain the word `session` and can create false positives. `max_turns` is not quota exhaustion: preserve the session ID, quarantine/rollback partial promotion, then resume the same context against the drafts with an adequate continuation budget.

For user-visible operations, a timer process being alive is not proof that ingestion is progressing. Distinguish and report `waiting`, active model child, producer terminal state, rollback, and retry scheduling. Report terminal failures immediately before entering any delayed window; do not remain silent until the retry time.

## Reusable Inbox runner

When repeated Inbox promotion should run through one stable command, use `references/reusable-inbox-runner-contract.md`. Keep the runner as an evidence-producing orchestrator with default dry-run, explicit apply, exact protected-set checks before traversal, deterministic queue freezing, role-identity verification, optional quota pause policy, one-writer transactions, rollback, and independent acceptance. An empty eligible queue is a successful no-op; a worker exit or model PASS is never acceptance. For Python implementations, enforce the opaque set with lexical absolute paths before every `lstat`, `open`, hash, parse, or recursion operation—do not resolve or probe a protected path first. Treat an absent quota command as `lookup_unavailable` and pause `--apply` rather than inventing a provider route; dry-run must not query quota or start workers. After any source patch, rerun the final compile/read-back/bytes/SHA-256 checks; earlier verification output is stale once the artifact changes.

### Reusable-runner hardening learned from implementation

When converting a one-off Inbox run into a stable executable, keep the policy and the artifact separate: the default scope file must live at a stable path outside timestamped evidence directories, and every run must record its scope hash. Never let an active worker and the commander edit the same draft concurrently; a worker may overwrite a local patch after the last read. Wait for its terminal state, re-read the final artifact, then patch, compile, and verify that final version before installation. Treat a provider quota adapter as a schema parser, not a truthy/falsey probe: for nested responses such as `results[].available` and `windows[]`, extract provider/window evidence, pause on missing or false availability, classify only explicit hard exhaustion/429 as hard quota failure, and never turn percentages into an implicit threshold. Before dispatch, mechanically verify the effective Hermes reasoning configuration (`agent.reasoning_effort` and `delegation.reasoning_effort`) is the requested value and persist it beside provider/model identity. After every patch or copy, recompute source/installed bytes and SHA-256, compile the installed file, run a real empty-queue or dry-run smoke, and read the resulting receipt. If the live queue is empty, report only a verified no-op; do not claim the non-empty planner/writer transaction was exercised.

## Verification split

Use deterministic tools for hashes, counts, permissions, schemas, paths, and link resolution. Use fresh semantic reviewers for privacy nuance, correctness risk, durable value, duplication, and quality. Never ask a semantic model to replace deterministic evidence, and never let deterministic regex alone certify natural-language privacy.

## Supporting references

- See `references/model-tiered-wiki-promotion.md` for Sol-main/Luna-planner/Terra-inbox-editor/Sol-knowledge-editor role contracts, runtime model-resolution guarantees, machine-verifiable promotion plans, phase-specific stops, evidence/opinion separation, bounded Sol governance, and non-Git checkpoint portability.
- See `references/large-batch-canonical-ingest-orchestration.md` for byte-balanced semantic slicing, oversized singleton review, manifest-repair evidence, post-artifact provider failures, concurrent unrelated root changes, atomic one-writer batches, and pause/resume boundaries.
- Use `scripts/validate_read_only_slice.py` for deterministic final validation of manifest-driven read-only slice results, including hash, order, locator-pair, uniqueness, routing-consistency, and permission gates.
- See `references/read-only-semantic-analysis-slices.md` for exact-slice classification with no knowledge writes, observation/inference/uncertainty boundaries, message-ID locator validation, one-to-one manifest reconciliation, and external JSON permission gates.
- See `references/large-slice-output-assembly.md` for ordinal-keyed result generation, oversized-source review discipline, manifest-derived identity fields, and governed-plus-supplemental verification.
- See `references/chatgpt-export-ingestion-pattern.md` for a concrete sharded-export pattern, credential-regex findings, partial-output rollback procedure, and provider-envelope lessons.
- See `references/transactional-ticket-orchestration.md` for exact preflight, rollback, resume, stale-baseline, deterministic acceptance, and progress-reporting patterns for multi-ticket ingestion.
- See `references/bounded-inbox-promotion.md` for approved small-batch Inbox promotion: byte-preserving payload moves, exact full-filename sidecars, URL deduplication, holds, import-run evidence, and the final-manifest immutability boundary.
- See `references/bounded-staging-classification-writes.md` for exact-allowlist staging reviews: stale-plan and target-absence stops, no-touch denylist enforcement, atomic staged installation, source-sidecar/hash read-back, and zero-formal-write evidence.
- See `references/manifest-driven-inbox-isolation.md` for no-ingestion isolation of reviewed archive Markdown: exact baseline gates, verified external rollback copies, atomic moves, restricted permissions, and deterministic source-location acceptance.
- See `references/external-archive-canonical-markdown-migration.md` for the governed exception where authority keeps the upstream archive outside the knowledge root and makes each deterministic per-item Markdown an immutable canonical source, including RED/GREEN provenance tests, JIT backups, manifest evidence, and tracked-bytecode drift prevention.
- See `references/reusable-inbox-runner-contract.md` for the repeatable command contract: dry-run/apply separation, exact protected-set enforcement, frozen queues, role identity, optional quota pause, rollback, and independent acceptance.
- See `references/quota-gated-batch-promotion.md` for promote/abandon/pending isolation, deterministic queue freezing, one-batch transactions, configured quota-policy gates, and pause/rollback evidence.
- See `references/exact-queue-canonical-batch-ingest.md` for exact ordinal-slice preflight, full later-queue/protected-set snapshots, byte-preserving canonical moves, exhaustive sidecar/staging read-back, and the finalized-root manifest immutability boundary.
