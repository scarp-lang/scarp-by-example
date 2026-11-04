#!/usr/bin/env python3
"""Verify all guided-lab starters and byte-exact solutions with the real Scarp CLI."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from guided_labs import GuidedLab, read_labs
from verify_examples import ROOT, VerificationError, read_expected_stdout, verify_one


def run_checked(compiler: Path, operation: str, source: Path, timeout: int) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            [str(compiler), operation, str(source)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise VerificationError(f"{source}: {operation} timed out after {timeout}s") from error
    if result.returncode:
        raise VerificationError(
            f"{source}: {operation} failed with exit {result.returncode}: "
            + result.stderr.decode("utf-8", errors="replace")
        )
    return result


def verify_lab(compiler: Path, lab: GuidedLab, timeout: int = 15) -> None:
    """Require a real compileable starter whose output differs from the goal."""
    if timeout <= 0:
        raise VerificationError("timeout must be positive")
    checked = run_checked(compiler, "verify", lab.starter, timeout)
    if checked.stdout or checked.stderr:
        raise VerificationError(f"{lab.identifier}: starter static verify must be silent")
    attempted = run_checked(compiler, "exec", lab.starter, timeout)
    if attempted.stderr:
        raise VerificationError(f"{lab.identifier}: starter emitted unexpected stderr")
    expected = read_expected_stdout(lab.expected)
    if attempted.stdout == expected:
        raise VerificationError(f"{lab.identifier}: starter already matches the solution output")
    verify_one(compiler, lab.solution, lab.expected, timeout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--timeout", default=15, type=int)
    args = parser.parse_args(argv)
    executable = args.compiler.resolve()
    if not executable.is_file():
        parser.error(f"compiler not found: {executable}")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        labs = read_labs(ROOT)
        for index, lab in enumerate(labs, 1):
            verify_lab(executable, lab, args.timeout)
            print(f"[{index}/{len(labs)}] PASS {lab.identifier}: starter and reference solution")
    except (ValueError, VerificationError, OSError, UnicodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(labs)} guided Scarp coding labs against actual compiler output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
