"""The alpha.14 diagnostic page must display real fixtures and safe, correct routes."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_site import build, render_alpha14_diagnostics_page
from test_alpha14_workshop_site import CodeText
from verify_alpha14_diagnostics import DIRECTORY, PIN, IDS, load_cases
from verify_examples import read_expected_stdout


class Alpha14DiagnosticSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases()

    def test_all_invalid_and_repaired_sources_survive_highlighting(self):
        html = render_alpha14_diagnostics_page()
        self.assertIn(PIN, html)
        self.assertIn('lang="hi"', html)
        self.assertIn("The website does not execute code in your browser", html)
        self.assertEqual(html.count('class="lab-card"'), len(IDS))
        self.assertEqual(html.count('class="lesson-notes" id="repair-'), len(IDS))
        for case in self.cases:
            identifier = case["id"]
            with self.subTest(identifier=identifier):
                self.assertIn(f'id="repair-{identifier}"', html)
                self.assertIn(f'href="#repair-{identifier}"', html)
                self.assertIn(case["title"], html)
                self.assertIn(case["title_hi"], html)
                self.assertIn(f'scarp verify --diagnostic-format=json '
                              f'tutorials/structured-patterns/diagnostics/{identifier}.invalid.srp', html)
                self.assertIn(f'scarp exec tutorials/structured-patterns/diagnostics/'
                              f'{identifier}.fixed.srp', html)
                self.assertIn(f'UTF-8 BYTE SPAN {case["span"][0]}..{case["span"][1]}', html)
                for code_id, original_path in (
                    (f"invalid-{identifier}", DIRECTORY / f"{identifier}.invalid.srp"),
                    (f"fixed-{identifier}", DIRECTORY / f"{identifier}.fixed.srp"),
                ):
                    collector = CodeText(code_id)
                    collector.feed(html)
                    self.assertEqual(
                        collector.result(),
                        original_path.read_text(encoding="utf-8"),
                    )
                output = CodeText(f"output-{identifier}")
                output.feed(html)
                self.assertEqual(
                    output.result(),
                    read_expected_stdout(DIRECTORY / f"{identifier}.stdout").decode("utf-8"),
                )
        self.assertNotIn("scarp exec --diagnostic-format=json", html)
        self.assertNotIn("<script>bind ", html)

    def test_site_adds_one_page_without_polluting_progress(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root)
            self.assertEqual(build(output), 60)
            index_files = list(output.rglob("index.html"))
            self.assertEqual(len(index_files), 99)
            route = "workshops/structured-patterns/diagnostics/index.html"
            self.assertTrue((output / route).is_file())
            self.assertIn(
                "https://scarp-lang.github.io/scarp-by-example/workshops/"
                "structured-patterns/diagnostics/",
                (output / "sitemap.xml").read_text(encoding="utf-8"),
            )
            overview = (output / "workshops/structured-patterns/index.html").read_text(encoding="utf-8")
            self.assertIn('href="diagnostics/index.html"', overview)
            search = json.loads((output / "search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(search), 60)
            self.assertNotIn("missing-tuple-comma", json.dumps(search))


if __name__ == "__main__":
    unittest.main()
