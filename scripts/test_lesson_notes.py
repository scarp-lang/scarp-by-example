"""Source-backed bilingual note coverage, provenance, and safe rendering tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lesson_notes import (
    HindiNote, inline_html, parse_hindi_guide, read_hindi_notes, render_hindi_note,
)
from verify_examples import EXAMPLES, ROOT, discover_examples


class HindiNoteTests(unittest.TestCase):
    def test_every_compiler_verified_lesson_has_one_matching_hindi_explanation(self):
        lessons = discover_examples(EXAMPLES)
        notes = read_hindi_notes()
        self.assertEqual(len(notes), len(lessons))
        self.assertEqual(len(notes), 51)
        for source, stdout in lessons:
            key = source.relative_to(ROOT).as_posix()
            with self.subTest(lesson=key):
                note = notes[key]
                self.assertEqual(note.source_path, key)
                self.assertEqual(note.stdout_path, stdout.relative_to(ROOT).as_posix())
                self.assertTrue(note.title)
                self.assertTrue(note.summary)
                self.assertTrue(any(block.startswith("**अभ्यास:**") for block in note.blocks))
                markup = render_hindi_note(note)
                self.assertIn('class="practice-challenge"', markup)
                self.assertNotIn("[Scarp स्रोत]", markup)
                self.assertTrue(markup.strip())

    def test_hindi_numbered_module_lesson_keeps_real_cli_code_block(self):
        notes = read_hindi_notes()
        note = notes["examples/05-modules/05-exported-signatures.srp"]
        markup = render_hindi_note(note)
        self.assertIn('<pre class="note-command"><code>', markup)
        self.assertIn("scarp inspect modules --json", markup)
        self.assertIn("scarp exec", markup)

    def test_html_and_untrusted_markdown_are_never_interpreted_as_markup(self):
        note = HindiNote(
            title="Title", source_path="examples/01-basics/01-example.srp",
            stdout_path="examples/01-basics/01-example.stdout",
            blocks=(
                'समझें <script>alert("x")</script> `print("<value>")` और **मजबूत**',
                '**अभ्यास:** <img src=x onerror=alert(1)>',
                "[unexpected](javascript:alert(1))",
            ),
        )
        rendered = render_hindi_note(note)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img src=x", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<img ", rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('<code>print(&quot;&lt;value&gt;&quot;)</code>', rendered)
        self.assertIn("<strong>मजबूत</strong>", rendered)
        self.assertIn("<strong>अभ्यास:</strong>", rendered)
        self.assertEqual(inline_html("plain & text"), "plain &amp; text")

    def test_invalid_lesson_output_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory) / "01-basics.md"
            guide.write_text(
                "### 01 · पहला कार्यक्रम\n\n"
                "परीक्षण\n\n"
                "[Scarp स्रोत](../../examples/01-basics/01-hello.srp) · "
                "[सटीक अपेक्षित आउटपुट](../../examples/01-basics/02-bindings.stdout)\n\n"
                "**अभ्यास:** समझाएँ।\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "unmatched"):
                parse_hindi_guide(
                    guide,
                    {"examples/01-basics/01-hello.srp":
                     "examples/01-basics/01-hello.stdout"},
                )

    def test_missing_practice_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory) / "01-basics.md"
            guide.write_text(
                "### 01 · पहला कार्यक्रम\n\n"
                "परीक्षण\n\n"
                "[Scarp स्रोत](../../examples/01-basics/01-hello.srp) · "
                "[सटीक अपेक्षित आउटपुट](../../examples/01-basics/01-hello.stdout)\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing teaching explanation or exercise"):
                parse_hindi_guide(
                    guide,
                    {"examples/01-basics/01-hello.srp":
                     "examples/01-basics/01-hello.stdout"},
                )


if __name__ == "__main__":
    unittest.main()
