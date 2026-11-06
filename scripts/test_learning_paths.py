"""The learning pathway is generated from the real course, quiz and lab inventories."""

from __future__ import annotations

import posixpath
import tempfile
import unittest
from pathlib import Path

from build_site import (build, read_course, render_chapter_path,
                        render_chapter_journey, render_lesson_chapter_handoff,
                        rel, chapter_url, render_chapter_review)
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


    def test_chapter_sequence_uses_real_course_order_and_boundaries(self):
        sections = list(self.chapters)
        self.assertEqual(len(sections), 6)
        for index, section in enumerate(sections):
            markup = render_chapter_journey(section, self.chapters)
            self.assertIn('aria-label="Previous and next chapters"', markup)
            self.assertIn(f"Chapter {index + 1} of {len(sections)}", markup)
            self.assertEqual(markup.count('class="chapter-journey-card"'),
                             int(index > 0) + int(index + 1 < len(sections)))
            self.assertEqual(markup.count('class="chapter-journey-end"'),
                             int(index == 0) + int(index + 1 == len(sections)))
            self.assertIn("verified lessons", markup)
            if index > 0:
                self.assertIn(rel(chapter_url(section), chapter_url(sections[index - 1])),
                              markup)
            if index + 1 < len(sections):
                self.assertIn(rel(chapter_url(section), chapter_url(sections[index + 1])),
                              markup)
        with self.assertRaisesRegex(ValueError, "unknown or empty chapter"):
            render_chapter_journey("99-unknown", self.chapters)
        with self.assertRaisesRegex(ValueError, "unknown or empty chapter"):
            render_chapter_journey(sections[0], {sections[0]: []})

    def test_lesson_handoff_only_at_real_chapter_boundaries(self):
        sections = list(self.chapters)
        handoffs = 0
        for index, section in enumerate(sections):
            chapter = self.chapters[section]
            for lesson in chapter[:-1]:
                self.assertEqual(
                    render_lesson_chapter_handoff(lesson, chapter, self.lessons), "")
            last = chapter[-1]
            markup = render_lesson_chapter_handoff(last, chapter, self.lessons)
            handoffs += 1
            self.assertIn('id="chapter-handoff-title"', markup)
            self.assertIn("labs/" + section + "/index.html", markup)
            self.assertIn("Your lesson progress changes only when", markup)
            if index + 1 < len(sections):
                self.assertIn("chapters/" + sections[index + 1] + "/index.html",
                              markup)
                self.assertIn(self.chapters[sections[index + 1]][0].chapter,
                              markup)
            else:
                self.assertIn("Review all chapters", markup)
                self.assertIn("index.html#chapters", markup)
        self.assertEqual(handoffs, len(sections))

    def test_generated_pages_connect_all_chapters_and_last_lessons(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            build(output)
            sections = list(self.chapters)
            for index, section in enumerate(sections):
                chapter_page = (output / "chapters" / section /
                                "index.html").read_text(encoding="utf-8")
                self.assertEqual(chapter_page.count('class="chapter-journey"'), 1)
                self.assertIn('aria-label="Previous and next chapters"', chapter_page)
                if index + 1 < len(sections):
                    self.assertIn(
                        'href="' + rel(chapter_url(section), chapter_url(sections[index + 1])) + '"',
                        chapter_page)
                last = self.chapters[section][-1]
                last_page = (output / last.url).read_text(encoding="utf-8")
                self.assertEqual(last_page.count('class="chapter-handoff"'), 1)
                self.assertIn('aria-label="Lesson navigation"', last_page)
                self.assertIn("labs/" + section + "/index.html", last_page)
                for lesson in self.chapters[section][:-1]:
                    markup = (output / lesson.url).read_text(encoding="utf-8")
                    self.assertNotIn('class="chapter-handoff"', markup)
            self.assertEqual(len(list(output.rglob("index.html"))), 68)


    def test_chapter_review_reuses_exact_three_validated_questions(self):
        for section, lessons in self.chapters.items():
            markup = render_chapter_review(section, lessons, self.questions)
            checks = [lesson for lesson in lessons
                      if lesson.source_path in self.questions]
            self.assertEqual(len(checks), 3)
            self.assertIn('id="chapter-review"', markup)
            self.assertIn('<summary>', markup)
            self.assertIn("no stored score", markup)
            self.assertEqual(markup.count(' data-checkpoint\n'), 3)
            self.assertEqual(markup.count('data-checkpoint-form'), 3)
            self.assertEqual(markup.count('data-checkpoint-fallback'), 3)
            self.assertEqual(markup.count('data-checkpoint-explanation'), 3)
            for index, lesson in enumerate(checks, 1):
                identity = f"chapter-check-{index:02}"
                self.assertEqual(markup.count('id="' + identity + '"'), 1)
                self.assertEqual(markup.count('id="' + identity + '-title"'), 1)
                self.assertIn('aria-labelledby="' + identity + '-title"', markup)
                source = self.questions[lesson.source_path]
                self.assertIn('data-checkpoint-answer="' +
                              str(source["correct"]) + '"', markup)
                self.assertIn(rel(chapter_url(section), lesson.url) +
                              '#verified-output', markup)
                self.assertIn("Question " + str(index) + " of 3", markup)
        first = next(iter(self.chapters))
        with self.assertRaisesRegex(ValueError, "three distinct verified"):
            render_chapter_review(first, self.chapters[first], {})
        with self.assertRaisesRegex(ValueError, "outside"):
            other = list(self.chapters)[1]
            render_chapter_review(first,
                                  [*self.chapters[first], self.chapters[other][0]],
                                  self.questions)

    def test_generated_chapter_review_works_without_javascript(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            build(output)
            self.assertEqual(len(list((output / "chapters").glob("*/index.html"))), 6)
            for section, lessons in self.chapters.items():
                markup = (output / chapter_url(section)).read_text(encoding="utf-8")
                self.assertIn('src="../../checkpoint.js"', markup)
                self.assertIn('id="chapter-review"', markup)
                self.assertIn('href="#chapter-review"', markup)
                self.assertEqual(markup.count('data-checkpoint-answer='), 3)
                self.assertEqual(markup.count('data-checkpoint-interactive hidden'), 3)
                self.assertEqual(markup.count('data-checkpoint-fallback'), 3)
                self.assertEqual(markup.count('class="chapter-review-context"'), 3)
                for index in range(1, 4):
                    self.assertIn(f'id="chapter-check-{index:02}"', markup)
                self.assertIn("does not run Scarp in the browser", markup)
            for lesson in self.lessons:
                markup = (output / lesson.url).read_text(encoding="utf-8")
                self.assertNotIn('id="chapter-review"', markup)
                if lesson.source_path in self.questions:
                    self.assertIn('id="checkpoint"', markup)
                    self.assertIn('aria-labelledby="checkpoint-title"', markup)

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
