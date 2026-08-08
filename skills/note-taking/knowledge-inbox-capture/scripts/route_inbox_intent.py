#!/usr/bin/env python3
"""Validate a model's semantic Inbox-routing decision without source I/O."""

import argparse
import json
import re
import sys


INBOX_CAPTURE_PROHIBITED_SCOPES = [
    "sources", "staging", "domains", "projects", "entities", "archive",
    "index", "log", "pipeline", "Inbox README", "frozen ZIP",
    "existing Inbox files", "audit artifacts", "extra workers",
]
PERMITTED_MODEL_INTENTS = {
    "inbox-only-full",
    "inbox-only-lightweight",
    "inbox-blocked-insufficient-source",
    "ambiguous-conflicting-intent",
    "formal-promotion",
    "not-inbox-request",
}
CAPTURE_INTENTS = {"inbox-only-full", "inbox-only-lightweight"}
URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def normalize_text(text):
    """Fold case and whitespace; never infer intent from token spelling."""
    return " ".join((text or "").casefold().split())


def _result(category, permitted, allowlist_shape, reason_code):
    return {
        "category": category,
        "packet_permitted": permitted,
        "write_allowlist_shape": allowlist_shape,
        "prohibited_scopes": list(INBOX_CAPTURE_PROHIBITED_SCOPES)
        if category in CAPTURE_INTENTS or category == "inbox-blocked-insufficient-source"
        else [],
        "reason_code": reason_code,
    }


def validate_model_intent(text, model_intent):
    """Validate an LLM's semantic decision; this is deliberately not a regex classifier."""
    if model_intent not in PERMITTED_MODEL_INTENTS:
        raise ValueError("unsupported model intent")

    normalized = normalize_text(text)
    has_url = bool(URL_PATTERN.search(normalized))

    if model_intent == "inbox-only-full":
        if not has_url:
            return _result(
                "inbox-blocked-insufficient-source",
                False,
                "none",
                "model-approved-full-capture-without-url",
            )
        return _result(
            "inbox-only-full",
            True,
            "single-new-inbox-markdown",
            "model-semantic-inbox-decision",
        )

    if model_intent == "inbox-only-lightweight":
        if not normalized:
            return _result(
                "inbox-blocked-insufficient-source",
                False,
                "none",
                "model-approved-lightweight-without-payload",
            )
        return _result(
            "inbox-only-lightweight",
            True,
            "single-new-inbox-markdown",
            "model-semantic-inbox-decision",
        )

    return _result(
        model_intent,
        False,
        "formal-flow-required" if model_intent == "formal-promotion" else "none",
        "model-semantic-non-capture-decision",
    )


def canonical_json(result):
    return json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="raw user request")
    parser.add_argument(
        "--model-intent",
        required=True,
        choices=sorted(PERMITTED_MODEL_INTENTS),
        help="semantic decision made by the active model",
    )
    args = parser.parse_args(argv)
    print(canonical_json(validate_model_intent(args.text, args.model_intent)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
