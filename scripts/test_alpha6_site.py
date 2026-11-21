"""Ensure alpha.6 input/tuple material is a real, linked bilingual site route."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from alpha6_input_page import read_workshop, COMMIT, RELEASE, VERSION, WORKSHOP
from build_site import ROOT, build, render_catalog
from verify_examples import read_expected_stdout, read_optional_stdin


class CodeText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag == "code" and dict(attrs).get("id") == "scarp-code":
            self.active = True

    def handle_endtag(self, tag):
        if tag == "code" and self.active:
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.chunks.append(data)


class Alpha6SiteTests(unittest.TestCase):
    def test_release_is_separate_from_active_course_target(self):
        target = read_workshop(ROOT, read_expected_stdout, read_optional_stdin)
        self.assertEqual(target["version"], VERSION)
        self.assertEqual(target["source_commit"], COMMIT)
        self.assertEqual(target["release_url"], RELEASE)
        active = json.loads((ROOT / "docs/compiler-target.json").read_text(encoding="utf-8"))
        self.assertNotEqual(target["source_commit"], active["source_commit"])

    def test_real_input_and_output_are_preserved_byte_for_byte(self):
        workshop = ROOT / WORKSHOP
        self.assertEqual((workshop / "main.stdin").read_bytes(), "  संस्कार 🌍\n42\n".encode("utf-8"))
        self.assertEqual(
            (workshop / "main.stdout").read_bytes(),
            'Profile\n("संस्कार 🌍", 42)\nअंक: 42\n'.encode("utf-8")
        )

    def test_rejects_mutated_source_and_stdin_without_updating_compiler(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / WORKSHOP, root / WORKSHOP)
            source = root / WORKSHOP / "main.srp"
            source.write_text(source.read_text(encoding="utf-8") + "// altered\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Git blob"):
                read_workshop(root, read_expected_stdout, read_optional_stdin)
            shutil.copyfile(ROOT / WORKSHOP / "main.srp", source)
            fixture = root / WORKSHOP / "main.stdin"
            fixture.write_bytes(" संस्कार 🌍\n42\n".encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "Git blob"):
                read_workshop(root, read_expected_stdout, read_optional_stdin)

    def test_site_publishes_one_bilingual_page_without_incrementing_core_lessons(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            self.assertEqual(build(dest), 58)
            self.assertEqual(len(list(dest.rglob("index.html"))), 81)
            page = (dest / "workshops/input-and-tuples/index.html").read_text(encoding="utf-8")
            home = (dest / "index.html").read_text(encoding="utf-8")
            expected = (ROOT / WORKSHOP / "main.srp").read_text(encoding="utf-8")
            parser = CodeText()
            parser.feed(page)
            self.assertEqual("".join(parser.chunks), expected)
            for needle in (
                'id="en-notes"', 'id="hi-notes"', "main.stdin", "main.stdout",
                "read_line()", "tuple&lt;string, integer&gt;", "E0055",
                "संस्कार 🌍", "अंक: 42", COMMIT, RELEASE,
                "scarp exec tutorials/input-and-tuples/main.srp",
                'href="../../styles.css"', 'data-output-practice hidden',
            ):
                self.assertIn(needle, page)
            self.assertIn("workshops/input-and-tuples/index.html", home)
            self.assertIn(
                "https://scarp-lang.github.io/scarp-by-example/workshops/input-and-tuples/",
                (dest / "sitemap.xml").read_text(encoding="utf-8"),
            )
            self.assertNotIn("scarp exec --interactive", page)
            self.assertNotIn("workshops/index.html", page)

    def test_home_uses_same_58_lesson_catalog(self):
        page, count = render_catalog()
        self.assertEqual(count, 58)
        self.assertIn("workshops/input-and-tuples/index.html", page)


if __name__ == "__main__":
    unittest.main()
