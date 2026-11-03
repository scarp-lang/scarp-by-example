"""Ensure imported course modules are real, portable and reachable from lessons."""

from __future__ import annotations

import re
import unittest
from pathlib import Path, PurePosixPath

from verify_examples import EXAMPLES

CHAPTER = EXAMPLES / "05-modules"
IMPORT = re.compile(r'(?m)^\s*import\s+"([^"]+)"\s+as\s+\w+\s*;')


def imports_in(source: Path) -> list[Path]:
    """Locate source-relative imports while enforcing the course's portable layout."""
    text = source.read_text(encoding="utf-8")
    imported = []
    for match in IMPORT.finditer(text):
        spec = match.group(1)
        path = PurePosixPath(spec)
        if (not spec.endswith(".srp") or "\\" in spec
                or path.is_absolute() or ".." in path.parts):
            raise ValueError(f"{source}: non-portable import {spec!r}")
        target = source.parent.joinpath(*path.parts)
        if not target.is_file():
            raise ValueError(f"{source}: missing import {spec!r}")
        imported.append(target)
    return imported


class ModuleImportTests(unittest.TestCase):
    def test_every_module_import_points_to_a_file(self):
        for source in CHAPTER.rglob("*.srp"):
            with self.subTest(source=source.name):
                imports_in(source)

    def test_every_helper_is_reachable_from_an_entry_lesson(self):
        entries = sorted(CHAPTER.glob("[0-9][0-9]-*.srp"))
        self.assertGreaterEqual(len(entries), 5)
        visited: set[Path] = set()
        stack = list(entries)
        while stack:
            source = stack.pop()
            if source in visited:
                continue
            visited.add(source)
            stack.extend(imports_in(source))
        helpers = set((CHAPTER / "_support").glob("*.srp"))
        self.assertTrue(helpers, "expected some imported helper modules")
        self.assertTrue(helpers.issubset(visited),
                        f"unused helper files: {sorted(helpers - visited)}")


if __name__ == "__main__":
    unittest.main()
