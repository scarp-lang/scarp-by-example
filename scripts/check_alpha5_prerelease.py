#!/usr/bin/env python3
"""Gate course v0.1.0-alpha.5 against its exact, published compiler milestone.

This editorial course release is independent of Scarp compiler releases.
The workflow additionally checks both successful main-branch Actions runs on
the identical SHA before it can create this immutable GitHub prerelease.
"""

from __future__ import annotations

import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from build_site import build
from check_prerelease import valid_prerelease_tag
from guided_labs import read_labs
from lesson_notes import read_hindi_notes
from practice_questions import read_practice_questions
from source_explorer import load_reference_map
from verify_examples import ROOT, discover_examples

TAG = "v0.1.0-alpha.5"
COMPILER_TAG = "v0.0.6-alpha.2"
COMPILER_SHA = "398b8ff705154a02423fe458ce3a427401e81e31"
LESSON_COUNT = 52
PAGE_COUNT = 69


def check_alpha5(root: Path = ROOT) -> str:
    if not valid_prerelease_tag(TAG):
        raise ValueError(f"stable or malformed prerelease tag: {TAG}")
    target = json.loads((root / "docs/compiler-target.json").read_text(encoding="utf-8"))
    if (target.get("release_tag") != COMPILER_TAG
            or target.get("source_commit") != COMPILER_SHA
            or target.get("version") != COMPILER_TAG.removeprefix("v")
            or target.get("status") != "prerelease"
            or target.get("release_url") !=
            "https://github.com/scarp-lang/scarp/releases/tag/" + COMPILER_TAG):
        raise ValueError("published alpha.2 compiler pin does not match this course milestone")

    pairs = discover_examples(root / "examples")
    chapters = {src.parent.name for src, _ in pairs}
    if len(pairs) != LESSON_COUNT or len(chapters) != 6:
        raise ValueError(f"expected {LESSON_COUNT} lessons across six chapters")
    if sum(src.parent.name == "02-control-flow" for src, _ in pairs) != 4:
        raise ValueError("the fourth control-flow lesson is missing")
    exercise = root / "examples/02-control-flow/04-nested-repeat.srp"
    stdout = exercise.with_suffix(".stdout")
    if (not exercise.is_file() or
            "repeat 4 as row" not in exercise.read_text(encoding="utf-8") or
            "repeat 3 as column" not in exercise.read_text(encoding="utf-8") or
            stdout.read_bytes() != b"9 3 24\n"):
        raise ValueError("nested repeat source or recorded output has changed")

    questions = read_practice_questions(root)
    chapter_counts = {chapter: sum(src.startswith(f"examples/{chapter}/") for src in questions)
                      for chapter in chapters}
    if len(questions) != 18 or set(chapter_counts.values()) != {3}:
        raise ValueError("expected three source-validated checkpoints per chapter")
    labs = read_labs(root)
    if len(labs) != 6 or {lab.identifier for lab in labs} != chapters:
        raise ValueError("expected one verified coding lab per chapter")
    if len(read_hindi_notes(root)) != LESSON_COUNT:
        raise ValueError("not all runnable lessons have source-backed Hindi explanations")
    if load_reference_map(root).get("compiler_commit") != COMPILER_SHA:
        raise ValueError("source-reference workshop pin differs from the released compiler")

    required = (
        "LICENSE", "LICENSE-APACHE-2.0", "THIRD_PARTY_NOTICES.md",
        "README.md", "docs/compatibility.md", "docs/cli-quickstart.md",
        "docs/hi/cli-quickstart.md", "docs/hi/README.md",
        "docs/hi/02-control-flow.md", "scripts/verify_examples.py",
        "scripts/verify_guided_labs.py", "scripts/verify_cli.py",
        "site/output-practice.js", "site/checkpoint.js",
        "tutorials/source-navigation/reference-map.json",
        f"docs/releases/{TAG}.md",
    )
    for path in required:
        if not (root / path).is_file():
            raise ValueError(f"missing required prerelease component: {path}")
    english = (root / "README.md").read_text(encoding="utf-8")
    hindi = (root / "docs/hi/README.md").read_text(encoding="utf-8")
    notes = (root / f"docs/releases/{TAG}.md").read_text(encoding="utf-8")
    if "52 numbered lessons" not in english or "कुल: 52 पाठ" not in hindi:
        raise ValueError("English/Hindi catalog counts do not match the release")
    if not all(item in notes for item in (
        TAG, "course prerelease", "not a Scarp compiler release", COMPILER_SHA,
        "52 lessons", "18 checkpoints", "Six coding labs", "69 HTML pages")):
        raise ValueError("release notes omit the verified milestone and limitations")

    # The release archive must produce a complete, self-contained site from
    # checked-in material, with no extra dependencies or browser compiler.
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        if build(output) != LESSON_COUNT:
            raise ValueError("site build does not contain the verified lesson count")
        if len(list(output.rglob("index.html"))) != PAGE_COUNT:
            raise ValueError("generated site has an unexpected number of HTML pages")
        sitemap = ET.parse(output / "sitemap.xml")
        locations = sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if len(locations) != PAGE_COUNT:
            raise ValueError("sitemap and generated HTML pages are inconsistent")
        target_lesson = output / "lessons/02-control-flow/04-nested-repeat/index.html"
        if not target_lesson.is_file() or "9 3 24" not in target_lesson.read_text(encoding="utf-8"):
            raise ValueError("new lesson is absent from the generated site")
    return (f"PASS: {TAG}; {LESSON_COUNT} compiler-verified lessons; "
            f"18 checkpoints; 6 labs; {PAGE_COUNT} HTML pages; "
            f"Scarp {COMPILER_TAG} at {COMPILER_SHA[:12]}")


def main() -> int:
    try:
        print(check_alpha5())
        return 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
