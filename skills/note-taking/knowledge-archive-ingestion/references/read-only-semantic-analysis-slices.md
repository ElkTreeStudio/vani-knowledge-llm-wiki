# Read-only semantic-analysis slice pattern

Use this pattern when a canonical archive batch has already been materialized and the assigned task is **classification only**: inspect an exact input slice, write reconciled JSON outside the knowledge root, and make no knowledge changes.

## Execution stop-gates

Before semantic work, load this reference successfully in full. If skill content is unavailable or marked pruned, reload the umbrella skill and then this reference; do not continue from a contract-only approximation.

Treat these as hard gates, not optional cleanup:

1. Inspect the bundled validator's expected manifest/output fields before drafting. Do not replace it with a handwritten partial validator merely because count/hash checks are easy to reproduce.
2. Build the message-number/UUID map from canonical bytes, but do not treat a parser's full-byte read, digest, user-turn inventory, heading list, or assistant head/tail preview as semantic review. Reopen each cited message body—and its contiguous exchange when context matters—before accepting the observation.
3. Resolve every output field from the contract plus manifest mapping. In particular, never infer output `filename` from the source path when the manifest provides a distinct staged filename.
   - Treat required top-level metadata (`batch`, slice identity, and `count`) as a preflight schema gate. **Generate canonical `analysis_slice` in every new manifest.** Accept a legacy `slice` alias only when the live contract or bundled validator explicitly declares that alias; never assume compatibility merely because an earlier helper emitted it. If both keys are explicitly allowed and present, require identical integer values. If the required key is absent or `null`, the value conflicts with the assignment, or the validator rejects the alias, do **not** infer it from a directory name such as `analysis-2`, copy it from a schema example, or emit JSON `null`. Stop before semantic work and repair the external manifest under evidence.
   - For a manifest-only repair, preserve the original file byte-for-byte, record pre/post SHA-256 and an item-list digest/count proving the semantic allowlist is unchanged, change only the invalid metadata key, and rerun every slice that stopped before producing results. A slice that already completed may be retained only after its output is revalidated against the repaired manifest and the aggregate provenance records the metadata normalization; never overwrite the original worker result.
4. Keep source routing and staging disposition separate when the governing profile defines them as separate axes. `suggested_source_subdir` may preserve a reliable topic/domain route even when `staging_kind: unclassified`; the unclassified staging contract requires `suggested_target: null`. Only force the source slug itself to `unclassified` when the governing schema explicitly couples those fields.
5. Run `scripts/validate_read_only_slice.py` after the initial write and again after any repair. A custom supplemental check may add evidence, but never substitutes for the governed validator.

If any hard gate cannot be met, stop without presenting the slice as verified.

## Contract-first sequence

1. Read the batch contract and the assigned slice manifest before touching any conversation.
2. Treat the slice manifest as the complete allowlist. Do not inspect records outside it, abandon/pending folders, sibling slice outputs, or a frozen upstream archive.
3. Resolve schema examples against authoritative manifest metadata before analysis: manifest `batch`, `analysis_slice`, `count`, per-item IDs, filenames, paths, and hashes govern reconciliation. Literal batch/slice values shown inside an output-schema example are illustrative unless the contract explicitly declares them fixed; never copy a stale example value over the manifest value.
4. Read each listed canonical Markdown fully. Use the knowledge map, existing domain/project indexes, staging schema, and source governance only as routing hints.
5. Preserve every source identifier, filename, conversation ID, and supplied SHA-256 verbatim.
6. Emit exactly one result per listed input, in input order, to the assigned **external** path. Never write classification artifacts into the knowledge root during this phase.

## Semantic boundary

- Separate `observation`, explicitly labelled `inference`, and `uncertainty`.
- Assistant-generated text is not verified evidence. Attribute it as a reply or recommendation and add a fact-check or staleness caveat where appropriate.
- Choose `knowledge_candidate` only when the conversation contains a durable claim, procedure, constraint, or decision and a reliable existing domain/project target exists.
- Otherwise use `unclassified`; do not manufacture a new domain merely to avoid that outcome.
- Keep excerpts bounded. Prefer paraphrases linked to precise message-number and message-ID locators.
- If a user says material was pasted into the wrong session or should not be retained, do not restate that material in observations; record only the exclusion boundary.

## Manifest-field normalization before analysis

Do not assume the manifest uses the output-schema field names. Build an explicit mapping before writing results. In canonical-slice manifests, common mappings are:

- result `filename` ← manifest `staged_markdown_filename` (not necessarily `basename(source_path)`);
- result `input_sha256` ← manifest `sha256`;
- conversation bytes to inspect ← manifest `source_path`.

Treat manifest values as authoritative strings, but independently hash the allowed Markdown bytes and require equality with the supplied hash. Fail closed on a missing field, duplicate identifier, path outside the allowlist, or hash mismatch rather than filling values heuristically.

Before assembling a large result, run a small manifest-shape preflight against the first item and assert every input→output mapping that the validator expects. In particular, confirm the actual filename key (`staged_markdown_filename` in the canonical profile) instead of coding against the output field name `filename`. Also print or retain the complete ordered `ordinal → staged filename → source path` map from the manifest before drafting: ordinals may be sparse, and truncated multi-file tool output can make an inferred sequence look plausible while being wrong. Never key a semantic decision table from filenames, capture order, or presumed ordinal progression. Before any write, require exact set equality between decision-table keys and manifest ordinals and report both missing and unexpected keys. Do this before embedding a large semantic decision table in a one-shot script: a late `KeyError` otherwise discards the whole draft and encourages an error-prone manual reconstruction. The safe sequence is: inspect keys → freeze the exact ordered ordinal/file map → assert the mapping on one item → assert decision-key coverage → build all items → run the bundled validator.

### Path resolution and large-slice review discipline

- Parse and print the manifest's exact `source_path` allowlist before opening conversation files. Never reconstruct paths from titles, dates, conversation IDs, or guessed slugs; `untitled` records and date/title drift make that unsafe.
- For large slices, run one deterministic in-memory inventory over every allowlisted file before semantic drafting. The inventory should read every byte, verify SHA-256, and parse `Message N → role → Message ID → text boundary` mappings. This proves byte coverage and gives a source-derived locator map, but it does **not** replace semantic review of every full conversation.
- When direct tool output would truncate, review in ordinal-bounded groups and use compact per-message navigation views (for example, all user turns plus bounded assistant head/tail cues) only to identify which complete source sections need focused rereading. Before accepting any observation, reopen the cited message's full body from the canonical Markdown; if the claim depends on context, reopen the contiguous exchange as well. A digest, preview, or heading inventory is lossy navigation—not semantic evidence—and must never become the sole basis for classification.
- If delegated read-only workers are unavailable, continue locally with the same ordinal-bounded workflow rather than lowering the review standard. Worker output is always a draft until the primary process reconciles it against canonical bytes and passes the locator/hash gates.
- Keep navigation inventories in memory or tool output. Do not create intermediate extracts under the knowledge root or beside the required result unless the contract explicitly authorizes them; the assigned external JSON should remain the only written artifact.
- Draft observations against message numbers first, then inject UUIDs programmatically from the parsed map. This avoids hand-copy errors and permits the final validator to reconcile number/UUID pairs deterministically.

For large slices, a deterministic parser may read every allowed Markdown byte and inventory message number, role, UUID, and text boundaries before semantic review. This reduces locator-copy errors, but does not replace reviewing the full conversation. Never write intermediate extracts under the knowledge root; prefer in-memory processing and write only the assigned external artifact.

## Large-batch fan-out and convergence

When authority raises the external transaction size (for example, from 10 to 100), do not make multiple semantic workers concurrent knowledge writers. Keep the user-visible batch as one transaction while splitting only the read-only analysis:

1. Freeze one contiguous batch descriptor with an exact whole-file hash.
2. Balance disjoint analysis slices by total input bytes, not only item count, so one oversized conversation does not dominate a worker.
3. Before launching parallel semantic workers, run exactly one minimal read-only inference probe with the intended CLI, model, sandbox, and account. Require a successful semantic response—not merely CLI startup or authentication—before fan-out. If the probe reports quota, auth, or provider failure, do not multiply the same failure across workers; switch to the local ordinal-bounded review path while preserving the full-review standard.
4. Give each worker an exact slice manifest and a unique external result path; knowledge remains read-only.
5. Deterministically converge every slice result into one aggregate artifact. Reconcile the union against the original batch descriptor for exact count, ordinal coverage, uniqueness, IDs, filenames, hashes, kind/target rules, locators, allowed source slugs, permissions, and live target existence.
6. If convergence finds a semantic-contract contradiction, do not silently normalize it and do not edit the original worker artifact. Re-review only the affected source under the same contract, write a separate restricted correction artifact, validate it, and record that correction in the aggregate provenance.
7. Hash and freeze the aggregate. A single writer then consumes that exact aggregate hash for the full batch transaction.

Choose slice count by total bytes as well as concurrency. When the number of safe byte-balanced slices exceeds available parallel workers, run multiple read-only waves and converge only after every slice passes. This changes neither the user-visible batch boundary nor the one-writer rule.

A changed batch size does not authorize interrupting an already-writing atomic batch. Let the active frozen transaction finish at its original size, then apply the new size to the next ordinal without renumbering or reprocessing completed records.

## Deterministic reconciliation gate

After writing, reparse the JSON and verify all of the following:

- batch, slice, producer, schema keys, and allowed enum values;
- item count equals the manifest count;
- ordinals, source keys, conversation IDs, filenames, and hashes reconcile one-to-one and in order;
- uniqueness of ordinals, source keys, conversation IDs, and filenames;
- each suggested source slug is an existing safe domain/project slug or `unclassified`;
- validate routing according to the governing profile's actual axes: every `knowledge_candidate` has a non-null existing target; every `unclassified` result has a null target. A safe domain/project `suggested_source_subdir` may remain on an unclassified staging result when source routing and staging promotion are intentionally separate; require `suggested_source_subdir: unclassified` only in schemas that explicitly couple them;
- every message UUID cited in observations or locators exists in that item’s Markdown;
- every `Message N` locator’s number and UUID refer to the same source message;
- actual input hashes match the supplied manifest hashes when the contract permits hashing those Markdown inputs;
- output reparses, file mode is `0600`, and parent mode is `0700`.

The UUID-existence check alone is insufficient: a hand-copied UUID can be valid-looking but wrong, and a correct UUID can be paired with the wrong message number. Validate the pair mechanically. The governed validator must fail closed on every unrecognized or empty `source_locators` entry rather than silently skipping syntax it does not parse. Accept the two established explicit forms—`Message N (UUID)` and `Message N / Message ID UUID`—and resolve either form to the same source-derived pair map.

**Rejected near-match pitfall:** do not embellish a locator as `Message N (user; ID UUID)` or `Message N (assistant; ID UUID)`. That form is human-readable but outside the governed grammar and must fail validation. Keep role or section context in the observation when needed; emit locators in one of the two exact accepted forms. Never claim a slice is verified after only a custom checker passes—run the bundled validator and require its `status: PASS` output.

### Locator construction discipline

Do not copy UUIDs from condensed semantic digests, truncated tool output, or working notes. Before writing results, deterministically parse every allowlisted Markdown into a per-item map of `Message N → role → Message ID`; construct each locator by looking up the message number in that map. Keep semantic review and locator resolution separate: draft the bounded observation against message numbers, then inject UUIDs from the parsed map. This prevents plausible but cross-file or stale UUIDs from surviving into the artifact.

Run `scripts/validate_read_only_slice.py INPUTS.json RESULTS.json` as the final deterministic gate when the manifest uses `source_path`, `staged_markdown_filename`, and `sha256`. Run it once immediately after the initial write, repair every reported pair from the source-derived locator map rather than by visual guesswork, then run it again after all edits. It reparses both JSON files, hashes only allowlisted Markdown inputs, reconciles identifiers in order, validates cited Message-number/UUID pairs, checks uniqueness and kind/target consistency, and enforces output `0600` plus parent `0700`.

After the governed validator passes, run a supplemental read-only target-resolution check: resolve every non-null `suggested_target` beneath the canonical knowledge root, reject path escape, and require the resolved path to be an existing regular file. Also enforce the candidate/target biconditional (`knowledge_candidate` exactly when the target is non-null). This proves the contract's “reliable existing target” requirement without replacing the governed validator, even when a particular validator version checks only target nullability.

## Read-only evidence and reporting

- Use only read operations under the knowledge root. Perform atomic writes and permission changes only at the external result path.
- If the knowledge root is not a Git repository, do not claim Git-based cleanliness. Report the narrower evidence: no knowledge-root write operation was performed and the only written artifact is outside the root.
- Final user-facing output should contain only aggregate counts and the absolute evidence path when the contract forbids private titles, bodies, or IDs.
