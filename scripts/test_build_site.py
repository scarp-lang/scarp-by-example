"""Tests for the deterministic, safe static course generator."""

import tempfile
import unittest
from pathlib import Path

from build_site import build, escape, lesson_description, render_catalog, render_lesson, section_heading
from verify_examples import EXAMPLES, discover_examples

ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_escapes_html_and_quotes(self):
        self.assertEqual(escape('<script x="a">'), '&lt;script x=&quot;a&quot;&gt;')

    def test_real_course_has_all_lessons(self):
        page, total = render_catalog()
        self.assertEqual(total, len(discover_examples(EXAMPLES)))
        self.assertEqual(page.count('class="lesson"'), total)
        self.assertIn("lang=\"en\"", page)
        self.assertIn("01 · Scarp basics", page)
        self.assertIn("06 · Foundations for AI-oriented programs", page)
        self.assertNotIn('src="https://', page)
        self.assertIn("हिन्दी में सीखें", page)
        self.assertIn("/docs/hi/README.md", page)

    def test_source_is_html_escaped(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory)
            src = path / "01-escape.srp"
            out = path / "01-escape.stdout"
            src.write_text('print("<unsafe>");\n', encoding="utf-8")
            out.write_text("<unsafe>\n", encoding="utf-8")
            markup = render_lesson(src, out, "Example & test")
            self.assertIn("&lt;unsafe&gt;", markup)
            self.assertNotIn('print("<unsafe>");', markup)
            self.assertIn("Example &amp; test", markup)

    def test_section_guides_describe_own_lessons(self):
        section = ROOT / "examples" / "01-basics"
        self.assertIn("Scarp basics", section_heading(section / "README.md"))
        self.assertIn("displays a string", lesson_description(section / "README.md", "01-hello.srp"))

    def test_build_creates_static_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            total = build(Path(directory))
            self.assertEqual(total, len(discover_examples(EXAMPLES)))
            page = (Path(directory) / "index.html").read_text(encoding="utf-8")
            self.assertIn("Scarp by Example", page)
            self.assertTrue((Path(directory) / "styles.css").is_file())
            self.assertTrue((Path(directory) / "search.js").is_file())
            self.assertTrue((Path(directory) / ".nojekyll").exists())


if __name__ == "__main__":
    unittest.main()
