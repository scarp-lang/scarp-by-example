"""Local and cross-platform unit tests for the project migration verifier."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from verify_project_migration import (
    MANIFEST_NAMES, MANIFESTS, MigrationVerificationError,
    SOURCE_PATHS, TEST_PATHS, WORKSHOP, check, metadata_contract,
    parse_json, test_contract, validate_fixtures,
)


class MigrationVerifierTests(unittest.TestCase):
    def test_checked_in_pair_is_byte_identical_except_manifests(self):
        self.assertEqual(validate_fixtures(), b"Migrated: 42\n")
        for path in SOURCE_PATHS:
            self.assertEqual((WORKSHOP / "legacy" / path).read_bytes(),
                             (WORKSHOP / "modern" / path).read_bytes(), path)
        self.assertEqual(len(TEST_PATHS), 2)
        for fmt, name in MANIFEST_NAMES.items():
            self.assertEqual((WORKSHOP / fmt / name).read_bytes(), MANIFESTS[fmt])

    def test_mutated_source_is_rejected_before_compiler_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            import shutil
            folder = Path(tmp)
            shutil.copytree(WORKSHOP / "legacy", folder / "legacy")
            shutil.copytree(WORKSHOP / "modern", folder / "modern")
            (folder / "modern/src/main.srp").write_text("print(999);\n", encoding="utf-8")
            with self.assertRaisesRegex(MigrationVerificationError, "changed executable fixture"):
                validate_fixtures(folder)

    def test_metadata_distinguishes_legacy_and_v2(self):
        legacy = {
            "schema_version": 1, "name": "project-migration", "version": None,
            "type": "application", "entry": "src/main.srp",
            "manifest": "Scarp.project", "format": "legacy-v1",
        }
        modern = {**legacy, "version": "0.1.0", "manifest": "scarp.project", "format": "v2"}
        metadata_contract(legacy, "legacy")
        metadata_contract(modern, "modern")
        with self.assertRaises(MigrationVerificationError):
            metadata_contract(legacy, "modern")
        with self.assertRaises(MigrationVerificationError):
            metadata_contract(modern, "legacy")

    def test_report_contract_rejects_hidden_failures(self):
        cases = [{"path": p, "status": "passed"} for p in TEST_PATHS]
        report = {"schema_version": 1, "mode": "run", "discovered": 2,
                  "passed": 2, "failed": 0, "tests": cases}
        test_contract(report, mode="run", selected=TEST_PATHS)
        for bad in ({**report, "failed": 1}, {**report, "tests": cases[::-1]},
                    {**report, "tests": cases[:-1]}, {**report, "passed": 1},
                    {**report, "schema_version": 2}):
            with self.subTest(bad=bad):
                with self.assertRaises(MigrationVerificationError):
                    test_contract(bad, mode="run", selected=TEST_PATHS)

    def test_reject_non_utf8_json_and_failed_commands(self):
        with self.assertRaises(MigrationVerificationError):
            parse_json(b"\xff", "json")
        with self.assertRaises(MigrationVerificationError):
            parse_json(b"[]", "json")
        result = subprocess.CompletedProcess(["scarp"], 1, b"", b"unexpected")
        with self.assertRaises(MigrationVerificationError):
            check(result, "program")


if __name__ == "__main__":
    unittest.main()
