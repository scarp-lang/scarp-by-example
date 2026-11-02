"""Enforce complete Hindi coverage without duplicating executable examples."""

from __future__ import annotations

import re
import unittest

from verify_examples import EXAMPLES, ROOT, discover_examples

GUIDE_ROOT = ROOT / "docs" / "hi"
LESSON_LINK = re.compile(r"\]\(\.\./\.\./(examples/[^)]+)\)")
CHAPTER_LINK = re.compile(r"\]\((\d{2}-[a-z0-9-]+)\.md\)")


class HindiTranslationCoverageTests(unittest.TestCase):
    def test_each_chapter_links_every_source_and_stdout_once(self):
        pairs = discover_examples(EXAMPLES)
        chapters = sorted({src.parent.name for src, _ in pairs})
        self.assertEqual(len(chapters), 6, "update the course plan when chapters change")
        for chapter in chapters:
            with self.subTest(chapter=chapter):
                guide = GUIDE_ROOT / (chapter + ".md")
                self.assertTrue(guide.is_file(), f"missing Hindi guide: {guide}")
                content = guide.read_text(encoding="utf-8")
                links = [
                    path for path in LESSON_LINK.findall(content)
                    if path.endswith((".srp", ".stdout"))
                ]
                chapter_pairs = [
                    (src, out) for src, out in pairs if src.parent.name == chapter
                ]
                expected_sources = {src.relative_to(ROOT).as_posix() for src, _ in chapter_pairs}
                expected_outputs = {out.relative_to(ROOT).as_posix() for _, out in chapter_pairs}
                actual_sources = {path for path in links if path.endswith(".srp")}
                actual_outputs = {path for path in links if path.endswith(".stdout")}
                self.assertEqual(actual_sources, expected_sources)
                self.assertEqual(actual_outputs, expected_outputs)
                self.assertEqual(len(links), 2 * len(chapter_pairs), "duplicate or missing lesson link")
                for relative in links:
                    self.assertTrue((ROOT / relative).is_file(), relative)

    def test_hindi_index_contains_every_chapter_once(self):
        index = (GUIDE_ROOT / "README.md").read_text(encoding="utf-8")
        actual = CHAPTER_LINK.findall(index)
        expected = sorted(p.parent.name for p in EXAMPLES.glob("*/README.md"))
        self.assertEqual(sorted(actual), expected)
        self.assertEqual(len(actual), len(set(actual)), "duplicate chapter in Hindi index")

    def test_hindi_directory_contains_only_explanations(self):
        self.assertEqual(list(GUIDE_ROOT.rglob("*.srp")), [])
        self.assertEqual(list(GUIDE_ROOT.rglob("*.stdout")), [])


if __name__ == "__main__":
    unittest.main()
