"""Unit tests for the separately compiler-pinned alpha.11 Decimal workshop."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha11_decimal as workshop
from verify_examples import VerificationError

PIN = "79b57395957f47e1270ee542a856c844b82386de"


class DecimalWorkshopTests(unittest.TestCase):
    def test_published_manifest(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["version"], "0.0.6-alpha.11")
        self.assertEqual(target["source_commit"], PIN)
        self.assertEqual(target["release_tag"], "v" + target["version"])
        self.assertEqual(target["status"], "prerelease")

    def test_source_backed_fixtures_and_lf_outputs(self):
        self.assertEqual(len(workshop.UPSTREAM_COPIES), 5)
        self.assertEqual(len(workshop.EXAMPLES), 2)
        for _, local in workshop.UPSTREAM_COPIES:
            self.assertTrue((workshop.WORKSHOP / local).is_file(), local)
        for stem in (*workshop.EXAMPLES, workshop.INTERACTIVE):
            self.assertTrue((workshop.WORKSHOP / f"{stem}.srp").is_file())
            expected = (workshop.WORKSHOP / f"{stem}.stdout").read_bytes()
            self.assertNotIn(b"\r\n", expected)
            self.assertTrue(expected.endswith(b"\n"))
        self.assertEqual((workshop.WORKSHOP / "interactive/exact_decimal.stdin").read_bytes(), b"2.675\n")
        self.assertEqual(
            (workshop.WORKSHOP / "rounding_and_conversion.stdout").read_bytes(),
            b"0.33\n0.13\n1.22\n-1.23\n1.20\n0.00\n42 42\n",
        )

    def test_wrong_checkout_aborts_before_running_binary(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value="0" * 40),
            patch.object(workshop, "run_checked") as run,
        ):
            with self.assertRaisesRegex(VerificationError, "immutable source pin"):
                workshop.verify_workshop(Path("binary"), Path("checkout"))
            run.assert_not_called()

    def test_wrong_binary_version_aborts_before_examples(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value=PIN),
            patch.object(workshop, "run_checked", return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.10\n", b"")),
            patch.object(workshop, "verify_one") as verify,
        ):
            with self.assertRaisesRegex(VerificationError, "executable version mismatch"):
                workshop.verify_workshop(Path("binary"), Path("checkout"))
            verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
