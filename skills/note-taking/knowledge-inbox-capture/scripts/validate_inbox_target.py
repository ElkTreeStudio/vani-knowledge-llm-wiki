#!/usr/bin/env python3
"""Mechanically validate the single Inbox Markdown write target."""

import argparse
import re
import sys
from pathlib import Path


FILENAME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


def validate_target(knowledge_root, target, mode):
    raw_root = Path(knowledge_root).expanduser()
    raw_target = Path(target).expanduser()

    if not raw_root.is_absolute():
        raise ValueError("knowledge root must be an absolute path")
    if not raw_target.is_absolute():
        raise ValueError("target must be an absolute path")

    raw_inbox_root = raw_root / "inbox"
    if raw_inbox_root.is_symlink():
        raise ValueError("knowledge inbox root must not be a symlink")
    if raw_target.is_symlink():
        raise ValueError("target must not be a symlink")

    resolved_root = raw_root.resolve(strict=False)
    inbox_root = raw_inbox_root.resolve(strict=False)
    resolved_target = raw_target.resolve(strict=False)

    try:
        inbox_root.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            "resolved knowledge inbox must remain within the resolved knowledge root"
        ) from exc

    if resolved_target.parent != inbox_root:
        raise ValueError("target must be directly under the resolved knowledge inbox")
    if resolved_target.suffix != ".md":
        raise ValueError("target must use the .md suffix")
    if resolved_target.name == "README.md":
        raise ValueError("Inbox README is never a capture target")
    if not FILENAME_PATTERN.fullmatch(resolved_target.name):
        raise ValueError("target filename must match YYYY-MM-DD-short-slug.md")

    exists = resolved_target.exists()
    if mode in {"full", "lightweight"}:
        if exists:
            raise ValueError("new capture target already exists; use in-place-upgrade when authorized")
    elif mode == "in-place-upgrade":
        if not exists:
            raise ValueError("in-place-upgrade target must already exist")
        if not resolved_target.is_file():
            raise ValueError("in-place-upgrade target must be an existing regular non-symlink file")
    else:
        raise ValueError("unsupported capture mode")

    return resolved_target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=["full", "lightweight", "in-place-upgrade"],
    )
    args = parser.parse_args(argv)

    try:
        target = validate_target(args.knowledge_root, args.target, args.mode)
    except ValueError as exc:
        print("validate-inbox-target: {}".format(exc), file=sys.stderr)
        return 2

    print(str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
