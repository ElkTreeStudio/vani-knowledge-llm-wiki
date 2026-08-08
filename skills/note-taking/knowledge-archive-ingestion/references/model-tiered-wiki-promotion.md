# Model-tiered Wiki Ingestion and Governance

Use this reference when a canonical knowledge workflow separates model tiers or named worker roles. Keep **role contracts** separate from **runtime model mappings** so model versions can change without rewriting the workflow.

## Stable role contracts

- **Commander / Policy Gate (Sol-class main brain):** owns routing, approval policy, handoffs, verification, and user reporting. Keep the user-facing session on the strongest reasoning tier; do not switch the main session merely to run a cheaper stage.
- **Inbox Editor (Terra-class worker):** captures the source, translates it when needed, summarizes it, writes clearly labeled reading notes and inferences, and preserves provenance. It may write only to Inbox/intake and must not modify canonical knowledge during this stage.
- **Ingestion Planner (Luna-class worker):** reads Inbox and canonical knowledge, compares and classifies candidates, detects duplicates, and emits a machine-verifiable change plan. It is read-only and must not create, edit, move, or delete canonical pages.
- **Knowledge Editor (Sol-class worker):** applies an approved, still-valid plan within its exact allowlist. It may merge knowledge, rewrite pages, update navigation, and resolve only bounded, evidence-backed conflicts; high-capability work must never be downgraded to Terra.
- **Knowledge Governor (Sol-class worker):** performs periodic cross-domain audits, contradiction review, index/taxonomy restructuring, and knowledge-aging analysis. Governance starts read-only and proceeds to bounded batches only after a policy gate.

Example dispatch mapping (illustrative aliases, not hard-coded model IDs):

```yaml
roles:
  commander: sol
  inbox_editor: terra
  ingestion_planner: luna
  knowledge_editor: sol
  knowledge_governor: sol
```

## Runtime guarantees

A role label is not proof that the intended model ran. Before dispatch, verify that the execution surface supports a per-worker model selection and record the resolved provider/model. If a child-agent API inherits the parent model and has no per-call model override, it cannot truthfully implement Luna/Terra routing; use an independently pinned worker process or job instead.

- The skill must not issue `/model`, change the global model default, or silently replace the user-facing main brain.
- A session-level `/model` changes the actual main model; it is not worker dispatch.
- Do not silently fallback or let another model impersonate an unavailable role.
- A user-authorized provider fallback for availability is separate from role routing and must be recorded.
- If a required role is unavailable, stop only the stage that requires it: Planner unavailable leaves Inbox `new`; Editor unavailable preserves the plan without canonical writes; Governor unavailable delays governance without blocking ordinary capture.
- Only explicit user authority may substitute a role/model. Record the substitution and actual runtime model.

## Inbox evidence contract

Keep evidence and interpretation visibly separate:

```markdown
## Source information
## Original content
## Traditional Chinese (Taiwan) translation
## Source summary
## Reading notes
## Inferences
## Fact-check status
## Provenance
```

Suggested metadata:

```yaml
status: new
source_verified: false
contains_personal_notes: true
```

The original source may support factual claims. Translation and summary are derivatives, not new evidence. Reading notes are opinions; inferences must be labeled. A planner must not promote notes or inferences as objective fact.

## Machine-verifiable promotion plan

The Planner should produce a fixed schema containing at minimum:

```yaml
plan_id: ingest-<timestamp>-<slug>
created_at: <ISO-8601>
input:
  inbox_file: <path>
  inbox_sha256: <sha256>
  knowledge_checkpoint: <checkpoint-id>
classification:
  primary_domain: <domain>
operations:
  - action: create | update | link-only | drop
    file: <canonical-path>
    sections: []
    evidence: []
    confidence: 0.0
allowlist: []
forbidden_operations: [delete, move, rename]
conflicts: []
requires_user_approval: false
```

Before writing, the Knowledge Editor must verify the Inbox hash, current knowledge checkpoint, operation type, target allowlist, and risk flags. A stale plan stops and returns to planning. The writer may not expand scope.

Low-risk plans may be auto-approved by the Commander only when policy permits: no conflicts, sufficient confidence, same-domain changes, bounded file count, and create/update only. Stop for user approval on low confidence, unresolved source conflict, cross-domain restructuring, deletion/move/rename, broad taxonomy changes, or reversal of an important established conclusion.

## Sol governance boundary

Do not give the strongest model unbounded write access merely because it reasons better:

```text
read-only whole-library audit
→ governance plan
→ scope/risk gate
→ one-domain bounded batch
→ deterministic diff/link/index/provenance checks
→ next batch
```

Default governance mode is `audit_only`. Destructive operations, broad taxonomy changes, and large cross-domain batches require explicit user approval.

## Checkpoint portability

Do not assume the knowledge root uses Git. Use the repository's actual rollback authority. For a knowledge root versioned by GCP backups, require a fresh GCP backup/checkpoint and content hashes before canonical edits rather than `clean git tree` or `checkpoint commit` gates. Never introduce Git only to satisfy a generic workflow example.
