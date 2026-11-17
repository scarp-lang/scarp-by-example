#!/usr/bin/env python3
"""Verify Scarp alpha.13 workshop against its published source and exact stdout."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_examples import ROOT, VerificationError, verify_one

WORKSHOP = ROOT / "tutorials" / "modern-collections"
TARGET = WORKSHOP / "compiler-target.json"
EXAMPLES = (
    "typed_dynamic_lists",
    "persistent_list_updates",
    "typed_maps",
    "persistent_maps",
    "map_projections",
    "typed_submission",
    "typed_propagation",
    "aggregate_resource_boundaries",
)
COPIES = tuple(
    (f"examples/{name}.{extension}", f"{name}.{extension}")
    for name in EXAMPLES
    for extension in ("srp", "stdout")
)


def verify_workshop(compiler: Path, compiler_source: Path) -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if not compiler.is_file():
        raise VerificationError(f"compiler does not exist: {compiler}")
    if not (compiler_source / ".git").exists():
        raise VerificationError("compiler-source must be an actual Git checkout")
    source_sha = subprocess.check_output(
        ["git", "-C", str(compiler_source), "rev-parse", "HEAD"],
        text=True,
        timeout=15,
    ).strip()
    if source_sha != target["source_commit"]:
        raise VerificationError("alpha.13 compiler checkout differs from published source pin")

    version = subprocess.run(
        [str(compiler), "version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=15,
        check=False,
    )
    expected_version = f"scarp {target['version']}\n".encode("ascii")
    if version.returncode or version.stdout != expected_version or version.stderr:
        raise VerificationError("alpha.13 compiler binary version does not match release")

    for upstream, local in COPIES:
        upstream_bytes = (compiler_source / upstream).read_bytes()
        local_bytes = (WORKSHOP / local).read_bytes()
        if upstream_bytes != local_bytes:
            raise VerificationError(f"upstream source or fixture changed: {upstream}")

    for name in EXAMPLES:
        verify_one(
            compiler,
            WORKSHOP / f"{name}.srp",
            WORKSHOP / f"{name}.stdout",
            timeout=20,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_workshop(args.compiler.resolve(), args.compiler_source.resolve())
    except (VerificationError, OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: alpha.13 immutable source, 8 upstream examples, static verify and exact stdout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
