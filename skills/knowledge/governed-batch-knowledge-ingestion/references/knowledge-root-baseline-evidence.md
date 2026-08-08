# Knowledge-root baseline and protected-set evidence

Use this pre-write evidence pattern whenever a governed writer may modify a formal knowledge root.

## Required outputs

Write all evidence outside the knowledge root, normally as three `0600` JSON files in a `0700` worker directory:

- `root-pre-manifest.worker.json`: sorted regular-file inventory with `path`, `root_relative_path`, `byte_count`, `sha256`, and `mode`.
- `root-protected-set.worker.json`: exact opaque no-touch paths plus fixed control/metadata markers, each with `touched: false` and `inspection: not_performed` when probing is forbidden.
- `root-baseline-summary.worker.json`: counts, status, scope assertions, output hashes, raw errors, and reconciliation results.

## Exclusion ordering

Define the opaque set before traversal. Compare each lexical absolute path against the exact opaque set before `lstat`, `open`, hashing, parsing, indexing, symlink checks, or recursion. Directory traversal may observe an immediate entry name solely to perform that comparison, but must never descend into an excluded directory or inspect an excluded file.

Keep opaque exclusions exact-path only; never broaden them by basename, extension, or directory name. Conversely, if the contract says control artifacts such as `README.md` or `.DS_Store` are outside the payload baseline, define that as a fixed marker policy and apply it before metadata/content probes. Record every encountered marker path in the protected set instead of hashing it. Do not assume that excluding only the Inbox copies protects markers elsewhere in the root.

## Opaque-folder count reporting

A parent directory listing may observe an immediate entry name solely to compare its lexical absolute path with the exact opaque set. If the exact opaque directory entry is absent, record `file_count: 0` with an absence-by-parent-observation status; this does not require probing the target. If the entry is present, the no-touch boundary wins: do not enumerate descendants and record `file_count: null` or another explicit not-probed value. Never derive a requested count by weakening the protected-path rule. Counts for eligible, non-opaque folders should be grouped from the frozen manifest rather than obtained through a second unrestricted traversal. For allowed control-marker handling, use metadata-only inspection if needed and record `content_opened: false` and `hashed: false`.

If the scanner or report generator changes after an evidence run, discard that run as authoritative, create a new unique external producer run, regenerate and read back all artifacts, rerun source reconciliation, and recompute the manifest/artifact hashes.

## Scanner and reconciliation

Inventory only non-excluded regular files. Reject symlinks, special files, permission failures, read failures, and source changes; capture the raw error and set the evidence status to `blocked`. Hash with a no-follow open and compare pre/open/post file identity and size. Sort entries by root-relative path.

After the provisional manifest/protected set is written, read both back once and reconcile the listed source files once: manifest count and ordered item equality, source byte counts, modes, and SHA-256 values. Reconcile the protected set as well. A single mismatch is a blocker; never publish `PASS` with partial or stale evidence. Verify the external JSON modes and hashes, but do not create verification files inside the knowledge root.

The summary must explicitly state `knowledge_root_write_count: 0`, an empty modified-path list, zero opaque probes/reads/stats/hashes/parses/followed symlinks, and `semantic_judgment_performed: false`. Preparation artifacts are evidence only; they are not a writer run or proof of a knowledge-root transaction.

## Minimal reconciliation shape

```json
{
  "status": "PASS",
  "reconciliation": {
    "performed_once": true,
    "manifest_items_equal_scan_items": true,
    "read_back_manifest_count": 0,
    "source_hash_count_matching": 0,
    "source_hash_mismatches": []
  },
  "scope": {
    "knowledge_root_write_count": 0,
    "knowledge_root_modified_paths": [],
    "opaque_paths_probed": 0,
    "semantic_judgment_performed": false
  },
  "raw_errors": []
}
```
