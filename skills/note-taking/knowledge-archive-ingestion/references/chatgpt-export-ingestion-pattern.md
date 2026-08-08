# ChatGPT Export Ingestion Pattern — 2026-07

This reference records a successful privacy-first pattern for a modern sharded ChatGPT export. Treat counts and paths as examples, not universal constants.

## Export shape observed

- ZIP archive: about 119 MB
- 194 members
- 19 conversation shards rather than one `conversations.json`
- 1,887 conversations
- 17,406 message nodes
- 101 conversations indicated attachments
- Source archive SHA-256 was pinned before parsing

Safe reconnaissance checked CRC, Zip Slip paths, symlinks, suspicious compression ratios, member count/size, and shard parseability. Parsing was incremental; `extractall` was never used.

## Staging and selection funnel

1. Phase 1 manifest: 1,887 conversations; 309 sensitivity-flagged; 1,578 eligible for redacted synopsis generation.
2. Phase 2 residual gate: 16 rejected after credential-hardening; 1,562 redacted synopses emitted.
3. Durable-value synopsis review: 851 engineering/product candidates reviewed; 88 selected for transcript generation.
4. Full-transcript residual gate: 86 emitted; 2 quarantined.
5. Semantic/full-content review: 32 conversations retained, grouped into 19 reviewer clusters.
6. Cross-wiki normalization: 15 creates, 2 updates, 2 link-only actions; cross-wiki deduplication reduced this to 17 unique canonical destinations.

Creative and personal-other queues were deferred rather than bulk imported.

## Credential finding that required TDD

A generic service-token regex required separators and let standard separatorless keys pass. The regression set added explicit alternatives for:

- `AKIA` / `ASIA` plus 16 uppercase alphanumeric characters
- `AIza` plus the provider-allowed suffix
- mixed-alphanumeric opaque values in the 20–31 character range

The fix used finding-specific RED tests, a minimal regex/residual change, a full rebuild, byte-identical output comparison, and a fresh verifier. Residual rejects rose only from 14 to 16, suggesting the lower opaque threshold was not broadly destructive on this corpus.

Never print synthetic secret values in reports; report placeholder replacement, original-retention count, boundary lengths, and finding type.

## Body-only hash governance finding

Three wiki schemas described frontmatter body hashing ambiguously. Existing raw pages showed 17/18 already excluded the closing delimiter line ending; one metadata hash included it. The authorized correction:

- backed up all affected schemas/logs and the one raw page
- clarified LF/CRLF exclusion consistently
- changed only the exceptional raw's frontmatter hash
- proved its body byte-for-byte identical to backup
- appended correction logs
- reran all 18 hashes and synthetic LF/CRLF boundary fixtures

A frontmatter example also used a taxonomy group name (`core`) as though it were a legal tag; it was replaced by an allowed tag.

## Deterministic raw Markdown staging pattern

For a user-authorized one-conversation-per-Markdown staging pass, do not spend one model call per conversation. Use one bounded producer to build a stdlib converter, then process the archive mechanically.

Required gates:

1. Pin the archive SHA-256 and CRC before rendering; reject Zip Slip paths, symlinks, malformed shards, duplicate/missing source identities, suspicious member sizes/ratios, and destination collisions.
2. Treat standard `conversations-NNN.json` records and separate `codex.json` records as distinct source types. `shared_conversations.json` may only describe existing conversations; prove overlap before deciding it creates no additional document.
3. Traverse the complete standard mapping graph deterministically from all roots, verify every mapping node is reachable, and prove every non-null message object is emitted exactly once. Do not derive the source count from the traversal itself because disconnected nodes could otherwise be silently omitted.
4. Preserve raw string parts byte-for-byte inside adaptive Markdown fences. Render non-string parts, attachment references, and Codex input/output items as deterministic canonical JSON so unsupported structures remain explicit and reversible. Add role, raw and localized timestamps, parent identity, and branch path outside original content.
5. Use source identity—not title—as the uniqueness key and filename suffix. Store archive provenance, renderer version, branch method, and a body-byte SHA-256 in every document.
6. Render into a restricted external staging directory (`0700`, files `0600`), rerender cleanly, and require byte-identical documents. Publish only after source-key coverage, message/turn counts, raw payload hashes, body hashes, and tests pass.
7. Independently recompute payload hashes from the archive and compare them to the manifest. A verifier that only compares emitted-object counts or Markdown markers is not sufficient evidence for text preservation.
8. After final destination read-back, move the archive byte-for-byte to the user-authorized external archive location and verify its hash before removing temporary staging. Keep manifests/tests outside the knowledge root; the Inbox should contain only the staged Markdown intended by the user.

Before promotion, a conservative deterministic filter can produce three report-only classes: `keep`, `exclude_candidate`, and `review`. Preserve all raw Markdown in place until the user approves disposition; candidates are not deletions. Keep titles and paths in a local restricted manifest rather than a shared-chat report. Automatic exclusion should be limited to empty/greeting-only records or explicit short translation-only records with no durable signals; route borderline records to review.

Translation and durable-context lexicons must cover the corpus languages. For Traditional/Simplified Chinese, test markers such as `翻成`, `幫我翻`/`帮我翻`, `請翻`/`请翻`, `怎麼說`/`怎么说`, and social-post terms such as `社群`, `貼文`/`贴文`, `推文`, `限動`, `文案`, and `字幕`; also include Chinese project/decision/research/troubleshooting terms so short durable records are not false exclusions. Pin an Inbox tree digest before screening and require it to remain unchanged after two byte-identical report runs.

## External-agent envelope lessons

Claude Code auth status alone was not treated as readiness. A one-turn probe with tools disabled had to return the exact sentinel and a successful JSON envelope.

Observed CLI/version lesson:

- inspect `claude --version` and `claude --help`
- do not assume optional output-file flags exist
- redirect JSON stdout to a restricted file and parse `result`

Observed terminal states must be handled distinctly:

- `error_max_turns`: files may be partially written
- `aborted_streaming` after host timeout: files may be materially complete but governance steps unfinished
- `api_error_status: 429` with reset time: stop later calls instead of repeatedly consuming attempts
- process exit 0 is not enough; require `is_error=false`, `terminal_reason=completed`, and an explicit verdict/result

Twelve turns were insufficient for multi-file read-only semantic verifiers; 18–19 turns were actually required in two cases. Producer prompts with broad read/write/check duties could exceed 30 turns. Prefer narrower producer tickets, reuse deterministic evidence, and reserve the stronger model for semantic verification.

## Partial-output rollback pattern

When three producer sessions ended non-successfully:

1. Compare current index/log bytes to the per-ticket baseline backup.
2. Enumerate only the ticket's new-file allowlist.
3. Inspect raw hashes and placeholder metadata without trusting producer summaries.
4. Move new, unregistered partial files into a `0700` quarantine tree; set files `0600` and write a hash manifest.
5. If index was changed but log was not appended, preserve the partial index in quarantine and restore the verified baseline index.
6. Verify canonical root counts and paths match the last fully passed ticket.
7. Resume later from quarantine drafts only after rechecking baseline hashes immediately before writing.

Do not delete partials merely for cleanliness; preserving them prevents expensive re-reading and supports forensic comparison.
