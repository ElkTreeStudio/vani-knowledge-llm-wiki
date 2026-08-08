# Raw-source metadata sidecar contract pattern

Use this pattern when a canonical payload remains byte-immutable and metadata lives in a neighboring Markdown/YAML sidecar.

## Contract

Define one unambiguous root-relative formula:

```text
sidecar_path = payload_path + '.source.md'
```

Appending to the full payload path preserves every filename extension and automatically enforces co-location. Examples:

- `sources/articles/example.html` → `sources/articles/example.html.source.md`
- `sources/articles/x.md` → `sources/articles/x.md.source.md`

Do not derive from `Path.stem`, compare only basenames, or accept a sidecar in another directory.

## Linter sequence

1. Parse only the supported metadata layer and retain the sidecar's actual root-relative path from the filesystem walk.
2. Validate `payload_path` as a canonical, root-relative, traversal-free POSIX path.
3. In strict mode compute `expected = payload_path + '.source.md'` and compare it byte-for-byte with the actual sidecar path.
4. On mismatch emit both `expected` and `actual`; do not silently normalize either value.
5. Continue enforcing pre-existing gates: payload is an existing regular file, symlinks are rejected according to repository policy, payload hash matches, and schema/lifecycle rules pass.
6. Keep transitional-mode compatibility explicit rather than weakening strict behavior.

## Regression-test matrix

Use only synthetic temporary fixtures and ordinary payload bytes:

| Case | Result |
|---|---|
| `example.html` + `example.html.source.md` | pass |
| `x.md` + `x.md.source.md` | pass |
| `example.html` + `example.source.md` | fail with expected/actual |
| nested payload + correct basename sidecar at root | fail |
| payload and sidecar in different directories | fail |

Run the narrow test before implementation and record the expected RED caused by the missing contract. After implementation, rerun the same command for GREEN, then run the repository's bounded regression suite once.

## Change-safety checklist

- Back up every existing file immediately before editing when repository policy requires it; preserve relative paths and write SHA-256 sums.
- Keep test fixtures away from real archives and frozen source artifacts.
- Read back the changed schema, documentation, linter, and tests with line references.
- Report the exact RED/GREEN commands and key outputs.
- Verify changes stayed within the explicit allowlist; do not broaden into ingestion or whole-corpus gates unless authorized.
