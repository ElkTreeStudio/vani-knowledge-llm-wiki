#!/usr/bin/env python3
"""Deterministically validate a read-only semantic-analysis slice result.

Usage:
  python validate_read_only_slice.py INPUTS.json RESULTS.json

The manifest is the complete allowlist. The script never writes or opens paths
other than the two JSON files and each manifest item's source_path.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter
from pathlib import Path

ITEM_KEYS = {
    "ordinal", "source_key", "conversation_id", "filename", "input_sha256",
    "suggested_source_subdir", "staging_kind", "suggested_target",
    "observation", "inference", "uncertainty", "source_locators", "reason",
}
TOP_KEYS = {"batch", "analysis_slice", "producer", "items"}
SAFE_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PAIR = re.compile(
    r"^Message (\d+)(?:\s*\(([0-9a-f-]+)\)|\s*/\s*Message ID\s+([0-9a-f-]+))(?:\s*/.*)?$"
)
SOURCE_PAIR = re.compile(
    r"(?m)^### Message (\d+)\n- Message ID: ([0-9a-f-]+)$"
)


def fail(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_read_only_slice.py INPUTS.json RESULTS.json")

    manifest_path, result_path = map(Path, sys.argv[1:])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    required_manifest_keys = {"batch", "count", "items"}
    missing_manifest_keys = required_manifest_keys - set(manifest)
    if missing_manifest_keys:
        errors.append(
            f"manifest missing required top-level keys: {sorted(missing_manifest_keys)}"
        )

    canonical_slice = manifest.get("analysis_slice")
    alias_slice = manifest.get("slice")
    if canonical_slice is not None and alias_slice is not None and canonical_slice != alias_slice:
        errors.append("manifest analysis_slice and slice conflict")
    manifest_slice = canonical_slice if canonical_slice is not None else alias_slice

    for key, value in (("batch", manifest.get("batch")),
                       ("analysis_slice/slice", manifest_slice),
                       ("count", manifest.get("count"))):
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"manifest {key} must be an integer")

    if set(result) != TOP_KEYS:
        errors.append(f"result top-level keys differ: {sorted(set(result) ^ TOP_KEYS)}")
    if result.get("batch") != manifest.get("batch"):
        errors.append("top-level batch does not reconcile")
    if result.get("analysis_slice") != manifest_slice:
        errors.append("top-level analysis_slice does not reconcile")
    if result.get("producer") != "hermes-agent-subagent":
        errors.append("unexpected producer")

    inputs = manifest.get("items", [])
    outputs = result.get("items", [])
    if len(outputs) != manifest.get("count") or len(outputs) != len(inputs):
        errors.append("item count does not reconcile")

    for position, (source, item) in enumerate(zip(inputs, outputs), 1):
        ordinal = source.get("ordinal", f"position-{position}")
        if set(item) != ITEM_KEYS:
            errors.append(f"ordinal {ordinal}: item schema keys differ")
        expected = {
            "ordinal": source.get("ordinal"),
            "source_key": source.get("source_key"),
            "conversation_id": source.get("conversation_id"),
            "filename": source.get("staged_markdown_filename"),
            "input_sha256": source.get("sha256"),
        }
        for key, value in expected.items():
            if item.get(key) != value:
                errors.append(f"ordinal {ordinal}: {key} does not reconcile")

        slug = item.get("suggested_source_subdir", "")
        if not SAFE_SLUG.fullmatch(slug):
            errors.append(f"ordinal {ordinal}: unsafe source slug")
        kind = item.get("staging_kind")
        target = item.get("suggested_target")
        if kind not in {"knowledge_candidate", "unclassified"}:
            errors.append(f"ordinal {ordinal}: invalid staging_kind")
        if kind == "knowledge_candidate" and not target:
            errors.append(f"ordinal {ordinal}: candidate lacks target")
        if kind == "unclassified" and target is not None:
            errors.append(f"ordinal {ordinal}: unclassified staging target must be null")

        source_path = Path(source["source_path"])
        source_bytes = source_path.read_bytes()
        actual_hash = hashlib.sha256(source_bytes).hexdigest()
        if actual_hash != source.get("sha256"):
            errors.append(f"ordinal {ordinal}: source hash mismatch")
        text = source_bytes.decode("utf-8")
        message_pairs = {int(n): uid for n, uid in SOURCE_PAIR.findall(text)}
        locators = item.get("source_locators", [])
        if not isinstance(locators, list) or not locators:
            errors.append(f"ordinal {ordinal}: source_locators must be a non-empty list")
        else:
            for locator in locators:
                if not isinstance(locator, str):
                    errors.append(f"ordinal {ordinal}: source locator is not a string")
                    continue
                match = PAIR.fullmatch(locator.strip())
                if not match:
                    errors.append(
                        f"ordinal {ordinal}: unrecognized source locator format"
                    )
                    continue
                number = int(match.group(1))
                uid = match.group(2) or match.group(3)
                if message_pairs.get(number) != uid:
                    errors.append(
                        f"ordinal {ordinal}: Message {number} / UUID pair is invalid"
                    )

    for key in ("ordinal", "source_key", "conversation_id", "filename"):
        values = [item.get(key) for item in outputs]
        duplicates = [value for value, n in Counter(values).items() if n > 1]
        if duplicates:
            errors.append(f"duplicate {key} values: {len(duplicates)}")

    result_mode = stat.S_IMODE(result_path.stat().st_mode)
    parent_mode = stat.S_IMODE(result_path.parent.stat().st_mode)
    if result_mode != 0o600:
        errors.append(f"result mode is {oct(result_mode)}, expected 0o600")
    if parent_mode != 0o700:
        errors.append(f"result parent mode is {oct(parent_mode)}, expected 0o700")

    if errors:
        fail(errors)

    kinds = Counter(item["staging_kind"] for item in outputs)
    print(
        json.dumps(
            {
                "status": "PASS",
                "count": len(outputs),
                "knowledge_candidate": kinds["knowledge_candidate"],
                "unclassified": kinds["unclassified"],
                "result": str(result_path.resolve()),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
