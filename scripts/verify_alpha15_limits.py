#!/usr/bin/env python3
"""Check Scarp v0.0.6-alpha.15 frontend limits using its published compiler."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281"
VERSION = "0.0.6-alpha.15"
MAX_SOURCE_BYTES = 1_048_576
LESSON = ROOT / "tutorials" / "alpha15-limits" / "string-comparisons.srp"


class LimitVerificationError(RuntimeError):
    """Published Scarp's observable behavior was not reproduced."""


def call(compiler: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [str(compiler), *args], cwd=ROOT, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LimitVerificationError(f"cannot run {' '.join(args)}: {error}") from error


def require(
    value: subprocess.CompletedProcess[bytes], name: str, *,
    status: int = 0, stdout: bytes | None = None, stderr: bytes | None = None,
) -> None:
    if value.returncode != status:
        raise LimitVerificationError(
            f"{name}: exit {value.returncode} instead of {status}, "
            f"stdout={value.stdout[:200]!r}, stderr={value.stderr[:300]!r}"
        )
    if stdout is not None and value.stdout != stdout:
        raise LimitVerificationError(f"{name}: unexpected stdout {value.stdout[:200]!r}")
    if stderr is not None and value.stderr != stderr:
        raise LimitVerificationError(f"{name}: unexpected stderr {value.stderr[:300]!r}")


def require_diagnostic(
    value: subprocess.CompletedProcess[bytes], name: str, *,
    message: str | None = None, code: str | None = None,
    null_primary: bool = False,
) -> None:
    require(value, name, status=1, stdout=b"")
    try:
        report = json.loads(value.stderr.decode("utf-8"))
    except (UnicodeError, ValueError) as error:
        raise LimitVerificationError(f"{name}: invalid UTF-8 diagnostic JSON") from error
    if not isinstance(report, dict) or report.get("schema_version") != 1:
        raise LimitVerificationError(f"{name}: unexpected diagnostic schema")
    if message is not None and message not in str(report.get("message", "")):
        raise LimitVerificationError(f"{name}: missing expected error text")
    if code is not None and report.get("code") != code:
        raise LimitVerificationError(f"{name}: expected diagnostic code {code}")
    if null_primary and ("primary" not in report or report["primary"] is not None):
        raise LimitVerificationError(f"{name}: expected null source span")


def verify_source_checkout(source: Path) -> None:
    if not (source / ".git").exists():
        raise LimitVerificationError("compiler source must be a Git checkout")
    try:
        head = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            stderr=subprocess.PIPE, timeout=15,
        ).decode("ascii").strip()
    except (OSError, UnicodeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise LimitVerificationError(f"cannot read compiler HEAD: {error}") from error
    if head != PIN:
        raise LimitVerificationError(f"compiler source pin mismatch: {head} != {PIN}")


def verify_alpha15(compiler: Path, source: Path) -> None:
    target = json.loads((ROOT / "docs/compiler-target.json").read_text("utf-8"))
    if (target.get("version"), target.get("source_commit")) != (VERSION, PIN):
        raise LimitVerificationError("active compiler metadata is not published alpha.15")
    verify_source_checkout(source)
    require(call(compiler, "version"), "compiler version",
            stdout=f"scarp {VERSION}\n".encode(), stderr=b"")
    require(call(compiler, "verify", str(LESSON)),
            "static comparison verification", stdout=b"", stderr=b"")
    expected = LESSON.with_suffix(".stdout").read_bytes()
    if expected != b"true\ntrue\n":
        raise LimitVerificationError("checked-in stdout fixture has changed")
    require(call(compiler, "exec", str(LESSON)),
            "UTF-8 comparison execution", stdout=expected, stderr=b"")

    with tempfile.TemporaryDirectory(prefix="scarp-alpha15-") as folder:
        path = Path(folder)
        exact = path / "सीमा.srp"
        oversized = path / "oversized.srp"
        exact.write_bytes(b" " * MAX_SOURCE_BYTES)
        oversized.write_bytes(b" " * (MAX_SOURCE_BYTES + 1))
        for mode in (("tokens",), ("inspect", "tokens"), ("inspect", "ast")):
            label = " ".join(mode)
            require(call(compiler, *mode, str(exact)),
                    f"{label}: exactly 1 MiB", stderr=b"")
            failure = call(compiler, *mode, "--diagnostic-format=json", str(oversized))
            require_diagnostic(
                failure, f"{label}: over 1 MiB", null_primary=True,
                message=f"source file exceeds {MAX_SOURCE_BYTES} bytes",
            )

        text = "a" * 129
        witness = path / "comparison-budget.srp"
        witness.write_text(
            f'bind a = "{text}"; bind b = "{text}"; '
            'eprint("pending"); print(a == b);',
            encoding="utf-8",
        )
        under = call(compiler, "exec", "--max-steps", "12",
                     "--diagnostic-format=json", str(witness))
        require_diagnostic(under, "129-byte under-budget comparison", code="E0017")
        exact_steps = call(compiler, "exec", "--max-steps", "13", str(witness))
        require(exact_steps, "129-byte exact-budget comparison",
                stdout=b"true\n", stderr=b"pending\n")
    print("PASS: published alpha.15 pin, UTF-8 sample, 1 MiB inspection and work budget.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--compiler-source", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify_alpha15(args.compiler, args.compiler_source)
    except (LimitVerificationError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
