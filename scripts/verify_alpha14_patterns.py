#!/usr/bin/env python3
"""Verify the published alpha.14 structured-patterns workshop against Git objects."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, verify_one, read_expected_stdout

WORKSHOP = ROOT / "tutorials" / "structured-patterns"
TARGET = WORKSHOP / "compiler-target.json"
PIN = "43627b74af5fccccc5e233e98207413983ebafc1"
VERSION = "0.0.6-alpha.14"
EXAMPLES = ("structured_pattern_coverage", "map_string_projection_snapshots")
COPIES = tuple(
    (f"examples/{name}.{ext}", WORKSHOP / f"{name}.{ext}")
    for name in EXAMPLES for ext in ("srp", "stdout")
)


def validate_manifest() -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if (
        target["source_commit"] != PIN
        or target["version"] != VERSION
        or target["release_tag"] != "v" + VERSION
        or target["release_url"] !=
        "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION
        or target["status"] != "prerelease"
    ):
        raise VerificationError("alpha.14 release manifest differs from approved immutable pin")


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    validate_manifest()
    if not compiler.is_file():
        raise VerificationError(f"compiler executable not found: {compiler}")
    if not (compiler_source / ".git").exists():
        raise VerificationError("compiler-source must be an actual Git checkout")
    sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        timeout=15,
    ).decode("ascii").strip()
    if sha != PIN:
        raise VerificationError("compiler checkout differs from published alpha.14 source pin")

    version = subprocess.run(
        [str(compiler), "version"], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False, timeout=15,
    )
    if (
        version.returncode != 0
        or version.stdout != f"scarp {VERSION}\n".encode("ascii")
        or version.stderr
    ):
        raise VerificationError("compiler version does not match published alpha.14 release")

    # HEAD:<path> reads committed blob bytes, not a mutable checkout file.
    # Neither unstaged upstream edits nor rewritten .stdout fixtures can pass.
    for upstream, local in COPIES:
        committed = subprocess.check_output(
            ["git", "-C", str(compiler_source), "show", f"HEAD:{upstream}"],
            timeout=15,
        )
        if not local.is_file() or committed != local.read_bytes():
            raise VerificationError(f"workshop differs from published Git object: {upstream}")

    for name in EXAMPLES:
        read_expected_stdout(WORKSHOP / f"{name}.stdout")
        verify_one(
            compiler, WORKSHOP / f"{name}.srp",
            WORKSHOP / f"{name}.stdout", timeout=20,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_workshop(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, KeyError, UnicodeError,
            subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: published alpha.14 pin, two Git-verified sources, static checks and exact stdout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
