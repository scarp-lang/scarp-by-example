"""Release-pinned optional workshop page validation and fidelity regression tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from build_site import (
    COMPILER, REPOSITORY, ROOT, build, escape, page_shell, rel,
    render_lesson,
)
from verify_examples import read_expected_stdout
from workshop_pages import (
    generate_workshop_pages, lesson_url, overview_url, read_workshops,
)


class SourceCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_source = False
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag == "code" and ("id", "scarp-code") in attrs:
            self.in_source = True

    def handle_endtag(self, tag):
        if self.in_source and tag == "code":
            self.in_source = False

    def handle_data(self, data):
        if self.in_source:
            self.chunks.append(data)


class WorkshopSiteTests(unittest.TestCase):
    def test_published_alpha7_pin_is_distinct_from_numbered_course(self):
        (workshop,) = read_workshops(ROOT, COMPILER, read_expected_stdout)
        self.assertEqual(workshop["slug"], "conditionals-and-unicode")
        self.assertEqual(workshop["target"]["version"], "0.0.6-alpha.7")
        self.assertEqual(
            workshop["target"]["source_commit"],
            "b1c1fd232b418267d95520c69ee563ac99ecae30",
        )
        course_target = json.loads(
            (ROOT / "docs/compiler-target.json").read_text(encoding="utf-8")
        )
        self.assertNotEqual(course_target["source_commit"], workshop["target"]["source_commit"])

    def test_generated_pages_display_original_unmodified_scarp_source(self):
        (workshop,) = read_workshops(ROOT, COMPILER, read_expected_stdout)
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)
            routes = generate_workshop_pages(
                output, [workshop], ROOT, REPOSITORY, page_shell,
                render_lesson, rel, escape
            )
            self.assertEqual(len(routes), 5)
            self.assertTrue((output / "workshops/index.html").is_file())
            self.assertTrue((output / overview_url(workshop)).is_file())
            for entry in workshop["lessons"]:
                generated = (output / lesson_url(workshop, entry)).read_text(encoding="utf-8")
                source = (workshop["folder"] / entry["source"]).read_text(encoding="utf-8")
                parser = SourceCollector()
                parser.feed(generated)
                self.assertEqual("".join(parser.chunks), source)
                self.assertIn('id="en-notes"', generated)
                self.assertIn('id="hi-notes"', generated)
                self.assertIn('data-output-practice hidden', generated)
                self.assertIn("scarp verify tutorials/conditionals-and-unicode/", generated)
                self.assertIn("v0.0.6-alpha.7", generated)
                expected = read_expected_stdout(
                    (workshop["folder"] / entry["source"]).with_suffix(".stdout")
                ).decode("utf-8")
                self.assertIn(escape(expected.rstrip("\n")), generated)

    def test_invalid_provenance_or_incomplete_translation_is_rejected(self):
        (workshop,) = read_workshops(ROOT, COMPILER, read_expected_stdout)
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "tutorials" / "conditionals-and-unicode"
            src.mkdir(parents=True)
            import shutil
            for name in ["site-notes.json", "compiler-target.json"]:
                shutil.copyfile(workshop["folder"] / name, src / name)
            for entry in workshop["lessons"]:
                for suffix in (".srp", ".stdout"):
                    filename = entry["source"].removesuffix(".srp") + suffix
                    shutil.copyfile(workshop["folder"] / filename, src / filename)
            metadata = json.loads((src / "site-notes.json").read_text(encoding="utf-8"))
            metadata["lessons"][0]["explanation_hi"] = ""
            (src / "site-notes.json").write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "incomplete bilingual"):
                read_workshops(Path(td), COMPILER, read_expected_stdout)

            metadata["lessons"][0]["explanation_hi"] = "परीक्षण"
            (src / "site-notes.json").write_text(json.dumps(metadata), encoding="utf-8")
            target = json.loads((src / "compiler-target.json").read_text(encoding="utf-8"))
            target["source_commit"] = "wrong"
            (src / "compiler-target.json").write_text(json.dumps(target), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid release provenance"):
                read_workshops(Path(td), COMPILER, read_expected_stdout)

    def test_generated_workshop_is_not_counted_as_a_numbered_course_lesson(self):
        with tempfile.TemporaryDirectory() as td:
            count = build(Path(td))
            self.assertEqual(count, 52)
            self.assertTrue((Path(td) / "workshops/conditionals-and-unicode/03-unicode-scalars/index.html").is_file())
            self.assertEqual(len(list(Path(td).rglob("index.html"))), 75)


if __name__ == "__main__":
    unittest.main()
