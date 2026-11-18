"""Schema and anti-drift regression tests for the compiler-backed diagnostic lab."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verify_examples import ROOT, VerificationError, read_expected_stdout
from verify_alpha14_diagnostics import (
    DIRECTORY, IDS, MANIFEST, PIN, VERSION, check_diagnostic,
    load_cases, position, verify_diagnostics,
)


class Alpha14DiagnosticWorkshopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases()

    def test_all_nine_cases_have_explicit_compiler_spans_and_valid_repairs(self):
        self.assertEqual(len(self.cases), 9)
        self.assertEqual(tuple(x["id"] for x in self.cases), IDS)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                invalid = DIRECTORY / f"{case['id']}.invalid.srp"
                fixed = DIRECTORY / f"{case['id']}.fixed.srp"
                self.assertNotEqual(invalid.read_bytes(), fixed.read_bytes())
                self.assertTrue(invalid.is_file())
                self.assertTrue(fixed.is_file())
                self.assertTrue(read_expected_stdout(DIRECTORY / f"{case['id']}.stdout"))
                self.assertEqual(
                    invalid.read_bytes()[slice(*case["span"])].decode("utf-8"),
                    case["token"],
                )

    def test_utf8_span_measures_bytes_not_text_columns(self):
        source = (DIRECTORY / "missing-tuple-comma.invalid.srp").read_text(encoding="utf-8")
        case = self.cases[0]
        self.assertEqual(case["start"], {"line": 2, "column": 13})
        self.assertEqual(case["span"], [39, 45])
        self.assertNotEqual(case["span"][0], source.index("second"))
        self.assertEqual(position(source, case["span"][0]), case["start"])
        with self.assertRaisesRegex(VerificationError, "UTF-8"):
            position(source, 4)  # split inside a Devanagari scalar

    def test_valid_diagnostic_envelope_and_fail_closed_properties(self):
        case = self.cases[0]
        path = DIRECTORY / f"{case['id']}.invalid.srp"
        good = {
            "schema_version": 1, "severity": "error", "code": "E0004",
            "span_encoding": "utf-8-bytes", "column_encoding": "unicode-scalar",
            "position_base": 1,
            "message": case["message_part"],
            "primary": {
                "path": str(path), "span": case["span"],
                "start": case["start"], "end": case["end"],
            },
            "related": [], "help": None,
        }
        def completed(doc, code=1, output=b""):
            return subprocess.CompletedProcess([], code, output,
                        json.dumps(doc).encode("utf-8"))
        check_diagnostic(case, path, completed(good))
        for key, invalid in (
            ("code", "E0010"), ("schema_version", 2),
            ("column_encoding", "utf-16"), ("span_encoding", "unicode-scalars"),
            ("severity", "warning"), ("message", "other diagnostic"),
        ):
            with self.subTest(field=key):
                modified = dict(good, **{key: invalid})
                with self.assertRaises(VerificationError):
                    check_diagnostic(case, path, completed(modified))
        for field, value in (
            ("path", "some-other.srp"),
            ("span", [0, 1]),
            ("start", {"line": 1, "column": 1}),
            ("end", {"line": 2, "column": 10}),
        ):
            with self.subTest(primary=field):
                bad = dict(good, primary={**good["primary"], field: value})
                with self.assertRaises(VerificationError):
                    check_diagnostic(case, path, completed(bad))
        with self.assertRaisesRegex(VerificationError, "without stdout"):
            check_diagnostic(case, path, completed(good, output=b"partial output"))
        with self.assertRaisesRegex(VerificationError, "without stdout"):
            check_diagnostic(case, path, completed(good, code=0))
        with self.assertRaisesRegex(VerificationError, "UTF-8 JSON"):
            check_diagnostic(case, path, subprocess.CompletedProcess([], 1, b"", b"{broken"))

    def test_source_drift_and_release_pin_drift_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            folder = temporary / "tutorials/structured-patterns/diagnostics"
            shutil.copytree(DIRECTORY, folder)
            source = folder / f"{IDS[0]}.invalid.srp"
            source.write_bytes(
                source.read_bytes().replace(b"first", b"a")
            )
            with self.assertRaisesRegex(VerificationError, "byte span or source drift"):
                load_cases(temporary)
            shutil.copyfile(DIRECTORY / source.name, source)
            manifest = json.loads((folder / "cases.json").read_text(encoding="utf-8"))
            manifest["source_commit"] = "0" * 40
            (folder / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(VerificationError, "manifest identity"):
                load_cases(temporary)

    def test_binary_mismatch_rejected_before_executing_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / ".git").mkdir()
            with (
                patch("verify_alpha14_diagnostics.subprocess.check_output",
                      return_value=(PIN + "\n").encode()),
                patch("verify_alpha14_diagnostics.subprocess.run",
                      return_value=subprocess.CompletedProcess(
                          [], 0, b"scarp 0.0.6-alpha.13\n", b"")) as runner,
            ):
                with self.assertRaisesRegex(VerificationError, "exact published"):
                    verify_diagnostics(Path(__file__), source)
                runner.assert_called_once()
        self.assertEqual(VERSION, "0.0.6-alpha.14")


if __name__ == "__main__":
    unittest.main()
