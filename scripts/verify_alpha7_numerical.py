#!/usr/bin/env python3
"""Verify the independent v0.0.7-alpha.1 numerical programming workshop."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "tutorials" / "alpha7-numerical"
PIN = "996bd5b83c8cb26e98637563729f67bdacc61cd4"
VERSION = "0.0.7-alpha.1"
RELEASE = "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION
PROGRAMS = ("array_concat", "integer_reductions", "stable_softplus")
INVALID = {
    "mixed_array_types": 'print(array_concat([array: 1], [array: "x"]));',
    "gcd_one_argument": "print(integer_gcd(7));",
    "lcm_one_argument": "print(integer_lcm(7));",
    "softplus_scalar": "print(softplus(1.0));",
}


def check_inventory(folder: Path = WORKSHOP) -> None:
    metadata = json.loads((folder / "compiler-target.json").read_text(encoding="utf-8"))
    if metadata != {
        "version": VERSION, "release_tag": "v" + VERSION,
        "source_commit": PIN, "release_url": RELEASE, "status": "prerelease",
    }:
        raise ValueError("incorrect v0.0.7-alpha.1 workshop target")
    expected = {stem + suffix for stem in PROGRAMS for suffix in (".srp", ".stdout")}
    actual = {p.name for p in folder.iterdir() if p.suffix in (".srp", ".stdout", ".stdin")}
    if actual != expected:
        raise ValueError(f"fixture inventory mismatch: missing={expected - actual}, extra={actual - expected}")
    for name in sorted(expected):
        data = (folder / name).read_bytes()
        data.decode("utf-8")
        if not data.endswith(b"\n") or b"\r" in data or b"\0" in data:
            raise ValueError(f"noncanonical UTF-8/LF fixture: {name}")


def call(compiler: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([str(compiler), *args], cwd=ROOT, input=b"",
                          capture_output=True, timeout=30, check=False)


def require_success(result: subprocess.CompletedProcess[bytes], expected: bytes, label: str) -> None:
    if result.returncode != 0 or result.stderr or result.stdout != expected:
        raise ValueError(f"{label}: status={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}")


def require_rejection(result: subprocess.CompletedProcess[bytes], label: str) -> None:
    if result.returncode != 1 or result.stdout or not result.stderr:
        raise ValueError(f"{label}: expected exit 1, empty stdout and a diagnostic")
    report = json.loads(result.stderr.decode("utf-8"))
    if (not isinstance(report, dict) or report.get("schema_version") != 1
            or not isinstance(report.get("code"), str) or not report["code"].startswith("E")):
        raise ValueError(f"{label}: invalid structured diagnostic: {report!r}")


def verify(compiler: Path, source: Path) -> None:
    check_inventory()
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"],
                                   timeout=15).decode("ascii").strip()
    if head != PIN:
        raise ValueError(f"compiler source mismatch: {head}")
    require_success(call(compiler, "version"), f"scarp {VERSION}\n".encode("ascii"), "version")
    for stem in PROGRAMS:
        path = WORKSHOP / (stem + ".srp")
        require_success(call(compiler, "verify", str(path)), b"", stem + " verify")
        require_success(call(compiler, "exec", str(path)), path.with_suffix(".stdout").read_bytes(), stem + " exec")
    with tempfile.TemporaryDirectory(prefix="scarp-alpha7-numeric-") as tmp:
        for name, program in INVALID.items():
            path = Path(tmp) / (name + ".srp")
            path.write_bytes((program + "\n").encode("utf-8"))
            require_rejection(call(compiler, "verify", "--diagnostic-format=json", str(path)), name)
    print(f"PASS: {len(PROGRAMS)} numerical programs and {len(INVALID)} malformed calls.")


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
