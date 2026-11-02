"""Unit tests for the lesson catalog's integrity checks."""

import tempfile
import unittest
from pathlib import Path

from verify_examples import VerificationError, discover_examples


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.examples = Path(self.workspace.name) / "examples"
        (self.examples / "01-basics").mkdir(parents=True)

    def add_lesson(self, stem: str = "01-hello") -> None:
        root = self.examples / "01-basics"
        (root / f"{stem}.srp").write_text('print("hello");\n', encoding="utf-8")
        (root / f"{stem}.stdout").write_text("hello\n", encoding="utf-8")

    def test_valid_catalog(self):
        self.add_lesson()
        pairs = discover_examples(self.examples)
        self.assertEqual(len(pairs), 1)
        self.assertTrue(pairs[0][0].name.endswith(".srp"))

    def test_missing_fixture(self):
        (self.examples / "01-basics" / "01-hello.srp").write_text("print(1);")
        with self.assertRaisesRegex(VerificationError, "missing fixtures"):
            discover_examples(self.examples)

    def test_orphan_fixture(self):
        self.add_lesson()
        (self.examples / "01-basics" / "02-extra.stdout").write_text("orphan")
        with self.assertRaisesRegex(VerificationError, "orphaned fixtures"):
            discover_examples(self.examples)

    def test_support_modules_are_not_lessons(self):
        self.add_lesson()
        folder = self.examples / "01-basics" / "_support"
        folder.mkdir()
        (folder / "helper.srp").write_text("pub bind x = 1;")
        self.assertEqual(len(discover_examples(self.examples)), 1)

    def test_requires_numeric_lesson_name(self):
        self.add_lesson("hello")
        with self.assertRaisesRegex(VerificationError, "numeric prefixes"):
            discover_examples(self.examples)

    def test_rejects_nested_runnable_lessons(self):
        self.add_lesson()
        nested = self.examples / "01-basics" / "nested"
        nested.mkdir()
        (nested / "02-extra.srp").write_text("print(1);")
        (nested / "02-extra.stdout").write_text("1\n")
        with self.assertRaisesRegex(VerificationError, "directly in its section"):
            discover_examples(self.examples)


if __name__ == "__main__":
    unittest.main()
