"""Unit tests for published Scarp alpha.10 source-backed workshop safeguards."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha10_foundations as workshop
from verify_examples import VerificationError


class Alpha10FoundationsTests(unittest.TestCase):
    def test_release_provenance_is_immutable(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["source_commit"], "44fcd0f77ccb92648cdb1fc7632495c506c87cb3")
        self.assertEqual(target["version"], "0.0.6-alpha.10")
        self.assertEqual(target["release_tag"], "v" + target["version"])
        self.assertEqual(target["status"], "prerelease")

    def test_source_copy_inventory_has_all_fixtures(self):
        self.assertEqual(len(workshop.PROGRAMS), 6)
        self.assertEqual(len(workshop.COPIES), 16)
        for upstream, local in workshop.COPIES:
            with self.subTest(upstream=upstream):
                self.assertTrue((workshop.WORKSHOP / local).is_file())
        for stem, interactive, has_input in workshop.PROGRAMS:
            with self.subTest(program=stem):
                self.assertNotIn(b"\r\n", (workshop.WORKSHOP / f"{stem}.stdout").read_bytes())
                self.assertEqual(interactive, stem.startswith("interactive/"))
                self.assertEqual(has_input, (workshop.WORKSHOP / f"{stem}.stdin").exists())

    def test_unicode_crlf_and_unterminated_line_are_preserved(self):
        data = (workshop.WORKSHOP / "line_inventory.stdin").read_bytes()
        self.assertIn(b"\r\n\n", data)
        self.assertFalse(data.endswith(b"\n"))
        self.assertIn("नमस्ते".encode("utf-8"), data)

    def test_wrong_source_checkout_never_executes_samples(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value="0" * 40),
            patch.object(workshop.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(VerificationError, "immutable source pin"):
                workshop.verify_workshop(Path("scarp"), Path("compiler"))
            run.assert_not_called()

    def test_wrong_executable_version_never_executes_samples(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value="44fcd0f77ccb92648cdb1fc7632495c506c87cb3"),
            patch.object(
                workshop.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.9\n", b""),
            ),
            patch.object(workshop, "verify_program") as verify,
        ):
            with self.assertRaisesRegex(VerificationError, "version mismatch"):
                workshop.verify_workshop(Path("scarp"), Path("compiler"))
            verify.assert_not_called()

    def test_interactive_mode_is_explicit_in_verifier(self):
        for stem, interactive, has_input in workshop.PROGRAMS:
            self.assertEqual(interactive, stem.startswith("interactive/"))
            if interactive:
                self.assertTrue(has_input)


if __name__ == "__main__":
    unittest.main()
