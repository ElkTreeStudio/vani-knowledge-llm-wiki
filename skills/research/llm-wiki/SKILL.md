---
name: llm-wiki
description: "Model-agnostic governed knowledge workflow and wiki query."
version: 4.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, governance]
    category: research
    related_skills: [obsidian, arxiv]
---

# Governed LLM Wiki

Maintain a persistent, compounding Markdown knowledge base without allowing an
unreviewed source, an LLM response, or an implementation convenience to silently
become formal knowledge.

The canonical root is `${KNOWLEDGE_ROOT}` when configured, otherwise
`~/knowledge`. The knowledge corpus itself is not required to use Git. Use the
configured backup/checkpoint mechanism before governed writes to existing formal
knowledge.

## Canonical knowledge layers

The live contracts under the knowledge root are authoritative for storage and
promotion details. The expected top-level architecture is:

```text
<knowledge-root>/
├── inbox/        # simple delivery entry; not formal knowledge
├── system/       # schemas, prompts, scripts, import runs, maintenance rules
├── sources/      # canonical source evidence and deterministic projections
├── staging/      # rebuildable analysis and review records
├── domains/      # reusable curated formal knowledge
├── projects/     # project-specific curated formal knowledge
├── entities/     # shared entities supported across domains/projects
└── archive/      # formerly active formal knowledge
```

New material enters through `inbox/`. Formal retrieval, indexing, linting, maps,
and source counts must respect the live scanner exclusions and must not treat
Inbox, staging, backups, generated caches, or frozen artifacts as formal
knowledge.

## Stable roles, runtime-selected models

Knowledge roles are governance contracts. They are **not model names**.
Provider/model identities change over time and belong to runtime configuration,
not to this skill.

| Role | Capability requirement | Permission boundary |
|---|---|---|
| Current main session / coordinator | Understand the request and current governance | Query synthesis, task routing, policy-gate decisions; no implicit promotion authority |
| Capture executor | Reliable source acquisition, rendering, translation, summarization, and exact-path tool use | May create or upgrade only the single allowlisted Inbox artifact under the capture contract |
| Promotion planner | Strong semantic classification and planning | Read only; returns a bounded promotion plan and never writes knowledge |
| Formal maintainer | Strong reasoning for merge, conflict resolution, and governed maintenance | May perform only policy-approved writes within the exact allowlist |
| Verifier | Deterministic validation first; semantic review when needed | Read only unless a separate repair/write operation is explicitly authorized |

### Model-selection policy

- This skill MUST NOT name, require, rank, or pin a provider/model release.
- The active runtime chooses an executor that satisfies the role's capability and
  permission requirements. Model aliases, capability tiers, reasoning settings,
  quotas, fallbacks, and provider availability belong to runtime configuration.
- The current main session may execute a role directly when it can satisfy the
  role contract. Do not dispatch another worker merely to satisfy a model-name
  convention.
- When a worker is delegated, record its actual provider/model and completion
  evidence outside the knowledge root. Identity is provenance, not promotion
  authority.
- If the runtime cannot provide an executor that can honor the required read/write
  boundary, stop that operation. Do not silently weaken the role contract.
- This skill MUST NOT change the active main-session model as a side effect of a
  knowledge operation.

## Worker dispatcher

The bundled dispatcher supports governance roles rather than named models:

```bash
python3 ${HERMES_HOME}/skills/research/llm-wiki/scripts/run-role-worker.py \
  --role planner \
  --prompt-file /absolute/path/to/task-packet.txt \
  --workdir "${KNOWLEDGE_ROOT:-$HOME/knowledge}"
```

By default the dispatcher uses the model/provider already selected by the runtime.
A caller may pass `--model` and `--provider` together when those values were
resolved by runtime policy outside this skill. The dispatcher verifies runtime
completion and, when an explicit identity is supplied, verifies that exact
identity in the usage report.

Inbox capture follows `knowledge-inbox-capture`; it is not forced through this
worker dispatcher. Policy-gate decisions stay in the current main session.

The dispatcher writes usage evidence under
`~/.hermes/worker-runs/llm-wiki/` by default, never inside the knowledge root.

## Inbox capture

When the user provides new material for retention, follow the live
`knowledge-inbox-capture` skill and `${KNOWLEDGE_ROOT}/inbox/README.md`.

The capture operation may create or upgrade only the one allowlisted Markdown
artifact under `inbox/`. It must not create canonical sources, classify into
formal domains/projects/entities, update indexes/maps, or run promotion as an
implicit continuation of capture.

Full capture is the default unless the user explicitly requests lightweight or
metadata-only retention. The capture skill owns the exact artifact shape and
verification requirements; this umbrella skill does not duplicate that field
list.

## Promotion planning

An Inbox artifact does not authorize a formal write. Promotion begins with a
read-only planner using the exact Inbox artifact plus a bounded snapshot of the
relevant formal scope.

The planner returns one fixed-schema plan and writes no file:

```yaml
plan_version: 1
plan_id: <unique id>
created_at: <ISO-8601 timestamp>
expires_at: <ISO-8601 timestamp>
input_hash: <Inbox artifact source hash>
knowledge_snapshot:
  version: <snapshot/version identifier>
  hash: <hash of the read formal scope>
  captured_at: <ISO-8601 timestamp>
operations:
  - action: create | update
    path: <formal-library path>
    intent: <bounded change>
    expected_content_hash: <optional pre-write hash for update>
evidence:
  - claim: <claim>
    source_locations: [<Inbox sections/anchors>]
    confidence: <0.00-1.00>
allowlist: [<only paths the formal maintainer may write>]
conflicts: []
requires_owner_approval: true | false
expiry_freshness:
  input_hash_valid: true
  snapshot_valid: true
  max_age: <duration>
  rationale: <why the plan is still fresh>
```

The planner reports conflicts, uncertainty, evidence gaps, and out-of-domain
impacts instead of resolving them by writing. Auto-approvable plans are limited
to explicit `create`/`update` operations; delete, move, rename, structural
rewrites, and boundary expansion require owner approval.

## Policy gate

The current main session may approve a promotion plan without separate owner
approval only when every condition holds:

1. all operations are inside one existing domain/project scope;
2. at most three formal-library files are affected;
3. every operation is `create` or `update`;
4. `conflicts` is empty;
5. every affected claim has confidence `>= 0.85`;
6. the plan is still within its freshness window and both the input hash and
   formal-scope snapshot hash still match current read-back values.

Owner approval is mandatory for delete, move, rename, cross-domain changes,
conflicts, confidence below `0.85`, structural rewrites, expired/stale evidence,
or any operation outside the approved plan/allowlist. Do not split or reinterpret
a change to evade this gate.

## Formal write

Only after a valid promotion plan and policy gate may a formal maintainer write
formal knowledge.

1. Revalidate plan expiry, input hash, snapshot/version, snapshot hash, and every
   applicable pre-write hash immediately before writing.
2. Treat the plan allowlist as the complete write boundary. Perform only the
   listed operation on each listed path.
3. Take the configured backup/checkpoint of affected existing formal content
   before writing and record its identifier outside the knowledge content.
4. Preserve provenance/evidence in formal content according to the live schema.
5. Read back the actual files after writing. Unexpected state, new conflicts, or
   any required scope expansion stops the operation and returns to planning/gate.

A model's confidence in its own output is never a substitute for hash, schema,
path, backup, and read-back checks.

## Verification

Producer completion is not acceptance. After a governed write:

- verify the exact changed path set;
- verify required hashes, schemas, links, and source references;
- compare protected/unchanged paths against the applicable baseline;
- verify index/map effects only when those paths were explicitly authorized;
- use a separate read-only semantic review when the change materially depends on
  synthesis quality rather than deterministic transformation.

A verifier defect must be fixed in the verifier; do not rewrite valid content to
make a broken verifier green.

## Whole-library governance

Cross-domain scanning, contradiction review, index restructuring, and aging
review are high-impact maintenance operations. Start audit-only and produce a
bounded governance plan with target scope, snapshot, findings, evidence, risks,
proposed operations, allowlist, and freshness data.

Do not turn a governance audit into an unbounded rewrite. Execute approved work
in small domain-sized batches with the same planning, gate, backup, write, and
verification boundaries used for ordinary formal maintenance.

## Query

For questions about existing formal knowledge, the current main session may read
the relevant formal indexes/pages, synthesize an answer, and cite the pages used.
Exclude Inbox, staging, backups, frozen artifacts, and generated/cache paths from
formal retrieval unless the user explicitly asks to inspect those layers.

Answering a query does not modify knowledge. Filing a useful answer is a new
capture/promotion operation and must follow the appropriate governance flow.

## Lint and archive boundaries

Lint is audit-only by default: report broken links, index gaps, required
frontmatter omissions, stale sources, provenance gaps, low-confidence claims,
and explicit contradictions. Do not auto-fix merely because lint was requested.

Archive, deletion, movement, and renaming are formal operations and require the
applicable plan and owner approval. A convenience archive procedure may not
bypass promotion governance.

## Required verification for skill changes

For edits to this skill:

1. Parse the YAML frontmatter and confirm the version was bumped appropriately.
2. Read back the role, capture, planning, gate, formal-write, verification, query,
   and archive sections.
3. Search for provider/model IDs or model-release-specific routing rules; none
   should be required by this skill.
4. Search for lettered workflow-stage terminology used as the primary public
   contract; use semantic operation names instead.
5. Search for legacy direct-ingest instructions, direct unplanned formal writes,
   or model-switch commands.

## Pitfalls

- Never ingest a new source directly into the formal library.
- Never let a planner write or a maintainer self-approve its own expansion.
- Never treat an expired plan, stale hash, or stale snapshot as advisory.
- Never make a particular model release part of the knowledge-governance ABI.
- Never use Git as a requirement for the private knowledge corpus.
- Never present translation, user commentary, or extended inference as source
  fact.
