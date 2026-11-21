#!/usr/bin/env python3
"""Validate the independent Scarp alpha.6 input/tuple lesson with a real binary.

Alpha.6 accepts redirected stdin, but predates --interactive and --input-file.
Never call the active course's verify_one() for this historical workshop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, read_expected_stdout, read_optional_stdin

VERSION = "0.0.6-alpha.6"
PIN = "cdf6a3924ec2a36c7beca5a9aec4f01a0bce515e"
RELEASE_URL = "https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.6"
WORKSHOP = ROOT / "tutorials/input-and-tuples"
TARGET = WORKSHOP / "compiler-target.json"
BLOBS = {
    "main.srp": "87d04f791e1e97e3341e7033dcae958f7c5363a6",
    "main.stdin": "136e269c8e1abaa698d1d7a3978aa3d2ef3265be",
    "main.stdout": "23ae008f9f88bc699d6beff887375b9a7212a6de",
}


def git_blob_sha(data: bytes) -> str:
    """Git object identity, including the UTF-8 byte length and LF boundaries."""
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def validate_files() -> tuple[Path, Path, bytes]:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    expected = {
        "version": VERSION,
        "release_tag": "v" + VERSION,
        "source_commit": PIN,
        "release_url": RELEASE_URL,
        "status": "prerelease",
    }
    if not isinstance(target, dict) or target != expected:
        raise VerificationError("alpha.6 workshop immutable published release pin changed")
    for name, sha in BLOBS.items():
        file = WORKSHOP / name
        if file.is_symlink() or not file.is_file() or git_blob_sha(file.read_bytes()) != sha:
            raise VerificationError(f"alpha.6 workshop byte-exact source/fixture changed: {name}")
    lesson = WORKSHOP / "main.srp"
    expected_stdout = read_expected_stdout(WORKSHOP / "main.stdout")
    exact_input = read_optional_stdin(WORKSHOP / "main.stdin")
    if b"\r" in exact_input:
        raise VerificationError("alpha.6 fixture must retain exact LF input")
    return lesson, WORKSHOP / "main.stdout", exact_input


def run_command(args: list[str], stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args, cwd=ROOT, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=25, check=False,
    )


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    lesson, stdout, supplied_input = validate_files()
    if not compiler.is_file():
        raise VerificationError(f"alpha.6 executable not found: {compiler}")
    if not (compiler_source / ".git").exists():
        raise VerificationError("alpha.6 compiler source must be an actual Git checkout")
    actual_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"], timeout=15
    ).decode("ascii").strip()
    if actual_sha != PIN:
        raise VerificationError("alpha.6 compiler checkout differs from its published immutable source pin")

    version = run_command([str(compiler), "version"])
    if version.returncode or version.stdout != f"scarp {VERSION}\n".encode("ascii") or version.stderr:
        raise VerificationError("alpha.6 executable version differs from its published release")

    # verify is static and cannot consume input or emit output on success.
    checked = run_command([str(compiler), "verify", str(lesson)])
    if checked.returncode or checked.stdout or checked.stderr:
        raise VerificationError("alpha.6 static verification must succeed silently")

    # Explicit subprocess pipe is non-interactive, preserves all UTF-8 bytes, and
    # needs no newer CLI flags (--interactive/--input-file appeared later).
    executed = run_command([str(compiler), "exec", str(lesson)], supplied_input)
    if executed.returncode or executed.stderr or executed.stdout != read_expected_stdout(stdout):
        raise VerificationError(
            "alpha.6 runtime output differs from exact workshop fixture: "
            f"status={executed.returncode}, stdout={executed.stdout!r}, stderr={executed.stderr!r}"
        )

    # Only the first line is supplied. E0055 is required and prior buffered
    # 'Profile' must not be emitted when the second read hits EOF.
    cut_after_first_line = supplied_input[:supplied_input.find(b"\n") + 1]
    early_eof = run_command([str(compiler), "exec", str(lesson)], cut_after_first_line)
    if early_eof.returncode != 1 or early_eof.stdout or b"E0055" not in early_eof.stderr:
        raise VerificationError("alpha.6 premature EOF must report E0055 without leaking buffered output")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_workshop(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, TypeError, KeyError,
            subprocess.SubprocessError, UnicodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: published alpha.6 compiler, exact UTF-8 input/tuple output and atomic E0055 EOF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
