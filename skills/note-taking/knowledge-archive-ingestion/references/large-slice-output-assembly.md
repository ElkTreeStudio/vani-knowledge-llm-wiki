# Large-slice output assembly and verification recipe

Use this note after semantic decisions are complete for a manifest-driven read-only slice, especially when one or two conversations are much larger than the rest.

## Assembly pattern

1. Parse the manifest once and freeze the ordered `ordinal → source_path → staged_markdown_filename → identifiers → SHA-256` map.
2. Keep the semantic decision table keyed only by ordinal. Before generating JSON, require exact set equality between manifest ordinals and decision-table ordinals.
3. Copy identity fields only from the manifest; never hand-enter IDs, filenames, or hashes in the semantic table.
4. Construct locators from a source-derived `Message N → Message ID` map. Keep locator strings in the validator's exact accepted grammar. Before generating the full result, run one representative locator through the live validator regex or a minimal fixture. The stable core forms are `Message N (UUID)` and `Message N / Message ID UUID`; optional context is accepted only after a slash (for example, `Message N (UUID) / 2025-08-01T00:00:00Z, Text Part 1`). Do not append timestamps with a comma directly after `)`—that visually plausible form fails the governed validator.
5. Generate all result items in manifest order. Derive route/kind/target fields from one explicit disposition value so contradictory combinations cannot be emitted.
6. Write only the assigned external result artifact, then set the parent to `0700` and result to `0600`.

## Large-source review discipline

- Byte verification and message inventories are prerequisites, not semantic review.
- Use compact user-turn plus bounded assistant previews only as navigation when direct output would truncate.
- Before accepting a classification, reopen the full conversation. Before accepting an observation, reopen every cited message body and any contiguous exchange needed for context.
- Do not let one oversized file cause the rest of the slice to be skimmed; review in ordinal-bounded groups and track completion per item.

## Two-layer verification

Run the governed validator first. Resolve it from the loaded skill's linked `scripts/` files when it is not present in the batch workspace; do not search only beside the batch and then silently replace it with an ad hoc checker.

```bash
python3 /absolute/path/to/knowledge-archive-ingestion/scripts/validate_read_only_slice.py INPUTS.json RESULTS.json
```

Require a machine-readable PASS and zero exit status. If the governed validator is genuinely unavailable, label the run as supplemental-only rather than claiming governed validation. Then run a supplemental read-only check for properties that validator versions may not all enforce:

- every `suggested_source_subdir` is safe kebab-case **and already exists** beneath the governed ChatGPT conversation source root; a domain slug is not valid merely because a same-named domain exists;
- every non-null target resolves beneath the knowledge root and is an existing regular file;
- candidate status is equivalent to target non-nullness when the governing contract couples them;
- every locator's message number and UUID pair resolves against the same source record;
- actual source hashes still equal manifest hashes;
- output count, manifest order, identity fields, and uniqueness still match the manifest;
- only the assigned external result artifact was written or modified;
- output and parent modes are `0600` and `0700`;
- record the final result SHA-256 as evidence.

A supplemental checker never replaces the governed validator. Final reporting remains aggregate-only when the contract forbids private titles, bodies, IDs, or locators.