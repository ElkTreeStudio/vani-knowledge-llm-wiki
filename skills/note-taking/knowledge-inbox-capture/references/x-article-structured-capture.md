# X Article structured capture

Use this reference when an X status links to a long-form X Article and the ordinary post text contains only a `t.co`/article URL or an empty preview.

## Retrieval order

1. Prefer the official X API/CLI when it is available and authorized. Request the `article` tweet field.
2. If the normal post-read surface does not expose the article body, a public structured embed endpoint may provide the article payload. Treat it as an acquisition fallback, not as independent verification. One observed endpoint is `https://api.fxtwitter.com/status/{tweet_id}`; verify HTTP success and that `tweet.article.content.blocks` exists before rendering.
3. When the status body is only a `t.co` URL, resolve it to record the canonical `https://x.com/i/article/{article_id}` URL, but keep the original status URL as `source_url` in Inbox metadata.
4. Preserve the canonical X status URL in Inbox metadata regardless of the acquisition endpoint.

A known structured shape is:

```text
tweet.article.title
tweet.article.preview_text
tweet.article.cover_media
tweet.article.content.blocks[]
tweet.article.content.entityMap[]
tweet.article.media_entities[]
```

### Entity and media normalization

Do not assume `entityMap` is a JSON object. One observed payload shape encodes it as a list of `{key, value}` records. Normalize it first:

```python
entity_map = {
    str(item["key"]): item["value"]
    for item in article["content"]["entityMap"]
}
```

For `MEDIA` atomic blocks, resolve `data.mediaItems[].mediaId` against `article.media_entities[].media_id`, then use `media_info.original_img_url` in Markdown. The article cover is separate from the body blocks; preserve `cover_media.media_info.original_img_url` explicitly near the title. This avoids silently losing screenshots, diagrams, parameter tables, or the cover while still visiting every source block.

## Deterministic Markdown rendering

Walk `content.blocks` in order:

- `header-one` → `# text`
- `header-two` → `## text`
- `header-three` → `### text`
- `unordered-list-item` → `- text`
- `ordered-list-item` → `1. text`
- `blockquote` → prefix each line with `> `
- `unstyled` → plain paragraph
- `atomic` → resolve its first `entityRanges[].key` through `entityMap`

Do not treat `entityRanges` as atomic-block-only metadata. Ordinary text blocks may use ranged `LINK` entities whose `data.url` contains the actual destination. Apply ranges by offset/length and preserve those destinations as Markdown links; otherwise resource lists can look complete while silently losing every URL. Apply inline style ranges only when fidelity requires them, but never discard link targets.

For an atomic entity:

- if `data.markdown` exists, emit it verbatim; this commonly contains fenced code blocks;
- if the entity type is `DIVIDER`, emit `---`;
- if the entity type is `TWEET`, read `data.tweetId` and preserve at minimum a stable link in source order: `https://x.com/i/status/{tweetId}`. If a structured post lookup is available, use it only to recover the author/display text; do not recursively ingest a linked long-form article unless Roy requested it;
- if the entity type is `MEDIA`, resolve and emit every referenced media item as described above;
- otherwise preserve an explicit placeholder rather than silently discarding unknown content.

Join rendered blocks with blank lines. Keep the source block order intact.

## Minimal completeness check

For a lightweight Inbox capture:

- record the number of source blocks while rendering;
- ensure all blocks were visited;
- read back the start of the file and each requested top-level section;
- confirm the final original-text paragraph or signature is present.

## Translation scope for embedded images

For a full capture under Roy's default contract or an explicit “完整翻譯” request, distinguish article text blocks from text embedded inside screenshots or diagrams:

- always preserve every media block in its original position;
- translate all substantive text blocks;
- if unique, decision-relevant content exists only inside an image, OCR and translate it when practical;
- otherwise disclose clearly that the prose is fully translated while image-internal text remains in the source language. Never silently call an image-omitting or image-untranslated capture “complete.”

Do not mistake social metrics, author profile metadata, or preview text for the article body. Do not claim third-party retrieval verifies the author's factual assertions; it only supplies the source text for capture.
