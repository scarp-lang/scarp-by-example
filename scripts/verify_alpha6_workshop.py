#!/usr/bin/env python3
"""Verify the separately pinned input/tuple workshop with its actual compiler."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, verify_one

WORKSHOP = ROOT / "tutorials" / "input-and-tuples"
TARGET = WORKSHOP / "compiler-target.json"


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    source_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        text=True,
        timeout=15,
    ).strip()
    if source_sha != target["source_commit"]:
        raise VerificationError("workshop compiler checkout differs from its immutable source pin")
    version = subprocess.run(
        [str(compiler), "version"], capture_output=True, timeout=15, check=False
    )
    expected_version = f"scarp {target['version']}\n".encode()
    if version.returncode or version.stdout != expected_version or version.stderr:
        raise VerificationError("workshop executable version differs from its published target")
    lesson = WORKSHOP / "main.srp"
    verify_one(compiler, lesson, lesson.with_suffix(".stdout"), 15)
    missing_input = subprocess.run(
        [str(compiler), "exec", str(lesson)],
        input=b"",
        capture_output=True,
        timeout=15,
        check=False,
    )
    if (
        missing_input.returncode != 1
        or missing_input.stdout
        or b"E0055" not in missing_input.stderr
    ):
        raise VerificationError("workshop EOF must report E0055 before replaying queued output")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_workshop(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: published alpha.6 workshop pin, static verify, exact input/output and atomic EOF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
