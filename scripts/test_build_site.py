"""Tests for the static multipage learning site, routes, and source fidelity."""

from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from build_site import (
    build, escape, lesson_description, read_course, render_catalog,
    render_lesson, section_heading, table_cells, plain_markdown,
)
from verify_examples import EXAMPLES, discover_examples

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths: list[str] = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag in {"a", "link"} and fields.get("href"):
            self.paths.append(fields["href"])
        if tag == "script" and fields.get("src"):
            self.paths.append(fields["src"])


class ScarpSourceText(HTMLParser):
    """Recover the exact code text from its syntax-highlighted DOM."""

    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "code" and dict(attrs).get("id") == "scarp-code":
            self.inside = True

    def handle_endtag(self, tag):
        if tag == "code":
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)


class SiteTests(unittest.TestCase):
    def test_html_escape_never_injects_source_markup(self):
        self.assertEqual(escape('<script x="a">'), '&lt;script x=&quot;a&quot;&gt;')

    def test_parses_markdown_table_with_bitwise_pipe_operators(self):
        cells = table_cells('| [14 · Bitwise](14-bitwise-fields.srp) | Uses ' +
                            chr(96) + '|=' + chr(96) + ' and ' + chr(96) + '&' +
                            chr(96) + ' | result |')
        self.assertEqual(len(cells), 3)
        self.assertIn("|=", cells[1])

    def test_inline_markdown_does_not_leak_into_cards(self):
        self.assertEqual(plain_markdown("A **real** " + chr(96) + "example" +
                                        chr(96)), "A real example")

    def test_course_has_matching_chapters_and_true_fixtures(self):
        lessons, chapters, target = read_course()
        self.assertEqual(len(lessons), len(discover_examples(EXAMPLES)))
        self.assertEqual(len(lessons), 50)
        self.assertEqual(len(chapters), 6)
        self.assertEqual(target["version"], json.loads((ROOT / "docs/compiler-target.json").read_text(encoding="utf-8"))["version"])
        for lesson in lessons:
            self.assertTrue(lesson.source.is_file())
            self.assertTrue(lesson.stdout.is_file())
            self.assertTrue((ROOT / "docs" / "hi" / (lesson.section + ".md")).is_file())
        self.assertIn("Scarp basics", section_heading(EXAMPLES / "01-basics" / "README.md"))
        self.assertIn("displays a string", lesson_description(
            EXAMPLES / "01-basics" / "README.md", "01-hello.srp"
        ))

    def test_home_is_chapter_focused_not_one_long_code_grid(self):
        page, total = render_catalog()
        self.assertEqual(total, 50)
        self.assertEqual(page.count('class="chapter-tile"'), 6)
        self.assertIn("One real program at a time", page)
        self.assertIn('href="chapters/01-basics/index.html"', page)
        self.assertIn("search-index.json", page)
        self.assertIn("हिन्दी", page)
        self.assertNotIn('class="lesson-card"', page)
        self.assertNotIn('src="https://', page)

    def test_render_lesson_escapes_untrusted_source_and_preserves_fixture(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            folder = Path(directory)
            src = folder / "01-escape.srp"
            stdout = folder / "01-escape.stdout"
            src.write_text('print("<unsafe>");\n', encoding="utf-8")
            stdout.write_bytes(b"<unsafe>\n")
            markup = render_lesson(src, stdout, "Control")
            self.assertIn("&lt;unsafe&gt;", markup)
            self.assertNotIn('print("<unsafe>");', markup)
            self.assertEqual(stdout.read_bytes(), b"<unsafe>\n")

    def test_highlighting_preserves_exact_copyable_scarp_source(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            folder = Path(directory)
            src = folder / "01-code.srp"
            stdout = folder / "01-code.stdout"
            raw = 'print("// <hello>"); // comment\nbind value = 42;\n'
            src.write_text(raw, encoding="utf-8")
            stdout.write_bytes(b"// <hello>\n")
            markup = render_lesson(src, stdout, "Syntax display")
            parser = ScarpSourceText()
            parser.feed(markup)
            self.assertEqual("".join(parser.parts), raw)
            self.assertIn("syntax-string", markup)
            self.assertIn("syntax-comment", markup)
            self.assertIn("syntax-keyword", markup)

    def test_carriage_return_display_does_not_modify_fixture(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            folder = Path(directory)
            src = folder / "01-cr.srp"
            stdout = folder / "01-cr.stdout"
            src.write_text('print("line\\rstart");\n', encoding="utf-8")
            raw = b"line\rstart\n"
            stdout.write_bytes(raw)
            markup = render_lesson(src, stdout, "CR output")
            self.assertIn(r"line\rstart", markup)
            self.assertNotIn("line\rstart", markup)
            self.assertIn("literal CR byte", markup)
            self.assertEqual(stdout.read_bytes(), raw)

    def test_build_all_pages_and_local_links(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            count = build(output)
            self.assertEqual(count, 50)
            self.assertTrue((output / ".nojekyll").is_file())
            sitemap = ET.parse(output / "sitemap.xml")
            locations = [
                element.text for element in sitemap.findall(
                    ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                )
            ]
            self.assertEqual(len(locations), 58)
            self.assertIn("https://scarp-lang.github.io/scarp-by-example/", locations)
            self.assertIn("https://scarp-lang.github.io/scarp-by-example/projects/", locations)
            self.assertIn(
                "https://scarp-lang.github.io/scarp-by-example/lessons/01-basics/01-hello/",
                locations,
            )
            self.assertTrue((output / "styles.css").is_file())
            self.assertTrue((output / "search.js").is_file())
            project = output / "projects/index.html"
            self.assertTrue(project.is_file())
            html = project.read_text(encoding="utf-8")
            self.assertIn("Scarp.project", html)
            self.assertIn("scarp create hello-world", html)
            self.assertIn("scarp verify tutorials/first-project", html)
            self.assertIn("scarp launch tutorials/first-project", html)
            self.assertIn("Hello from Scarp!", html)
            self.assertIn('id="hi-notes"', html)
            self.assertIn('id="en-notes"', html)
            self.assertIn("79141329176f", html)
            self.assertTrue((output / "progress.js").is_file())
            self.assertIn('data-progress-index="search-index.json"',
                          (output / "index.html").read_text(encoding="utf-8"))
            self.assertEqual(
                (output / "index.html").read_text(encoding="utf-8").count("data-progress-chapter="), 6
            )
            self.assertEqual(len(list((output / "chapters").glob("*/index.html"))), 6)
            pages = list((output / "lessons").glob("*/*/index.html"))
            self.assertEqual(len(pages), 50)
            self.assertEqual(len(list(output.rglob("index.html"))), 58)
            search = json.loads((output / "search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(search), 50)
            self.assertEqual(len({x["url"] for x in search}), 50)
            self.assertEqual(len({x["id"] for x in search}), 50)
            for item in search:
                self.assertEqual(item["url"], "lessons/" + item["id"] + "/index.html")
                self.assertRegex(item["id"], r"^[0-9]{2}-[a-z0-9-]+/[0-9]{2}-[a-z0-9-]+$")
            self.assertTrue(all(x["hindi_title"] and x["hindi_summary"] for x in search))
            self.assertIn("पहला Scarp प्रोग्राम", search[0]["hindi_title"])
            self.assertEqual({x["url"] for x in search},
                             {p.relative_to(output).as_posix() for p in pages})
            # Dedicated language notes exist on every generated lesson page.
            for lesson_page in pages:
                markup = lesson_page.read_text(encoding="utf-8")
                self.assertIn('id="en-notes"', markup, lesson_page)
                self.assertIn('id="hi-notes"', markup, lesson_page)
                self.assertIn('data-note-switch="en"', markup, lesson_page)
                self.assertIn('data-note-switch="hi"', markup, lesson_page)
                self.assertIn('class="practice-challenge"', markup, lesson_page)
                self.assertIn('id="lesson-notes"', markup, lesson_page)

            for page in output.rglob("index.html"):
                content = page.read_text(encoding="utf-8")
                self.assertIn('id="main-content"', content)
                self.assertIn('href="#main-content"', content)
                self.assertIn('id="theme-toggle"', content)
                self.assertIn('rel="canonical"', content)
                self.assertIn('progress.js', content)
                self.assertNotIn('src="https://', content)
                links = References()
                links.feed(content)
                for link in links.paths:
                    if link.startswith(("http:", "https:", "mailto:", "#")):
                        continue
                    path = link.split("#", 1)[0]
                    if not path:
                        continue
                    destination = (page.parent / path).resolve()
                    self.assertTrue(destination.is_file(),
                                    f"{page.relative_to(output)} -> {link}")
            first = output / "lessons/01-basics/01-hello/index.html"
            lesson = first.read_text(encoding="utf-8")
            self.assertIn("EXPECTED OUTPUT", lesson)
            self.assertIn("पहला Scarp प्रोग्राम", lesson)
            self.assertIn("What this example teaches", lesson)
            self.assertIn("Explanation &amp; practice", lesson)
            self.assertIn('href="#hi-notes"', lesson)
            self.assertIn("scarp verify examples/01-basics/01-hello.srp", lesson)
            self.assertIn("scarp exec examples/01-basics/01-hello.srp", lesson)
            self.assertIn('data-copy="scarp-code"', lesson)
            self.assertIn('aria-current="page"', lesson)
            self.assertIn('data-progress-current="01-basics/01-hello"', lesson)
            self.assertIn('data-progress-toggle', lesson)
            self.assertIn('data-progress-complete="01-basics/01-hello"', lesson)
            chapter = (output / "chapters/01-basics/index.html").read_text(encoding="utf-8")
            self.assertIn('data-progress-scope="01-basics"', chapter)
            self.assertIn('data-progress-count="01-basics"', chapter)
            self.assertIn('data-progress-resume', chapter)
            last = output / "lessons/06-ai-foundations/11-matrix-probabilities/index.html"
            self.assertIn("End of course", last.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
