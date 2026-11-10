#!/usr/bin/env python3
"""Check every lesson against a real Scarp executable and its stdout fixture."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
MAX_STDIN_BYTES = 64 * 1024


class VerificationError(Exception):
    """The lesson catalog is incomplete or malformed."""


def read_optional_stdin(input_path: Path) -> bytes:
    """Return exact fixture bytes, or EOF when a lesson has no stdin fixture.

    Unlike stdout, CRLF is meaningful input and must not be rewritten. Keep
    fixtures UTF-8 and small enough for a deterministic introductory course.
    """
    if not input_path.exists():
        return b""
    data = input_path.read_bytes()
    if len(data) > MAX_STDIN_BYTES:
        raise VerificationError(f"{input_path}: stdin fixture exceeds {MAX_STDIN_BYTES} bytes")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationError(f"{input_path}: stdin fixture is not valid UTF-8") from error
    return data


def discover_examples(examples_root: Path) -> list[tuple[Path, Path]]:
    """Return lesson and fixture pairs; reject missing or orphaned fixtures."""
    lessons = sorted(
        p
        for p in examples_root.rglob("*.srp")
        if "_support" not in p.relative_to(examples_root).parts
    )
    if not lessons:
        raise VerificationError("no runnable .srp lessons were found")
    fixtures = set(examples_root.rglob("*.stdout"))
    expected = {p.with_suffix(".stdout") for p in lessons}
    missing = expected - fixtures
    orphaned = fixtures - expected
    if missing:
        raise VerificationError(
            "missing fixtures: " + ", ".join(str(p.relative_to(examples_root)) for p in sorted(missing))
        )
    if orphaned:
        raise VerificationError(
            "orphaned fixtures: " + ", ".join(str(p.relative_to(examples_root)) for p in sorted(orphaned))
        )
    stdin_fixtures = set(examples_root.rglob("*.stdin"))
    expected_stdin = {p.with_suffix(".stdin") for p in lessons}
    orphaned_stdin = stdin_fixtures - expected_stdin
    if orphaned_stdin:
        raise VerificationError(
            "orphaned stdin fixtures: "
            + ", ".join(str(p.relative_to(examples_root)) for p in sorted(orphaned_stdin))
        )
    for fixture in sorted(stdin_fixtures):
        read_optional_stdin(fixture)
    chapter_numbers: dict[str, list[int]] = {}
    for lesson in lessons:
        relative = lesson.relative_to(examples_root)
        if len(relative.parts) != 2:
            raise VerificationError(f"lesson must live directly in its section: {relative}")
        if not relative.parts[0][:2].isdigit() or not relative.name[:2].isdigit():
            raise VerificationError(f"lesson and section must have numeric prefixes: {relative}")
        if relative.parts[0][2:3] != "-" or relative.stem[2:3] != "-":
            raise VerificationError(f"lesson and section must use NN-name prefixes: {relative}")
        chapter_numbers.setdefault(relative.parts[0], []).append(int(relative.name[:2]))
    for chapter, values in chapter_numbers.items():
        found = sorted(values)
        expected_numbers = list(range(1, len(values) + 1))
        if found != expected_numbers:
            raise VerificationError(
                f"{chapter}: lesson numbers must be unique and contiguous "
                f"starting at 01; found {found}, expected {expected_numbers}"
            )
    return [(p, p.with_suffix(".stdout")) for p in lessons]


def read_expected_stdout(expected_path: Path) -> bytes:
    """Read a byte-exact UTF-8 fixture, allowing intentional inline CR bytes.

    Reject CRLF line endings to keep fixtures portable between operating systems.
    An interior carriage return followed by a non-LF byte is real program output.
    """
    expected = expected_path.read_bytes()
    if b"\r\n" in expected:
        raise VerificationError(f"{expected_path}: expected output must use LF line endings (not CRLF)")
    try:
        expected.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationError(f"{expected_path}: fixture is not valid UTF-8") from error
    return expected


def verify_one(compiler: Path, lesson: Path, expected_path: Path, timeout: int) -> None:
    expected = read_expected_stdout(expected_path)
    provided_stdin = read_optional_stdin(lesson.with_suffix(".stdin"))
    for command in ("verify", "exec"):
        try:
            result = subprocess.run(
                [str(compiler), command, str(lesson)],
                cwd=ROOT,
                input=provided_stdin if command == "exec" else b"",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise VerificationError(f"{lesson}: `{command}` exceeded {timeout}s") from error
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise VerificationError(
                f"{lesson}: `{command}` failed with exit {result.returncode}:\n{stderr}"
            )
        if command == "verify" and (result.stdout or result.stderr):
            raise VerificationError(
                f"{lesson}: static verify must be silent on success; "
                f"stdout={result.stdout!r}, stderr={result.stderr!r}"
            )
        if command == "exec" and result.stdout != expected:
            raise VerificationError(
                f"{lesson}: stdout mismatch\n"
                f"  expected: {expected!r}\n"
                f"  actual:   {result.stdout!r}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compiler", required=True, type=Path, help="path to the built Scarp executable"
    )
    parser.add_argument("--timeout", type=int, default=15, help="timeout for each CLI operation")
    args = parser.parse_args(argv)
    compiler = args.compiler.resolve()
    if not compiler.is_file():
        parser.error(f"compiler not found: {compiler}")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        lessons = discover_examples(EXAMPLES)
        for index, (lesson, expected) in enumerate(lessons, start=1):
            verify_one(compiler, lesson, expected, args.timeout)
            print(f"[{index}/{len(lessons)}] PASS {lesson.relative_to(ROOT)}")
    except (VerificationError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(lessons)} runnable Scarp examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
