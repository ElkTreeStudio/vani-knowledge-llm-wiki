---
name: knowledge-inbox-capture
description: "Capture user-provided material into Inbox; full by default."
version: 2.0.2
---

# Knowledge Inbox Capture

## Purpose

Use this skill when the user provides a webpage, X article, newsletter, document,
excerpt, idea, or other material and asks to preserve it under
`${KNOWLEDGE_ROOT}/inbox/`.

Inbox capture is intentionally narrow. It creates or upgrades one Inbox artifact
only. It does **not** create canonical sources, classify into formal
domains/projects/entities, update indexes/maps, or run promotion implicitly.

## Default behavior

A normal request to retain material in Inbox means **full capture** unless the
current request explicitly asks for a lightweight/metadata-only result.

### Full capture

Preserve all obtainable source content or all user-supplied content. A URL is not
required when the material itself is supplied in the request, attachment, or
conversation context. When the source is not already Taiwan Traditional Chinese,
include a complete Taiwan Traditional Chinese translation. Add:

- `Vani 摘要`
- `Vani 心得與延伸見解`
- the complete translated content when translation is required
- the complete original/source content

The exact frontmatter and section formatting come from the live
`${KNOWLEDGE_ROOT}/inbox/README.md`. The normal filename is
`YYYY-MM-DD-short-slug.md`, where the slug uses lowercase ASCII alphanumerics and
hyphens.

### Lightweight capture

Use lightweight capture only when the current request explicitly asks for a
restriction such as metadata only, link only, no source fetch, no translation,
no summary, or equivalent wording.

A lightweight artifact contains only the live Inbox contract's minimum metadata,
user-provided title/description when available, source identification, capture
date, and a note that full capture remains pending. Do not fetch or synthesize
content that the user explicitly asked not to include.

A short request or a bare URL is **not** evidence of lightweight intent.

## Source of truth

Before every write, read `${KNOWLEDGE_ROOT}/inbox/README.md` and use its current
storage contract. Do not infer the current format from old Inbox artifacts.

When that README describes later source canonicalization, staging, promotion, or
indexing, those later procedures do not expand the scope of an Inbox-only request.

### Protected no-touch Inbox subtrees

These exact Inbox subtrees are protected governance boundaries and must not be
opened, enumerated, moved, renamed, indexed, searched as duplicate-preflight
content, or used as capture targets:

- `${KNOWLEDGE_ROOT}/inbox/gpt-message-import-abandon/`
- `${KNOWLEDGE_ROOT}/inbox/gpt-message-import-pending/`

The exact frozen artifact declared by the live Inbox contract is also no-touch.
The duplicate preflight may inspect only eligible direct Inbox Markdown files and
must exclude README, the two protected subtrees, the frozen artifact, and any
other live contract exclusions.

## Semantic intent routing

Intent is decided by the active model from the complete request, attachments,
links, and conversation context. Do not use a keyword list, regex, spelling
variant, or single phrase as the intent classifier.

After the semantic decision, validate the category with:

```text
python3 ${HERMES_HOME}/skills/note-taking/knowledge-inbox-capture/scripts/route_inbox_intent.py \
  --text <raw-user-request> \
  --model-intent <semantic-category>
```

Supported capture categories are:

- `inbox-only-full` — default material-to-Inbox capture
- `inbox-only-lightweight` — explicit lightweight exception

The validator also recognizes blocked, promotion, ambiguous, and non-Inbox
categories. It validates the declared semantic decision and boundary; it does not
replace semantic intent understanding and must not fetch source content.

Only a validator result with `packet_permitted: true` authorizes an Inbox capture
packet. A non-URL full capture is valid when the model has semantically identified
actual user-supplied material in the current request/context; ambiguous requests
must be routed as ambiguous/blocked rather than forced through by the validator.

## Executor policy

The capture executor is a **capability role, not a model identity**.

The selected executor must be able to:

- acquire the allowed source reliably;
- perform deterministic rendering where the source type supports it;
- translate the complete required text when translation is required;
- generate the required summary and insights;
- obey an exact single-file write boundary;
- stop instead of weakening the contract when a real source/tool/context/output
  blocker prevents complete capture.

Model/provider selection, capability tiers, reasoning settings, quotas, and
fallbacks are runtime concerns. This skill MUST NOT name or compare model
releases. The active main session may execute capture directly or delegate it
according to current runtime policy.

When delegated, use one selected executor for the semantic capture work on that
material. Do not silently switch executors mid-capture merely to work around a
failure. Runtime usage evidence must record the actual provider/model and
completion state outside the knowledge root; identity is provenance, not
promotion authority.

## Capture boundary

Before source acquisition, establish one bounded capture packet. It must contain:

```text
intent_router_result: inbox-only-full | inbox-only-lightweight
source: <exact source/material identity>
read allowlist: <exact permitted reads>
write allowlist: <resolved absolute path under KNOWLEDGE_ROOT/inbox/*.md>
stop conditions: <concrete blockers>
```

The packet has one semantic mode field: `intent_router_result`. Do not add a
second operation-mode label that can disagree with it.

Before any write, mechanically validate the target. The example below validates
a normal full-capture target; valid `--mode` values are `full`, `lightweight`, and
`in-place-upgrade`.

```bash
python3 ${HERMES_HOME}/skills/note-taking/knowledge-inbox-capture/scripts/validate_inbox_target.py \
  --knowledge-root /absolute/path/to/knowledge \
  --target /absolute/path/to/knowledge/inbox/2026-08-09-example.md \
  --mode full
```

Requirements:

1. `write allowlist` appears exactly once and names exactly one Markdown path
   directly under the resolved Inbox root.
2. A new full/lightweight target must be absent. An `in-place-upgrade` target must
   already exist and must be the explicitly authorized same-source lightweight
   artifact.
3. The target filename follows `YYYY-MM-DD-short-slug.md`; `README.md` is never a
   capture target.
4. The target itself must not be a symlink; symlink rejection is performed before
   canonical path resolution.
5. The packet may allow a non-recursive exact canonical-URL duplicate preflight
   over eligible direct Inbox Markdown only.
6. The read/write boundary must exclude the protected no-touch subtrees, frozen
   artifact, README, rollback files, usage files, and unrelated Inbox artifacts.
7. The packet must not allow writes to `system/`, `sources/`, `staging/`,
   `domains/`, `projects/`, `entities/`, `archive/`, indexes/maps, or any path
   outside the single validated target.
8. Packet, rollback, usage, and temporary audit artifacts stay outside the
   knowledge root unless a live contract explicitly says otherwise.

## Full-capture execution

For a permitted `inbox-only-full` request:

1. Acquire the complete allowed source or use the complete user-supplied material.
2. Prefer deterministic structured rendering when available; preserve source
   order, headings, links, code, quotations, media references, and explicit
   placeholders for unsupported atomic content.
3. Preserve all obtainable substantive source text.
4. Translate the complete required text into natural Taiwan Traditional Chinese
   when the source language requires translation.
5. Generate `Vani 摘要` and `Vani 心得與延伸見解` without presenting those sections
   as source fact.
6. Assemble exactly one final Inbox Markdown according to the live README.
7. Write only the mechanically validated allowlisted target.
8. Read back and independently verify the artifact before reporting success.

For long/structured material, use the bounded batching guidance in
`references/long-article-batch-translation.md`. Batch size is an execution detail;
it is not permission to create additional Inbox files or switch to a partial
capture.

For X long-form articles, follow
`references/x-article-structured-capture.md` for structured retrieval/rendering.

## Lightweight execution

For a permitted `inbox-only-lightweight` request:

1. Do not fetch source bodies when the request forbids source fetch.
2. Do not translate, summarize, or generate insights when the request excludes
   them.
3. Store only the permitted minimum metadata/content in one Inbox Markdown.
4. Mark that full material capture remains pending when appropriate.
5. Read back the artifact and verify the exact boundary.

## Duplicate and in-place upgrade behavior

Do not create a second Inbox file for the same canonical source identity merely
because full capture is requested later.

If an existing same-source artifact is already complete, stop and report it. If
it is a lightweight artifact and the current request semantically requires full
capture, use `references/in-place-lightweight-upgrade.md`:

- create rollback outside the knowledge root first;
- preserve the same final Inbox path;
- validate that path with `--mode in-place-upgrade`;
- perform the full capture under the same single-target boundary;
- restore rollback on any failure or failed verification;
- remove rollback only after final independent verification passes.

## Verification

Executor completion is not artifact acceptance. Verify at minimum:

- the actual target path equals the one mechanically validated allowlist;
- no other knowledge-root path changed;
- YAML/frontmatter satisfies the live Inbox contract;
- required fixed sections are present in the correct order;
- source/original coverage is complete for full capture;
- translation coverage is complete when translation is required;
- summary and insights are present and clearly separated from source fact;
- structured-source block counts/order match deterministic rendering evidence
  where applicable;
- beginning, middle, and final source ranges survive read-back;
- delegated runtime usage records a non-empty actual provider/model and reports
  `completed: true` and `failed: false`;
- green usage alone is never treated as proof of capture correctness.

If verification fails, the capture is incomplete. Do not relabel a partial result
as a full capture.

## References

- `references/default-full-capture-semantic-routing.md`
- `references/long-article-batch-translation.md`
- `references/x-article-structured-capture.md`
- `references/in-place-lightweight-upgrade.md`

## Pitfalls

- Do not promote while capturing.
- Do not treat a model name as part of the Inbox contract.
- Do not turn a short request into a lightweight capture unless the restriction is
  explicit.
- Do not replace a broken mechanical gate with prose-only instructions.
- Do not read or enumerate protected no-touch Inbox subtrees.
- Do not use a worker's self-report as the only completeness check.
- Do not create temporary payload/audit files inside the knowledge root merely for
  convenience.
- Do not invent unavailable source content or metadata.
