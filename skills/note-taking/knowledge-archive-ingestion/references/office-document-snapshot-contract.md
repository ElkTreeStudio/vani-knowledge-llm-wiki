# Office-document snapshot ingestion contract

Use this reference when a user submits a bounded set of office files (for example DOCX, XLSX, XLSM, PPTX, PDF) as the authoritative state of a project at a named point in time and wants future comparisons.

## Why this needs a distinct preflight

A generic raw-source sidecar schema can record a binary payload hash, but it does **not** by itself authorize either:

- a new canonical source taxonomy/path for office documents; or
- a deterministic, reproducible text projection suitable for search and later semantic review.

Do not classify a document as an `article` merely from its filename or extension. First confirm that the target knowledge base has an approved document-source profile and canonical directory. If either the taxonomy, converter contract, or applicable importer is absent, stop before any formal `sources/`, `staging/`, or `projects/` write and request explicit authority to extend the governance contract.

## Required source-set preflight

1. Treat the supplied directory as an immutable source set. Do not move, rename, modify, or delete it.
2. Build a machine-generated, sorted manifest with one entry per ordinary file:
   - root-relative path;
   - byte size;
   - source filesystem mtime (metadata only; never the snapshot authority);
   - whole-file SHA-256.
3. Record two separate times:
   - `snapshot_label` / `as_of_date`: the user-declared business cutoff; and
   - `ingested_at`: actual UTC admission time.
4. Verify the manifest through a byte-level program or exact hash comparison. Do not ask an LLM to manually transcribe or compare hashes; truncated/copy errors are not source drift.
5. Refuse symlinks, unexpected files, source-manifest drift, unknown ownership, or unhandled sensitive/secret material before planning a write.
6. Assess sensitivity by category only in reports. Keep full business, personnel, compensation, account, customer, schedule, and contract data in the restricted corpus; do not echo values into chat or public summaries.

## Contract required before an office-file write

The approved document-source profile must define all of the following before a writer starts:

- canonical payload path and exact extension-preserving `.source.md` sidecar path;
- allowed media types and immutable whole-file hash fields;
- approved extraction method for each file type, including converter name, version, parameters, and failure handling;
- deterministic projection path and sidecar linkage to the canonical payload hash;
- a non-executing policy for macro-enabled files (XLSM must be treated as opaque input; extract values/metadata without running macros);
- reproducibility tests: same payload + same tool version + same parameters produces identical projection bytes;
- importer, dry-run, apply, manifest, schema, path/link, and rollback gates.

A raw binary payload may be preserved only within an approved canonical document-source profile. A readable projection is a derivative, not a second source and never a replacement for the original bytes.

## Formal project publication boundary

Only after the payload, sidecar, projection, and import-run gates pass may a project receive concise formal navigation/provenance pages. Those pages must:

- explicitly mark draft/unverified source status;
- link to source IDs/hashes rather than reproduce unsupported claims;
- distinguish current source facts from assumptions and unresolved conflicts;
- state the snapshot label and actual ingestion timestamp;
- remain within the target project-note schema and promotion authority.

A user request to import the material authorizes the ingestion objective, but does not implicitly authorize inventing or changing canonical source schemas, converters, or import enforcement. Obtain explicit approval for that governance change.

## Successor snapshot comparison

For every later source set, create a new immutable snapshot directory/record and full manifest. Compare manifests deterministically by root-relative path and whole-file hash:

- path present only in newer manifest → added;
- path present only in older manifest → removed;
- path present in both with differing hash → changed (including same-name/different-content);
- path present in both with equal hash → unchanged.

Never overwrite an earlier payload, sidecar, projection, project provenance, or manifest. A later snapshot may supersede a project note according to its schema, but must retain the predecessor link and preservation evidence.
