#!/usr/bin/env python3
"""Deterministically render an FxTwitter X Article payload to Markdown.

Usage:
    python3 render_fxtwitter_x_article.py payload.json article.md manifest.json

The input must be the JSON returned by https://api.fxtwitter.com/status/<tweet_id>.
The renderer preserves block order, ranged links, the cover image, media, embedded
tweet links, code/markdown entities, dividers, and explicit placeholders for
unknown or empty atomic blocks. It does not translate or summarize content.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def normalize_entity_map(raw: Any) -> dict[str, dict[str, Any]]:
    if isinstance(raw, list):
        return {str(item["key"]): item["value"] for item in raw}
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items()}
    return {}


def apply_links(text: str, ranges: list[dict[str, Any]], entity_map: dict[str, dict[str, Any]]) -> str:
    """Apply DraftJS LINK ranges from right to left to preserve offsets."""
    replacements: list[tuple[int, int, str]] = []
    for item in ranges:
        entity = entity_map.get(str(item.get("key")), {})
        if entity.get("type") != "LINK":
            continue
        start = int(item.get("offset", 0))
        end = start + int(item.get("length", 0))
        url = entity.get("data", {}).get("url")
        if url and 0 <= start <= end <= len(text):
            replacements.append((start, end, url))
    for start, end, url in sorted(replacements, reverse=True):
        text = text[:start] + f"[{text[start:end]}]({url})" + text[end:]
    return text


def render(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    tweet = payload["tweet"]
    article = tweet["article"]
    content = article["content"]
    blocks = content.get("blocks", [])
    entity_map = normalize_entity_map(content.get("entityMap", {}))
    media_map = {
        str(item.get("media_id")): item
        for item in article.get("media_entities", [])
    }

    out: list[str] = []
    unknown: list[dict[str, Any]] = []

    cover = article.get("cover_media", {}).get("media_info", {}).get("original_img_url")
    if cover:
        out.append(f"![Article cover image]({cover})")

    for index, block in enumerate(blocks):
        block_type = block.get("type", "unstyled")
        text = apply_links(block.get("text", ""), block.get("entityRanges", []), entity_map)

        if block_type == "header-one":
            rendered = f"# {text}"
        elif block_type == "header-two":
            rendered = f"## {text}"
        elif block_type == "header-three":
            rendered = f"### {text}"
        elif block_type == "unordered-list-item":
            rendered = f"- {text}"
        elif block_type == "ordered-list-item":
            rendered = f"1. {text}"
        elif block_type == "blockquote":
            rendered = "\n".join(f"> {line}" for line in text.splitlines())
        elif block_type == "unstyled":
            rendered = text
        elif block_type == "atomic":
            ranges = block.get("entityRanges", [])
            entity = entity_map.get(str(ranges[0].get("key"))) if ranges else None
            entity_type = entity.get("type") if entity else None
            data = entity.get("data", {}) if entity else {}

            if data.get("markdown"):
                rendered = data["markdown"].rstrip()
            elif entity_type == "DIVIDER":
                rendered = "---"
            elif entity_type == "TWEET":
                tweet_id = data.get("tweetId")
                rendered = (
                    f"[Embedded X post](https://x.com/i/status/{tweet_id})"
                    if tweet_id
                    else "[Unresolved block: TWEET without tweetId]"
                )
            elif entity_type == "MEDIA":
                media_lines: list[str] = []
                for media_item in data.get("mediaItems", []):
                    media_id = str(media_item.get("mediaId"))
                    media = media_map.get(media_id, {})
                    url = media.get("media_info", {}).get("original_img_url")
                    media_lines.append(
                        f"![Article media]({url})"
                        if url
                        else f"[Unresolved media: {media_id}]"
                    )
                rendered = "\n\n".join(media_lines) or "[Unresolved block: MEDIA without mediaItems]"
            else:
                rendered = f"[Unresolved block: atomic entity={entity_type or 'missing'}]"
                unknown.append(
                    {
                        "index": index,
                        "entity_type": entity_type,
                        "data_keys": sorted(data.keys()),
                    }
                )
        else:
            rendered = f"[Unresolved block type: {block_type}]\n\n{text}"
            unknown.append({"index": index, "block_type": block_type})

        out.append(rendered)

    markdown = "\n\n".join(out).strip() + "\n"
    manifest = {
        "title": article.get("title"),
        "article_id": article.get("id"),
        "article_created_at": article.get("created_at"),
        "tweet_id": tweet.get("id"),
        "tweet_created_at": tweet.get("created_at"),
        "author": tweet.get("author", {}).get("name"),
        "handle": tweet.get("author", {}).get("screen_name"),
        "blocks_total": len(blocks),
        "blocks_visited": len(blocks),
        "entity_count": len(entity_map),
        "unknown": unknown,
        "cover": cover,
        "rendered_characters": len(markdown),
        "rendered_lines": markdown.count("\n"),
    }
    return markdown, manifest


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: render_fxtwitter_x_article.py payload.json article.md manifest.json", file=sys.stderr)
        return 2

    payload_path, markdown_path, manifest_path = map(Path, sys.argv[1:])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    markdown, manifest = render(payload)
    markdown_path.write_text(markdown, encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
