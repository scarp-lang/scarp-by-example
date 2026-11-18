#!/usr/bin/env python3
"""Test published alpha.14 parser diagnostics and executable repairs on real Scarp."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, read_expected_stdout, verify_one

VERSION = "0.0.6-alpha.14"
PIN = "43627b74af5fccccc5e233e98207413983ebafc1"
DIRECTORY = ROOT / "tutorials" / "structured-patterns" / "diagnostics"
MANIFEST = DIRECTORY / "cases.json"
IDS = (
    "missing-tuple-comma",
    "missing-record-comma",
    "missing-array-comma",
    "wrong-inner-delimiter",
    "wrong-record-delimiter",
    "duplicate-comma",
    "empty-group",
    "missing-closer",
    "singleton-trailing-comma",
)


def position(source: str, byte_offset: int) -> dict[str, int]:
    """Map a checked UTF-8 byte boundary to a one-based Unicode-scalar position."""
    raw = source.encode("utf-8")
    if not 0 <= byte_offset <= len(raw):
        raise VerificationError("diagnostic span outside source")
    try:
        prefix = raw[:byte_offset].decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationError("diagnostic span splits a UTF-8 scalar") from error
    lines = prefix.split("\n")
    return {"line": len(lines), "column": len(lines[-1]) + 1}


def load_cases(root: Path = ROOT) -> list[dict]:
    """Check source identity, expected coordinates and fixture structure before CLI runs."""
    folder = root / "tutorials/structured-patterns/diagnostics"
    manifest = json.loads((folder / "cases.json").read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != 1
        or manifest.get("version") != VERSION
        or manifest.get("release_tag") != "v" + VERSION
        or manifest.get("source_commit") != PIN
        or manifest.get("source_reference")
        != "https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.14/tests/pattern_separator_diagnostics.rs"
        or not isinstance(manifest.get("cases"), list)
        or tuple(c.get("id") for c in manifest["cases"]) != IDS
    ):
        raise VerificationError("published alpha.14 diagnostic manifest identity changed")
    cases = manifest["cases"]
    for case in cases:
        name = case["id"]
        if not re.fullmatch(r"[a-z]+(?:-[a-z]+)*", name):
            raise VerificationError("invalid diagnostic case ID")
        raw = (folder / f"{name}.invalid.srp").read_bytes()
        fixed = (folder / f"{name}.fixed.srp").read_bytes()
        expected = read_expected_stdout(folder / f"{name}.stdout")
        if (
            b"\r" in raw or b"\r" in fixed or not raw or not fixed
            or not fixed.endswith(b"\n") or not expected.endswith(b"\n")
            or len(raw) > 4096 or len(fixed) > 4096
        ):
            raise VerificationError(f"invalid source or repair fixture: {name}")
        source = raw.decode("utf-8")
        fixed.decode("utf-8")
        bounds = case["span"]
        if (
            not isinstance(bounds, list) or len(bounds) != 2
            or any(type(value) is not int for value in bounds)
            or not 0 <= bounds[0] <= bounds[1] <= len(raw)
            or case.get("start") != position(source, bounds[0])
            or case.get("end") != position(source, bounds[1])
            or raw[bounds[0]:bounds[1]].decode("utf-8") != case.get("token")
        ):
            raise VerificationError(f"diagnostic byte span or source drift: {name}")
        for key in ("title", "title_hi", "message_part", "explanation", "explanation_hi"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise VerificationError(f"missing {key} for {name}")
    return cases


def check_diagnostic(case: dict, source: Path, result: subprocess.CompletedProcess[bytes]) -> None:
    """Require the versioned schema, exact UTF-8 span and native no-output contract."""
    if result.returncode != 1 or result.stdout:
        raise VerificationError(f"{case['id']}: invalid program must fail without stdout")
    try:
        text = result.stderr.decode("utf-8")
        diagnostic = json.loads(text)
    except (UnicodeDecodeError, ValueError) as error:
        raise VerificationError(f"{case['id']}: expected one UTF-8 JSON diagnostic") from error
    if not isinstance(diagnostic, dict):
        raise VerificationError(f"{case['id']}: expected one diagnostic object")
    primary = diagnostic.get("primary")
    if (
        diagnostic.get("schema_version") != 1
        or diagnostic.get("severity") != "error"
        or diagnostic.get("code") != "E0004"
        or diagnostic.get("span_encoding") != "utf-8-bytes"
        or diagnostic.get("column_encoding") != "unicode-scalar"
        or diagnostic.get("position_base") != 1
        or not isinstance(primary, dict)
        or not isinstance(primary.get("path"), str)
        or primary["path"].replace("\\", "/").split("/")[-1] != source.name
        or primary.get("span") != case["span"]
        or primary.get("start") != case["start"]
        or primary.get("end") != case["end"]
        or not isinstance(diagnostic.get("message"), str)
        or case["message_part"] not in diagnostic["message"]
        or not isinstance(diagnostic.get("related"), list)
    ):
        raise VerificationError(
            f"{case['id']}: compiler diagnostic code, message, UTF-8 span or schema differs"
        )


def verify_diagnostics(compiler: Path, compiler_source: Path) -> None:
    cases = load_cases()
    if not compiler.is_file():
        raise VerificationError(f"compiler binary not found: {compiler}")
    if not (compiler_source / ".git").exists():
        raise VerificationError("compiler-source must be an actual Git checkout")
    sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"], timeout=15,
    ).decode("ascii").strip()
    if sha != PIN:
        raise VerificationError("diagnostic workshop compiler checkout differs from alpha.14 pin")
    version = subprocess.run(
        [str(compiler), "version"],
        check=False, timeout=15,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if version.returncode or version.stdout != f"scarp {VERSION}\n".encode() or version.stderr:
        raise VerificationError("diagnostic workshop requires the exact published alpha.14 binary")

    for case in cases:
        name = case["id"]
        invalid = DIRECTORY / f"{name}.invalid.srp"
        result = subprocess.run(
            [str(compiler), "verify", "--diagnostic-format=json", str(invalid)],
            cwd=ROOT, check=False, timeout=20,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check_diagnostic(case, invalid, result)
        verify_one(compiler, DIRECTORY / f"{name}.fixed.srp",
                   DIRECTORY / f"{name}.stdout", timeout=20)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--compiler-source", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        verify_diagnostics(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, KeyError, TypeError,
            UnicodeError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(IDS)} alpha.14 E0004 UTF-8 diagnostic spans and runnable repairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
