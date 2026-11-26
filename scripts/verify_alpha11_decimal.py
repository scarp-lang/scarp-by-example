#!/usr/bin/env python3
"""Check Scarp alpha.11 exact decimals against the published compiler source."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from verify_examples import (
    ROOT,
    VerificationError,
    read_expected_stdout,
    read_optional_stdin,
    verify_one,
)

WORKSHOP = ROOT / "tutorials" / "exact-decimal"
TARGET = WORKSHOP / "compiler-target.json"
EXAMPLES = ("decimal_exact", "rounding_and_conversion")
INTERACTIVE = "interactive/exact_decimal"
UPSTREAM_COPIES = (
    ("examples/decimal_exact.srp", "decimal_exact.srp"),
    ("examples/decimal_exact.stdout", "decimal_exact.stdout"),
    ("examples/interactive/exact_decimal.srp", "interactive/exact_decimal.srp"),
    ("examples/interactive/exact_decimal.stdin", "interactive/exact_decimal.stdin"),
    ("examples/interactive/exact_decimal.stdout", "interactive/exact_decimal.stdout"),
)


def run_checked(compiler: Path, args: list[str], stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [str(compiler), *args],
            cwd=ROOT,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=25,
        )
    except subprocess.TimeoutExpired as exc:
        raise VerificationError(f"Scarp command timed out: {args!r}") from exc


def check_interactive(compiler: Path) -> None:
    src = WORKSHOP / (INTERACTIVE + ".srp")
    stdin = read_optional_stdin(WORKSHOP / (INTERACTIVE + ".stdin"))
    expected = read_expected_stdout(WORKSHOP / (INTERACTIVE + ".stdout"))
    verified = run_checked(compiler, ["verify", str(src)])
    if verified.returncode or verified.stdout or verified.stderr:
        raise VerificationError("interactive decimal static verification failed")
    executed = run_checked(compiler, ["exec", "--interactive", str(src)], stdin)
    if executed.returncode or executed.stderr or executed.stdout != expected:
        raise VerificationError(
            f"interactive decimal output mismatch; expected {expected!r}, "
            f"got {executed.stdout!r}, diagnostic {executed.stderr!r}"
        )
    rejected = run_checked(compiler, ["exec", str(src)], stdin)
    if rejected.returncode == 0 or rejected.stdout or b"E0054" not in rejected.stderr:
        raise VerificationError("input_decimal must reject missing --interactive (E0054)")


def check_negative_diagnostics(compiler: Path) -> None:
    # Use fresh temporary programs: do not alter source-backed teaching examples.
    cases = (
        ('print("prior"); print(decimal("NaN"));\n', b"E0068"),
        ('print("prior"); print(decimal("1") / decimal("3"));\n', b"E0070"),
    )
    with tempfile.TemporaryDirectory(prefix="scarp-alpha11-decimal-") as folder:
        for index, (source, code) in enumerate(cases):
            program = Path(folder) / f"failure-{index}.srp"
            program.write_text(source, encoding="utf-8", newline="\n")
            result = run_checked(compiler, ["exec", str(program)])
            if result.returncode == 0 or result.stdout or code not in result.stderr:
                raise VerificationError(f"expected atomic {code.decode()} failure for {program}")


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    source_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        text=True,
        timeout=15,
    ).strip()
    if source_sha != target["source_commit"]:
        raise VerificationError("alpha.11 compiler checkout differs from immutable source pin")

    version = run_checked(compiler, ["version"])
    expected = f"scarp {target['version']}\n".encode("ascii")
    if version.returncode or version.stderr or version.stdout != expected:
        raise VerificationError("alpha.11 compiler executable version mismatch")

    for upstream, local in UPSTREAM_COPIES:
        if (compiler_source / upstream).read_bytes() != (WORKSHOP / local).read_bytes():
            raise VerificationError(f"published source/fixture drift: {upstream} != {local}")
    for stem in EXAMPLES:
        verify_one(compiler, WORKSHOP / f"{stem}.srp", WORKSHOP / f"{stem}.stdout", 25)
    check_interactive(compiler)
    check_negative_diagnostics(compiler)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_workshop(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: alpha.11 pin, release examples, exact decimals, input and failure diagnostics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
