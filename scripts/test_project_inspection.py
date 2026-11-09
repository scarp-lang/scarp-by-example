"""Check source fidelity, bilingual guidance and navigation for alpha.5 inspection."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from site_inventory import expected_lesson_count, expected_page_paths
from build_site import build, read_course, render_project_inspection_page
from verify_examples import ROOT


class ProjectInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ROOT / "tutorials/module-inspection"
        cls.target = read_course()[2]

    def test_published_alpha5_target_preserves_project_fixture(self):
        self.assertEqual(self.target["release_tag"], "v0.0.6-alpha.5")
        self.assertEqual(self.target["source_commit"],
                         "205e92f166f186c3905e5880d41c31717b697b8e")
        self.assertEqual((self.root / "Scarp.project").read_bytes(),
                         b"scarp-project: 1\nname: module-inspection\nentry: src/main.srp\n")
        self.assertEqual((self.root / "src/main.srp").read_bytes(),
                         b'import "lib/math.srp" as math;\nprint(math.answer);\n')
        self.assertIn(b"pub bind answer = 21 * 2;",
                      (self.root / "src/lib/math.srp").read_bytes())
        self.assertEqual((self.root / "expected.stdout").read_bytes(), b"42\n")

    def test_rendered_tutorial_explains_distinct_static_and_runtime_commands(self):
        markup = render_project_inspection_page(self.target)
        for fragment in (
            "scarp verify tutorials/module-inspection",
            "scarp inspect modules --json tutorials/module-inspection",
            "scarp inspect symbols --json tutorials/module-inspection",
            "scarp inspect references --json tutorials/module-inspection",
            "docs/source-navigation.md", "docs/hi/source-navigation.md",
            "scarp launch tutorials/module-inspection",
            "src/main.srp", "src/lib/math.srp", "expected.stdout",
            'id="en-notes"', 'id="hi-notes"',
            "does not execute", "No browser Scarp execution",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, markup)
        self.assertIn(
            "https://github.com/scarp-lang/scarp-by-example/blob/main/"
            "tutorials/module-inspection/src/lib/math.srp", markup
        )

    def test_generator_rejects_unverified_project_manifest(self):
        fake_manifest = self.root / "Scarp.project"
        original = fake_manifest.read_bytes()
        with patch("pathlib.Path.read_bytes", autospec=True) as reader:
            def read(path):
                if path == fake_manifest:
                    return original.replace(b"module-inspection", b"wrong-project")
                with Path.open(path, "rb") as stream:
                    return stream.read()
            reader.side_effect = read
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                render_project_inspection_page(self.target)

    def test_course_build_publishes_one_independent_inspection_page(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(build(target), expected_lesson_count())
            pages = list(target.rglob("index.html"))
            self.assertEqual(len(pages), len(expected_page_paths()))
            self.assertIn(
                "projects/module-inspection/",
                (target / "sitemap.xml").read_text(encoding="utf-8")
            )
            home_project = (target / "projects/index.html").read_text(encoding="utf-8")
            self.assertIn('href="module-inspection/index.html"', home_project)
            self.assertIn('href="source-navigation/index.html"', home_project)
            page = (target / "projects/module-inspection/index.html").read_text(encoding="utf-8")
            self.assertIn('href="../../index.html"', page)
            self.assertIn("schema-v1", page)
            self.assertNotIn("scarp compile tutorials/", page)


if __name__ == "__main__":
    unittest.main()
