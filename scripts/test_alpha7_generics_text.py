"""Offline regression tests for the Alpha.3 workshop verifier."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verify_alpha7_generics_text import (
    PIN, WORKSHOP, check_inventory, require_diagnostic, require_success, verify,
)

class WorkshopTests(unittest.TestCase):
    def changed(self, name, data, message):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "workshop"
            shutil.copytree(WORKSHOP, folder)
            (folder / name).write_bytes(data)
            with self.assertRaisesRegex(ValueError, message):
                check_inventory(folder)

    def test_real_inventory(self):
        check_inventory()

    def test_pin_mismatch(self):
        self.changed("compiler-target.json", b"{}", "incorrect")

    def test_upstream_trailing_space_is_significant(self):
        actual = (WORKSHOP / "string_operators.stdout").read_bytes()
        self.changed("string_operators.stdout", actual.replace(b"Scarp Scarp \n", b"Scarp Scarp\n"),
                     "blob mismatch")

    def test_missing_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "workshop"
            shutil.copytree(WORKSHOP, folder)
            (folder / "generic_result.stdout").unlink()
            with self.assertRaisesRegex(ValueError, "inventory"):
                check_inventory(folder)

    def test_orphan(self):
        self.changed("unexpected.srp", b"print(1);\n", "inventory")

    def test_crlf(self):
        self.changed("generic_option.stdout", b"x\r\n", "noncanonical")

    def test_bom(self):
        self.changed("generic_option.stdout", b"\xef\xbb\xbfx\n", "noncanonical")

    def test_bad_checkout_stops_before_compiler(self):
        with patch("verify_alpha7_generics_text.subprocess.check_output",
                   return_value=b"wrong\n"), patch("verify_alpha7_generics_text.call") as call:
            with self.assertRaisesRegex(ValueError, "source mismatch"):
                verify(Path("compiler"), Path("checkout"))
            call.assert_not_called()

    def test_upstream_source_mismatch(self):
        with patch("verify_alpha7_generics_text.subprocess.check_output",
                   side_effect=[(PIN + "\n").encode(), b"wrong\n"]), \
             patch("verify_alpha7_generics_text.call") as call:
            with self.assertRaisesRegex(ValueError, "upstream blob mismatch"):
                verify(Path("compiler"), Path("checkout"))
            call.assert_not_called()

    def test_success_is_byte_exact_and_silent(self):
        require_success(subprocess.CompletedProcess([], 0, b"x\n", b""), b"x\n", "test")
        for result in (
            subprocess.CompletedProcess([], 1, b"x\n", b""),
            subprocess.CompletedProcess([], 0, b"x", b""),
            subprocess.CompletedProcess([], 0, b"x\n", b"warning"),
        ):
            with self.assertRaises(ValueError):
                require_success(result, b"x\n", "test")

    def test_diagnostic_schema_code_and_atomicity(self):
        payload = json.dumps({"schema_version": 1, "code": "E0086"}).encode()
        require_diagnostic(subprocess.CompletedProcess([], 1, b"", payload), "E0086", "test")
        for result in (
            subprocess.CompletedProcess([], 0, b"", payload),
            subprocess.CompletedProcess([], 1, b"leak", payload),
            subprocess.CompletedProcess([], 1, b"", b"not-json"),
            subprocess.CompletedProcess([], 1, b"", b'{"schema_version":2,"code":"E0086"}'),
            subprocess.CompletedProcess([], 1, b"", b'{"schema_version":1,"code":"E0015"}'),
        ):
            with self.assertRaises(ValueError):
                require_diagnostic(result, "E0086", "test")

if __name__ == "__main__":
    unittest.main()
