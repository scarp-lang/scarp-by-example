"""Regression checks for the published Scarp alpha.6 input/tuple workshop."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha6_workshop as workshop
from verify_examples import VerificationError


class Alpha6WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.folder = Path(self.work.name)
        (self.folder / ".git").mkdir()
        self.compiler = self.folder / "scarp"
        self.compiler.write_bytes(b"test binary")

    def test_release_pin_and_three_byte_exact_fixtures(self):
        self.assertEqual(workshop.VERSION, "0.0.6-alpha.6")
        self.assertEqual(workshop.PIN, "cdf6a3924ec2a36c7beca5a9aec4f01a0bce515e")
        target = json.loads(workshop.TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["source_commit"], workshop.PIN)
        source, output, data = workshop.validate_files()
        self.assertTrue(source.is_file())
        self.assertTrue(output.is_file())
        self.assertEqual(data, "  संस्कार 🌍\n42\n".encode("utf-8"))
        self.assertEqual(len(workshop.BLOBS), 3)

    def test_rejects_non_git_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(workshop.subprocess, "run") as run:
                with self.assertRaisesRegex(VerificationError, "actual Git checkout"):
                    workshop.verify_workshop(self.compiler, Path(td))
                run.assert_not_called()

    def test_rejects_wrong_compiler_sha_before_running(self):
        with (
            patch.object(workshop.subprocess, "check_output", return_value=b"0" * 40),
            patch.object(workshop.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(VerificationError, "source pin"):
                workshop.verify_workshop(self.compiler, self.folder)
            run.assert_not_called()

    def test_rejects_wrong_binary_version(self):
        with (
            patch.object(workshop.subprocess, "check_output",
                         return_value=(workshop.PIN + "\n").encode("ascii")),
            patch.object(workshop.subprocess, "run",
                         return_value=subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.5\n", b"")) as run,
        ):
            with self.assertRaisesRegex(VerificationError, "executable version"):
                workshop.verify_workshop(self.compiler, self.folder)
            self.assertEqual(run.call_count, 1)

    def test_exec_uses_redirected_raw_stdin_without_newer_flags(self):
        raw = (workshop.WORKSHOP / "main.stdin").read_bytes()
        stdout = (workshop.WORKSHOP / "main.stdout").read_bytes()
        results = [
            subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.6\n", b""),
            subprocess.CompletedProcess([], 0, b"", b""),
            subprocess.CompletedProcess([], 0, stdout, b""),
            subprocess.CompletedProcess([], 1, b"", b"E0055 early EOF"),
        ]
        with (
            patch.object(workshop.subprocess, "check_output",
                         return_value=(workshop.PIN + "\n").encode("ascii")),
            patch.object(workshop.subprocess, "run", side_effect=results) as run,
        ):
            workshop.verify_workshop(self.compiler, self.folder)
        self.assertEqual(run.call_count, 4)
        first, checked, executed, eof = run.call_args_list
        self.assertEqual(first.args[0][1:], ["version"])
        self.assertEqual(checked.args[0][1], "verify")
        self.assertEqual(executed.args[0][1], "exec")
        self.assertEqual(executed.kwargs["input"], raw)
        self.assertEqual(eof.kwargs["input"], raw.split(b"\n", 1)[0] + b"\n")
        self.assertTrue(all("--interactive" not in c.args[0] and "--input-file" not in c.args[0]
                            for c in run.call_args_list))

    def test_buffered_output_on_early_eof_is_rejected(self):
        results = [
            subprocess.CompletedProcess([], 0, b"scarp 0.0.6-alpha.6\n", b""),
            subprocess.CompletedProcess([], 0, b"", b""),
            subprocess.CompletedProcess([], 0, (workshop.WORKSHOP / "main.stdout").read_bytes(), b""),
            subprocess.CompletedProcess([], 1, b"Profile\n", b"E0055"),
        ]
        with (
            patch.object(workshop.subprocess, "check_output",
                         return_value=(workshop.PIN + "\n").encode("ascii")),
            patch.object(workshop.subprocess, "run", side_effect=results),
        ):
            with self.assertRaisesRegex(VerificationError, "without leaking buffered output"):
                workshop.verify_workshop(self.compiler, self.folder)


if __name__ == "__main__":
    unittest.main()
