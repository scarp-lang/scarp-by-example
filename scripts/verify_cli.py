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
    """Observed CLI behavior differs from the pinned published CLI contract."""


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
    """Prove published source-pinned commands, static checks and project workflows."""
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
    target = json.loads((ROOT / "docs/compiler-target.json").read_text(encoding="utf-8"))
    if capabilities.get("version") != target["version"] or capabilities.get("project_workflow") is not True:
        raise CliSmokeError("diagnose --json: expected pinned published compiler capabilities")
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
    project_inspection_smoke(compiler, timeout)
    symbol_navigation_smoke(compiler, timeout)
    print("PASS: Scarp-first CLI, static project/metadata validation, symbol navigation and launch.")


def project_smoke(compiler: Path, timeout: int) -> None:
    """Test real project scaffolding, static verify, launch and rejection paths."""
    expected = read_expected_stdout(ROOT / "examples/01-basics/01-hello.stdout")
    checked_in = ROOT / "tutorials" / "first-project"
    if (checked_in / "expected.stdout").read_bytes() != expected:
        raise CliSmokeError("checked-in project fixture disagrees with hello lesson")
    require(invoke(compiler, "verify", str(checked_in), timeout=timeout),
            "verify checked-in sample project", stdout=b"", stderr=b"")
    require(invoke(compiler, "launch", str(checked_in), timeout=timeout),
            "launch checked-in sample project", stdout=expected, stderr=b"")
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


def project_inspection_smoke(compiler: Path, timeout: int) -> None:
    """Alpha.5: source and project-directory imports have identical read-only metadata."""
    project = ROOT / "tutorials/module-inspection"
    source = project / "src/main.srp"
    expected = read_expected_stdout(project / "expected.stdout")
    require(invoke(compiler, "verify", str(project), timeout=timeout),
            "verify two-module project", stdout=b"", stderr=b"")
    require(invoke(compiler, "launch", str(project), timeout=timeout),
            "launch two-module project", stdout=expected, stderr=b"")
    file_inspect = invoke(compiler, "inspect", "modules", "--json", str(source), timeout=timeout)
    project_inspect = invoke(compiler, "inspect", "modules", "--json", str(project), timeout=timeout)
    old_alias = invoke(compiler, "modules", "--json", str(project), timeout=timeout)
    for label, result in (("file modules", file_inspect),
                          ("project modules", project_inspect),
                          ("legacy project modules", old_alias)):
        require(result, label, nonempty_stdout=True, stderr=b"")
    try:
        from_file = json.loads(file_inspect.stdout)
        from_project = json.loads(project_inspect.stdout)
        from_alias = json.loads(old_alias.stdout)
    except (ValueError, UnicodeError) as error:
        raise CliSmokeError("module inspection did not produce schema-v1 JSON") from error
    if (from_file.get("schema_version") != 1
            or not isinstance(from_file.get("modules"), list)
            or len(from_file["modules"]) != 2):
        raise CliSmokeError("project module inspection: unexpected two-module inventory")
    # Schema-v1 module.path is a loader-provided *display label*, not a stable
    # identity. Directory/file entrypaths can display differently on Windows.
    # Preserve every other field: graph IDs, spans, symbol metadata and edges.
    def semantic_inventory(inventory: dict) -> dict:
        modules = inventory.get("modules")
        if not isinstance(modules, list):
            raise CliSmokeError("module inspection: missing modules array")
        for module in modules:
            if not isinstance(module, dict) or not isinstance(module.get("path"), str):
                raise CliSmokeError("module inspection: missing display path")
            if not module["path"].replace(chr(92), "/").endswith(".srp"):
                raise CliSmokeError("module inspection: unexpected source label")
        return {**inventory, "modules": [
            {key: value for key, value in module.items() if key != "path"}
            for module in modules
        ]}

    expected_graph = semantic_inventory(from_file)
    for label, metadata in (("project directory", from_project),
                            ("legacy project alias", from_alias)):
        actual = semantic_inventory(metadata)
        if actual != expected_graph:
            keys = sorted(
                key for key in set(actual) | set(expected_graph)
                if actual.get(key) != expected_graph.get(key)
            )
            raise CliSmokeError(f"{label}: non-display metadata differs in {keys}")

    # Static inspection must not evaluate ordinary runtime statements.
    with tempfile.TemporaryDirectory(prefix="scarp-inspection-smoke-") as directory:
        folder = Path(directory)
        (folder / "Scarp.project").write_text(
            "scarp-project: 1\nname: inspect-only\nentry: src/main.srp\n", encoding="utf-8"
        )
        (folder / "src").mkdir()
        (folder / "src/main.srp").write_text("print(1 / 0);\n", encoding="utf-8")
        inspection = invoke(compiler, "inspect", "modules", "--json", str(folder), timeout=timeout)
        require(inspection, "inspection must not execute runtime division",
                nonempty_stdout=True, stderr=b"")
        if json.loads(inspection.stdout).get("schema_version") != 1:
            raise CliSmokeError("static inspection schema changed")
        require(invoke(compiler, "launch", str(folder), timeout=timeout),
                "launch does execute runtime division", code=1, stdout=b"",
                nonempty_stderr=True)
        # Manifest path traversal must fail without leaking a partial inventory.
        (folder / "Scarp.project").write_text(
            "scarp-project: 1\nname: inspect-only\nentry: ../outside.srp\n",
            encoding="utf-8",
        )
        invalid = invoke(compiler, "inspect", "modules", "--json",
                         "--diagnostic-format=json", str(folder), timeout=timeout)
        require(invalid, "project inspection rejects traversal",
                code=1, stdout=b"", nonempty_stderr=True)
        try:
            problem = json.loads(invalid.stderr)
        except (ValueError, UnicodeError) as error:
            raise CliSmokeError("bad project manifest did not provide JSON diagnostic") from error
        if problem.get("schema_version") != 1:
            raise CliSmokeError("invalid project manifest diagnostic schema changed")


def validate_navigation_inventory(payload: bytes, kind: str) -> dict:
    """Check the published schema before using any version-local symbol IDs."""
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeError) as error:
        raise CliSmokeError(f"inspect {kind}: invalid JSON") from error
    expected = {
        "schema_version": 1,
        "kind": f"scarp.{kind}",
        "span_encoding": "utf-8-bytes",
        "column_encoding": "unicode-scalar",
        "position_base": 1,
    }
    if not isinstance(data, dict) or any(data.get(k) != v for k, v in expected.items()):
        raise CliSmokeError(f"inspect {kind}: unsupported schema or position encoding")
    if not isinstance(data.get("files"), list) or not isinstance(data.get("symbols"), list):
        raise CliSmokeError(f"inspect {kind}: missing file or symbol inventory")
    if not all(isinstance(f, dict) and isinstance(f.get("path"), str) and
               isinstance(f.get("id"), int) and not isinstance(f.get("id"), bool)
               for f in data["files"]):
        raise CliSmokeError(f"inspect {kind}: malformed file records")
    ids = []
    for symbol in data["symbols"]:
        if not isinstance(symbol, dict) or not isinstance(symbol.get("id"), int) or (
            isinstance(symbol.get("id"), bool)
        ) or not isinstance(symbol.get("name"), str) or not isinstance(symbol.get("kind"), str):
            raise CliSmokeError(f"inspect {kind}: malformed symbol")
        ids.append(symbol["id"])
    if len(ids) != len(set(ids)):
        raise CliSmokeError(f"inspect {kind}: duplicate symbol ids")
    if kind == "references":
        references = data.get("references")
        if not isinstance(references, list):
            raise CliSmokeError("inspect references: missing reference inventory")
        for ref in references:
            if (not isinstance(ref, dict) or ref.get("target") not in ids
                    or not isinstance(ref.get("kind"), str)
                    or not isinstance(ref.get("location"), dict)):
                raise CliSmokeError("inspect references: dangling or malformed reference")
    return data


def symbol_navigation_smoke(compiler: Path, timeout: int) -> None:
    """Alpha.6 symbol/reference inspection must be static and project-aware."""
    project = ROOT / "tutorials/module-inspection"
    source = project / "src/main.srp"
    for kind in ("symbols", "references"):
        project_result = invoke(compiler, "inspect", kind, "--json", str(project), timeout=timeout)
        source_result = invoke(compiler, "inspect", kind, "--json", str(source), timeout=timeout)
        require(project_result, f"project inspect {kind}", nonempty_stdout=True, stderr=b"")
        require(source_result, f"file inspect {kind}", nonempty_stdout=True, stderr=b"")
        project_data = validate_navigation_inventory(project_result.stdout, kind)
        source_data = validate_navigation_inventory(source_result.stdout, kind)
        # Display path spelling may differ when inspecting a file vs a directory;
        # symbol membership and reference counts must still describe one graph.
        for label, data in (("project", project_data), ("file", source_data)):
            if len(data["files"]) != 2:
                raise CliSmokeError(f"{kind}: {label} should include both source files")
            names = {s["name"] for s in data["symbols"]}
            if not {"math", "answer"}.issubset(names):
                raise CliSmokeError(f"{kind}: {label} lost the imported public binding")
        if {(s["name"], s["kind"]) for s in project_data["symbols"]} != {
            (s["name"], s["kind"]) for s in source_data["symbols"]
        }:
            raise CliSmokeError(f"{kind}: project and entrypoint symbols disagree")
        if kind == "references":
            if not project_data["references"] or len(project_data["references"]) != len(
                source_data["references"]
            ):
                raise CliSmokeError("references: project and file use sites disagree")

    with tempfile.TemporaryDirectory(prefix="scarp-symbols-smoke-") as directory:
        witness = Path(directory) / "static-only.srp"
        witness.write_text("print(1 / 0);\n", encoding="utf-8")
        for kind in ("symbols", "references"):
            checked = invoke(compiler, "inspect", kind, "--json", str(witness), timeout=timeout)
            require(checked, f"static {kind} does not run program", nonempty_stdout=True,
                    stderr=b"")
            validate_navigation_inventory(checked.stdout, kind)
        witness.write_text("print(undefined_symbol);\n", encoding="utf-8")
        for kind in ("symbols", "references"):
            invalid = invoke(compiler, "inspect", kind, "--json", str(witness), timeout=timeout)
            require(invalid, f"{kind} rejects unbound name without partial JSON",
                    code=1, stdout=b"", nonempty_stderr=True)


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
