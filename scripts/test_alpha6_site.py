"""Regression tests for published alpha.6 input-and-tuples workshop site route."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from alpha6_input_page import read_workshop, COMMIT, RELEASE, VERSION, WORKSHOP
from build_site import ROOT, build
from verify_examples import read_expected_stdout, read_optional_stdin


class SourceText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag == "code" and dict(attrs).get("id") == "scarp-code":
            self.active = True

    def handle_endtag(self, tag):
        if self.active and tag == "code":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.chunks.append(data)


class Alpha6PageTests(unittest.TestCase):
    def test_release_pin_and_real_input_output_bytes(self):
        target = read_workshop(ROOT, read_expected_stdout, read_optional_stdin)
        self.assertEqual(target["version"], VERSION)
        self.assertEqual(target["source_commit"], COMMIT)
        self.assertEqual(target["release_url"], RELEASE)
        root = ROOT / WORKSHOP
        self.assertEqual((root / "main.stdin").read_bytes(), "  संस्कार 🌍\n42\n".encode())
        self.assertEqual(
            (root / "main.stdout").read_bytes(),
            'Profile\n("संस्कार 🌍", 42)\nअंक: 42\n'.encode(),
        )

    def test_provenance_and_exact_stdin_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / WORKSHOP, root / WORKSHOP)
            fixture = root / WORKSHOP / "main.stdin"
            fixture.write_bytes(" संस्कार 🌍\n42\n".encode())
            with self.assertRaisesRegex(ValueError, "stdin fixture changed"):
                read_workshop(root, read_expected_stdout, read_optional_stdin)
            fixture.write_bytes("  संस्कार 🌍\n42\n".encode())
            pin = root / WORKSHOP / "compiler-target.json"
            data = json.loads(pin.read_text(encoding="utf-8"))
            data["source_commit"] = "0" * 40
            pin.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "release provenance"):
                read_workshop(root, read_expected_stdout, read_optional_stdin)

    def test_generated_page_has_exact_program_and_reachable_hub_link(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            self.assertEqual(build(dest), 52)
            self.assertEqual(len(list(dest.rglob("index.html"))), 76)
            page = (dest / "workshops/input-and-tuples/index.html").read_text(encoding="utf-8")
            hub = (dest / "workshops/index.html").read_text(encoding="utf-8")
            source = (ROOT / WORKSHOP / "main.srp").read_text(encoding="utf-8")
            parser = SourceText()
            parser.feed(page)
            self.assertEqual("".join(parser.chunks), source)
            for needle in (
                "main.stdin", "main.stdout", "scarp exec", "E0055", "text_trim",
                "tuple&lt;string, integer&gt;", "संस्कार 🌍", "अंक: 42",
                'id="en-notes"', 'id="hi-notes"', COMMIT, RELEASE,
                'data-output-practice hidden', 'href="../../styles.css"',
            ):
                self.assertIn(needle, page)
            self.assertIn("input-and-tuples/index.html", hub)
            self.assertIn(
                "https://scarp-lang.github.io/scarp-by-example/workshops/input-and-tuples/",
                (dest / "sitemap.xml").read_text(encoding="utf-8"),
            )
            self.assertNotIn("scarp test --json=v2", page)


if __name__ == "__main__":
    unittest.main()
