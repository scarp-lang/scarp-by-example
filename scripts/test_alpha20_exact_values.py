"""Offline regression tests for alpha.20 fixture integrity and diagnostics."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from verify_alpha20_exact_values import (
    WORKSHOP, check_inventory, require_diagnostic, require_success,
)


class ExactValuesTests(unittest.TestCase):
    def test_real_inventory(self):
        check_inventory()

    def test_mutated_upstream_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "workshop"
            shutil.copytree(WORKSHOP, copy)
            (copy / "tuple_ordering.stdout").write_bytes(b"false\n")
            with self.assertRaisesRegex(ValueError, "blob mismatch"):
                check_inventory(copy)

    def test_orphan_fixture_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "workshop"
            shutil.copytree(WORKSHOP, copy)
            (copy / "orphan.stdout").write_bytes(b"x\n")
            with self.assertRaisesRegex(ValueError, "inventory"):
                check_inventory(copy)

    def test_exact_success_requires_silent_stderr(self):
        with self.assertRaises(ValueError):
            require_success(subprocess.CompletedProcess([], 0, b"x\n", b"warning"),
                            b"x\n", "test")

    def test_diagnostic_checks_schema_code_and_output(self):
        payload = json.dumps({"schema_version": 1, "code": "E0059"}).encode()
        require_diagnostic(subprocess.CompletedProcess([], 1, b"", payload),
                           "E0059", "test")
        for result in (
            subprocess.CompletedProcess([], 0, b"", payload),
            subprocess.CompletedProcess([], 1, b"leak", payload),
            subprocess.CompletedProcess([], 1, b"", b"not-json"),
            subprocess.CompletedProcess([], 1, b"", b'{"schema_version":2,"code":"E0059"}'),
        ):
            with self.assertRaises(ValueError):
                require_diagnostic(result, "E0059", "test")


if __name__ == "__main__":
    unittest.main()
