"""Unit tests for Scarp-first CLI smoke-check helpers (no compiler required)."""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from verify_cli import CliSmokeError, invoke, require
from verify_examples import ROOT


class CliSmokeTests(unittest.TestCase):
    def output(self, code=0, stdout=b"", stderr=b""):
        return subprocess.CompletedProcess(["scarp"], code, stdout, stderr)

    def test_require_checks_exact_output_and_status(self):
        require(self.output(stdout=b"hello\n"), "exec", stdout=b"hello\n", stderr=b"")
        with self.assertRaisesRegex(CliSmokeError, "stdout mismatch"):
            require(self.output(stdout=b"wrong"), "exec", stdout=b"expected")
        with self.assertRaisesRegex(CliSmokeError, "exit"):
            require(self.output(code=1), "verify", stdout=b"")
        with self.assertRaisesRegex(CliSmokeError, "unexpected stderr"):
            require(self.output(stderr=b"warning"), "verify", stderr=b"")

    def test_require_can_check_inspection_and_error_streams(self):
        require(self.output(stdout=b"tokens"), "inspect", nonempty_stdout=True)
        require(self.output(code=1, stderr=b"error"), "invalid", code=1,
                stdout=b"", nonempty_stderr=True)
        with self.assertRaisesRegex(CliSmokeError, "expected nonempty stdout"):
            require(self.output(), "inspect", nonempty_stdout=True)
        with self.assertRaisesRegex(CliSmokeError, "expected a diagnostic"):
            require(self.output(code=1), "invalid", code=1, nonempty_stderr=True)

    @patch("verify_cli.subprocess.run")
    def test_invoke_passes_arguments_without_shell(self, runner):
        runner.return_value = self.output(stdout=b"ok")
        compiler = Path("scarp")
        result = invoke(compiler, "verify", "example.srp", timeout=7)
        self.assertEqual(result.stdout, b"ok")
        runner.assert_called_once_with(
            ["scarp", "verify", "example.srp"],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=7, check=False,
        )

    @patch("verify_cli.subprocess.run")
    def test_invoke_reports_timeout(self, runner):
        runner.side_effect = subprocess.TimeoutExpired(["scarp"], 2)
        with self.assertRaisesRegex(CliSmokeError, "exceeded 2s"):
            invoke(Path("scarp"), "verify", "example.srp", timeout=2)


if __name__ == "__main__":
    unittest.main()
