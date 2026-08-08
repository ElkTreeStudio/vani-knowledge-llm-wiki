# Generated Markdown as canonical source with an external archive

Use this migration pattern when authority explicitly keeps an upstream export/archive outside the knowledge root but makes each deterministic per-item Markdown an immutable canonical source.

## Sidecar contract

Keep the exact sidecar function:

```text
sidecar_path = payload_path + '.source.md'
```

A generated Markdown may be `record_kind: canonical_source` only with all of:

- original conversation/item ID;
- upstream archive absolute location outside the knowledge root;
- upstream archive whole-file SHA-256;
- deterministic converter name, version, and parameters;
- source Markdown whole-file SHA-256, equal to the normal payload hash;
- `media_type: text/markdown`;
- `immutable: true`;
- the explicit authority decision.

Do not relabel existing deterministic projections or legacy records. Preserve their linkage, path, and hash checks.

## Minimum migration sequence

1. Read the live source governance, raw-source schema, import prompt, strict linter/tests, migration-manifest contract, import-run contract, and append-only maintenance log.
2. Create a fresh whole-tree baseline manifest outside the knowledge root.
3. Snapshot exact protected sets (for example Inbox files and existing source payloads) for pre/post comparison.
4. Immediately before every planned edit, create and read back a byte-exact external backup; use `0700` directories and `0600` files.
5. RED–GREEN tests must prove:
   - a complete synthetic canonical sidecar passes;
   - omission of each new field fails independently;
   - source-hash mismatch and an archive path inside the root fail;
   - deterministic-projection and legacy fixtures still pass.
6. Change only the minimum governance/schema/prompt/linter/test surfaces.
7. Add run, mapping, validation, rollback, and append-only maintenance evidence.
8. Run unit tests, strict lint, migration-link checks, fresh external manifest build/verify, exact backup read-back, and protected-set pre/post hash comparison.
9. Any non-zero gate stops subsequent writes and triggers the documented rollback.

## Tracked cache/bytecode pitfall

Tests that import edited Python modules can mutate tracked `__pycache__` files and silently expand a minimum-scope diff. Before testing, check whether generated/cache artifacts are present in the baseline manifest. Run final validation with bytecode writes disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest ...
PYTHONDONTWRITEBYTECODE=1 python3 path/to/linter.py ...
```

If a test already changed tracked bytecode, first JIT-back up its current bytes, restore the exact baseline bytes, and rerun every final gate with bytecode writes disabled. Do not accept derived-file drift merely because source tests pass.

## Final evidence

The final manifest diff should contain only intended governance surfaces and required run evidence—no source payload, Inbox, domain, or project changes. Report exact paths, commands, exit codes, key outputs, and any remediated side effect.
