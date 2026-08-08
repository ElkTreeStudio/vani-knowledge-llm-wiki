# Reusable Inbox Runner Contract

Use this reference when turning a governed Inbox promotion into a repeatable command or scheduled runner. The runner is an orchestrator and evidence producer; it is not permission to bypass the ingestion stages.

## 1. Stable entrypoint and run boundary

- Keep one stable entrypoint with a documented `--dry-run` mode and an explicit `--apply` mode. Dry-run is the default for new installations and must never mutate the knowledge root.
- Create a fresh, timestamped external run directory for every invocation. Store scope, resolved configuration, frozen inputs, model usage, quota receipts, rollback manifests, and deterministic verification there—not under the active knowledge corpus.
- Return explicit terminal states such as `no-op`, `prepared`, `model-running`, `producer-completed`, `accepted`, `rolled-back`, `paused`, and `failed`. A process exit code or a model's `PASS` string is not acceptance.
- An empty eligible queue is a successful deterministic no-op with a receipt; it must not launch a worker.

## 2. Exact protected-set enforcement

- Load the authorized exact protected paths before walking the queue. Preserve the user's denylist without broadening it by basename, extension, or pattern. If a prior scope artifact declares an additional protected path, reconcile it before the run rather than silently dropping it.
- A walker may observe a protected entry at its allowed parent boundary, but must skip it before `stat`, `open`, hashing, parsing, recursion, move, or write logic. Never use a broad recursive glob that crosses the protected set.
- Test exact exclusion separately from near matches: the exact protected path is excluded; a same-named item elsewhere, a near-match name, and an unrelated archive follow the normal policy.
- Emit only aggregate protected-set evidence. Do not publish protected titles, bodies, IDs, hashes, or contents.

## 3. Freeze before semantics

1. Inventory only eligible items and classify control files separately from promotion candidates.
2. Choose deterministic ordering and freeze the complete queue: ordinal, source path, byte size, source hash, disposition, batch size, total batches, and queue hash.
3. Do not refill a batch from a protected, pending, abandon, or newly discovered item after the freeze.
4. Revalidate source hashes and destination absence immediately before each write. A changed source or pre-existing destination returns the item to planning.

Default batch sizing may be 100 items when the governing policy says so, but batch size is an explicit run parameter and is not a quota policy.

## 4. Role routing and identity evidence

For an existing Inbox item being promoted, do not invoke Terra. The normal route is:

- **Terra:** Stage A Inbox intake only; may create a new, provenance-rich Inbox artifact, never canonical/formal knowledge.
- **Luna:** Stage B read-only semantic planner; emits a fixed, machine-verifiable plan and never writes.
- **Current main brain / Vani:** Stage C policy gate; checks scope, freshness, conflicts, allowlist, risk, and required approval. This is not a reason to switch the user-facing session model.
- **Sol or the strongest currently available operator:** Stage D canonical/formal writer and whole-library governor, subject to the effective plan, allowlist, backup, and deterministic acceptance gates.
- **Deterministic tooling:** freeze, hashes, manifests, sidecars, rollback copies, permissions, schema checks, link checks, and read-back; do not spend model quota on these operations.

Before dispatching a role-bound worker:

- inspect the actual runner help instead of inventing optional flags;
- resolve the requested provider/model against the live catalog;
- record the exact provider/model in the run receipt and usage envelope;
- verify the returned usage identity before accepting output;
- keep model identity separate from reasoning effort. For Hermes, Roy's "GPT-5.6 Luna Max" preference means prefer the real `gpt-5.6-luna` model with `reasoning_effort=max` unless the live catalog exposes a distinct Max model slug; do not invent or relabel model IDs. Set `agent.reasoning_effort=max` for the main session and `delegation.reasoning_effort=max` for delegated workers when that scope is authorized. Verify with `hermes config get` plus the installed Hermes venv's shared `resolve_reasoning_config()`; a successful `hermes config show` or a model name alone is not runtime proof. Do not confuse display reasoning visibility with model reasoning effort. If the effective resolver does not return enabled `max`, stop or apply only an explicitly authorized fallback policy without silently substituting a role or provider.

## 5. Quota is observability plus a conditional pause policy

- Query live quota before the first batch and after every accepted batch. Keep the receipt even when quota is not an active stop gate.
- Do not hardcode a percentage threshold. A user may explicitly enable, change, or remove a percentage pause condition; the runner must apply the active comparator literally when one exists.
- If the authority has removed the percentage pause condition, continue at frozen batch boundaries after independent acceptance unless quota lookup is unavailable, the provider reports hard exhaustion/429, a safety/integrity gate fails, or the user stops the run.
- Never interpret "ignore the threshold" as permission to weaken no-touch, hash, backup, rollback, one-writer, model-identity, or verification gates.
- If quota lookup is ambiguous while quota is an active gate, fail closed and pause rather than guessing.

## 6. Write and rollback transaction

Before a model writer starts a batch, persist:

- exact input list and hashes;
- protected-set boundary evidence;
- current knowledge snapshot and destination absence checks;
- an approved effective plan and complete write allowlist;
- a verified backup/checkpoint or an external rollback copy with manifest and hashes;
- selected writer model/provider and stop conditions.

Use one writer for a shared index/log or overlapping canonical files. If the writer fails, times out, exhausts quota, or returns an error envelope, audit actual filesystem state, quarantine unregistered partials, and restore only from the current batch's verified baseline. Do not infer success from files that happen to exist.

A backup command that has not passed a real read-back check is not backup evidence. Fail closed or use an already-authorized verified rollback provider; never print a synthetic success receipt.

## 7. Acceptance and continuation

After a producer completes, run independent deterministic acceptance against actual paths:

- payload, sidecar, and staging hashes/read-back;
- schema, permissions, links, and index/count reconciliation;
- exact scope/allowlist comparison;
- protected-set unchanged check;
- rollback manifest completeness;
- source and destination manifest reconciliation.

Only an `accepted` batch may unlock the next frozen batch. Preserve the complete receipt even for `no-op`, `rolled-back`, `paused`, and `failed` runs. Report aggregate state and absolute evidence paths; do not report protected content or treat preparation as execution.

## 8. Implementation verification and race-safe hardening

For a Python runner implementation, use this order after the worker has produced a draft:

1. Confirm the delegated worker has reached a terminal state before editing or copying its shared artifact. Concurrent commander/worker edits can overwrite a patch after the commander's last read; re-read the final artifact after the worker stops.
2. Replace timestamped evidence scope defaults with a stable policy path outside run directories. Record the stable scope's SHA-256 in every run; never silently reuse an old session's scope file as the default.
3. Parse the live quota provider schema. The `check-ai-cli-quota` JSON observed in this workflow places provider state under `results[].available` and windows under `results[].windows[]`; copy provider, window, reset, and percentage fields into the receipt for observability. Missing or false availability pauses; only explicit structured hard exhaustion/429 is a hard-quota classification. Percentages have no implicit threshold.
4. Before each Luna/Sol dispatch, read back both Hermes `agent.reasoning_effort` and `delegation.reasoning_effort`; require the requested value (`max` here) and persist it next to exact provider/model identity. A model name or a successful process exit is not reasoning-effort evidence.
5. After every source patch or installation copy, rerun compile, source/installed byte and SHA-256 equality, a real dry-run/empty-queue smoke, and read the generated receipt. Test an apply gate with a synthetic non-empty fixture and an unavailable quota command to prove `models_started=[]` and zero root writes. Do not claim full non-empty semantic execution when the live queue is empty.
