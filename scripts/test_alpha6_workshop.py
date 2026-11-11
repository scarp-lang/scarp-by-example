"""Guard the independent compiler pin and the workshop's failure contract."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha6_workshop as workshop
from verify_examples import VerificationError


class WorkshopTests(unittest.TestCase):
    def test_workshop_is_pinned_to_published_alpha6(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["version"], "0.0.6-alpha.6")
        self.assertEqual(target["source_commit"], "cdf6a3924ec2a36c7beca5a9aec4f01a0bce515e")
        self.assertEqual(target["release_tag"], "v" + target["version"])
        self.assertEqual(target["status"], "prerelease")

    def test_wrong_checkout_is_rejected_before_executing_compiler(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value="a" * 40),
            patch.object(workshop.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(VerificationError, "immutable source pin"):
                workshop.verify_workshop(Path("compiler"), Path("source"))
            run.assert_not_called()

    def test_wrong_binary_version_is_rejected_before_fixture_execution(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        with (
            patch.object(workshop.subprocess, "check_output", return_value=target["source_commit"]),
            patch.object(
                workshop.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.5\n", b""),
            ),
            patch.object(workshop, "verify_one") as verify,
        ):
            with self.assertRaisesRegex(VerificationError, "executable version"):
                workshop.verify_workshop(Path("compiler"), Path("source"))
            verify.assert_not_called()

    def test_eof_output_leak_is_rejected(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        replies = [
            subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.6\n", b""),
            subprocess.CompletedProcess([], 1, b"Profile\n", b"E0055"),
        ]
        with (
            patch.object(workshop.subprocess, "check_output", return_value=target["source_commit"]),
            patch.object(workshop.subprocess, "run", side_effect=replies),
            patch.object(workshop, "verify_one"),
        ):
            with self.assertRaisesRegex(VerificationError, "before replaying"):
                workshop.verify_workshop(Path("compiler"), Path("source"))


if __name__ == "__main__":
    unittest.main()
