# Quota-gated batched archive promotion

Use this pattern when a reviewed raw corpus is split into promote / abandon / pending classes and promotion follows a user-defined external-agent quota policy. A fixed percentage stop condition is optional and may be removed by explicit authority; quota observability, integrity gates, and hard provider exhaustion handling remain mandatory.

## Sequence

1. **Freeze disposition before promotion.** Persist a manifest with one stable source key, one current path, one class, and one hash per raw item. Isolate `abandon` and `pending` into distinct restricted directories first; only `promote` items enter the queue.
2. **Freeze the queue.** Choose and record a deterministic ordering, batch size, total batches, queue hash, and exact input list for every batch. Do not refill a batch from pending/abandon when an input is missing.
3. **Preflight quota as well as postflight quota.** Query the provider's live quota immediately before the first batch and after every accepted batch. A stale earlier result is not authority. Apply the user's comparison literally (`<`, `<=`, etc.); report boundary cases explicitly.
4. **One batch is one transaction.** Before model launch, record exact inputs, hashes, destination absence, protected sets, rollback copies, and the batch work contract. Do not start batch N+1 until batch N has terminal success **and** independent deterministic acceptance.
5. **Separate deterministic and semantic work.** Hashing, byte-preserving moves, sidecars, manifests, permissions, counts, and rollback should be deterministic. Spend model quota only on semantic classification/candidate extraction that cannot be done mechanically.
6. **Postflight gate.** After acceptance, query live quota. If an active configured stop condition is crossed, persist the completed batch receipt and stop before creating or launching the next batch. If authority has removed the percentage pause condition, persist the receipt and continue at the next frozen boundary unless quota is unavailable, the provider reports hard exhaustion/429, or a safety/integrity gate fails. If quota lookup fails or is ambiguous, fail closed and pause.
7. **Partial or quota-exhausted runs.** A producer exit, partial files, or a quota error is not batch completion. Audit actual state, rollback or quarantine according to the batch manifest, verify protected sets, and preserve the model session/envelope for later continuation.

## Evidence per batch

Keep under a restricted external work root:

- frozen `inputs.json` and its SHA-256;
- pre/post manifests and protected-set hashes;
- verified rollback copies;
- migration mapping and import-run record;
- tests/lint/link/read-back outputs;
- independent acceptance result;
- live post-batch quota receipt and explicit `continue|pause` decision.

## Reporting

Report aggregate counts and state only; do not publish conversation titles, IDs, or bodies. Distinguish `prepared`, `model running`, `producer completed`, `accepted`, `rolled back`, and `paused for quota`. A background process starting is not evidence that a batch was accepted.
