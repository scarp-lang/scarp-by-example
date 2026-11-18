"""Check the public alpha.13 workshop page renders verified source and output."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_site import MODERN_WORKSHOP, build, escape, read_course, render_modern_collections_page
from verify_examples import ROOT, read_expected_stdout

WORKSHOP = ROOT / "tutorials/modern-collections"


class ModernWorkshopSiteTests(unittest.TestCase):
    def setUp(self):
        self.target = read_course()[2]

    def test_page_includes_every_actual_source_and_exact_output(self):
        html = render_modern_collections_page(self.target)
        self.assertEqual(len(MODERN_WORKSHOP), 8)
        self.assertIn(self.target["source_commit"], html)
        self.assertIn('lang="hi"', html)
        self.assertIn("website does not execute code in your browser", html)
        for name, _, _ in MODERN_WORKSHOP:
            with self.subTest(name=name):
                self.assertIn(f'id="example-{name}"', html)
                self.assertIn(f'href="#example-{name}"', html)
                self.assertIn(f"scarp verify tutorials/modern-collections/{name}.srp", html)
                self.assertIn(f"scarp exec tutorials/modern-collections/{name}.srp", html)
                self.assertIn(
                    escape(read_expected_stdout(WORKSHOP / f"{name}.stdout").decode("utf-8")),
                    html,
                )
                self.assertIn(
                    f"tutorials/modern-collections/{name}.srp",
                    html,
                )
        self.assertNotIn("scarp compile tutorials/modern-collections/", html)

    def test_generated_page_is_discoverable_and_counted(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            self.assertEqual(build(output), 52)
            self.assertEqual(len(list(output.rglob("index.html"))), 73)
            page = output / "workshops/modern-collections/index.html"
            self.assertTrue(page.is_file())
            self.assertIn(
                'href="workshops/modern-collections/index.html"',
                (output / "index.html").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "workshops/modern-collections/",
                (output / "sitemap.xml").read_text(encoding="utf-8"),
            )

    def test_malformed_or_cross_release_manifest_rejected(self):
        target = dict(self.target)
        target["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "modern workshop compiler source_commit"):
            render_modern_collections_page(target)
        manifest = json.loads((WORKSHOP / "compiler-target.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], self.target["version"])


if __name__ == "__main__":
    unittest.main()
