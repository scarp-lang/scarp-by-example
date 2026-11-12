#!/usr/bin/env python3
"""Integration-check the independently pinned alpha.8 project workshop.

No external Python packages. The compiler itself is built from the exact
published Scarp source SHA in .github/workflows/alpha8-project-testing.yml.
This script never downloads software, changes the checked-in project, or
relies on the calling shell's stdin.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "tutorials" / "alpha8-project-testing"
SOURCE_SHA = "37253e7805c0ca594560700dd1deb3928458e60d"
RELEASE = "0.0.6-alpha.8"


class WorkshopFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkshopFailure(message)


def invoke(binary: Path, *args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [str(binary), *args],
            cwd=str(cwd),
            input="",
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkshopFailure(f"Failed to execute {args}: {exc}") from exc


def success(result: subprocess.CompletedProcess[str], label: str) -> None:
    require(
        result.returncode == 0,
        f"{label}: exit {result.returncode}; stdout={result.stdout!r}; stderr={result.stderr!r}",
    )


def report(result: subprocess.CompletedProcess[str], label: str) -> dict:
    try:
        obj = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise WorkshopFailure(f"{label}: invalid JSON: {result.stdout!r}") from exc
    require(isinstance(obj, dict), f"{label}: expected a JSON object")
    require(obj.get("schema_version") == 1, f"{label}: unexpected report schema")
    require(isinstance(obj.get("tests"), list), f"{label}: missing test entries")
    return obj


def assert_suite(obj: dict, *, mode: str, discovered: int, passed: int, failed: int) -> None:
    for key, expected in (
        ("mode", mode), ("discovered", discovered),
        ("passed", passed), ("failed", failed),
    ):
        require(obj.get(key) == expected, f"{key}: expected {expected!r}, got {obj.get(key)!r}")


def check_release_source(checkout: Path) -> None:
    require(checkout.is_dir(), f"Compiler checkout is absent: {checkout}")
    try:
        result = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkshopFailure(f"Cannot inspect compiler checkout: {exc}") from exc
    require(result.returncode == 0, f"git rev-parse failed: {result.stderr}")
    require(result.stdout.strip() == SOURCE_SHA, "Compiler is not the exact published alpha.8 source")


def verify(binary: Path, project: Path, checkout: Path | None) -> None:
    if checkout is not None:
        check_release_source(checkout)
    version = invoke(binary, "version")
    success(version, "compiler version")
    require(RELEASE in version.stdout, f"Expected {RELEASE}; got {version.stdout!r}")

    expected = (project / "expected.stdout").read_bytes()
    require(expected == b"42\\n", "Expected-output fixture has changed")
    require((project / "tests" / "input.stdin").read_bytes() == b"17\\n25\\n",
            "Input fixture has changed")
    success(invoke(binary, "verify", str(project)), "static project verify")
    run = invoke(binary, "run", str(project))
    success(run, "run project")
    require(run.stdout.encode("utf-8") == expected,
            f"Project stdout mismatch: expected {expected!r}, got {run.stdout!r}")
    require(not run.stderr, f"Unexpected application stderr: {run.stderr!r}")

    info = invoke(binary, "project", "info", "--json", str(project))
    success(info, "project metadata")
    require(isinstance(json.loads(info.stdout), dict), "Project metadata must be a JSON object")

    listed = invoke(binary, "test", "--json", "--list", str(project))
    success(listed, "read-only test discovery")
    lst = report(listed, "test list")
    assert_suite(lst, mode="list", discovered=2, passed=0, failed=0)
    require([row.get("path") for row in lst["tests"]] ==
            ["tests/addition.srp", "tests/input.srp"], "Unexpected test order or paths")

    tested = invoke(binary, "test", "--json", "--require-tests", str(project))
    success(tested, "two real Scarp tests")
    suite = report(tested, "test execution")
    assert_suite(suite, mode="run", discovered=2, passed=2, failed=0)
    require(all(row.get("status") == "passed" for row in suite["tests"]),
            "Not every example assertion passed")

    filtered = invoke(binary, "test", "--json", "--filter", "input", str(project))
    success(filtered, "filename-filtered tests")
    selected = report(filtered, "test filter")
    assert_suite(selected, mode="run", discovered=1, passed=1, failed=0)
    require(selected["tests"][0].get("path") == "tests/input.srp",
            "Filter ran a different test")

    with tempfile.TemporaryDirectory(prefix="scarp-alpha8-workshop-") as temp:
        scratch = Path(temp) / "project"
        shutil.copytree(project, scratch)
        (scratch / "tests" / "input.stdin").write_bytes(b"17\\n24\\n")
        negative = invoke(binary, "test", "--json", "--filter", "input", str(scratch))
        require(negative.returncode == 1, "False assertion must fail with exit code 1")
        failed = report(negative, "negative assertion")
        assert_suite(failed, mode="run", discovered=1, passed=0, failed=1)
        require("E0065" in failed["tests"][0].get("error", ""),
                "Expected source-located E0065 assertion diagnostic")

        (scratch / "tests" / "input.stdin").write_bytes(b"\\xff")
        read_only = invoke(binary, "test", "--json", "--list", str(scratch))
        success(read_only, "list must not inspect stdin fixture contents")
        assert_suite(report(read_only, "read-only listing"), mode="list",
                     discovered=2, passed=0, failed=0)

        shutil.rmtree(scratch / "tests")
        empty = invoke(binary, "test", "--json", "--require-tests", str(scratch))
        require(empty.returncode == 1, "Empty required suite must exit with code 1")
        assert_suite(report(empty, "required empty suite"), mode="run",
                     discovered=0, passed=0, failed=0)

    print("PASS: pinned alpha.8 project, exact output, metadata, assertions, "
          "isolated input, JSON schema, filtering, read-only listing and empty-suite guard")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--source-checkout", type=Path, default=None)
    args = parser.parse_args()
    try:
        verify(args.compiler.resolve(), args.project.resolve(),
               args.source_checkout.resolve() if args.source_checkout else None)
        return 0
    except (WorkshopFailure, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
