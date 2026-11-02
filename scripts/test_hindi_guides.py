"""Keep the Hindi companion guides linked to their exact canonical lessons."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from verify_examples import EXAMPLES, ROOT, discover_examples

GUIDE_ROOT = ROOT / "docs" / "hi"


class HindiTranslationCoverageTests(unittest.TestCase):
    def test_canonical_lessons_and_fixtures_are_linked(self):
        entries = discover_examples(EXAMPLES)
        for chapter, guide_name in (
            ("01-basics", "01-basics.md"),
            ("02-control-flow", "02-control-flow.md"),
        ):
            with self.subTest(chapter=chapter):
                content = (GUIDE_ROOT / guide_name).read_text(encoding="utf-8")
                links = re.findall(r"\]\(\.\./\.\./(examples/[^)]+)\)", content)
                actual_sources = {p for p in links if p.endswith(".srp")}
                actual_outputs = {p for p in links if p.endswith(".stdout")}
                chapter_entries = [
                    (src, fixture) for src, fixture in entries if src.parent.name == chapter
                ]
                expected_sources = {src.relative_to(ROOT).as_posix() for src, _ in chapter_entries}
                expected_outputs = {fixture.relative_to(ROOT).as_posix() for _, fixture in chapter_entries}
                self.assertEqual(actual_sources, expected_sources)
                self.assertEqual(actual_outputs, expected_outputs)
                self.assertEqual(len(links), 2 * len(chapter_entries))
                for relative in links:
                    self.assertTrue((ROOT / relative).is_file(), relative)

    def test_hindi_index_links_both_guides(self):
        content = (GUIDE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(01-basics.md)", content)
        self.assertIn("(02-control-flow.md)", content)

    def test_no_duplicate_scarp_source_in_translation_directory(self):
        self.assertEqual(list(GUIDE_ROOT.rglob("*.srp")), [])
        self.assertEqual(list(GUIDE_ROOT.rglob("*.stdout")), [])


if __name__ == "__main__":
    unittest.main()
