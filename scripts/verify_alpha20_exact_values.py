#!/usr/bin/env python3
"""Validate the independent published alpha.20 exact-values workshop."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "tutorials" / "alpha20-exact-values"
PIN = "b1a9347f93540fdf95b0ddecba4adc55a3b4bb98"
VERSION = "0.0.6-alpha.20"
PROGRAMS = ("decimal_exact", "decimal_literals", "tuple_index_updates",
            "tuple_ordering", "tuple_snapshots")
UPSTREAM = {
    "decimal_exact.srp": "4890c10b15d7a8e827bb9549e987a0a2eb0d973d",
    "decimal_exact.stdout": "d1f149f581b635d7f5ec6a6604805c2146bbe803",
    "tuple_index_updates.srp": "9d89b922449df3f8111182cfdd99fd9c14ff0ffa",
    "tuple_index_updates.stdout": "c166e32d29280009cc5633270bb04b9ed3c31181",
    "tuple_ordering.srp": "d87d59df5b9f77f8c72087b12b12d2e3eabcb849",
    "tuple_ordering.stdout": "271474188fea2eaadf632f5039d964f9962fff68"
}
INVALID = {
    "decimal_float": ("print(0.1d + 0.2);", "E0015"),
    "decimal_integer": ("print(1d + 1);", "E0015"),
    "immutable_tuple": ("bind t=(1,2); t[0]=9;", "E0013"),
    "dynamic_index": ("var t=(1,2); var i=0; t[i]=3;", "E0059"),
    "out_of_range": ("var t=(1,2); t[2]=3;", "E0059"),
    "wrong_member_type": ('var t=(1,2); t[0]="no";', "E0015"),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def check_inventory(folder: Path = WORKSHOP) -> None:
    metadata = json.loads((folder / "compiler-target.json").read_text(encoding="utf-8"))
    if metadata != {
        "version": VERSION, "release_tag": "v" + VERSION,
        "source_commit": PIN, "status": "prerelease",
        "release_url": "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION,
    }:
        raise ValueError("incorrect alpha.20 workshop target")
    if json.loads((folder / "upstream-blobs.json").read_text(encoding="utf-8")) != UPSTREAM:
        raise ValueError("upstream blob manifest differs from published inventory")
    for suffix in (".srp", ".stdout"):
        if {p.stem for p in folder.glob("*" + suffix)} != set(PROGRAMS):
            raise ValueError(f"incomplete or unexpected {suffix} inventory")
    for name, sha in UPSTREAM.items():
        if git_blob((folder / name).read_bytes()) != sha:
            raise ValueError(f"upstream blob mismatch: {name}")
    for stem in PROGRAMS:
        for suffix in (".srp", ".stdout"):
            data = (folder / (stem + suffix)).read_bytes()
            data.decode("utf-8")
            if not data.endswith(b"\n") or b"\r\n" in data:
                raise ValueError(f"noncanonical UTF-8/LF fixture: {stem}{suffix}")


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
    if not isinstance(report, dict) or report.get("schema_version") != 1 or report.get("code") != code:
        raise ValueError(f"{label}: expected schema 1 diagnostic {code}, got {report!r}")


def verify(compiler: Path, source: Path) -> None:
    check_inventory()
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"],
                                   timeout=15).decode("ascii").strip()
    if head != PIN:
        raise ValueError(f"compiler source mismatch: {head}")
    require_success(call(compiler, "version"), f"scarp {VERSION}\n".encode(), "version")
    for stem in PROGRAMS:
        path = WORKSHOP / (stem + ".srp")
        require_success(call(compiler, "verify", str(path)), b"", stem + " verify")
        require_success(call(compiler, "exec", str(path)),
                        path.with_suffix(".stdout").read_bytes(), stem + " exec")
    with tempfile.TemporaryDirectory(prefix="scarp-alpha20-") as tmp:
        for name, (program, code) in INVALID.items():
            path = Path(tmp) / (name + ".srp")
            path.write_bytes((program + "\n").encode("utf-8"))
            require_diagnostic(call(compiler, "verify", "--diagnostic-format=json", str(path)),
                               code, name)
    print(f"PASS: {len(PROGRAMS)} alpha.20 programs and {len(INVALID)} diagnostic cases.")


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
