#!/usr/bin/env python3
"""Tests for the model-agnostic llm-wiki worker dispatcher."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name("run-role-worker.py")
SPEC = importlib.util.spec_from_file_location("run_role_worker", SCRIPT)
worker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(worker)


class DispatcherTests(unittest.TestCase):
    def args(self, model=None, provider=None):
        return argparse.Namespace(model=model, provider=provider)

    def test_roles_are_governance_roles_not_model_aliases(self):
        self.assertEqual({"planner", "maintainer"}, set(worker.CONTRACTS))

    def test_runtime_default_requires_no_model_identity(self):
        worker.validate_runtime_selection(self.args())

    def test_explicit_model_and_provider_must_be_supplied_together(self):
        with self.assertRaises(ValueError):
            worker.validate_runtime_selection(self.args(model="example-model"))
        with self.assertRaises(ValueError):
            worker.validate_runtime_selection(self.args(provider="example-provider"))
        worker.validate_runtime_selection(
            self.args(model="example-model", provider="example-provider")
        )

    def test_planner_packet_is_read_only_and_allowlist_is_unique(self):
        packet = """operation_mode: promotion-plan
read allowlist: /tmp/source.md
write allowlist: none
stop conditions: stale input
"""
        worker.validate_planner_packet(packet)

        with self.assertRaises(ValueError):
            worker.validate_planner_packet(
                packet + "write allowlist: /tmp/out.md\n"
            )
        with self.assertRaises(ValueError):
            worker.validate_planner_packet(
                packet.replace("write allowlist: none", "write allowlist: /tmp/out.md")
            )
        with self.assertRaises(ValueError):
            worker.validate_planner_packet(
                packet.replace("write allowlist: none", "write allowlist:\nnone")
            )

    def test_maintainer_audit_packet_is_read_only_and_allowlist_is_unique(self):
        packet = """operation_mode: audit-only
write allowlist: none
stop conditions: boundary expansion
"""
        worker.validate_maintainer_packet(packet)
        with self.assertRaises(ValueError):
            worker.validate_maintainer_packet(
                packet + "write allowlist: /tmp/knowledge/page.md\n"
            )

    def test_maintainer_formal_write_requires_approved_gate_and_unique_allowlist(self):
        packet = """operation_mode: formal-write
effective promotion plan: plan-123
policy gate: approved
write allowlist: /tmp/knowledge/page.md
stop conditions: stale hash
"""
        worker.validate_maintainer_packet(packet)

        for invalid_gate in ("pending", "denied", "needs-owner"):
            with self.subTest(invalid_gate=invalid_gate):
                with self.assertRaises(ValueError):
                    worker.validate_maintainer_packet(
                        packet.replace("policy gate: approved", "policy gate: " + invalid_gate)
                    )

        with self.assertRaises(ValueError):
            worker.validate_maintainer_packet(
                packet + "write allowlist: /tmp/knowledge/other.md\n"
            )

    def test_runtime_default_command_does_not_pin_model_or_provider(self):
        args = argparse.Namespace(model=None, provider=None)
        command = worker.build_command(args, "prompt", Path("/tmp/usage.json"))
        self.assertNotIn("--model", command)
        self.assertNotIn("--provider", command)

    def test_explicit_runtime_selection_is_forwarded(self):
        args = argparse.Namespace(model="example-model", provider="example-provider")
        command = worker.build_command(args, "prompt", Path("/tmp/usage.json"))
        self.assertIn("--model", command)
        self.assertIn("example-model", command)
        self.assertIn("--provider", command)
        self.assertIn("example-provider", command)

    def test_usage_identity_is_required_even_for_runtime_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.json"

            for payload in (
                {"completed": True, "failed": False},
                {"completed": True, "failed": False, "model": "m"},
                {"completed": True, "failed": False, "provider": "p"},
                {"completed": True, "failed": False, "model": "", "provider": "p"},
            ):
                with self.subTest(payload=payload):
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaises(RuntimeError):
                        worker.load_and_verify_usage(path)

            path.write_text(
                json.dumps(
                    {
                        "completed": True,
                        "failed": False,
                        "model": "runtime-selected-model",
                        "provider": "runtime-selected-provider",
                    }
                ),
                encoding="utf-8",
            )

            data = worker.load_and_verify_usage(path)
            self.assertEqual("runtime-selected-model", data["model"])

            worker.load_and_verify_usage(
                path,
                expected_model="runtime-selected-model",
                expected_provider="runtime-selected-provider",
            )

            with self.assertRaises(RuntimeError):
                worker.load_and_verify_usage(
                    path,
                    expected_model="different-model",
                    expected_provider="runtime-selected-provider",
                )

    def test_default_usage_path_respects_hermes_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"HERMES_HOME": tmp}, clear=False):
                path = worker.default_usage_path()
                expected_parent = Path(tmp) / "worker-runs" / "llm-wiki"
                self.assertEqual(expected_parent, path.parent)
                self.assertTrue(path.name.startswith("worker-"))
                self.assertEqual(".json", path.suffix)


if __name__ == "__main__":
    unittest.main()
