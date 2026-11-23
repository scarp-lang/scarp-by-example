#!/usr/bin/env python3
"""Prove v1 -> v2 Scarp project migration with the published compiler.

Checked-in projects have byte-identical source, imports, tests, stdin,
and exact expected stdout. Only their manifest formats differ.
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

WORKSHOP = ROOT / "tutorials" / "project-migration"
SOURCE_PATHS = (
    "src/main.srp", "src/lib/math.srp",
    "tests/01-arithmetic.srp", "tests/02-input.srp",
    "tests/02-input.stdin", "expected.stdout",
)
TEST_PATHS = ("tests/01-arithmetic.srp", "tests/02-input.srp")
MANIFESTS = {
    "legacy": b"scarp-project: 1\nname: project-migration\nentry: src/main.srp\n",
    "modern": (
        b'project "project-migration" {\n'
        b'    version: "0.1.0"\n'
        b'    entry: "src/main.srp"\n'
        b'    type: "application"\n'
        b'    dependencies {}\n'
        b'}\n'
    ),
}
MANIFEST_NAMES = {"legacy": "Scarp.project", "modern": "scarp.project"}
EXPECTED_OUTPUT = b"Migrated: 42\n"


class MigrationVerificationError(RuntimeError):
    """Observed compiler behavior or workshop source has drifted."""


def validate_fixtures(root: Path = WORKSHOP) -> bytes:
    """Guard exact manifests and compare all programs and test fixtures."""
    roots = {format_: root / format_ for format_ in MANIFESTS}
    for format_, folder in roots.items():
        if not folder.is_dir():
            raise MigrationVerificationError(f"missing {format_} project directory")
        name = MANIFEST_NAMES[format_]
        if (folder / name).read_bytes() != MANIFESTS[format_]:
            raise MigrationVerificationError(f"{format_} manifest content differs from course")
        # Filename lookup is case-insensitive on many Windows/macOS volumes.
        names = {entry.name for entry in folder.iterdir()}
        if name not in names or any(
            other in names for other in MANIFEST_NAMES.values() if other != name
        ):
            raise MigrationVerificationError(f"{format_} project has unexpected manifest filenames")
        for path in SOURCE_PATHS:
            if not (folder / path).is_file():
                raise MigrationVerificationError(f"{format_} project misses {path}")
    for path in SOURCE_PATHS:
        left = (roots["legacy"] / path).read_bytes()
        right = (roots["modern"] / path).read_bytes()
        if left != right:
            raise MigrationVerificationError(f"migration changed executable fixture {path}")
    if (roots["legacy"] / "tests/02-input.stdin").read_bytes() != b"19\n23\n":
        raise MigrationVerificationError("migration input fixture no longer matches tutorial")
    if (roots["legacy"] / "expected.stdout").read_bytes() != EXPECTED_OUTPUT:
        raise MigrationVerificationError("migration expected stdout has drifted")
    return EXPECTED_OUTPUT


def invoke(binary: Path, *args: str, cwd: Path = ROOT, timeout: int = 15
           ) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [str(binary), *args], cwd=cwd, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise MigrationVerificationError(f"{args!r} timed out after {timeout}s") from error


def check(result: subprocess.CompletedProcess[bytes], label: str, *,
          code: int = 0, stdout: bytes | None = b"",
          stderr: bytes | None = b"") -> None:
    if result.returncode != code:
        raise MigrationVerificationError(
            f"{label}: status {result.returncode} != {code}; "
            f"stdout={result.stdout[:200]!r}; stderr={result.stderr[:200]!r}"
        )
    if stdout is not None and result.stdout != stdout:
        raise MigrationVerificationError(f"{label}: stdout differs {result.stdout[:200]!r}")
    if stderr is not None and result.stderr != stderr:
        raise MigrationVerificationError(f"{label}: unexpected stderr {result.stderr[:200]!r}")


def parse_json(value: bytes, label: str) -> dict:
    try:
        data = json.loads(value.decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise MigrationVerificationError(f"{label}: invalid UTF-8 JSON") from error
    if not isinstance(data, dict):
        raise MigrationVerificationError(f"{label}: expected JSON object")
    return data


def metadata_contract(info: dict, format_: str) -> None:
    expected = {
        "schema_version": 1, "name": "project-migration",
        "version": None if format_ == "legacy" else "0.1.0",
        "type": "application", "entry": "src/main.srp",
        "manifest": MANIFEST_NAMES[format_],
        "format": "legacy-v1" if format_ == "legacy" else "v2",
    }
    if info != expected:
        raise MigrationVerificationError(f"{format_} project metadata changed: {info!r}")


def test_contract(data: dict, *, mode: str, selected: tuple[str, ...]) -> None:
    if (data.get("schema_version") != 1
            or data.get("mode") != mode
            or data.get("discovered") != len(selected)
            or data.get("passed") != (len(selected) if mode == "run" else 0)
            or data.get("failed") != 0):
        raise MigrationVerificationError(f"unexpected test counts: {data!r}")
    status = "passed" if mode == "run" else "discovered"
    cases = data.get("tests")
    if (not isinstance(cases, list) or len(cases) != len(selected)
            or not all(isinstance(c, dict) for c in cases)):
        raise MigrationVerificationError("test cases missing or malformed")
    if [(c.get("path"), c.get("status")) for c in cases] != [
        (p, status) for p in selected
    ]:
        raise MigrationVerificationError(f"test path/order/status differs: {cases!r}")


def verify_pair(binary: Path, timeout: int = 15) -> None:
    """Compare two real projects and the released compiler's JSON contracts."""
    output = validate_fixtures()
    for format_ in MANIFESTS:
        project = WORKSHOP / format_
        directory = str(project)
        check(invoke(binary, "verify", directory, timeout=timeout),
              f"{format_} static verify")
        check(invoke(binary, "verify", cwd=project, timeout=timeout),
              f"{format_} implicit static verify")
        check(invoke(binary, "run", directory, timeout=timeout),
              f"{format_} run", stdout=output)
        check(invoke(binary, "exec", cwd=project, timeout=timeout),
              f"{format_} implicit exec", stdout=output)
        meta = invoke(binary, "project", "info", "--json", directory, timeout=timeout)
        check(meta, f"{format_} project info", stdout=None)
        metadata_contract(parse_json(meta.stdout, f"{format_} metadata"), format_)
        for flags, mode, selected in [
            (("--list", "--json"), "list", TEST_PATHS),
            (("--require-tests", "--json"), "run", TEST_PATHS),
            (("--json", "--filter", "input"), "run", ("tests/02-input.srp",)),
        ]:
            result = invoke(binary, "test", *flags, directory, timeout=timeout)
            check(result, f"{format_} test {flags}", stdout=None)
            test_contract(parse_json(result.stdout, f"{format_} test"), mode=mode,
                          selected=selected)
        inspected = invoke(binary, "inspect", "modules", "--json", directory, timeout=timeout)
        check(inspected, f"{format_} read-only module inspection", stdout=None)
        inventory = parse_json(inspected.stdout, f"{format_} module inspection")
        if (inventory.get("schema_version") != 1
                or not isinstance(inventory.get("modules"), list)
                or len(inventory["modules"]) != 2):
            raise MigrationVerificationError(f"{format_} module graph was not preserved")

    # Renaming only the old header does not create declarative v2 format.
    # No committed project is modified.
    with tempfile.TemporaryDirectory(prefix="scarp-migration-") as folder:
        changed = Path(folder) / "rename-only"
        shutil.copytree(WORKSHOP / "legacy", changed)
        old_file = changed / "Scarp.project"
        intermediate = changed / "manifest.tmp"
        old_file.rename(intermediate)
        intermediate.rename(changed / "scarp.project")
        if (changed / "scarp.project").read_bytes() != MANIFESTS["legacy"]:
            raise MigrationVerificationError("rename-only witness unexpectedly changed content")
        inspect = invoke(binary, "project", "info", "--json", str(changed), timeout=timeout)
        if inspect.returncode == 0:
            if parse_json(inspect.stdout, "rename-only").get("format") == "v2":
                raise MigrationVerificationError("renaming old body was misreported as v2")
        elif inspect.returncode != 1 or inspect.stdout or not inspect.stderr:
            raise MigrationVerificationError("rename-only returned unexpected metadata behavior")

        # Prove JSON-v2 runtime diagnostics on an intentionally failing test.
        failed = Path(folder) / "failing-test"
        shutil.copytree(WORKSHOP / "modern", failed)
        (failed / "tests/99-intentional-failure.srp").write_text(
            'assert(19 + 23 == 99, "intentional verification failure");\n',
            encoding="utf-8",
        )
        result = invoke(binary, "test", "--require-tests", "--json=v2",
                        str(failed), timeout=timeout)
        if result.returncode != 1 or result.stderr:
            raise MigrationVerificationError(
                f"structured failure status changed: {result.returncode}, {result.stderr[:200]!r}"
            )
        structured = parse_json(result.stdout, "v2 intentional assertion failure")
        if (structured.get("schema_version") != 2
                or structured.get("discovered") != 3
                or structured.get("passed") != 2
                or structured.get("failed") != 1):
            raise MigrationVerificationError(f"structured failure counts changed: {structured!r}")
        cases = structured.get("tests", [])
        if not isinstance(cases, list) or len(cases) != 3:
            raise MigrationVerificationError("structured failure missing test case")
        case = cases[-1]
        if (not isinstance(case, dict)
                or case.get("path") != "tests/99-intentional-failure.srp"
                or case.get("status") != "failed"
                or case.get("phase") != "runtime"
                or not isinstance(case.get("diagnostic"), dict)):
            raise MigrationVerificationError(f"intentional failure lost runtime diagnostic: {case!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args(argv)
    binary = args.compiler.resolve()
    if not binary.is_file():
        parser.error(f"compiler not found: {binary}")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        verify_pair(binary, args.timeout)
    except (OSError, MigrationVerificationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: v1/v2 migration parity, tests, metadata, fixtures and failure reports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
