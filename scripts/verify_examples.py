#!/usr/bin/env python3
"""Check every lesson against a real Scarp executable and its stdout fixture."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class VerificationError(Exception):
    """The lesson catalog is incomplete or malformed."""


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
    for lesson in lessons:
        relative = lesson.relative_to(examples_root)
        if len(relative.parts) != 2:
            raise VerificationError(f"lesson must live directly in its section: {relative}")
        if not relative.parts[0][:2].isdigit() or not relative.name[:2].isdigit():
            raise VerificationError(f"lesson and section must have numeric prefixes: {relative}")
    return [(p, p.with_suffix(".stdout")) for p in lessons]


def verify_one(compiler: Path, lesson: Path, expected_path: Path, timeout: int) -> None:
    expected = expected_path.read_bytes()
    if b"\r" in expected:
        raise VerificationError(f"{expected_path}: expected output must use LF only")
    try:
        expected.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationError(f"{expected_path}: fixture is not valid UTF-8") from error
    for command in ("check", "run"):
        try:
            result = subprocess.run(
                [str(compiler), command, str(lesson)],
                cwd=ROOT,
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
        if command == "run" and result.stdout != expected:
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
