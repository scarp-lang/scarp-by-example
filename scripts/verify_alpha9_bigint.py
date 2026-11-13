#!/usr/bin/env python3
"""Verify the separately release-pinned Scarp alpha.9 BigInt workshop."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, verify_one

WORKSHOP = ROOT / "tutorials" / "exact-bigint"
TARGET = WORKSHOP / "compiler-target.json"
EXAMPLES = ("bigint_arithmetic", "bigint_sequences", "bigint_module")
# Upstream files and their checked-in workshop copies must stay byte-identical.
COPIES = tuple(
    (f"examples/{name}.{suffix}", f"{name}.{suffix}")
    for name in EXAMPLES
    for suffix in ("srp", "stdout")
) + (("examples/modules/bigint_math.srp", "modules/bigint_math.srp"),)


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    checkout_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        text=True,
        timeout=15,
    ).strip()
    if checkout_sha != target["source_commit"]:
        raise VerificationError("alpha.9 compiler checkout differs from immutable source pin")

    version = subprocess.run(
        [str(compiler), "version"], capture_output=True, timeout=15, check=False
    )
    expected = f"scarp {target['version']}\n".encode("ascii")
    if version.returncode != 0 or version.stdout != expected or version.stderr:
        raise VerificationError("alpha.9 compiler executable version mismatch")

    for upstream, local in COPIES:
        reference = (compiler_source / upstream).read_bytes()
        checked_in = (WORKSHOP / local).read_bytes()
        if reference != checked_in:
            raise VerificationError(f"upstream source/fixture drift: {upstream} != {local}")

    for name in EXAMPLES:
        src = WORKSHOP / f"{name}.srp"
        verify_one(compiler, src, WORKSHOP / f"{name}.stdout", 20)


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
    print("PASS: alpha.9 source pin, published fixtures, static checks and exact BigInt output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
