# Ordinary article-source promotion

Use this reference when authority explicitly reclassifies a bounded Inbox folder as ordinary newly delivered articles rather than an archive/export. The user’s explicit classification controls the semantic route for that folder; it does not waive byte, privacy, schema, rollback, or independent-verification gates.

## Decision matrix

| Input condition | Route |
|---|---|
| User says a named curated folder is ordinary articles and may enter the KB | Fresh article-source plan; no archive conversation profile; no external archive provenance requirement |
| A file outside the overridden folder has a mixed source/translation/notes body with no deterministic source boundary | Keep that ordinal blocked; do not broaden the folder override |
| Article payload contains an actual secret or fails the live source schema | Block that item; user classification cannot bypass safety/schema gates |
| User requests formal domain pages, synthesis, or indexes | Separate promotion plan and high-capability governance gate; do not fold it into source capture |

## Required plan transition

1. Preserve the frozen queue and the original planner output for audit history.
2. Record the user correction verbatim in a revised planner packet.
3. Generate a fresh plan for the affected ordinals only. Do not reuse an archive-specific provenance blocker after the correction.
4. If a model proposes a deterministic representation typo (for example, a sidecar path that does not equal `payload_path + '.source.md'`), preserve the raw plan and create a commander-normalized plan. Record raw-plan SHA-256, normalized-plan SHA-256, the exact changed field, and that scope/semantics were unchanged.
5. Revalidate queue coverage, source hashes, target absence, protected entries, and zero formal/staging/index targets before dispatching the writer.

## Article source and sidecar shape

For each accepted Markdown article:

- Copy/move the payload byte-for-byte to the live article-source target, normally `sources/articles/<stable-name>.md`.
- Use a sidecar at exactly `payload_path + '.source.md'`.
- Keep source identity deterministic, e.g. `source-article-<payload_sha256>`.
- A minimal sidecar frontmatter contract is:

```yaml
---
schema: raw-source
schema_version: 1.0.0
id: source-article-<sha256>
created: '<capture-date>'
updated: '<capture-date>'
status: captured
record_kind: canonical_source
captured_at: '<capture-timestamp>'
source_uri: file:///.../inbox/<original-relative-path>
media_type: text/markdown
payload_path: sources/articles/<stable-name>.md
payload_sha256: <payload-sha256>
immutable: true
---
```

Do not infer or invent conversation IDs, archive-member IDs, renderer metadata, or upstream archive hashes when the source is explicitly being treated as an ordinary article. Historical Inbox location may be recorded as `source_uri`; it is not proof of an upstream archive.

## Exact transaction delta

A bounded article-source transaction normally has this expected path delta:

- remove only the verified Inbox source paths;
- add one payload and one sidecar for each accepted source;
- add the import-run record files required by the live contract (`run.md`, `manifest.yaml`, `validation.json`, or the current equivalent);
- append one maintenance-log entry if required by the live contract;
- add zero formal pages, staging records, index files, or map changes.

Create external rollback copies before mutation. Verify each backup’s whole-file SHA-256, byte count, and mode. The writer’s `committed` result is only a producer state; independent read-back must verify source removal, payload bytes, sidecar fields, target paths, rollback copies, and exact root diff.

## Acceptance evidence

Run and preserve, outside the knowledge root where possible:

1. direct payload/sidecar read-back for every ordinal;
2. exact pre/post manifest comparison with no unexpected paths;
3. rollback manifest byte/hash/mode verification;
4. migration-manifest and import-run read-back;
5. targeted strict lint for changed paths;
6. full-root strict lint, tests, and migration-link checks.

If full-root strict lint reports errors whose paths are absent from the exact delta, prove they are unchanged by the pre/post manifest and report them as pre-existing unrelated blockers. Do not edit unrelated files or claim a green full-root gate. Likewise, if an ordinal remains blocked outside the explicitly overridden folder, report the accepted bounded batch separately from the unfinished queue.

The final report should distinguish:

- bounded article-source batch accepted;
- remaining Inbox items and their concrete blockers;
- pre-existing full-root governance blockers;
- evidence paths and hashes;
- whether any cloud backup/checkpoint was performed. Never imply that a local rollback manifest is a remote backup.
