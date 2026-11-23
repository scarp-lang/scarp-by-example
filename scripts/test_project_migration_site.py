"""Project migration HTML is source-backed, indexed, and bilingually explained."""

import tempfile
import unittest
from pathlib import Path

from build_site import build, escape, highlight_scarp, page_shell, read_course, rel
from project_migration_page import render_page
from verify_examples import ROOT
from verify_project_migration import validate_fixtures


class MigrationSiteTests(unittest.TestCase):
    def test_render_has_exact_fixtures_and_bilingual_practice(self):
        target = read_course()[2]
        html = render_page(ROOT, target, page_shell, rel, escape, highlight_scarp)
        for expected in (
            "Scarp.project", "scarp.project",
            "legacy-v1", "format: v2", "project-migration/legacy",
            "project-migration/modern", "Migrated: 42", "src/main.srp",
            "src/lib/math.srp", "tests/02-input.srp", "02-input.stdin",
            "scarp test --require-tests --json", 'lang="en"', 'lang="hi"',
            "Filename-only renaming", target["source_commit"][:12],
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, html)
        self.assertEqual(validate_fixtures(), b"Migrated: 42\n")

    def test_site_links_to_migration_and_sitemaps_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            self.assertEqual(build(site), 60)
            self.assertEqual(len(list(site.rglob("index.html"))), 85)
            migration = site / "projects/migration/index.html"
            self.assertTrue(migration.is_file())
            self.assertIn("projects/migration/",
                          (site / "sitemap.xml").read_text(encoding="utf-8"))
            self.assertIn("projects/migration/index.html",
                          (site / "index.html").read_text(encoding="utf-8"))
            self.assertIn('href="../migration/index.html"',
                          (site / "projects/declarative/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
