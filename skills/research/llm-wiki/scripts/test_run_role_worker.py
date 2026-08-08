#!/usr/bin/env python3
"""Tests for the model-agnostic llm-wiki worker dispatcher."""

import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

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

    def test_planner_packet_is_read_only(self):
        packet = """operation_mode: promotion-plan
read allowlist: /tmp/source.md
write allowlist: none
stop conditions: stale input
"""
        worker.validate_planner_packet(packet)

        with self.assertRaises(ValueError):
            worker.validate_planner_packet(packet.replace("write allowlist: none", "write allowlist: /tmp/out.md"))

    def test_maintainer_audit_packet_is_read_only(self):
        packet = """operation_mode: audit-only
write allowlist: none
stop conditions: boundary expansion
"""
        worker.validate_maintainer_packet(packet)

    def test_maintainer_formal_write_requires_plan_gate_and_allowlist(self):
        packet = """operation_mode: formal-write
effective promotion plan: plan-123
policy gate: approved
write allowlist: /tmp/knowledge/page.md
stop conditions: stale hash
"""
        worker.validate_maintainer_packet(packet)

        with self.assertRaises(ValueError):
            worker.validate_maintainer_packet(packet.replace("policy gate: approved\n", ""))

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

    def test_usage_identity_is_optional_for_runtime_default_and_exact_when_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.json"
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


if __name__ == "__main__":
    unittest.main()
