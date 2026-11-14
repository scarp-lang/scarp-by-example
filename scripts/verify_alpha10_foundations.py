#!/usr/bin/env python3
"""Verify the independently pinned published Scarp alpha.10 teaching workshop."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, read_expected_stdout, read_optional_stdin

WORKSHOP = ROOT / "tutorials" / "alpha10-foundations"
TARGET = WORKSHOP / "compiler-target.json"
# (stem relative to workshop, needs explicit interactive capability, uses stdin)
PROGRAMS = (
    ("fixed_arrays", False, False),
    ("bigint_exact", False, False),
    ("line_inventory", False, True),
    ("interactive/greeting", True, True),
    ("interactive/typed_calculator", True, True),
    ("interactive/exact_integer", True, True),
)
COPIES = tuple(
    (f"examples/{stem}.{suffix}", f"{stem}.{suffix}")
    for stem, _, has_input in PROGRAMS
    for suffix in (("srp", "stdout", "stdin") if has_input else ("srp", "stdout"))
)


def verify_program(compiler: Path, stem: str, interactive: bool, has_input: bool) -> None:
    src = WORKSHOP / f"{stem}.srp"
    stdin_path = WORKSHOP / f"{stem}.stdin"
    expected = read_expected_stdout(WORKSHOP / f"{stem}.stdout")
    if not has_input and stdin_path.exists():
        raise VerificationError(f"unexpected stdin fixture: {stdin_path}")
    provided_input = read_optional_stdin(stdin_path) if has_input else b""
    for command in ("verify", "exec"):
        argv = [str(compiler), command]
        if command == "exec" and interactive:
            argv.append("--interactive")
        argv.append(str(src))
        result = subprocess.run(
            argv,
            cwd=ROOT,
            input=provided_input if command == "exec" else b"",
            capture_output=True,
            timeout=25,
            check=False,
        )
        if result.returncode:
            raise VerificationError(
                f"{stem}: {command} failed (exit {result.returncode}): "
                + result.stderr.decode("utf-8", errors="replace")
            )
        if result.stderr:
            raise VerificationError(f"{stem}: {command} unexpectedly wrote stderr: {result.stderr!r}")
        if command == "verify" and result.stdout:
            raise VerificationError(f"{stem}: static verify should not print: {result.stdout!r}")
        if command == "exec" and result.stdout != expected:
            raise VerificationError(
                f"{stem}: exact output mismatch; expected {expected!r}; got {result.stdout!r}"
            )


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    source_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        text=True,
        timeout=15,
    ).strip()
    if source_sha != target["source_commit"]:
        raise VerificationError("alpha.10 compiler checkout differs from immutable source pin")

    version = subprocess.run(
        [str(compiler), "version"], capture_output=True, timeout=15, check=False
    )
    expected_version = f"scarp {target['version']}\n".encode("ascii")
    if version.returncode or version.stderr or version.stdout != expected_version:
        raise VerificationError("alpha.10 compiler executable version mismatch")

    for upstream, local in COPIES:
        actual = (WORKSHOP / local).read_bytes()
        expected = (compiler_source / upstream).read_bytes()
        if actual != expected:
            raise VerificationError(f"published source/fixture drift: {upstream} != {local}")
    for stem, interactive, has_input in PROGRAMS:
        verify_program(compiler, stem, interactive, has_input)

    # The prompt APIs must not work without explicit --interactive capability.
    for stem in ("interactive/greeting", "interactive/typed_calculator", "interactive/exact_integer"):
        src = WORKSHOP / f"{stem}.srp"
        result = subprocess.run(
            [str(compiler), "exec", str(src)],
            cwd=ROOT,
            input=read_optional_stdin(WORKSHOP / f"{stem}.stdin"),
            capture_output=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0 or result.stdout or b"E0054" not in result.stderr:
            raise VerificationError(f"{stem}: expected E0054 and no stdout without --interactive")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--compiler-source", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify_workshop(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: alpha.10 published source, compiler version, inputs, outputs and interactive gating")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
