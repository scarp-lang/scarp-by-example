"""Guards for the source-backed published Scarp alpha.13 workshop."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha13_compat as workshop
from verify_examples import VerificationError


class ModernCompilerWorkshopTests(unittest.TestCase):
    def test_manifest_tracks_published_annotated_tag(self):
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["source_commit"], "e755fda37cdaeed29434e848cb5dd41f2f2e7eb2")
        self.assertEqual(target["version"], "0.0.6-alpha.13")
        self.assertEqual(target["release_tag"], "v" + target["version"])
        self.assertEqual(target["status"], "prerelease")
        self.assertEqual(
            target["release_url"],
            "https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.13",
        )

    def test_all_upstream_programs_and_exact_fixtures_present(self):
        self.assertEqual(len(workshop.EXAMPLES), 8)
        self.assertEqual(len(workshop.COPIES), 16)
        self.assertEqual(len(set(workshop.COPIES)), 16)
        for upstream, local in workshop.COPIES:
            self.assertTrue(upstream.startswith("examples/"))
            self.assertTrue((workshop.WORKSHOP / local).is_file(), local)
        for name in workshop.EXAMPLES:
            expected = (workshop.WORKSHOP / f"{name}.stdout").read_bytes()
            self.assertNotIn(b"\r\n", expected)
            self.assertTrue(expected.endswith(b"\n"))
            expected.decode("utf-8")

    def test_refuses_directory_without_git_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(workshop.subprocess, "run") as run:
                with self.assertRaisesRegex(VerificationError, "actual Git checkout"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                run.assert_not_called()

    def test_refuses_wrong_git_revision_before_binary_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            with (
                patch.object(workshop.subprocess, "check_output", return_value="0" * 40),
                patch.object(workshop.subprocess, "run") as run,
            ):
                with self.assertRaisesRegex(VerificationError, "published source pin"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                run.assert_not_called()

    def test_refuses_wrong_executable_version_before_examples(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            with (
                patch.object(workshop.subprocess, "check_output", return_value="e755fda37cdaeed29434e848cb5dd41f2f2e7eb2"),
                patch.object(
                    workshop.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.12\n", b""),
                ),
                patch.object(workshop, "verify_one") as verify,
            ):
                with self.assertRaisesRegex(VerificationError, "binary version"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                verify.assert_not_called()

    def test_rejects_source_drift_before_examples(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)
            (source / ".git").mkdir()
            upstream, _ = workshop.COPIES[0]
            (source / upstream).parent.mkdir(parents=True)
            (source / upstream).write_text("modified source\n", encoding="utf-8")
            with (
                patch.object(workshop.subprocess, "check_output", return_value="e755fda37cdaeed29434e848cb5dd41f2f2e7eb2"),
                patch.object(
                    workshop.subprocess, "run",
                    return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.13\n", b""),
                ),
                patch.object(workshop, "verify_one") as verify,
            ):
                with self.assertRaisesRegex(VerificationError, "upstream source or fixture changed"):
                    workshop.verify_workshop(Path(__file__), source)
                verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
