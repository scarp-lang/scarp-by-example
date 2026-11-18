"""Regression guards for the immutable Scarp alpha.14 workshop."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha14_patterns as workshop
from verify_examples import VerificationError, read_expected_stdout


class Alpha14StructuredPatternsTests(unittest.TestCase):
    def test_published_release_pin_is_immutable(self):
        metadata = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(workshop.PIN, "43627b74af5fccccc5e233e98207413983ebafc1")
        self.assertEqual(metadata["source_commit"], workshop.PIN)
        self.assertEqual(metadata["version"], workshop.VERSION)
        self.assertEqual(metadata["release_tag"], "v" + workshop.VERSION)
        self.assertEqual(metadata["status"], "prerelease")
        workshop.validate_manifest()

    def test_two_unique_upstream_sources_and_exact_utf8_fixtures(self):
        self.assertEqual(len(workshop.EXAMPLES), 2)
        self.assertEqual(len(workshop.COPIES), 4)
        self.assertEqual(len({p for _, p in workshop.COPIES}), 4)
        for upstream, local in workshop.COPIES:
            self.assertTrue(upstream.startswith("examples/"))
            self.assertTrue(local.is_file(), str(local))
        for name in workshop.EXAMPLES:
            expected = read_expected_stdout(workshop.WORKSHOP / f"{name}.stdout")
            self.assertTrue(expected.endswith(b"\n"))
            self.assertNotIn(b"\r\n", expected)

    def test_refuses_non_git_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(workshop.subprocess, "run") as run:
                with self.assertRaisesRegex(VerificationError, "actual Git checkout"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                run.assert_not_called()

    def test_refuses_mismatched_compiler_source_before_running(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            with (
                patch.object(workshop.subprocess, "check_output", return_value=b"0" * 40),
                patch.object(workshop.subprocess, "run") as run,
            ):
                with self.assertRaisesRegex(VerificationError, "source pin"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                run.assert_not_called()

    def test_refuses_wrong_compiler_version(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            with (
                patch.object(workshop.subprocess, "check_output", return_value=(workshop.PIN + "\n").encode()),
                patch.object(workshop.subprocess, "run",
                    return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.13\n", b"")),
                patch.object(workshop, "verify_one") as verify,
            ):
                with self.assertRaisesRegex(VerificationError, "compiler version"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                verify.assert_not_called()

    def test_refuses_workshop_source_or_stdout_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            def git_output(argv, **kwargs):
                if argv[-2:] == ["rev-parse", "HEAD"]:
                    return (workshop.PIN + "\n").encode()
                return b"not-the-published-blob\n"
            with (
                patch.object(workshop.subprocess, "check_output", side_effect=git_output),
                patch.object(workshop.subprocess, "run",
                    return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.14\n", b"")),
                patch.object(workshop, "verify_one") as verify,
            ):
                with self.assertRaisesRegex(VerificationError, "published Git object"):
                    workshop.verify_workshop(Path(__file__), Path(folder))
                verify.assert_not_called()

    def test_success_verifies_both_samples_using_committed_blobs(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            def git_output(argv, **kwargs):
                if argv[-2:] == ["rev-parse", "HEAD"]:
                    return (workshop.PIN + "\n").encode()
                upstream = argv[-1].removeprefix("HEAD:").removeprefix("examples/")
                return (workshop.WORKSHOP / upstream).read_bytes()
            with (
                patch.object(workshop.subprocess, "check_output", side_effect=git_output),
                patch.object(workshop.subprocess, "run",
                    return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.14\n", b"")),
                patch.object(workshop, "verify_one") as verify,
            ):
                workshop.verify_workshop(Path(__file__), Path(folder))
                self.assertEqual(verify.call_count, 2)


if __name__ == "__main__":
    unittest.main()
