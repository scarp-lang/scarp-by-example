"""Validate standalone published alpha.11 Decimal web pages without changing core course."""

from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from build_site import (
    DECIMAL_DIR, DECIMAL_PIN, DECIMAL_EXAMPLES, build,
    decimal_url, read_decimal_workshop,
)
from test_build_site import ScarpSourceText


class DecimalPagesTests(unittest.TestCase):
    def test_pinned_version_and_output_cannot_silently_drift(self):
        self.assertEqual(read_decimal_workshop()["source_commit"], DECIMAL_PIN)
        with patch("build_site.read_expected_stdout", return_value=b"drift"):
            with self.assertRaisesRegex(ValueError, "fixture changed"):
                read_decimal_workshop()

    def test_published_examples_have_separate_source_faithful_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(build(root), 52)
            index = json.loads((root / "search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(index), 52)
            self.assertEqual(len(list(root.rglob("index.html"))), 73)
            home = (root / "index.html").read_text(encoding="utf-8")
            overview = (root / "workshops/exact-decimal/index.html").read_text(encoding="utf-8")
            self.assertIn("workshops/exact-decimal/index.html", home)
            self.assertIn(DECIMAL_PIN, overview)
            self.assertIn("28 coefficient digits", overview)
            sitemap = ET.parse(root / "sitemap.xml")
            urls = [element.text for element in sitemap.findall(
                ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
            self.assertEqual(len(urls), 73)
            self.assertIn(
                "https://scarp-lang.github.io/scarp-by-example/workshops/exact-decimal/",
                urls,
            )
            for slug, stem, title, en, hi, output in DECIMAL_EXAMPLES:
                with self.subTest(slug=slug):
                    html = (root / decimal_url(slug)).read_text(encoding="utf-8")
                    self.assertIn(title, html)
                    self.assertIn(DECIMAL_PIN, html)
                    self.assertIn("lang=\"hi\"", html)
                    self.assertIn("id=\"main-content\"", html)
                    self.assertIn(slug + "/index.html", overview)
                    parser = ScarpSourceText()
                    parser.feed(html)
                    self.assertEqual(
                        "".join(parser.parts),
                        (DECIMAL_DIR / f"{stem}.srp").read_text(encoding="utf-8"),
                    )
                    for line in output.decode("utf-8").splitlines():
                        self.assertIn(line, html)
                    if stem.startswith("interactive/"):
                        self.assertIn("E0054", html)
                        self.assertIn("2.675", html)
                        self.assertIn("--interactive", html)
                    else:
                        self.assertNotIn("id=\"decimal-stdin-title\"", html)

    def test_mismatched_compiler_pin_is_rejected_before_site_generation(self):
        bad = {"source_commit": "0" * 40, "version": "0.0.6-alpha.11",
               "release_tag": "v0.0.6-alpha.11", "status": "prerelease"}
        with patch("build_site.json.loads", return_value=bad):
            with self.assertRaisesRegex(ValueError, "compiler provenance"):
                read_decimal_workshop()

    def test_corrupt_stdin_cannot_be_rendered(self):
        with patch("build_site.read_optional_stdin", return_value=b"wrong"):
            with self.assertRaisesRegex(ValueError, "input fixture changed"):
                read_decimal_workshop()


if __name__ == "__main__":
    unittest.main()
