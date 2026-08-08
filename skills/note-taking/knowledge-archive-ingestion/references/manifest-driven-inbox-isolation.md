# Manifest-Driven Inbox Isolation

Use this pattern when a reviewed manifest classifies already-materialized archive Markdown and the user wants selected classes moved into restricted Inbox subdirectories **without ingestion, deletion, reclassification, or content edits**.

## Safety contract

- Treat the manifest as the sole classification authority. Map only explicitly approved class values to destinations; leave every other class in place.
- Verify the stated Inbox baseline using the producer's exact digest convention before creating destinations or moving anything. Do not invent a new tree-hash convention when a generating script or ledger defines one.
- Require unique stable source keys and unique staged filenames, safe basename-only paths, exact expected class counts, and one regular source file per manifest row.
- Refuse pre-existing destination directories, destination files, backup files, unsafe names, symlinks, unexpected root entries, or a baseline mismatch.
- Snapshot `README.md` and non-target knowledge files before the transaction so unchanged scope can be proved afterward.
- Keep all work local and content-preserving. Do not invoke scanners, embeddings, importers, indexers, or semantic review during an isolation-only ticket.

## Transaction sequence

1. Create a restricted evidence root (`0700`) outside the knowledge tree.
2. Record a preflight JSON containing manifest hash/counts, class counts, source baseline digest, filename/source-key uniqueness checks, README hash, and a digest of non-target knowledge files.
3. Create the external rollback-copy directory and requested Inbox destination directories as `0700`; require them to be absent first.
4. For every file that will move:
   - read the regular source without following symlinks;
   - record byte count and SHA-256;
   - copy exact bytes to `<evidence>/backups/<original-relative-path>` using exclusive creation;
   - set the backup to `0600`;
   - reread the backup and require identical byte count and SHA-256.
5. Write a rollback mapping before moving anything. Each row must include source key, class, source, destination, backup, byte count, and SHA-256.
6. Only after **all** backups verify, move each source with a same-filesystem atomic rename. Refuse destination collisions immediately before each rename and reread the destination afterward.
7. If any move or verification fails, rename already-moved files back in reverse order. Preserve backups and write the original exception plus rollback errors to restricted evidence. Never infer rollback success.

Backing up the full move set before the first rename gives a clean transaction boundary: backup failure causes no knowledge-tree mutation, while later move failure has both reverse-renames and verified external copies available.

## Direct acceptance gate

Mechanically verify once, then stop:

- requested destination counts and root keep count are exact;
- each manifest source exists in exactly one allowed live location;
- every keep file remains at the Inbox root;
- every moved file and rollback copy matches its recorded size and SHA-256;
- `README.md` is unchanged;
- non-target knowledge snapshot is unchanged;
- destination and backup directories are `0700` and payload/evidence files are `0600`;
- no error artifact exists on PASS;
- the validation JSON explicitly records `no_ingestion_performed: true`.

Save concise evidence under the restricted work root: `preflight.json`, `rollback-mapping.json`, `file-hashes.json`, `counts.json`, `validation.json`, and command/read-back logs. Reports should contain hashes, paths, counts, modes, and status—not archive bodies, titles, or sensitive text.

## Pitfalls

- `os.rename`/`os.replace` may overwrite on Unix. Check that every destination is absent immediately before rename; use a controlled, newly created destination directory and a single-writer transaction.
- A directory containing many files is not itself proof that backup completed. Require a per-file hash/size mapping and an exact final count.
- A successful producer exit is not acceptance. Run an independent read-back against live source/destination/backup paths.
- Do not call a move "safe" merely because it is reversible. Sensitive or large archive handling may require explicit authorization, restricted permissions, verified external copies, and a tested rollback path.
