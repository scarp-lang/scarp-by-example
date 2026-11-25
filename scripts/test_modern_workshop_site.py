"""Check the public alpha.13 workshop page renders verified source and output."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from catalog_test_support import EXPECTED_PAGE_COUNT
from build_site import MODERN_WORKSHOP, build, escape, read_course, render_modern_collections_page
from verify_examples import ROOT, read_expected_stdout

WORKSHOP = ROOT / "tutorials/modern-collections"


class ModernWorkshopSiteTests(unittest.TestCase):
    def setUp(self):
        self.target = read_course()[2]

    def test_page_includes_every_actual_source_and_exact_output(self):
        html = render_modern_collections_page(self.target)
        self.assertEqual(len(MODERN_WORKSHOP), 8)
        self.assertIn("e755fda37cdaeed29434e848cb5dd41f2f2e7eb2", html)
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
            self.assertEqual(build(output), 60)
            self.assertEqual(len(list(output.rglob("index.html"))), EXPECTED_PAGE_COUNT)
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

    def test_historical_workshop_does_not_follow_active_compiler(self):
        manifest = json.loads((WORKSHOP / "compiler-target.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.0.6-alpha.13")
        self.assertEqual(manifest["source_commit"], "e755fda37cdaeed29434e848cb5dd41f2f2e7eb2")
        self.assertEqual(self.target["version"], "0.0.6-alpha.20")
        html = render_modern_collections_page(self.target)
        self.assertIn(manifest["source_commit"], html)
        self.assertNotIn(self.target["source_commit"], html)

    def test_rejects_historical_manifest_drift(self):
        from unittest.mock import patch
        manifest = json.loads((WORKSHOP / "compiler-target.json").read_text(encoding="utf-8"))
        manifest["source_commit"] = "0" * 40
        with patch("build_site.json.loads", return_value=manifest):
            with self.assertRaisesRegex(ValueError, "modern workshop compiler source_commit"):
                render_modern_collections_page(self.target)


if __name__ == "__main__":
    unittest.main()
