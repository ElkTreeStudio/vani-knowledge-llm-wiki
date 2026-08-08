#!/usr/bin/env python3
"""Tests for the Inbox capture target validator."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("validate_inbox_target.py")
SPEC = importlib.util.spec_from_file_location("validate_inbox_target", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class InboxTargetTests(unittest.TestCase):
    def test_new_full_and_lightweight_targets_must_be_direct_new_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            inbox = root / "inbox"
            inbox.mkdir()

            full = inbox / "2026-08-09-example.md"
            self.assertEqual(full, validator.validate_target(root, full, "full"))
            self.assertEqual(full, validator.validate_target(root, full, "lightweight"))

            nested = inbox / "nested" / "2026-08-09-example.md"
            with self.assertRaises(ValueError):
                validator.validate_target(root, nested, "full")

            wrong_suffix = inbox / "2026-08-09-example.txt"
            with self.assertRaises(ValueError):
                validator.validate_target(root, wrong_suffix, "full")

            bad_name = inbox / "example.md"
            with self.assertRaises(ValueError):
                validator.validate_target(root, bad_name, "full")

    def test_new_capture_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            inbox = root / "inbox"
            inbox.mkdir()
            target = inbox / "2026-08-09-example.md"
            target.write_text("existing", encoding="utf-8")

            with self.assertRaises(ValueError):
                validator.validate_target(root, target, "full")
            with self.assertRaises(ValueError):
                validator.validate_target(root, target, "lightweight")

    def test_in_place_upgrade_requires_existing_regular_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            inbox = root / "inbox"
            inbox.mkdir()
            target = inbox / "2026-08-09-example.md"

            with self.assertRaises(ValueError):
                validator.validate_target(root, target, "in-place-upgrade")

            target.write_text("existing", encoding="utf-8")
            self.assertEqual(
                target,
                validator.validate_target(root, target, "in-place-upgrade"),
            )

    def test_in_place_upgrade_rejects_symlink_before_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            inbox = root / "inbox"
            inbox.mkdir()
            real_target = inbox / "2026-08-09-real.md"
            alias_target = inbox / "2026-08-09-alias.md"
            real_target.write_text("existing", encoding="utf-8")

            try:
                alias_target.symlink_to(real_target.name)
            except (OSError, NotImplementedError) as exc:
                self.skipTest("symlink creation unavailable: {}".format(exc))

            self.assertTrue(alias_target.is_symlink())
            with self.assertRaises(ValueError):
                validator.validate_target(root, alias_target, "in-place-upgrade")

    def test_target_must_be_absolute_and_readme_is_forbidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            inbox = root / "inbox"
            inbox.mkdir()

            with self.assertRaises(ValueError):
                validator.validate_target(root, Path("2026-08-09-example.md"), "full")
            with self.assertRaises(ValueError):
                validator.validate_target(root, inbox / "README.md", "full")


if __name__ == "__main__":
    unittest.main()
