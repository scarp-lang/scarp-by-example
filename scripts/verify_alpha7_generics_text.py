#!/usr/bin/env python3
"""Verify the independently pinned Alpha.3 generics and text workshop."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "tutorials" / "alpha7-generics-text"
PIN = "44a3bb0a91e67570e46ce058a3f6211f8e5db0f5"
VERSION = "0.0.7-alpha.3"
PROGRAMS = (
    "generic_values", "generic_constraints", "contextual_inference",
    "generic_option", "generic_result", "string_operators", "text_snapshots",
)
UPSTREAM = {
    "string_operators.srp": "e313b914b819d9e94fea87938122bb1317e42f81",
    "string_operators.stdout": "dc5a3ecb096da9b000957e18689287154ba0e06f",
}
INVALID = {
    "ambiguous": (
        "pure funcra f<T>() -> list<T> { return [list: <T>]; } print(f());",
        "E0086",
    ),
    "conflicting": (
        "pure funcra f<T>(a:T,b:T)->T{return a;} f(1,2.0);",
        "E0086",
    ),
    "numeric_string": (
        'pure funcra f<T: Numeric>(a:T)->T{return a*a;} f("text");',
        "E0086",
    ),
    "option_nonexhaustive": (
        "pure funcra get<T>(x:option<T>)->boolean{match on x{case Some(v){return true;}}}",
        "E0076",
    ),
    "string_integer_add": ('print("a"+1);', "E0015"),
    "integer_left_repeat": ('print(2*"a");', "E0015"),
}

def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def check_inventory(folder: Path = WORKSHOP) -> None:
    metadata = json.loads((folder / "compiler-target.json").read_text(encoding="utf-8"))
    if metadata != {
        "version": VERSION, "release_tag": "v" + VERSION, "source_commit": PIN,
        "release_url": "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION,
        "status": "prerelease",
    }:
        raise ValueError("incorrect Alpha.3 workshop target")
    for suffix in (".srp", ".stdout"):
        actual = {p.name for p in folder.glob("*" + suffix) if p.is_file()}
        expected = {stem + suffix for stem in PROGRAMS}
        if actual != expected:
            raise ValueError(f"unexpected {suffix} inventory: {actual ^ expected}")
        for name in sorted(expected):
            data = (folder / name).read_bytes()
            data.decode("utf-8")
            if not data.endswith(b"\n") or b"\r" in data or data.startswith(b"\xef\xbb\xbf"):
                raise ValueError(f"noncanonical UTF-8/LF fixture: {name}")
            if name in UPSTREAM and git_blob(data) != UPSTREAM[name]:
                raise ValueError(f"upstream blob mismatch: {name}")

def call(compiler: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([str(compiler), *args], cwd=ROOT, input=b"",
                          capture_output=True, timeout=30, check=False)

def require_success(result: subprocess.CompletedProcess[bytes],
                    expected: bytes, label: str) -> None:
    if result.returncode != 0 or result.stderr or result.stdout != expected:
        raise ValueError(f"{label}: status={result.returncode}, "
                         f"stdout={result.stdout!r}, stderr={result.stderr!r}")

def require_diagnostic(result: subprocess.CompletedProcess[bytes],
                       code: str, label: str) -> None:
    if result.returncode != 1 or result.stdout:
        raise ValueError(f"{label}: expected exit 1 and empty stdout")
    report = json.loads(result.stderr.decode("utf-8"))
    if (not isinstance(report, dict) or report.get("schema_version") != 1
            or report.get("code") != code):
        raise ValueError(f"{label}: expected schema 1 diagnostic {code}, got {report!r}")

def verify(compiler: Path, source: Path) -> None:
    check_inventory()
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"],
                                   timeout=15).decode("ascii").strip()
    if head != PIN:
        raise ValueError(f"compiler source mismatch: {head}")
    for name, sha in UPSTREAM.items():
        upstream = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", f"{PIN}:examples/{name}"], timeout=15
        ).decode("ascii").strip()
        if upstream != sha:
            raise ValueError(f"compiler upstream blob mismatch: {name}")
    require_success(call(compiler, "version"), f"scarp {VERSION}\n".encode(), "version")
    for stem in PROGRAMS:
        path = WORKSHOP / (stem + ".srp")
        require_success(call(compiler, "verify", str(path)), b"", stem + " verify")
        require_success(call(compiler, "exec", str(path)),
                        path.with_suffix(".stdout").read_bytes(), stem + " exec")
    with tempfile.TemporaryDirectory(prefix="scarp-alpha7-generics-") as temp:
        for name, (program, code) in INVALID.items():
            path = Path(temp) / (name + ".srp")
            path.write_bytes((program + "\n").encode("utf-8"))
            require_diagnostic(call(compiler, "verify", "--diagnostic-format=json", str(path)),
                               code, name)
    print(f"PASS: {len(PROGRAMS)} Alpha.3 programs and {len(INVALID)} diagnostic cases.")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify(args.compiler.resolve(), args.compiler_source.resolve())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
