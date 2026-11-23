"""Fast, offline tests for the modern-project verifier and its fixtures."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from verify_declarative_project import (
    PROJECT, ProjectVerificationError, TEST_PATHS, json_result, require,
    validate_fixtures, validate_info, validate_test_report,
)


class DeclarativeProjectTests(unittest.TestCase):
    @staticmethod
    def output(code=0, stdout=b"", stderr=b""):
        return subprocess.CompletedProcess(["scarp"], code, stdout, stderr)

    def test_checked_in_project_fixture(self):
        self.assertEqual(validate_fixtures(), b"Total: 42\n")
        self.assertEqual(len(TEST_PATHS), 2)

    def test_mixed_case_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scarp.project").write_bytes((PROJECT / "scarp.project").read_bytes())
            modern_bytes = (root / "scarp.project").read_bytes()
            (root / "Scarp.project").write_text("scarp-project: 1\n", encoding="utf-8")
            # Case-insensitive volumes cannot represent the two spellings
            # simultaneously. Keep the duplicate-file test Linux-specific.
            if (root / "scarp.project").read_bytes() != modern_bytes:
                self.skipTest("case-insensitive filesystem aliases the two manifest spellings")
            (root / "tests").mkdir()
            (root / "src").mkdir()
            for path in ("src/main.srp", "src/totals.srp", *TEST_PATHS):
                f = root / path
                f.write_bytes((PROJECT / path).read_bytes())
            (root / "tests/02-input.stdin").write_bytes(b"6\n7\n")
            (root / "expected.stdout").write_bytes(b"Total: 42\n")
            with self.assertRaisesRegex(ProjectVerificationError, "mix legacy"):
                validate_fixtures(root)

    def test_require_checks_exact_streams_and_diagnostics(self):
        require(self.output(stdout=b"Total: 42\n"), "run", stdout=b"Total: 42\n")
        with self.assertRaisesRegex(ProjectVerificationError, "stdout differs"):
            require(self.output(stdout=b"wrong\n"), "run", stdout=b"Total: 42\n")
        with self.assertRaisesRegex(ProjectVerificationError, "exit"):
            require(self.output(1, stderr=b"problem"), "run")
        with self.assertRaisesRegex(ProjectVerificationError, "missing failure diagnostic"):
            require(self.output(1), "bad project", status=1, stdout=b"", stderr=None)

    def test_metadata_schema_must_match_v2(self):
        valid = {
            "schema_version": 1, "name": "learning-project", "version": "0.1.0",
            "type": "application", "entry": "src/main.srp",
            "manifest": "scarp.project", "format": "v2",
        }
        validate_info(valid)
        for patch in ({"format": "legacy-v1"}, {"entry": "../evil.srp"},
                      {"manifest": "Scarp.project"}, {"type": "library"}):
            with self.subTest(patch=patch):
                with self.assertRaises(ProjectVerificationError):
                    validate_info({**valid, **patch})

    def test_schema_and_malformed_json(self):
        parsed = json_result(self.output(stdout=b'{"schema_version":1}\n'), "metadata")
        self.assertEqual(parsed["schema_version"], 1)
        for payload in (b"not json", b'{"schema_version":2}', b'[]', b"\xff"):
            with self.subTest(payload=payload):
                with self.assertRaises(ProjectVerificationError):
                    json_result(self.output(stdout=payload), "metadata")

    def test_test_report_rejects_hidden_failure_or_bad_order(self):
        report = {
            "schema_version": 1, "mode": "run", "discovered": 2,
            "passed": 2, "failed": 0,
            "tests": [{"path": path, "status": "passed"} for path in TEST_PATHS],
        }
        validate_test_report(report, mode="run", selected=TEST_PATHS)
        with self.assertRaises(ProjectVerificationError):
            validate_test_report({**report, "failed": 1}, mode="run", selected=TEST_PATHS)
        with self.assertRaises(ProjectVerificationError):
            validate_test_report({**report, "tests": report["tests"][::-1]},
                                 mode="run", selected=TEST_PATHS)
        with self.assertRaises(ProjectVerificationError):
            validate_test_report({**report, "passed": 1}, mode="run", selected=TEST_PATHS)


if __name__ == "__main__":
    unittest.main()
