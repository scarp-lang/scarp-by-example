#!/usr/bin/env python3
"""Verify the published compiler's modern declarative project workflow.

Checks the actual binary: static verify, exact stdout, implicit exec from cwd,
read-only metadata, test discovery/execution, stdin fixture, and invalid
manifest precedence. Does not modify the checked-in project.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from verify_examples import ROOT

PROJECT = ROOT / "tutorials" / "declarative-project"
MANIFEST = b'''project "learning-project" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
'''
TEST_PATHS = ("tests/01-multiplication.srp", "tests/02-input.srp")


class ProjectVerificationError(RuntimeError):
    """The declared modern workflow has regressed."""


def validate_fixtures(project: Path = PROJECT) -> bytes:
    """Guard source fixtures before any compiler process executes."""
    manifest = project / "scarp.project"
    if manifest.read_bytes() != MANIFEST:
        raise ProjectVerificationError("modern project manifest changed; review its contract")
    # Compare actual directory-entry spellings, not the result of a case-insensitive
    # filesystem lookup: on Windows/macOS, Scarp.project may alias scarp.project.
    if any(entry.name == "Scarp.project" for entry in project.iterdir()):
        raise ProjectVerificationError("do not mix legacy and declarative manifests")
    if (project / "tests/02-input.stdin").read_bytes() != b"6\n7\n":
        raise ProjectVerificationError("stdin fixture must be exact, UTF-8 and LF terminated")
    for path in ("src/main.srp", "src/totals.srp", *TEST_PATHS):
        if not (project / path).is_file():
            raise ProjectVerificationError(f"missing project source: {path}")
    expected = (project / "expected.stdout").read_bytes()
    if expected != b"Total: 42\n":
        raise ProjectVerificationError("project output fixture was unexpectedly modified")
    return expected


def invoke(compiler: Path, *args: str, cwd: Path = ROOT, timeout: int = 15
           ) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [str(compiler), *args], cwd=cwd, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ProjectVerificationError(f"{args!r} timed out after {timeout}s") from error


def require(result: subprocess.CompletedProcess[bytes], label: str,
            *, status: int = 0, stdout: bytes | None = None,
            stderr: bytes | None = b"") -> None:
    if result.returncode != status:
        raise ProjectVerificationError(
            f"{label}: exit {result.returncode}, expected {status}; "
            f"stdout={result.stdout[:300]!r}, stderr={result.stderr[:300]!r}"
        )
    if stdout is not None and result.stdout != stdout:
        raise ProjectVerificationError(
            f"{label}: stdout differs; expected={stdout[:300]!r}, actual={result.stdout[:300]!r}"
        )
    if stderr is not None and result.stderr != stderr:
        raise ProjectVerificationError(f"{label}: unexpected stderr={result.stderr[:300]!r}")
    if status and not result.stderr:
        raise ProjectVerificationError(f"{label}: missing failure diagnostic on stderr")


def json_result(result: subprocess.CompletedProcess[bytes], label: str) -> dict:
    try:
        value = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise ProjectVerificationError(f"{label}: invalid UTF-8 JSON") from error
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ProjectVerificationError(f"{label}: unsupported JSON schema")
    return value


def validate_info(info: dict) -> None:
    expected = {
        "schema_version": 1, "name": "learning-project", "version": "0.1.0",
        "type": "application", "entry": "src/main.srp", "manifest": "scarp.project",
        "format": "v2",
    }
    if info != expected:
        raise ProjectVerificationError(f"project info changed: {info!r}")


def validate_test_report(report: dict, *, mode: str, selected: tuple[str, ...]) -> None:
    if (report.get("mode") != mode or report.get("discovered") != len(selected)
            or report.get("passed") != (len(selected) if mode == "run" else 0)
            or report.get("failed") != 0):
        raise ProjectVerificationError(f"project tests: unexpected {mode} counts: {report!r}")
    cases = report.get("tests")
    if not isinstance(cases, list) or len(cases) != len(selected):
        raise ProjectVerificationError("project tests: missing or extra results")
    status = "passed" if mode == "run" else "discovered"
    if [(case.get("path"), case.get("status")) for case in cases
        if isinstance(case, dict)] != [(p, status) for p in selected]:
        raise ProjectVerificationError(f"project tests: paths/order/status changed: {cases!r}")


def verify(compiler: Path, timeout: int = 15) -> None:
    """Prove the modern manifest and the interpreter agree with the fixture."""
    expected = validate_fixtures()
    directory = str(PROJECT)
    require(invoke(compiler, "verify", directory, timeout=timeout),
            "verify directory", stdout=b"")
    require(invoke(compiler, "verify", cwd=PROJECT, timeout=timeout),
            "verify from project cwd", stdout=b"")
    require(invoke(compiler, "run", directory, timeout=timeout),
            "run directory", stdout=expected)
    require(invoke(compiler, "exec", cwd=PROJECT, timeout=timeout),
            "implicit exec from project cwd", stdout=expected)
    metadata = invoke(compiler, "project", "info", "--json", directory, timeout=timeout)
    require(metadata, "project info --json")
    validate_info(json_result(metadata, "project info"))
    listing = invoke(compiler, "test", "--list", "--json", directory, timeout=timeout)
    require(listing, "read-only test discovery")
    validate_test_report(json_result(listing, "test listing"), mode="list", selected=TEST_PATHS)
    execution = invoke(compiler, "test", "--require-tests", "--json", directory, timeout=timeout)
    require(execution, "project test execution")
    validate_test_report(json_result(execution, "test run"), mode="run", selected=TEST_PATHS)
    filtered = invoke(compiler, "test", "--json", "--filter", "input",
                      directory, timeout=timeout)
    require(filtered, "filtered test execution")
    validate_test_report(json_result(filtered, "filtered test"), mode="run",
                         selected=("tests/02-input.srp",))

    with tempfile.TemporaryDirectory(prefix="scarp-declarative-check-") as temporary:
        root = Path(temporary)
        invalid = root / "invalid-project"
        shutil.copytree(PROJECT, invalid)
        original = (invalid / "scarp.project").read_bytes()
        (invalid / "scarp.project").write_bytes(
            original.replace(b'entry: "src/main.srp"', b'entry: "../outside.srp"')
        )
        for label, args, cwd in (
            ("invalid manifest metadata", ("project", "info", "--json", str(invalid)), ROOT),
            ("invalid manifest verification", ("verify", str(invalid)), ROOT),
            ("invalid manifest implicit exec", ("exec",), invalid),
        ):
            require(invoke(compiler, *args, cwd=cwd, timeout=timeout),
                    label, status=1, stdout=b"", stderr=None)

        fresh = root / "fresh-init"
        require(invoke(compiler, "init", str(fresh), timeout=timeout),
                "modern project init", stdout=None)
        # On case-insensitive volumes, a lookup for "Scarp.project" also
        # resolves the lowercase file. Inspect exact directory-entry names.
        names = {entry.name for entry in fresh.iterdir()}
        if "scarp.project" not in names or "Scarp.project" in names:
            raise ProjectVerificationError("scarp init must create lowercase v2 manifest")
        generated = (fresh / "scarp.project").read_bytes()
        if b'project "fresh-init"' not in generated or b'entry: "src/main.srp"' not in generated:
            raise ProjectVerificationError("scarp init generated invalid declarative fields")
        require(invoke(compiler, "verify", str(fresh), timeout=timeout),
                "verify freshly initialized project", stdout=b"")
        require(invoke(compiler, "init", str(fresh), timeout=timeout),
                "init must refuse an existing directory", status=1, stdout=b"", stderr=None)
        if (fresh / "scarp.project").read_bytes() != generated:
            raise ProjectVerificationError("scarp init modified an existing project")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args(argv)
    compiler = args.compiler.resolve()
    if not compiler.is_file():
        parser.error(f"compiler not found: {compiler}")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        verify(compiler, args.timeout)
    except (OSError, ProjectVerificationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: lower-case declarative project, implicit exec, exact output and tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
