"""Fail-closed unit tests for the published alpha.15 boundary verifier."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_alpha15_limits as limits


def result(code: int, *, stdout: bytes = b"", diag: dict | None = None):
    stderr = json.dumps(diag).encode() if diag is not None else b""
    return subprocess.CompletedProcess([], code, stdout, stderr)


class Alpha15VerifierTests(unittest.TestCase):
    def test_immutable_pin_and_source_fixture(self):
        self.assertEqual(limits.VERSION, "0.0.6-alpha.15")
        self.assertEqual(limits.PIN, "a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281")
        self.assertEqual(limits.MAX_SOURCE_BYTES, 1024 * 1024)
        target = json.loads(limits.HISTORICAL_TARGET.read_text("utf-8"))
        self.assertEqual((target["version"], target["source_commit"]), (limits.VERSION, limits.PIN))
        active = json.loads((limits.ROOT / "docs/compiler-target.json").read_text("utf-8"))
        self.assertNotEqual(active["version"], limits.VERSION)
        self.assertNotEqual(active["source_commit"], target["source_commit"])
        self.assertIn("नमस्ते", limits.LESSON.read_text("utf-8"))
        self.assertEqual(limits.LESSON.with_suffix(".stdout").read_bytes(), b"true\ntrue\n")

    def test_accepts_valid_oversized_diagnostic(self):
        limits.require_diagnostic(
            result(1, diag={"schema_version": 1, "primary": None,
                            "message": "source file exceeds 1048576 bytes"}),
            "inspect", message="source file exceeds 1048576 bytes",
            null_primary=True,
        )

    def test_rejects_malformed_json_or_schema(self):
        with self.assertRaisesRegex(limits.LimitVerificationError, "invalid UTF-8 diagnostic JSON"):
            limits.require_diagnostic(
                subprocess.CompletedProcess([], 1, b"", b"invalid"), "tokens",
            )
        with self.assertRaisesRegex(limits.LimitVerificationError, "schema"):
            limits.require_diagnostic(result(1, diag={"schema_version": 2}), "ast")

    def test_rejects_spurious_stdout_or_missing_span(self):
        with self.assertRaisesRegex(limits.LimitVerificationError, "stdout"):
            limits.require_diagnostic(result(1, stdout=b"bad"), "ast")
        with self.assertRaisesRegex(limits.LimitVerificationError, "null source span"):
            limits.require_diagnostic(
                result(1, diag={"schema_version": 1}), "tokens", null_primary=True,
            )

    def test_rejects_wrong_work_budget_code(self):
        with self.assertRaisesRegex(limits.LimitVerificationError, "E0017"):
            limits.require_diagnostic(
                result(1, diag={"schema_version": 1, "code": "E0018"}),
                "comparison", code="E0017",
            )
        with self.assertRaisesRegex(limits.LimitVerificationError, "exit"):
            limits.require(result(1), "unexpected failure")

    def test_refuses_nongit_checkout_or_wrong_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            with self.assertRaisesRegex(limits.LimitVerificationError, "Git checkout"):
                limits.verify_source_checkout(p)
            (p / ".git").mkdir()
            with patch.object(limits.subprocess, "check_output",
                              return_value=b"0" * 40 + b"\n"):
                with self.assertRaisesRegex(limits.LimitVerificationError, "pin mismatch"):
                    limits.verify_source_checkout(p)

    def test_accepts_exact_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / ".git").mkdir()
            with patch.object(limits.subprocess, "check_output",
                              return_value=(limits.PIN + "\n").encode("ascii")):
                limits.verify_source_checkout(p)


if __name__ == "__main__":
    unittest.main()
