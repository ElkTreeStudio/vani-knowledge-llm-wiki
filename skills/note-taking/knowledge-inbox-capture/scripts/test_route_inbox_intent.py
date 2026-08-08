#!/usr/bin/env python3
"""Tests for the model-semantic Inbox decision validator."""

import builtins
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("route_inbox_intent.py")
SPEC = importlib.util.spec_from_file_location("route_inbox_intent", SCRIPT)
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)


class RouterTests(unittest.TestCase):
    def route(self, text, intent):
        return router.validate_model_intent(text, intent)

    def test_semantically_approved_url_is_packet_permitted_regardless_of_spelling(self):
        for request in (
            "請收錄進 Inbox https://example.com/article",
            "收錄inbox https://example.com/article",
            "收錄 Inbox https://example.com/article",
            "這篇留著：https://example.com/article",
        ):
            with self.subTest(request=request):
                result = self.route(request, "stage-a-inbox-only")
                self.assertEqual("stage-a-inbox-only", result["category"])
                self.assertTrue(result["packet_permitted"])

    def test_model_can_decline_inbox_intent_without_regex_override(self):
        result = self.route("讀得到嗎？https://example.com/article", "not-inbox-request")
        self.assertEqual("not-inbox-request", result["category"])
        self.assertFalse(result["packet_permitted"])

    def test_url_stage_a_requires_a_url(self):
        result = self.route("請收錄這個", "stage-a-inbox-only")
        self.assertEqual("stage-a-blocked-insufficient-source", result["category"])
        self.assertFalse(result["packet_permitted"])

    def test_lightweight_requires_payload(self):
        result = self.route("", "stage-a-inbox-only-lightweight")
        self.assertEqual("stage-a-blocked-insufficient-source", result["category"])

    def test_formal_promotion_is_not_packet_permitted(self):
        result = self.route("請正式入庫", "formal-promotion")
        self.assertEqual("formal-promotion", result["category"])
        self.assertFalse(result["packet_permitted"])
        self.assertEqual("formal-flow-required", result["write_allowlist_shape"])

    def test_serialized_output_is_byte_identical(self):
        first = router.canonical_json(self.route("保留 https://example.com/a", "stage-a-inbox-only"))
        second = router.canonical_json(self.route("保留 https://example.com/a", "stage-a-inbox-only"))
        self.assertEqual(first, second)
        self.assertEqual(first, json.dumps(json.loads(first), ensure_ascii=False,
                                           sort_keys=True, separators=(",", ":")))

    def test_validator_needs_no_filesystem_reads_or_writes(self):
        def forbidden_open(*args, **kwargs):
            raise AssertionError("validator must not open files")
        original_open = builtins.open
        builtins.open = forbidden_open
        try:
            result = self.route("存下這篇 https://example.com/a", "stage-a-inbox-only")
        finally:
            builtins.open = original_open
        self.assertTrue(result["packet_permitted"])

    def test_stage_a_prohibited_scopes_are_exact(self):
        expected = [
            "sources", "staging", "domains", "projects", "entities", "archive",
            "index", "log", "pipeline", "Inbox README", "frozen ZIP",
            "existing Inbox files", "audit artifacts", "extra workers",
        ]
        self.assertEqual(expected, self.route(
            "收錄inbox https://example.com/a", "stage-a-inbox-only")["prohibited_scopes"])


if __name__ == "__main__":
    unittest.main()
