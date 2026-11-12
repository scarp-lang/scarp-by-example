#!/usr/bin/env python3
"""Check alpha.7 workshop against its actual immutable compiler and exact fixtures."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, verify_one

WORKSHOP = ROOT / "tutorials" / "conditionals-and-unicode"
TARGET = WORKSHOP / "compiler-target.json"
VERSION = "0.0.6-alpha.7"
SOURCE_COMMIT = "b1c1fd232b418267d95520c69ee563ac99ecae30"
LESSONS = ("01-grading", "02-lazy-branches", "03-unicode-scalars")


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if (
        target.get("version") != VERSION
        or target.get("release_tag") != f"v{VERSION}"
        or target.get("source_commit") != SOURCE_COMMIT
        or target.get("status") != "prerelease"
    ):
        raise VerificationError("alpha.7 workshop target does not match its published release")

    source_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        text=True,
        timeout=15,
    ).strip()
    if source_sha != SOURCE_COMMIT:
        raise VerificationError("workshop compiler checkout differs from its immutable source pin")

    version = subprocess.run(
        [str(compiler), "version"], capture_output=True, timeout=15, check=False
    )
    if (
        version.returncode != 0
        or version.stdout != f"scarp {VERSION}\n".encode("utf-8")
        or version.stderr
    ):
        raise VerificationError("workshop executable version differs from its published target")

    names = {f"{stem}.srp" for stem in LESSONS}
    stdout_names = {f"{stem}.stdout" for stem in LESSONS}
    if (
        {p.name for p in WORKSHOP.glob("*.srp")} != names
        or {p.name for p in WORKSHOP.glob("*.stdout")} != stdout_names
    ):
        raise VerificationError("workshop has missing or unpaired source/output fixtures")

    for stem in LESSONS:
        lesson = WORKSHOP / f"{stem}.srp"
        verify_one(compiler, lesson, lesson.with_suffix(".stdout"), 15)


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
    print("PASS: published alpha.7 source pin, version, three typed lessons and byte-exact stdout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
