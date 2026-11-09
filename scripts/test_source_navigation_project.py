"""Ensure the source-navigation workshop is source-backed and navigable."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from site_inventory import expected_lesson_count, expected_page_paths
from build_site import build, read_course, render_source_navigation_page
from source_explorer import load_reference_map, render_reference_explorer
from verify_examples import ROOT, read_expected_stdout

PROJECT = ROOT / "tutorials/source-navigation"


class SourceNavigationWorkshopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target = read_course()[2]

    def test_manifest_source_and_stdout_are_compiler_fixtures(self):
        self.assertEqual(self.target["version"], "0.0.6-alpha.5")
        self.assertEqual((PROJECT / "Scarp.project").read_bytes(),
                         b"scarp-project: 1\nname: source-navigation\nentry: src/main.srp\n")
        main = (PROJECT / "src/main.srp").read_text(encoding="utf-8")
        helper = (PROJECT / "src/lib/navigation_values.srp").read_text(encoding="utf-8")
        self.assertTrue(main.startswith('import "lib/navigation_values.srp" as library;'))
        self.assertEqual(main.count("bind base ="), 2)
        self.assertIn("twice(value: library.adjust(n: base + step))", main)
        self.assertIn("pub bind offset = private_seed;", helper)
        self.assertIn("pub pure funcra adjust(n: integer)", helper)
        self.assertEqual(read_expected_stdout(PROJECT / "expected.stdout"), b"30\n")

    def test_rendered_page_shows_sources_and_bilingual_practice(self):
        markup = render_source_navigation_page(self.target)
        for fragment in (
            "src/main.srp", "src/lib/navigation_values.srp", "expected.stdout",
            "scarp verify tutorials/source-navigation",
            "scarp inspect references --json tutorials/source-navigation",
            "scarp inspect symbols --json tutorials/source-navigation",
            "scarp launch tutorials/source-navigation",
            'id="scarp-code"', 'id="en-notes"', 'id="hi-notes"',
            "private_seed", "argument", "निजी", "<details>", "browser does not execute Scarp",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment.lower(), markup.lower())
        self.assertIn('href="../module-inspection/index.html"', markup)
        self.assertIn("205e92f166f", markup)
        self.assertIn('data-reference-explorer', markup)
        self.assertIn('src="../../reference-explorer.js"', markup)
        self.assertIn('href="#ref-card-base-outer"', markup)
        self.assertIn('href="#ref-card-base-inner"', markup)
        self.assertNotIn("scarp compile tutorials/source-navigation", markup)

    def test_website_build_and_sitemap_include_workshop(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            self.assertEqual(build(dest), expected_lesson_count())
            self.assertEqual(len(list(dest.rglob("index.html"))), len(expected_page_paths()))
            self.assertTrue((dest / "projects/source-navigation/index.html").is_file())
            self.assertTrue((dest / "reference-explorer.js").is_file())
            self.assertIn("projects/source-navigation/",
                          (dest / "sitemap.xml").read_text(encoding="utf-8"))
            home = (dest / "projects/index.html").read_text(encoding="utf-8")
            self.assertIn('href="source-navigation/index.html"', home)
            previous = (dest / "projects/module-inspection/index.html").read_text(encoding="utf-8")
            self.assertIn('href="../source-navigation/index.html"', previous)

    def test_bilingual_linked_source_is_checked_and_available_without_javascript(self):
        mapping = load_reference_map()
        self.assertEqual(len(mapping["symbols"]), 11)
        self.assertEqual(sum(len(x["references"]) for x in mapping["symbols"]), 20)
        markup = render_reference_explorer()
        self.assertEqual(markup.count('class="ref-token"'), 31)
        self.assertEqual(markup.count('class="ref-card"'), 11)
        self.assertIn('data-ref-symbol="base-outer"', markup)
        self.assertIn('data-ref-symbol="base-inner"', markup)
        self.assertIn('lang="hi"', markup)
        self.assertIn('href="#ref-card-value"', markup)
        self.assertIn("browser does not execute Scarp", render_source_navigation_page(self.target))

    def test_project_manifest_corruption_fails_build(self):
        manifest = PROJECT / "Scarp.project"
        original = manifest.read_bytes()
        with patch("pathlib.Path.read_bytes", autospec=True) as reader:
            def read(path):
                if path == manifest:
                    return original.replace(b"source-navigation", b"wrong-workshop")
                with Path.open(path, "rb") as stream:
                    return stream.read()
            reader.side_effect = read
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                render_source_navigation_page(self.target)


if __name__ == "__main__":
    unittest.main()
