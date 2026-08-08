# Bounded staging-classification writes

Use this pattern when a valid, short-lived planner packet authorizes a small, exact allowlist of staging records but explicitly forbids canonical or formal-layer changes.

## Preconditions

1. Read the authorization packet first. Extract: expiry, exact output paths, required record kinds, source ordinal → hash mapping, per-record content caveats, formal-layer restrictions, and the exact denylist.
2. Check the plan expiry against the live UTC clock. If stale, stop before any write.
3. Preflight **all** target paths as absent before creating any file. A pre-existing target is a stop condition, not an overwrite opportunity.
4. Treat a denylist as a no-touch set: exclude its exact paths before filename discovery, metadata probes, hashing, parsing, indexing, or root-wide validation. Do not run ordinary root walkers if they would cross the denylist.

## Write discipline

- Write only the allowlisted paths. Do not create manifests, reports, indexes, formal pages, or temporary artifacts inside the knowledge root unless explicitly authorized.
- Respect the staging directory ↔ `record_kind` mapping and require schema/version, pending status, unique ID, dates, paired `input_refs`/`input_hashes`, actual producer, and `suggested_target` (nullable where the schema permits it).
- Keep body sections explicitly separated as **Observation**, **Inference**, **Uncertainty**, and **Recommendation**. Preserve source claims as claims; do not turn product, version, cost, platform, performance, marketing, or benefit assertions into verified facts.
- For duplicate groups, retain every canonical source as a distinct reference/hash. For candidate updates, name the existing formal target but make clear that promotion authority has not been exercised.
- Stage every file in its destination directory, validate the complete set, `fsync`, and then install the set. If preflight or validation fails, remove only staged temporary files and leave target paths absent.

## Targeted verification

Use a verifier constrained to the exact new records and their exact source payloads/sidecars. For each record verify:

1. frontmatter begins at byte zero and has one closing delimiter;
2. schema/version, status, directory, and `record_kind` agree;
3. `input_refs` and `input_hashes` have equal length and match the authorized ordinal mapping in order;
4. each referenced sidecar has the expected source ID and recorded payload SHA-256;
5. the SHA-256 of each exact payload byte stream equals that recorded/authorized SHA-256.

Report each changed root-relative path, its referenced source hashes, the real verifier output, and an explicit statement of zero formal-layer writes. If a full-repository checker would touch a denylisted path, do not substitute invented global validation; report that targeted validation was used because it preserves the no-touch boundary.
