"""Unit tests for the lesson catalog's integrity checks."""

import tempfile
import unittest
from pathlib import Path
import subprocess
from unittest.mock import patch

from verify_examples import VerificationError, discover_examples, read_expected_stdout, verify_one


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




class NestedRepeatLessonTests(unittest.TestCase):
    """Regress the new exercise's expected arithmetic independently of Scarp.

    The cross-platform workflows additionally execute the actual source using
    the exact released compiler and require the stdout fixture byte-for-byte.
    """

    def test_nested_continue_keeps_only_nonmatching_grid_pairs(self):
        from verify_examples import ROOT, EXAMPLES
        source = EXAMPLES / "02-control-flow" / "04-nested-repeat.srp"
        fixture = source.with_suffix(".stdout")
        text = source.read_text(encoding="utf-8")
        self.assertIn("repeat 4 as row", text)
        self.assertIn("repeat 3 as column", text)
        self.assertIn("if row == column", text)
        self.assertIn("continue;", text)
        self.assertIn("print(accepted, skipped, total);", text)
        pairs = [(row, column) for row in range(4) for column in range(3)]
        allowed = [(row, column) for row, column in pairs if row != column]
        result = f"{len(allowed)} {len(pairs) - len(allowed)} " + (
            str(sum(row + column for row, column in allowed)) + "\n"
        )
        self.assertEqual(result, "9 3 24\n")
        self.assertEqual(read_expected_stdout(fixture), result.encode("utf-8"))
        self.assertIn((source, fixture), discover_examples(EXAMPLES))


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


class RunnerCommandTests(unittest.TestCase):
    def test_verifier_uses_static_verify_then_exec(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lesson = root / "01-hello.srp"
            stdout = root / "01-hello.stdout"
            lesson.write_text('print("hello");\n', encoding="utf-8")
            stdout.write_bytes(b"hello\n")
            checked = subprocess.CompletedProcess(["scarp"], 0, b"", b"")
            executed = subprocess.CompletedProcess(["scarp"], 0, b"hello\n", b"")
            with patch("verify_examples.subprocess.run", side_effect=[checked, executed]) as runner:
                verify_one(Path("scarp"), lesson, stdout, 5)
            self.assertEqual(
                [call.args[0][1] for call in runner.call_args_list],
                ["verify", "exec"],
            )

    def test_verifier_rejects_output_during_static_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lesson = root / "01-hello.srp"
            stdout = root / "01-hello.stdout"
            lesson.write_text('print("hello");\n', encoding="utf-8")
            stdout.write_bytes(b"hello\n")
            noisy = subprocess.CompletedProcess(["scarp"], 0, b"hello\n", b"")
            with patch("verify_examples.subprocess.run", return_value=noisy):
                with self.assertRaisesRegex(VerificationError, "static verify must be silent"):
                    verify_one(Path("scarp"), lesson, stdout, 5)


if __name__ == "__main__":
    unittest.main()
