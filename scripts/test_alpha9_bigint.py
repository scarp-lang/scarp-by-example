"""Unit tests for the independent Scarp alpha.9 BigInt workshop."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha9_bigint as workshop
from verify_examples import VerificationError


class BigIntWorkshopTests(unittest.TestCase):
    def test_manifest_is_exact_published_alpha9(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["source_commit"], "0814997dc43982eb707a9a1aee72aab3a7ac8b41")
        self.assertEqual(target["version"], "0.0.6-alpha.9")
        self.assertEqual(target["release_tag"], "v" + target["version"])
        self.assertEqual(target["status"], "prerelease")

    def test_three_programs_and_all_upstream_files_exist(self):
        self.assertEqual(len(workshop.EXAMPLES), 3)
        self.assertEqual(len(workshop.COPIES), 7)
        for _, local in workshop.COPIES:
            self.assertTrue((workshop.WORKSHOP / local).is_file(), local)
        for name in workshop.EXAMPLES:
            self.assertNotIn(b"\r\n", (workshop.WORKSHOP / f"{name}.stdout").read_bytes())

    def test_wrong_checkout_does_not_run_compiler(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value="0" * 40),
            patch.object(workshop.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(VerificationError, "immutable source pin"):
                workshop.verify_workshop(Path("binary"), Path("checkout"))
            run.assert_not_called()

    def test_wrong_binary_version_does_not_run_samples(self):
        correct_sha = "0814997dc43982eb707a9a1aee72aab3a7ac8b41"
        with (
            patch.object(workshop.subprocess, "check_output", return_value=correct_sha),
            patch.object(
                workshop.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.8\n", b""),
            ),
            patch.object(workshop, "verify_one") as verify,
        ):
            with self.assertRaisesRegex(VerificationError, "executable version mismatch"):
                workshop.verify_workshop(Path("binary"), Path("checkout"))
            verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
