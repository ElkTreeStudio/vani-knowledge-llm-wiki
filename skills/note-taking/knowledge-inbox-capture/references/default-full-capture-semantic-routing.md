# Default full-capture semantic routing and verification

Use this reference for every request that may convert Roy-provided material into the Knowledge Inbox.

## Semantic routing contract

1. Decide from the complete request context whether Roy wants the supplied material converted, preserved, or captured in Inbox. This is a semantic decision, not a keyword, phrase, regex, or spelling decision.
2. If the semantic intent is material-to-Inbox capture, choose `stage-a-inbox-only` by default.
3. The default full capture preserves all obtainable source content / all supplied content, translates it into natural Taiwan Traditional Chinese when the source is not already Taiwan Traditional Chinese, and adds `Vani 摘要` plus `Vani 心得與延伸見解` (summary and explanation/insights).
4. `stage-a-inbox-only-lightweight` is valid only when the current request explicitly asks for a lightweight intake, metadata-only preservation, no source fetch, no translation, no summary, or an equivalent restriction. Do not infer lightweight from a short message, a bare link, or an ordinary Inbox request.
5. A request to capture the same material again is not a new file. If the existing artifact is complete, stop. If it is lightweight and the current semantic intent is the default full capture, use the rollback-backed in-place upgrade flow.

## Stage A packet requirements and translation routing

- State the semantic intent and `intent_router_result` explicitly.
- Keep the write allowlist to the one final Inbox Markdown path.
- For long or structured sources, require in-memory / pipe acquisition, deterministic source rendering, ordered Stage A batches by the selected executor, and concrete stop conditions. If the active main brain is at or below `GPT-5.6-luna max`, it executes; if it is higher, it assigns `GPT-5.6-luna max`; no Terra executor or fallback is permitted. Do not create payload, manifest, renderer, or rollback files inside the knowledge tree.
- Explicitly prohibit reads/writes to protected Inbox subtrees, Frozen ZIP, unrelated existing files, packet, usage audit, and rollback.
- The parent session verifies the artifact independently, including selected translation model/completion evidence; a green worker self-report or usage record is not sufficient.

## Structured-source verification recipe

For X Article or similar block sources:

1. Fetch the structured payload directly and require the expected source object and block list.
2. Deterministically render every source block in order. Require `blocks_total == blocks_visited`.
3. Require both the source/original and translation sections to carry marker IDs `1..N` in order, with no empty block segments.
4. Compare source probes after normalizing only Markdown wrappers (blockquote prefixes, list prefixes, link wrappers, emphasis/code markers, and whitespace). Do not alter the underlying source text.
5. Verify cover/body media URLs, code, embedded posts, and explicit placeholders for unknown entities are retained.
6. Parse fixed top-level sections using exact section delimiters such as `## Vani 摘要` and `## Vani 心得與延伸見解`; do not terminate at nested `##` headings inside the translated/original material.
7. Require non-empty summary and explanation/insights, explicit disclosure of any image-internal OCR/translation limitation, exact model/provider usage, `completed: true`, `failed: false`, and successful beginning/middle/final read-back.

## Failure patterns captured from the routing correction

- A short request or bare URL is not evidence of lightweight intent.
- The phrase used by the user is not itself the classifier; the active model must understand the requested operation from the whole message.
- A parser that treats every Markdown `##` as a fixed section boundary will truncate article headings and falsely report missing coverage; use the known fixed section headings.
- Raw source-text probes can falsely fail on deterministic Markdown wrappers; normalize wrappers only, then re-check the lexical source content.
- Do not delete a lightweight rollback until source coverage, translation coverage, summary, insights, and runtime usage have all passed independent verification.
