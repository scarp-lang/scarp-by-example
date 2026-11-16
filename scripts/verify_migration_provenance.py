#!/usr/bin/env python3
"""Enforce byte-for-byte provenance of lessons imported from tagged compiler fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "migration-provenance.json"
PIN = ROOT / "docs" / "compiler-target.json"

SOURCE_FIELDS = ("compiler_source", "compiler_stdout", "course_source", "course_stdout")
PATH_PATTERN = re.compile(r"examples(?:/[a-z0-9][a-z0-9_-]*)+\.(?:srp|stdout)")


class ProvenanceError(ValueError):
    """Manifest or fixture changes invalidate the recorded published release provenance."""


def checked_path(root: Path, value: Any, suffix: str) -> Path:
    """Limit manifest paths to plain repository-local example source/output files."""
    if not isinstance(value, str) or not PATH_PATTERN.fullmatch(value):
        raise ProvenanceError(f"invalid example path: {value!r}")
    if not value.endswith(suffix) or any(part in (".", "..") for part in value.split("/")):
        raise ProvenanceError(f"wrong extension or path traversal: {value!r}")
    resolved_root = root.resolve()
    target = (resolved_root / value).resolve()
    if not target.is_relative_to(resolved_root):
        raise ProvenanceError(f"example path escapes the repository: {value!r}")
    if not target.is_file():
        raise ProvenanceError(f"missing example fixture: {value!r}")
    return target


def verify_provenance(
    manifest: dict[str, Any], target: dict[str, Any], compiler_root: Path, course_root: Path
) -> int:
    if manifest.get("schema_version") != 1:
        raise ProvenanceError("unsupported migration provenance schema")
    if (
        manifest.get("compiler_release") != target.get("release_tag")
        or manifest.get("compiler_source_commit") != target.get("source_commit")
    ):
        raise ProvenanceError("migration provenance differs from the pinned published compiler")
    entries = manifest.get("migrations")
    if not isinstance(entries, list) or not entries:
        raise ProvenanceError("migration provenance requires at least one mapped example")
    if not isinstance(manifest.get("compiler_source_commit"), str) or not re.fullmatch(
        r"[0-9a-f]{40}", manifest["compiler_source_commit"]
    ):
        raise ProvenanceError("invalid pinned compiler commit")
    seen_source: set[str] = set()
    seen_course: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != set(SOURCE_FIELDS):
            raise ProvenanceError(f"migration {index}: required source/output mapping is incomplete")
        for side in ("compiler", "course"):
            source = entry[side + "_source"]
            stdout = entry[side + "_stdout"]
            if not isinstance(source, str) or not isinstance(stdout, str):
                raise ProvenanceError(f"migration {index}: paths must be strings")
            if not PATH_PATTERN.fullmatch(source) or not PATH_PATTERN.fullmatch(stdout):
                raise ProvenanceError(f"migration {index}: invalid example path")
            if source.removesuffix(".srp") != stdout.removesuffix(".stdout"):
                raise ProvenanceError(f"migration {index}: source and stdout names do not match")
            seen = seen_source if side == "compiler" else seen_course
            if source in seen:
                raise ProvenanceError(f"migration {index}: duplicate {side} source {source}")
            seen.add(source)
        for ext in ("source", "stdout"):
            suffix = ".srp" if ext == "source" else ".stdout"
            src = checked_path(compiler_root, entry["compiler_" + ext], suffix)
            dst = checked_path(course_root, entry["course_" + ext], suffix)
            original = src.read_bytes()
            copied = dst.read_bytes()
            if original != copied:
                upstream = hashlib.sha256(original).hexdigest()[:16]
                local = hashlib.sha256(copied).hexdigest()[:16]
                raise ProvenanceError(
                    f"migration {index}: {ext} diverged from tagged compiler "
                    f"({entry['course_' + ext]}, upstream sha256={upstream}, local sha256={local})"
                )
    return len(entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path, help="tag-pinned compiler checkout")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--target", type=Path, default=PIN, help="exact release pin manifest")
    args = parser.parse_args(argv)
    try:
        target = json.loads(args.target.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        commit = subprocess.run(
            ["git", "-C", str(args.compiler), "rev-parse", "HEAD"],
            check=False, capture_output=True, text=True,
        )
        if commit.returncode != 0 or commit.stdout.strip() != target["source_commit"]:
            raise ProvenanceError(
                "compiler checkout is not the exact published source commit "
                + str(target["source_commit"])
            )
        count = verify_provenance(manifest, target, args.compiler, ROOT)
    except (ProvenanceError, OSError, json.JSONDecodeError, KeyError) as error:
        print(f"FAIL: migrated example provenance: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {count} migrated Scarp source/stdout pairs match exact published compiler bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
