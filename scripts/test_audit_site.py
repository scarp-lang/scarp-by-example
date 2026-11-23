"""Offline regression tests for the generated website's link integrity gate."""

from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from audit_site import PUBLIC_SITE, audit_site, main
from build_site import build


def make_site(root: Path) -> None:
    (root / "topic").mkdir(parents=True)
    (root / "index.html").write_text(
        '<link rel="canonical" href="' + PUBLIC_SITE + '">'
        '<script src="app.js"></script>'
        '<a href="topic/#%E0%A4%B9">Topic</a>'
        '<a href="https://example.org/resource">External</a>'
        '<a href="mailto:help@example.org">Email</a>'
        '<div id="home">Home</div>', encoding="utf-8"
    )
    (root / "topic/index.html").write_text(
        '<link rel="canonical" href="' + PUBLIC_SITE + 'topic/">'
        '<a href="../index.html#home">Home</a>'
        '<a href="' + PUBLIC_SITE + '#home">Absolute site link</a>'
        '<section id="ह">Hindi anchor</section>', encoding="utf-8"
    )
    (root / "app.js").write_text("/* local fixture */\n", encoding="utf-8")
    (root / "sitemap.xml").write_text(
        '<?xml version="1.0"?><urlset '
        'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>' + PUBLIC_SITE + '</loc></url>'
        '<url><loc>' + PUBLIC_SITE + 'topic/</loc></url>'
        '</urlset>', encoding="utf-8"
    )


class SiteIntegrityTests(unittest.TestCase):
    def setup_site(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        make_site(root)
        return root

    def test_valid_local_and_absolute_links_utf8_fragments_and_assets(self):
        report = audit_site(self.setup_site())
        self.assertTrue(report.valid, report.errors)
        self.assertEqual(report.pages, 2)
        self.assertEqual(report.fragments, 3)
        self.assertGreaterEqual(report.links, 5)

    def test_missing_fragment_is_reported_with_origin(self):
        root = self.setup_site()
        index = root / "index.html"
        index.write_text(index.read_text(encoding="utf-8").replace("#%E0%A4%B9", "#missing"), encoding="utf-8")
        errors = audit_site(root).errors
        self.assertTrue(any("index.html" in e and "missing id='missing'" in e for e in errors))

    def test_repeated_id_is_rejected(self):
        root = self.setup_site()
        page = root / "topic/index.html"
        page.write_text(page.read_text(encoding="utf-8") + '<span id="ह"></span>', encoding="utf-8")
        self.assertTrue(any("repeated or empty id" in e for e in audit_site(root).errors))

    def test_local_asset_missing(self):
        root = self.setup_site()
        (root / "app.js").unlink()
        self.assertTrue(any("missing app.js" in e for e in audit_site(root).errors))

    def test_directory_traversal_and_javascript_protocol_are_disallowed(self):
        root = self.setup_site()
        page = root / "index.html"
        page.write_text(page.read_text(encoding="utf-8") + '<a href="../../outside">escape</a>'
                        + '<a href="javascript:alert(1)">script</a>', encoding="utf-8")
        messages = audit_site(root).errors
        self.assertTrue(any("outside the published site" in e for e in messages))
        self.assertTrue(any("unsafe/unsupported URL scheme" in e for e in messages))

    def test_canonical_mismatch_and_missing_sitemap_page(self):
        root = self.setup_site()
        page = root / "topic/index.html"
        page.write_text(page.read_text(encoding="utf-8").replace(PUBLIC_SITE + 'topic/', PUBLIC_SITE + 'other/'), encoding="utf-8")
        sitemap = root / "sitemap.xml"
        sitemap.write_text(sitemap.read_text(encoding="utf-8").replace(
            '<url><loc>' + PUBLIC_SITE + 'topic/</loc></url>', ''), encoding="utf-8"
        )
        messages = audit_site(root).errors
        self.assertTrue(any("canonical URL must" in e for e in messages))
        self.assertTrue(any("missing HTML routes" in e for e in messages))

    def test_duplicate_sitemap_entries_are_rejected(self):
        root = self.setup_site()
        sitemap = root / "sitemap.xml"
        sitemap.write_text(sitemap.read_text(encoding="utf-8").replace(
            "</urlset>", f"<url><loc>{PUBLIC_SITE}</loc></url></urlset>"
        ), encoding="utf-8")
        self.assertTrue(any("duplicate locations" in e for e in audit_site(root).errors))

    def test_relative_query_and_fragment_links(self):
        root = self.setup_site()
        page = root / "topic/index.html"
        page.write_text(page.read_text(encoding="utf-8") + '<a href="?q=one#%E0%A4%B9">Self</a>', encoding="utf-8")
        self.assertTrue(audit_site(root).valid)

    def test_no_pages_and_invalid_root_are_errors(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertFalse(audit_site(Path(empty)).valid)
            self.assertFalse(audit_site(Path(empty) / "none").valid)

    def test_cli_status_is_machine_readable(self):
        root = self.setup_site()
        output = StringIO()
        with redirect_stdout(output):
            status = main(["--site", str(root)])
        self.assertEqual(status, 0)
        self.assertIn("PASS:", output.getvalue())
        (root / "app.js").unlink()
        with redirect_stdout(StringIO()):
            self.assertEqual(main(["--site", str(root)]), 1)

    def test_real_generated_course_has_no_broken_navigation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            count = build(root)
            self.assertEqual(count, 58)
            report = audit_site(root)
            self.assertTrue(report.valid, "\n".join(report.errors[:30]))
            self.assertEqual(report.pages, 81)
            self.assertGreater(report.links, report.pages)
            self.assertGreater(report.fragments, 0)


if __name__ == "__main__":
    unittest.main()
