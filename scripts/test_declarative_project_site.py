"""Validate the modern v2 project page, manifest provenance and route discoverability."""

import tempfile
import unittest
from pathlib import Path

from build_site import build, read_course, render_declarative_project_page
from verify_declarative_project import validate_fixtures


class ModernProjectSiteTests(unittest.TestCase):
    def test_render_uses_real_checked_in_manifest_output_and_sources(self):
        _, _, target = read_course()
        content = render_declarative_project_page(target)
        self.assertIn("scarp.project", content)
        self.assertIn('project &quot;learning-project&quot;', content)
        self.assertIn("Total: 42", content)
        self.assertIn("02-input.stdin", content)
        self.assertIn('lang="hi"', content)
        self.assertIn('lang="en"', content)
        self.assertIn("scarp test --require-tests --json", content)
        self.assertIn("source-pinned", content)
        self.assertNotIn("browser VM is implemented", content)
        self.assertEqual(validate_fixtures(), b"Total: 42\n")

    def test_page_is_linked_from_home_and_legacy_project_and_sitemap(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            self.assertEqual(build(site), 60)
            pages = list(site.rglob("index.html"))
            self.assertEqual(len(pages), 84)
            page = site / "projects/declarative/index.html"
            self.assertTrue(page.exists())
            self.assertIn('href="projects/declarative/index.html"',
                          (site / "index.html").read_text(encoding="utf-8"))
            self.assertIn("scarp.project guide",
                          (site / "projects/index.html").read_text(encoding="utf-8"))
            self.assertIn("projects/declarative/",
                          (site / "sitemap.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
