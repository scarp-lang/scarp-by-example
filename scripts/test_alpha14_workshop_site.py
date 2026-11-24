"""Website assertions for the two original, published Scarp alpha.14 examples."""

from __future__ import annotations

import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from build_site import (
    ALPHA14_WORKSHOP, alpha14_example_path, build,
    render_alpha14_workshop_index, render_alpha14_example_page,
)
from verify_alpha14_patterns import PIN, TARGET, VERSION
from verify_examples import ROOT, VerificationError, read_expected_stdout


class CodeText(HTMLParser):
    """Recover text, including across syntax-highlighting spans, by unique code ID."""

    def __init__(self, code_id: str):
        super().__init__(convert_charrefs=True)
        self.code_id = code_id
        self.inside = False
        self.matches = 0
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "code" and dict(attrs).get("id") == self.code_id:
            self.matches += 1
            self.inside = True

    def handle_endtag(self, tag):
        if tag == "code" and self.inside:
            self.inside = False

    def handle_data(self, value):
        if self.inside:
            self.text.append(value)

    def result(self) -> str:
        if self.matches != 1 or self.inside:
            raise ValueError(f"expected one complete code block: {self.code_id}")
        return "".join(self.text)


class PublishedAlpha14WebsiteTests(unittest.TestCase):
    def test_manifest_keeps_immutable_alpha14_pin_after_course_promotion(self):
        manifest = json.loads(TARGET.read_text(encoding="utf-8"))
        active = json.loads((ROOT / "docs/compiler-target.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_commit"], PIN)
        self.assertEqual(manifest["version"], VERSION)
        self.assertNotEqual(manifest["source_commit"], active["source_commit"])
        self.assertEqual(active["version"], "0.0.6-alpha.20")

    def test_dedicated_pages_preserve_original_source_and_stdout_dom(self):
        self.assertEqual(len(ALPHA14_WORKSHOP), 2)
        self.assertEqual(len({entry[0] for entry in ALPHA14_WORKSHOP}), 2)
        self.assertEqual(len({entry[1] for entry in ALPHA14_WORKSHOP}), 2)
        for name, slug, heading, *_ in ALPHA14_WORKSHOP:
            with self.subTest(name=name):
                html = render_alpha14_example_page(name)
                source = (ROOT / "tutorials/structured-patterns" / f"{name}.srp").read_text(
                    encoding="utf-8"
                )
                fixture = read_expected_stdout(
                    ROOT / "tutorials/structured-patterns" / f"{name}.stdout"
                ).decode("utf-8")
                code = CodeText("scarp-code")
                code.feed(html)
                output = CodeText("scarp-output")
                output.feed(html)
                self.assertEqual(code.result(), source)
                self.assertEqual(output.result(), fixture.replace("\r", "\\r"))
                self.assertIn(f"<h1>{heading}</h1>", html)
                self.assertIn('lang="en"', html)
                self.assertIn('lang="hi"', html)
                self.assertIn(f"scarp verify tutorials/structured-patterns/{name}.srp", html)
                self.assertIn(f"scarp exec tutorials/structured-patterns/{name}.srp", html)
                self.assertIn(f"/blob/{PIN}/examples/{name}.srp", html)
                self.assertIn(f"/blob/{PIN}/examples/{name}.stdout", html)
                self.assertIn("does not execute code in your browser", html)
                self.assertIn(
                    "https://scarp-lang.github.io/scarp-by-example/" +
                    alpha14_example_path(slug).removesuffix("index.html"), html,
                )

    def test_overview_provenance_and_linked_exercises(self):
        page = render_alpha14_workshop_index()
        self.assertIn(PIN, page)
        self.assertIn("PUBLISHED SCARP", page)
        self.assertIn('lang="hi"', page)
        self.assertIn("60 numbered lessons", page)
        self.assertEqual(page.count('class="lab-card"'), 2)
        for _, slug, heading, *_ in ALPHA14_WORKSHOP:
            self.assertIn(heading, page)
            self.assertIn(f'href="{slug}/index.html"', page)
        self.assertIn("website does not execute code in your browser", page)

    def test_build_adds_four_workshop_routes_without_changing_progress_inventory(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            self.assertEqual(build(out), 60)
            pages = sorted((out / "workshops/structured-patterns").rglob("index.html"))
            self.assertEqual(len(pages), 4)
            self.assertEqual(len(list(out.rglob("index.html"))), 85)
            home = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="workshops/structured-patterns/index.html"', home)
            sitemap = (out / "sitemap.xml").read_text(encoding="utf-8")
            for route in ["workshops/structured-patterns/index.html",
                          *(alpha14_example_path(item[1]) for item in ALPHA14_WORKSHOP)]:
                self.assertTrue((out / route).is_file())
                self.assertIn(
                    "https://scarp-lang.github.io/scarp-by-example/" +
                    route.removesuffix("index.html"), sitemap,
                )
            search = json.loads((out / "search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(search), 60)
            self.assertNotIn("structured-patterns", json.dumps(search))

    def test_malformed_pin_and_unknown_examples_fail_closed(self):
        with patch("build_site.validate_alpha14_manifest",
                   side_effect=VerificationError("alpha.14 release manifest changed")):
            with self.assertRaisesRegex(VerificationError, "release manifest"):
                render_alpha14_workshop_index()
            with self.assertRaisesRegex(VerificationError, "release manifest"):
                render_alpha14_example_page(ALPHA14_WORKSHOP[0][0])
        with self.assertRaisesRegex(ValueError, "unknown alpha.14 workshop"):
            render_alpha14_example_page("not-an-upstream-example")


if __name__ == "__main__":
    unittest.main()
