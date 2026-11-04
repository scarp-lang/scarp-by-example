"""Regression tests for fixture-backed bilingual knowledge checks."""

from __future__ import annotations

import copy
import unittest

from build_site import read_course, render_checkpoint
from practice_questions import read_practice_questions, validate_question
from verify_examples import ROOT, discover_examples, read_expected_stdout


class PracticeQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = read_practice_questions()
        cls.fixtures = {
            src.relative_to(ROOT).as_posix(): read_expected_stdout(out)
            for src, out in discover_examples(ROOT / "examples")
        }

    def test_one_real_question_in_each_of_six_chapters(self):
        self.assertEqual(len(self.questions), 6)
        self.assertEqual(
            {src.split("/")[1] for src in self.questions},
            {"01-basics", "02-control-flow", "03-functions",
             "04-collections", "05-modules", "06-ai-foundations"},
        )
        for src, question in self.questions.items():
            self.assertEqual(validate_question(question, self.fixtures), src)

    def test_missing_or_fake_fixture_evidence_is_rejected(self):
        question = copy.deepcopy(next(iter(self.questions.values())))
        question["evidence_line"] = "This output was never produced by the compiler."
        with self.assertRaisesRegex(ValueError, "absent from verified stdout"):
            validate_question(question, self.fixtures)

    def test_invalid_answer_index_and_duplicate_choices_are_rejected(self):
        question = copy.deepcopy(next(iter(self.questions.values())))
        question["correct"] = 8
        with self.assertRaisesRegex(ValueError, "option index"):
            validate_question(question, self.fixtures)
        question["correct"] = 1
        question["options"][0] = copy.deepcopy(question["options"][1])
        with self.assertRaisesRegex(ValueError, "duplicate answer"):
            validate_question(question, self.fixtures)

    def test_missing_translation_and_unknown_source_are_rejected(self):
        question = copy.deepcopy(next(iter(self.questions.values())))
        del question["question"]["hi"]
        with self.assertRaisesRegex(ValueError, "English and Hindi"):
            validate_question(question, self.fixtures)
        question = copy.deepcopy(next(iter(self.questions.values())))
        question["source"] = "examples/99-unknown/01-example.srp"
        with self.assertRaisesRegex(ValueError, "unknown lesson"):
            validate_question(question, self.fixtures)

    def test_checkpoint_markup_escapes_bilingual_source_data(self):
        lessons, _, _ = read_course()
        lesson = next(lesson for lesson in lessons if lesson.source_path in self.questions)
        question = copy.deepcopy(self.questions[lesson.source_path])
        question["question"]["en"] = '<script>alert("unsafe")</script>'
        markup = render_checkpoint(lesson, {lesson.source_path: question})
        self.assertIn("&lt;script&gt;", markup)
        self.assertNotIn("<script>", markup)
        self.assertIn('data-checkpoint-interactive hidden', markup)
        self.assertIn('data-checkpoint-fallback', markup)
        self.assertIn('data-checkpoint-lang="hi"', markup)
        self.assertIn('type="radio"', markup)
        self.assertIn('aria-live="polite"', markup)

    def test_other_lessons_remain_unmodified(self):
        lessons, _, _ = read_course()
        unquizzed = next(item for item in lessons if item.source_path not in self.questions)
        self.assertEqual(render_checkpoint(unquizzed, self.questions), "")


if __name__ == "__main__":
    unittest.main()
