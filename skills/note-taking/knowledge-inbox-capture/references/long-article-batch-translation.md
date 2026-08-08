# Long-Article Batch Stage A Protocol

Use this reference when a full article is larger than roughly 200 source blocks or 20,000 rendered characters, or when the selected Stage A executor previously stopped with a generic “cannot reliably complete” report.

## Execution contract

1. The selected Stage A executor is authoritative for the isolated capture task. If the active main brain is at or below `GPT-5.6-luna max`, it executes the task in the main session; if it is higher, the active main brain assigns exact `GPT-5.6-luna max` through the configured model dispatch path. No Terra role is part of this contract; if the selected execution path is unavailable, stop.
2. Use the source's structured payload in memory or through a pipe. Do not create temporary HTML, JSON, Markdown, image, manifest, cache, or other files outside the one allowlisted final Inbox Markdown.
3. Deterministically render every source block first. Preserve source order, headings, lists, links, code, quotes, cover/body media, embedded posts, and explicit placeholders for unknown atomic blocks.
4. The selected Stage A executor must process the source and translate in ordered ranges. Start with a manageable batch (for example 20–40 blocks); if a tool/context/output call is too large, shrink to 10 or 5 blocks and continue. The same executor must render, translate, summarize, assemble, and write the one final allowlisted path. Do not switch to Terra, another worker, or an unranked fallback. Multiple ordered writes or patches to the same final allowlisted path are allowed while constructing the artifact.
5. A block count, character count, latency, or generic self-assessment is not a valid stop reason. A blocker must identify a concrete source/parser/translation-tool/context/output/runtime error, the batch sizes attempted, and the processed ranges. Do not substitute a preview, summary, or partial translation.
6. Before success, the selected executor must check frontmatter, fixed section order, source and translation marker coverage, and beginning/middle/final content. The main session then verifies selected-executor runtime usage and deterministic source evidence; it must not replace the executor's semantic source processing, translation, summary, or insights.

## In-place upgrade safety

When a previously created lightweight intake is upgraded to a full capture under Roy's default material-to-Inbox contract or an explicit full-capture request:

- Confirm the current request semantically requires the default full material capture or explicitly requests full capture before overwriting; do not require a fixed phrase such as “in-place upgrade”.
- Move the existing lightweight file to a rollback backup outside `knowledge/`; do not put the backup in the worker read allowlist.
- Keep the write allowlist as the original single target path; do not create `-full`, `-v2`, or a second source file.
- If the worker stops, usage is green without a valid artifact, or deterministic verification fails, restore the backup and report that the upgrade did not complete.
- Delete the backup and packet only after the final artifact passes verification; retain the usage audit outside `knowledge/`.

## Main-session verification recipe

Keep the payload and checks in memory. At minimum:

1. Read the selected executor usage/evidence and require the exact active-main-brain identity/completion when it executes directly, or the exact `GPT-5.6-luna max` model/provider/completion when it is assigned. Green runtime status alone does not prove a valid capture or correct Stage A routing.
2. Fetch the structured source payload after dispatch and assert the renderer's `blocks_total == blocks_visited`.
3. Split the final file at the fixed section boundaries. Assert the translation and original sections each contain marker IDs `1..N` in order, where `N` is the source block count.
4. For every non-atomic source block with substantive text, verify a normalized source-text probe appears in the original section. Normalize only Markdown wrappers such as emphasis and link syntax; do not alter the file.
5. Read the beginning, middle, and final source ranges and the summary/insights tail. Confirm media/code/placeholders are retained and image-internal OCR limitations are disclosed.
6. Remove only the known packet and successful-upgrade rollback backup. Never enumerate or clean unrelated Inbox paths.

## Failure patterns and fixes

- **Temporary acquisition file trips the single-writer gate:** switch the request to an in-memory or pipe-based fetch/renderer; do not expand the write allowlist.
- **Worker stops because the article is long:** strengthen the packet with explicit ordered batch ranges and smaller-batch retries; do not accept the generic blocker.
- **Selected executor identity mismatch:** verify the model/provider from the active main session or configured `GPT-5.6-luna max` dispatch evidence; do not change to Terra or another unranked role.
- **Worker reports success but coverage is uncertain:** treat the report as unverified until usage, marker ranges, deterministic source probes, and beginning/middle/final read-backs pass.
