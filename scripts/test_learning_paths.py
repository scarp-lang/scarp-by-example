"""The learning pathway is generated from the real course, quiz and lab inventories."""

from __future__ import annotations

import posixpath
import tempfile
import unittest
from pathlib import Path

from build_site import build, read_course, render_chapter_path
from guided_labs import read_labs
from practice_questions import read_practice_questions


class LearningPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons, cls.chapters, _ = read_course()
        cls.questions = read_practice_questions()
        cls.labs = {lab.identifier: lab for lab in read_labs()}

    def test_all_chapters_have_matching_quizzes_and_verified_lab(self):
        self.assertEqual(set(self.chapters), set(self.labs))
        question_paths = set(self.questions)
        self.assertEqual(len(question_paths), 18)
        for chapter, lessons in self.chapters.items():
            markup = render_chapter_path(chapter, lessons, question_paths, self.labs[chapter])
            self.assertIn('id="chapter-path"', markup)
            self.assertIn('data-path-lesson-status="' + chapter + '"', markup)
            self.assertEqual(markup.count('class="path-step"'), 3)
            self.assertEqual(markup.count('class="path-check-links"'), 1)
            self.assertEqual(markup.count('#checkpoint"'), 3)
            self.assertIn('labs/' + chapter, markup)
            self.assertIn('No quiz score is stored.', markup)
            self.assertIn('not automatically recorded', markup)

    def test_mismatched_lab_and_missing_quizzes_fail_fast(self):
        chapters = list(self.chapters)
        source = chapters[0]
        with self.assertRaisesRegex(ValueError, "does not match chapter"):
            render_chapter_path(source, self.chapters[source],
                                set(self.questions), self.labs[chapters[1]])
        with self.assertRaisesRegex(ValueError, "no source-backed checkpoints"):
            render_chapter_path(source, self.chapters[source], set(), self.labs[source])

    def test_generated_pages_form_real_navigation_to_lessons_quizzes_and_lab(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            build(destination)
            for chapter, lessons in self.chapters.items():
                path = destination / "chapters" / chapter / "index.html"
                html = path.read_text(encoding="utf-8")
                self.assertIn('id="chapter-path"', html)
                self.assertEqual(html.count('class="path-step"'), 3)
                first = lessons[0]
                first_href = "../../" + first.url
                self.assertIn('href="' + first_href + '"', html)
                for lesson in lessons:
                    if lesson.source_path not in self.questions:
                        continue
                    target = "../../" + lesson.url + "#checkpoint"
                    self.assertIn('href="' + target + '"', html)
                    quiz_markup = (destination / lesson.url).read_text(encoding="utf-8")
                    self.assertIn('id="checkpoint"', quiz_markup)
                    self.assertIn('href="../../../chapters/' + chapter +
                                  '/index.html#chapter-path"', quiz_markup)
                    self.assertIn('href="../../../labs/' + chapter +
                                  '/index.html"', quiz_markup)
                lab_url = "labs/" + chapter + "/index.html"
                self.assertIn('href="../../' + lab_url + '"', html)
                lab_markup = (destination / lab_url).read_text(encoding="utf-8")
                self.assertIn('href="../../chapters/' + chapter +
                              '/index.html#chapter-path"', lab_markup)
                self.assertNotIn('data-path-lab-passed', lab_markup)
            self.assertEqual(len(list(destination.rglob("index.html"))), 68)


if __name__ == "__main__":
    unittest.main()
