#!/usr/bin/env python3
"""Verify the immutable 55-lesson alpha.14-compatible course snapshot.

Newer active lessons must never silently be checked with historical compilers.
The baseline records exact Git blob SHA-1 values; all current source and stdout
files from the snapshot must remain present and byte-identical.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from verify_examples import ROOT, EXAMPLES, VerificationError, read_expected_stdout, verify_one

MANIFEST = ROOT / "docs" / "historical-alpha14-course.json"
COMPILER_PIN = "43627b74af5fccccc5e233e98207413983ebafc1"
COURSE_BASELINE = "03e0c93807e509e0a3a88da37e7ea4b3f6ef98d8"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PATH_RE = re.compile(r"^examples/[0-9]{2}-[a-z0-9-]+/[0-9]{2}-[a-z0-9-]+\.srp$")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\\0".encode("ascii") + data).hexdigest()


def validate_manifest(document: dict, root: Path = ROOT) -> list[tuple[Path, Path]]:
    if not isinstance(document, dict) or (
        document.get("schema_version") != 1
        or document.get("release_tag") != "v0.0.6-alpha.14"
        or document.get("compiler_source_commit") != COMPILER_PIN
        or document.get("course_baseline_commit") != COURSE_BASELINE
        or not isinstance(document.get("lessons"), list)
        or len(document["lessons"]) != 55
    ):
        raise VerificationError("historical alpha.14 course manifest identity or count changed")

    seen = set()
    pairs: list[tuple[Path, Path]] = []
    for item in document["lessons"]:
        if not isinstance(item, dict) or set(item) != {
            "source", "source_blob", "stdout", "stdout_blob"
        }:
            raise VerificationError("invalid historical course inventory record")
        path = item["source"]
        if not isinstance(path, str) or not PATH_RE.fullmatch(path) or path in seen:
            raise VerificationError("invalid or duplicate historical lesson path")
        seen.add(path)
        stdout_path = path[:-4] + ".stdout"
        if item["stdout"] != stdout_path or any(
            not isinstance(item[key], str) or not SHA_RE.fullmatch(item[key])
            for key in ("source_blob", "stdout_blob")
        ):
            raise VerificationError("historical lesson source/output pairing invalid")
        source = root / path
        output = root / stdout_path
        if git_blob_sha(source.read_bytes()) != item["source_blob"]:
            raise VerificationError(f"historical lesson source differs from baseline: {path}")
        if git_blob_sha(output.read_bytes()) != item["stdout_blob"]:
            raise VerificationError(f"historical lesson stdout differs from baseline: {stdout_path}")
        if source.with_suffix(".stdin").exists():
            raise VerificationError("historical alpha.14 lessons unexpectedly require stdin")
        read_expected_stdout(output)
        pairs.append((source, output))
    if len({source.parent.name for source, _ in pairs}) != 6:
        raise VerificationError("historical course must retain six original chapters")
    return sorted(pairs)


def verify_historical_course(compiler: Path) -> int:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pairs = validate_manifest(document)
    if not compiler.is_file():
        raise VerificationError(f"compiler executable missing: {compiler}")
    for source, stdout in pairs:
        verify_one(compiler, source, stdout, timeout=20)
    return len(pairs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    args = parser.parse_args()
    try:
        count = verify_historical_course(args.compiler.resolve())
    except (VerificationError, OSError, ValueError, TypeError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {count} frozen alpha.14 course lessons match baseline Git blobs and stdout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
