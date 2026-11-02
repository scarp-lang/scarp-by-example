"""Unit tests for the lesson catalog's integrity checks."""

import tempfile
import unittest
from pathlib import Path

from verify_examples import VerificationError, discover_examples, read_expected_stdout


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

    def test_rejects_duplicate_lesson_numbers_in_a_chapter(self):
        self.add_lesson("01-hello")
        self.add_lesson("01-another")
        with self.assertRaisesRegex(VerificationError, "unique and contiguous"):
            discover_examples(self.examples)

    def test_rejects_numbering_gap(self):
        self.add_lesson("01-hello")
        self.add_lesson("03-third")
        with self.assertRaisesRegex(VerificationError, "unique and contiguous"):
            discover_examples(self.examples)

    def test_rejects_chapters_not_starting_at_one(self):
        self.add_lesson("02-second")
        with self.assertRaisesRegex(VerificationError, "starting at 01"):
            discover_examples(self.examples)

    def test_accepts_contiguous_numbering(self):
        self.add_lesson("01-first")
        self.add_lesson("02-second")
        self.assertEqual(len(discover_examples(self.examples)), 2)

    def test_rejects_nested_runnable_lessons(self):
        self.add_lesson()
        nested = self.examples / "01-basics" / "nested"
        nested.mkdir()
        (nested / "02-extra.srp").write_text("print(1);")
        (nested / "02-extra.stdout").write_text("1\n")
        with self.assertRaisesRegex(VerificationError, "directly in its section"):
            discover_examples(self.examples)



class FixtureByteTests(unittest.TestCase):
    def test_literal_carriage_return_is_valid_output(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "control.stdout"
            expected = b"line\rstart\n"
            fixture.write_bytes(expected)
            self.assertEqual(read_expected_stdout(fixture), expected)

    def test_crlf_line_endings_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "crlf.stdout"
            fixture.write_bytes(b"first\r\nsecond\r\n")
            with self.assertRaisesRegex(VerificationError, "CRLF"):
                read_expected_stdout(fixture)

    def test_invalid_utf8_fixture_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "binary.stdout"
            fixture.write_bytes(b"invalid \xff")
            with self.assertRaisesRegex(VerificationError, "UTF-8"):
                read_expected_stdout(fixture)


if __name__ == "__main__":
    unittest.main()
