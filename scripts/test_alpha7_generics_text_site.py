"""Protect the seven Alpha.3 static lesson pages and independent provenance."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import alpha7_generics_text_page as workshop
from build_site import build, page_shell, rel, highlight_scarp
from test_alpha14_workshop_site import CodeText
from test_compiler_target import checkout_inputs
from verify_alpha7_generics_text import ROOT


class Alpha7GenericsWebsiteTests(unittest.TestCase):
    def test_exact_source_output_and_provenance(self):
        for name in workshop.PROGRAMS:
            with self.subTest(name=name):
                html = workshop.render_example(name, page_shell, rel, highlight_scarp)
                for code_id, suffix in (("scarp-code", ".srp"), ("scarp-output", ".stdout")):
                    parser = CodeText(code_id)
                    parser.feed(html)
                    expected = (workshop.WORKSHOP / (name + suffix)).read_bytes().decode("utf-8")
                    self.assertEqual(parser.result(), expected)
                self.assertIn(workshop.PIN, html)
                self.assertIn('lang="hi"', html)
                self.assertIn('lang="en"', html)
                self.assertIn("does not execute code in your browser", html)
                self.assertIn(f"scarp verify tutorials/alpha7-generics-text/{name}.srp", html)
                if name + ".srp" in workshop.UPSTREAM:
                    self.assertIn(workshop.ORIGIN + name + ".srp", html)
                    self.assertIn(workshop.ORIGIN + name + ".stdout", html)
                else:
                    self.assertIn("Original Scarp by Example teaching program (MIT)", html)
                    self.assertNotIn(workshop.ORIGIN + name, html)

    def test_pages_verifies_exact_workshop_before_generation(self):
        path = ROOT / ".github" / "workflows"
        for name in ("pages.yml", "alpha7-generics-text.yml"):
            with self.subTest(workflow=name):
                content = (path / name).read_text(encoding="utf-8")
                entries = [entry for entry in checkout_inputs(content)
                           if entry.get("path") == ".compiler-alpha7-generics"]
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["repository"], "scarp-lang/scarp")
                self.assertEqual(entries[0]["ref"], workshop.PIN)
                self.assertIn(".compiler-alpha7-generics/Cargo.toml", content)
                self.assertIn("--compiler-source .compiler-alpha7-generics", content)
        pages = (path / "pages.yml").read_text(encoding="utf-8")
        self.assertLess(pages.index("run: python scripts/verify_alpha7_generics_text.py"),
                        pages.index("run: python scripts/build_site.py"))
        self.assertEqual(pages.count("if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'"), 3)

    def test_unknown_route_and_drift_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown alpha.3"):
            workshop.lesson_path("../unknown")
        with patch.object(workshop, "check_inventory", side_effect=ValueError("fixture drift")):
            with self.assertRaisesRegex(ValueError, "fixture drift"):
                workshop.render_index(page_shell, rel)
            with self.assertRaisesRegex(ValueError, "fixture drift"):
                workshop.render_example(workshop.PROGRAMS[0], page_shell, rel, highlight_scarp)

    def test_generated_routes_sitemap_and_numbered_course_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            site = Path(temp)
            self.assertEqual(build(site), 60)
            routes = [workshop.INDEX, *(workshop.lesson_path(name) for name in workshop.PROGRAMS)]
            self.assertEqual(len(set(routes)), 8)
            sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
            home = (site / "index.html").read_text(encoding="utf-8")
            index = (site / workshop.INDEX).read_text(encoding="utf-8")
            self.assertIn(f'href="{workshop.INDEX}"', home)
            self.assertEqual(index.count('class="lab-card"'), 7)
            for route in routes:
                self.assertTrue((site / route).is_file())
                self.assertIn("https://scarp-lang.github.io/scarp-by-example/" +
                              route.removesuffix("index.html"), sitemap)
            for name in workshop.PROGRAMS:
                self.assertIn(f'href="{name.replace("_", "-")}/index.html"', index)
            numbered = json.loads((site / "search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(numbered), 60)
            self.assertNotIn("alpha7-generics-text", json.dumps(numbered))


if __name__ == "__main__":
    unittest.main()
