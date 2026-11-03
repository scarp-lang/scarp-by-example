#!/usr/bin/env python3
"""Smoke-test the pinned Scarp-first CLI using real lessons and a temporary witness."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from verify_examples import ROOT, read_expected_stdout


class CliSmokeError(RuntimeError):
    """Observed CLI behavior differs from the pinned alpha.4 CLI contract."""


def invoke(compiler: Path, *arguments: str, timeout: int = 15) -> subprocess.CompletedProcess[bytes]:
    """Run a single compiler command in the course root without using a shell."""
    try:
        return subprocess.run(
            [str(compiler), *arguments],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise CliSmokeError(f"{' '.join(arguments)} exceeded {timeout}s") from error


def require(
    result: subprocess.CompletedProcess[bytes],
    label: str,
    *,
    code: int = 0,
    stdout: bytes | None = None,
    stderr: bytes | None = None,
    nonempty_stdout: bool = False,
    nonempty_stderr: bool = False,
) -> None:
    """Check exit code and byte-level streams without relying on Python assert."""
    if result.returncode != code:
        raise CliSmokeError(
            f"{label}: exit {result.returncode} != {code}; "
            f"stdout={result.stdout[:300]!r}; stderr={result.stderr[:300]!r}"
        )
    if stdout is not None and result.stdout != stdout:
        raise CliSmokeError(f"{label}: stdout mismatch: {result.stdout[:300]!r} != {stdout[:300]!r}")
    if stderr is not None and result.stderr != stderr:
        raise CliSmokeError(f"{label}: unexpected stderr: {result.stderr[:300]!r}")
    if nonempty_stdout and not result.stdout:
        raise CliSmokeError(f"{label}: expected nonempty stdout")
    if nonempty_stderr and not result.stderr:
        raise CliSmokeError(f"{label}: expected a diagnostic on stderr")


def smoke_test(compiler: Path, timeout: int = 15) -> None:
    """Prove published alpha.4 commands, static checks and real project workflows."""
    version = invoke(compiler, "version", timeout=timeout)
    require(version, "version", nonempty_stdout=True, stderr=b"")
    require(invoke(compiler, "--version", timeout=timeout), "--version",
            stdout=version.stdout, stderr=b"")

    guide = invoke(compiler, "guide", timeout=timeout)
    require(guide, "guide", nonempty_stdout=True, stderr=b"")
    if b"scarp exec" not in guide.stdout:
        raise CliSmokeError("guide: missing the Scarp-first exec command")
    help_exec = invoke(compiler, "guide", "exec", timeout=timeout)
    require(help_exec, "guide exec", nonempty_stdout=True, stderr=b"")
    if b"Usage: scarp exec" not in help_exec.stdout:
        raise CliSmokeError("guide exec: missing usage heading")

    diagnostic = invoke(compiler, "diagnose", "--json", timeout=timeout)
    require(diagnostic, "diagnose --json", nonempty_stdout=True, stderr=b"")
    try:
        capabilities = json.loads(diagnostic.stdout)
    except (UnicodeDecodeError, ValueError) as error:
        raise CliSmokeError("diagnose --json: invalid JSON") from error
    if (capabilities.get("schema_version") != 1
            or capabilities.get("static_verify") is not True
            or capabilities.get("native_executable") is not False):
        raise CliSmokeError("diagnose --json: misleading or unsupported capabilities")
    if capabilities.get("version") != "0.0.5-alpha.4" or capabilities.get("project_workflow") is not True:
        raise CliSmokeError("diagnose --json: expected published alpha.4 project capabilities")
    expected_version = f"scarp {capabilities['version']}\n".encode("utf-8")
    if version.stdout != expected_version:
        raise CliSmokeError("version and diagnose disagree")

    for relative in (
        "examples/01-basics/01-hello.srp",
        "examples/05-modules/01-modular-inference.srp",
    ):
        lesson = ROOT / relative
        fixture = read_expected_stdout(lesson.with_suffix(".stdout"))
        checked = invoke(compiler, "verify", str(lesson), timeout=timeout)
        require(checked, f"verify {relative}", stdout=b"", stderr=b"")
        executed = invoke(compiler, "exec", str(lesson), timeout=timeout)
        require(executed, f"exec {relative}", stdout=fixture, stderr=b"")
        legacy = invoke(compiler, "run", str(lesson), timeout=timeout)
        require(legacy, f"run {relative}", stdout=executed.stdout, stderr=executed.stderr)

    hello = str(ROOT / "examples/01-basics/01-hello.srp")
    for arguments in (
        ("inspect", "tokens", hello),
        ("inspect", "ast", hello),
    ):
        result = invoke(compiler, *arguments, timeout=timeout)
        require(result, " ".join(arguments[:2]), nonempty_stdout=True, stderr=b"")
    modules = str(ROOT / "examples/05-modules/01-modular-inference.srp")
    plain = invoke(compiler, "inspect", "modules", modules, timeout=timeout)
    require(plain, "inspect modules", nonempty_stdout=True, stderr=b"")
    structured = invoke(compiler, "inspect", "modules", "--json", modules, timeout=timeout)
    require(structured, "inspect modules --json", nonempty_stdout=True, stderr=b"")
    try:
        module_info = json.loads(structured.stdout)
    except (UnicodeDecodeError, ValueError) as error:
        raise CliSmokeError("inspect modules --json: invalid JSON") from error
    if not isinstance(module_info, dict) or module_info.get("schema_version") != 1:
        raise CliSmokeError("inspect modules --json: unsupported schema version")

    with tempfile.TemporaryDirectory(prefix="scarp-cli-smoke-") as directory:
        witness = Path(directory) / "static-only.srp"
        witness.write_text("print(1 / 0);\n", encoding="utf-8")
        static = invoke(compiler, "verify", str(witness), timeout=timeout)
        require(static, "verify does not execute runtime division", stdout=b"", stderr=b"")
        legacy_check = invoke(compiler, "check", str(witness), timeout=timeout)
        require(legacy_check, "legacy check evaluates runtime division",
                code=1, stdout=b"", nonempty_stderr=True)
        witness.write_text("print(unknown_identifier);\n", encoding="utf-8")
        invalid = invoke(compiler, "verify", str(witness), timeout=timeout)
        require(invalid, "verify rejects unresolved identifiers",
                code=1, stdout=b"", nonempty_stderr=True)

    project_smoke(compiler, timeout)
    print("PASS: Scarp-first CLI, legacy migration, static validation, inspection and projects.")


def project_smoke(compiler: Path, timeout: int) -> None:
    """Test real project scaffolding, static verify, launch and rejection paths."""
    expected = read_expected_stdout(ROOT / "examples/01-basics/01-hello.stdout")
    with tempfile.TemporaryDirectory(prefix="scarp-project-smoke-") as folder:
        project = Path(folder) / "first-project"
        created = invoke(compiler, "create", str(project), timeout=timeout)
        require(created, "create project", nonempty_stdout=True, stderr=b"")
        manifest = project / "Scarp.project"
        source = project / "src" / "main.srp"
        original = b"scarp-project: 1\nname: first-project\nentry: src/main.srp\n"
        if manifest.read_bytes() != original:
            raise CliSmokeError("create wrote an unexpected project manifest")
        if source.read_bytes() != b'print("Hello from Scarp!");\n':
            raise CliSmokeError("create wrote an unexpected source template")
        require(invoke(compiler, "verify", str(project), timeout=timeout),
                "static project verify", stdout=b"", stderr=b"")
        require(invoke(compiler, "launch", str(project), timeout=timeout),
                "interpreter-backed launch", stdout=expected, stderr=b"")
        require(invoke(compiler, "exec", str(source), timeout=timeout),
                "scaffold entry execution", stdout=expected, stderr=b"")
        # Never adopt or overwrite an existing project directory.
        require(invoke(compiler, "create", str(project), timeout=timeout),
                "existing project rejected", code=1, stdout=b"", nonempty_stderr=True)
        if manifest.read_bytes() != original:
            raise CliSmokeError("create unexpectedly modified an existing project")
        source.write_text("print(1 / 0);\n", encoding="utf-8")
        require(invoke(compiler, "verify", str(project), timeout=timeout),
                "static project verify skips runtime arithmetic", stdout=b"", stderr=b"")
        require(invoke(compiler, "launch", str(project), timeout=timeout),
                "launch catches runtime arithmetic failure", code=1, stdout=b"",
                nonempty_stderr=True)
        manifest.write_text(
            "scarp-project: 1\nname: first-project\nentry: ../outside.srp\n",
            encoding="utf-8",
        )
        invalid = invoke(compiler, "verify", "--diagnostic-format=json",
                         str(project), timeout=timeout)
        require(invalid, "reject project path traversal", code=1, stdout=b"",
                nonempty_stderr=True)
        try:
            diagnostic = json.loads(invalid.stderr)
        except (UnicodeDecodeError, ValueError) as error:
            raise CliSmokeError("invalid manifest did not produce JSON diagnostic") from error
        if diagnostic.get("schema_version") != 1:
            raise CliSmokeError("invalid manifest diagnostic schema differs from v1")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    compiler = args.compiler.resolve()
    if not compiler.is_file():
        parser.error(f"compiler not found: {compiler}")
    try:
        smoke_test(compiler, args.timeout)
    except (CliSmokeError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
