---
name: llm-wiki
description: "Governed Luna/Terra knowledge workflow and wiki query."
version: 3.1.7
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

Maintain a persistent, compounding Markdown knowledge base without letting an
unreviewed source silently become formal knowledge. The authoritative knowledge
root is `WIKI_PATH` when set, otherwise `~/knowledge`. It is not a Git workflow:
use the configured GCP backup/checkpoint mechanism before formal-library writes;
do not initialize or require Git.

## Non-negotiable role and model routing

Roles, model names, and the current main session are separate concerns.

| Role | Required provider/model identity | Permission |
|---|---|---|
| Luna, Read-only Planner | `openai-codex/gpt-5.6-luna` | Read only; create a promotion plan in its response, never write a file. |
| Terra, restricted legacy role | `openai-codex/gpt-5.6-terra` | Not used as the current Stage A executor; never modify formal-library files. |
| Current main-brain model, Policy Gate | The model active in the current main session | Main-session governance, query synthesis, and policy-gate decision. |
| High-capability knowledge operator | GPT-5.6-Sol, a model demonstrably stronger than the current main brain, or the most capable model currently available | Knowledge merge, conflict resolution, and governed formal-library maintenance. |

- The policy gate is performed by the **current main-brain model**. This skill
  MUST NOT switch the active main-session model or invoke a model-changing command.
- **High-capability work requirement:** `Knowledge Merge`, `Conflict Resolution`,
  `Update Wiki`, `Update Knowledge Graph`, `Update Index`, and all **whole-library
  governance** work—cross-domain scanning, contradiction checking, index
  restructuring, and aging governance—must use GPT-5.6-Sol, a model demonstrably
  stronger than the current main brain, or the most capable model currently
  usable. **If the current main-brain model is itself the most capable available,
  it satisfies this condition and must execute the work directly in the current
  main session.** Do not dispatch a separate worker merely to satisfy this rule.
  Record the selected model and why it meets this condition in the task packet or
  result. Do not silently downgrade these operations to Terra.
- Model routing occurs only through an independent worker dispatcher. Before every
  Luna, Terra, or dispatched high-capability stage, the dispatcher must verify the
  assigned worker's actual model identity. If the requested model is unavailable
  or the actual model does not match the selected role/condition, stop that stage
  and report the mismatch. Do not silently substitute another model, role,
  provider, or main-session model.
- The dispatcher passes an explicit task packet: source/artifact path, permitted
  reads, permitted writes, required output schema, and stop conditions. A worker
  may not expand that packet.
- The current main brain may answer queries directly from already formalized
  knowledge. Querying does not require Luna/Terra routing and does not create or
  modify knowledge unless a separate governed promotion is requested.

### Dispatcher entry point

Use the bundled dispatcher for every model-bound worker stage:

```bash
python3 ~/.hermes/skills/research/llm-wiki/scripts/run-role-worker.py \
  --role luna \
  --prompt-file /absolute/path/to/task-packet.txt \
  --workdir "${WIKI_PATH:-$HOME/knowledge}"
```

Do not use `--role terra` for current Stage A Inbox capture. Follow the
`knowledge-inbox-capture` executor selection instead. Use `--role sol` only
when GPT-5.6-Sol is the selected high-capability operator. If it is
unavailable—or if the current main-brain model is already the most capable
available—the current main brain executes the high-capability stage directly
after recording the selection rationale; another worker model must be
identity-verified before it performs that stage. Policy-gate work stays in the current main session;
do not dispatch it as a standalone worker stage. The dispatcher
starts a separate `hermes --oneshot` process with the complete model ID and
provider, preloads this skill, captures the response, and validates the actual
model/provider in the usage report before releasing the response. Its default
usage reports live under `~/.hermes/worker-runs/llm-wiki/`, never in the knowledge
root. User aliases for worker roles are convenience aliases only; the dispatcher
deliberately does not pass aliases to oneshot because that path is not runtime-safe
on the current OpenAI Codex surface.

## Knowledge areas and exclusions

```text
<knowledge-root>/
├── Inbox/                 # non-formal source artifacts under the current capture contract
├── SCHEMA.md              # formal-library convention and domain boundary
├── index.md               # formal-library navigation
├── log.md                 # formal-library action log
├── entities/
├── concepts/
├── comparisons/
└── queries/
```

`Inbox/` is a drop point, not formal knowledge. New sources MUST enter Inbox
first. Formal-library scans, retrieval, lint, duplicate detection, and source
counts MUST exclude `Inbox/`, `_backups/`, `.git/`, and generated/cache paths.
Never use backup contents as retrieval context.

## Stage A — new-source intake (Inbox only; executor per current capture SOP)

For Inbox capture, the detailed and current contract is
`knowledge-inbox-capture` (currently v1.9.0), together with the live
`inbox/README.md`. The active main brain first determines whether the request is
full capture or an explicitly requested lightweight intake. If the active main
brain is not higher than `GPT-5.6-luna max`, it executes full Stage A itself; if
it is higher, it dispatches the exact `GPT-5.6-luna max` executor. Terra is not a
Stage A executor. In every case Stage A may create only the single allowlisted
Markdown under `inbox/` and MUST NOT modify `knowledge-map.md`, `system/`,
`sources/`, `staging/`, `domains/`, `projects/`, `entities/`, `archive/`, or
any formal index.

The artifact shape is governed by the live `inbox/README.md` and the
`knowledge-inbox-capture` skill, not by a separate legacy field list in this
umbrella skill. Full capture preserves the complete source and uses the Inbox
contract plus the required translation/summary/insight sections; an explicitly
requested lightweight intake uses only the permitted minimum metadata and a
pending-full-capture note. Source provenance and any hashes must be recorded
according to the active capture or formal-source contract; incomplete capture
must state its limit rather than inventing missing material.

## Stage B — promotion planning (Luna only; read-only)

An Inbox artifact does not authorize a formal write. To promote it, dispatch
**Luna** with the exact artifact path and a read-only snapshot of the relevant
formal domain. Luna MUST write no file and return one fixed-schema plan:

```yaml
plan_version: 1
plan_id: <unique id>
created_at: <ISO-8601 timestamp>
expires_at: <ISO-8601 timestamp>
input_hash: <Inbox artifact source_hash>
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
allowlist: [<only paths the selected high-capability operator may write>]
conflicts: []
requires_roy_approval: true | false
expiry_freshness:
  input_hash_valid: true
  snapshot_valid: true
  max_age: <duration>
  rationale: <why the plan is still fresh>
```

Luna must report conflicts, uncertainty, evidence gaps, and out-of-domain impacts
instead of resolving them by writing. The plan must be limited to explicit
`create`/`update` operations; no delete, move, rename, or structural rewrite is
allowed in an auto-approvable plan.

## Stage C — current main-brain policy gate

The current main-brain model/Vani may automatically approve a Luna plan only
when every condition holds:

1. all operations are in one existing domain;
2. there are at most three formal-library files;
3. every operation is `create` or `update`;
4. `conflicts` is empty;
5. every affected claim has confidence `>= 0.85`;
6. the plan is within its freshness window, and both `input_hash` and
   `knowledge_snapshot.hash` still match current read-back values.

Roy approval is mandatory for any delete, move, rename, cross-domain change,
conflict, confidence below `0.85`, structural rewrite, expired/stale hash or
snapshot, or any operation outside the approved plan/allowlist. Stop and request
Roy; do not split or reinterpret the change to evade approval.

## Stage D — formal write (high-capability knowledge operator only)

Only after an effective Luna plan and a valid current-main-brain/Roy gate may a
**high-capability knowledge operator** write formal knowledge. It must meet the
high-capability work requirement before any `Knowledge Merge`, `Conflict
Resolution`, `Update Wiki`, `Update Knowledge Graph`, or `Update Index` work.

1. Revalidate plan expiry, `input_hash`, snapshot/version, snapshot hash, and
   every pre-write hash immediately before writing. Any mismatch or expiry is a
   stop condition; return to Luna/current main brain, never continue on stale evidence.
2. Use the plan's `allowlist` as the complete write boundary. Write only the
   listed files, only with the listed `create`/`update` operation, and preserve
   explicit provenance/evidence in the formal content.
3. Take a GCP backup/checkpoint of the affected formal scope before writing and
   record its identifier and the selected operator model in the write result. Do
   not require or initialize Git.
4. Use a direct read-back after writing. Simple, repeated, conflict-free plans may
   be executed. Complex changes, conflicting evidence, unexpected file state, or
   any boundary expansion must stop and escalate to the current main brain/Roy.

Terra is not a current Stage A executor and may never self-approve a plan,
perform a high-capability operation, convert an Inbox artifact directly into
formal knowledge, or broaden an allowlist.

## Formal-library governance (high-capability operator only)

All **whole-library governance** work—cross-domain scanning, contradiction
checking, index restructuring, and aging governance—must meet the
high-capability work requirement: GPT-5.6-Sol, a model demonstrably stronger
than the current main brain, or the most capable model currently usable. If the
current main-brain model is the most capable available, it must execute the work
directly; no separate worker is required. Its default is **audit-only**. First
produce a bounded governance plan: target domain, snapshot/version, findings,
proposed operations,
evidence, risks, allowlist, selected model and selection rationale, and
freshness/expiry. Execute only after the applicable policy gate, one domain-sized
small batch at a time. A governance audit or an index/lint request never
authorizes an unbounded full-library rewrite.

## Query (current main brain)

For a question about the existing formal library, the current main brain may read the relevant
formal index and pages, synthesize an answer, and cite the pages used. Exclude
Inbox, backups, and generated/cache directories from retrieval. A useful answer
may be proposed for filing, but filing is a new formal write and must begin at
Stage B (or Stage A when it relies on a new source).

## Lint and archive boundaries

Lint is audit-only by default: report broken links, index gaps, required
frontmatter omissions, stale sources, provenance gaps, low-confidence claims,
and explicit contradictions. Do not append logs or auto-fix while linting.

Archive, deletion, movement, and renaming are always Roy-approved formal
operations. Do not use a convenience archive procedure to bypass Stage B–D.

## Required verification for skill changes

For edits to this skill, perform the minimum sufficient V1 verification:

1. Read back the role-routing and Stage A–D sections.
2. Search the skill for legacy direct-ingest instructions or contradictory rules,
   including the former direct-ingest wording, `raw/articles`, the former page-write
   heading, direct `index.md`/`log.md` writes, and model-switch instructions.
3. Parse the YAML frontmatter and confirm its required fields and bumped version.

## Pitfalls

- Never ingest a new source directly into the formal library.
- Never let Luna write or Terra approve its own plan.
- Never treat an expired plan, stale hash, or stale snapshot as advisory.
- Never silently substitute a model or use `/model` to alter the current
  main-brain session.
- Never use Git as a requirement for `${KNOWLEDGE_ROOT}`; use GCP
  backup/checkpoint.
- Never present translation, Vani's心得, or extended inference as source fact.
