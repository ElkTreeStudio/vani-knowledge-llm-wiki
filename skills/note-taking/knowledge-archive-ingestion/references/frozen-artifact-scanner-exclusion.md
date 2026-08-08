# Frozen artifact scanner exclusion

Use this pattern when an intake directory contains an archive or binary that the user has explicitly frozen for a later migration while allowing sibling Markdown or text records to be ingested now.

## Contract

Define one canonical root-relative path for every frozen artifact. The scanner must compare the computed root-relative path against an exact exclusion set **before** symlink, file-type, size, stat-derived metadata, content-open, or hash logic.

Do not exclude by basename or extension: that can silently hide unrelated files. A frozen `inbox/export.zip` must not suppress `archive/export.zip`, `inbox/export.zip.bak`, or `inbox/other.zip`.

Directory traversal may observe an entry name to perform the exact comparison, but the excluded file itself must not be opened, hashed, moved, renamed, parsed, extracted, indexed, or inspected for archive members. Describe this distinction clearly when the user says to “ignore” the archive.

## Minimal implementation shape

```python
EXCLUDED_RELATIVE_FILES = {"inbox/export.zip"}

relative = Path(entry.path).relative_to(root_path).as_posix()
if relative in EXCLUDED_RELATIVE_FILES:
    continue
# only now perform symlink/type/content/hash handling
```

Keep the exclusion in the shared iterator used by manifest, lint, and link tools so every full-root gate receives the same inventory.

## Tests

Use only synthetic ordinary files under `tempfile`; never use the real frozen artifact as a fixture.

RED/GREEN coverage should prove:

- the exact root-relative path is absent;
- the same basename in another directory remains visible;
- a similar filename remains visible;
- another archive in the same directory remains visible;
- existing sorting, excluded-directory, and symlink-rejection behavior is unchanged.

After implementation, run the targeted scanner test and the validator/script suite. Then a full-root gate may run only if all consumers route through the corrected shared iterator.

## Operational pitfall

If governance prose already says the scanner must exclude the artifact but code still inventories or hashes it, treat this as a blocker rather than weakening the user’s freeze instruction. Correct the scanner contract first, with backup and tests, then resume the original ingestion ticket without widening its content scope.
