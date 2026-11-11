"""Regression tests for the separately pinned alpha.7 course workshop."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import call, patch

import verify_alpha7_workshop as workshop
from verify_examples import VerificationError


class Alpha7WorkshopTests(unittest.TestCase):
    def test_release_pin_is_fixed_and_not_copied_from_main_course(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["version"], "0.0.6-alpha.7")
        self.assertEqual(target["release_tag"], "v0.0.6-alpha.7")
        self.assertEqual(target["source_commit"], workshop.SOURCE_COMMIT)
        self.assertEqual(target["status"], "prerelease")
        self.assertEqual(len(workshop.LESSONS), 3)

    def test_unrelated_source_checkout_fails_without_running_binary(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value="0" * 40),
            patch.object(workshop.subprocess, "run") as version,
        ):
            with self.assertRaisesRegex(VerificationError, "immutable source pin"):
                workshop.verify_workshop(Path("compiler"), Path("checkout"))
            version.assert_not_called()

    def test_mismatched_binary_version_fails_before_running_examples(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value=workshop.SOURCE_COMMIT),
            patch.object(
                workshop.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.6\n", b""),
            ),
            patch.object(workshop, "verify_one") as verify,
        ):
            with self.assertRaisesRegex(VerificationError, "executable version"):
                workshop.verify_workshop(Path("compiler"), Path("checkout"))
            verify.assert_not_called()

    def test_all_three_sources_are_checked_against_adjacent_stdout(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value=workshop.SOURCE_COMMIT),
            patch.object(
                workshop.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, b"scarp 0.0.6-alpha.7\n", b""
                ),
            ),
            patch.object(workshop, "verify_one") as verify,
        ):
            workshop.verify_workshop(Path("compiler"), Path("checkout"))
            self.assertEqual(verify.call_count, 3)
            verify.assert_has_calls(
                [
                    call(
                        Path("compiler"),
                        workshop.WORKSHOP / f"{stem}.srp",
                        workshop.WORKSHOP / f"{stem}.stdout",
                        15,
                    )
                    for stem in workshop.LESSONS
                ]
            )

    def test_workshop_syntax_and_expected_unicode_bytes_are_preserved(self):
        source = (workshop.WORKSHOP / "03-unicode-scalars.srp").read_text(encoding="utf-8")
        self.assertIn(r"\u{1F44B}", source)
        self.assertIn(r"\\u{1F44B}", source)
        self.assertEqual(
            (workshop.WORKSHOP / "03-unicode-scalars.stdout").read_bytes(),
            (
                "नमस्ते 👋\nScalars: 2\nBytes: 3\n"
                "Equal composed: false\nEscaped backslash: \\u{1F44B}\n"
            ).encode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
