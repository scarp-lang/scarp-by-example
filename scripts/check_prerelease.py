#!/usr/bin/env python3
"""Guard the first editorial prerelease against an incomplete or unpinned course.

Only the prerelease workflow invokes this milestone-specific check. Ordinary
course CI intentionally stays version-agnostic for later lesson additions.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from verify_examples import ROOT, discover_examples

TAG = "v0.1.0-alpha.1"
COMPILER_SHA = "7715c28df09c7703b39e14fddb963275b25df476"


def valid_prerelease_tag(tag: str) -> bool:
    return re.fullmatch(r"v\d+\.\d+\.\d+-(?:alpha|beta|rc)\.\d+", tag) is not None


def check_prerelease(root: Path = ROOT) -> str:
    if not valid_prerelease_tag(TAG):
        raise ValueError(f"stable or malformed tag rejected: {TAG}")
    target = json.loads((root / "docs/compiler-target.json").read_text(encoding="utf-8"))
    if (target.get("source_commit") != COMPILER_SHA
            or target.get("version") != "0.0.5-alpha.3"
            or target.get("status") != "prerelease"):
        raise ValueError("the compiler pin no longer matches the course milestone")
    lessons = discover_examples(root / "examples")
    if len(lessons) != 50:
        raise ValueError(f"expected 50 executable lessons; found {len(lessons)}")
    if sum(src.parent.name == "05-modules" for src, _ in lessons) != 5:
        raise ValueError("expected five module chapter lessons")
    required = (
        "LICENSE", "LICENSE-APACHE-2.0", "THIRD_PARTY_NOTICES.md", "README.md",
        "docs/hi/README.md", "docs/cli-quickstart.md", "docs/hi/cli-quickstart.md",
        "scripts/verify_examples.py", "scripts/verify_cli.py",
        f"docs/releases/{TAG}.md",
    )
    for rel in required:
        if not (root / rel).is_file():
            raise ValueError(f"required release component missing: {rel}")
    english = (root / "README.md").read_text(encoding="utf-8")
    hindi = (root / "docs/hi/README.md").read_text(encoding="utf-8")
    notes = (root / f"docs/releases/{TAG}.md").read_text(encoding="utf-8")
    if "50 lessons in Hindi" not in english or "कुल: 50 पाठ" not in hindi:
        raise ValueError("the lesson count is inconsistent across languages")
    if not all(part in notes for part in
               (TAG, "course prerelease", "not a Scarp compiler release", COMPILER_SHA)):
        raise ValueError("release notes must identify scope, version and exact pin")
    return f"PASS: {TAG}, 50 lessons, compiler SHA {COMPILER_SHA[:12]}"


def main() -> int:
    try:
        print(check_prerelease())
        return 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
