"""Validate the fifth prerelease gate, milestone contents and publication guard."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from check_alpha5_prerelease import check_alpha5, COMPILER_SHA, TAG
from verify_examples import ROOT


class Alpha5MilestoneTests(unittest.TestCase):
    def test_current_course_is_complete_and_prerelease_eligible(self):
        message = check_alpha5()
        self.assertIn("PASS: " + TAG, message)
        self.assertIn("52 compiler-verified lessons", message)
        self.assertIn("18 checkpoints; 6 labs; 69 HTML pages", message)
        self.assertIn(COMPILER_SHA[:12], message)

    def test_rejects_compiler_pin_drift(self):
        with patch("check_alpha5_prerelease.COMPILER_SHA", "0" * 40):
            with self.assertRaisesRegex(ValueError, "compiler pin"):
                check_alpha5()

    def test_rejects_stable_tag(self):
        with patch("check_alpha5_prerelease.TAG", "v0.1.0"):
            with self.assertRaisesRegex(ValueError, "stable or malformed"):
                check_alpha5()

    def test_rejects_incomplete_lesson_milestone(self):
        with patch("check_alpha5_prerelease.LESSON_COUNT", 53):
            with self.assertRaisesRegex(ValueError, "expected 53 lessons"):
                check_alpha5()

    def test_rejects_missing_source_backed_checkpoints(self):
        with patch("check_alpha5_prerelease.read_practice_questions", return_value={}):
            with self.assertRaisesRegex(ValueError, "three source-validated checkpoints"):
                check_alpha5()

    def test_rejects_stale_source_reference_map(self):
        with patch("check_alpha5_prerelease.load_reference_map", return_value={"compiler_commit": "stale"}):
            with self.assertRaisesRegex(ValueError, "source-reference workshop pin"):
                check_alpha5()

    def test_rejects_missing_generated_page(self):
        with patch("check_alpha5_prerelease.PAGE_COUNT", 70):
            with self.assertRaisesRegex(ValueError, "number of HTML pages"):
                check_alpha5()

    def test_workflow_requires_success_on_current_main_sha(self):
        workflow = (ROOT / ".github/workflows/course-prerelease.yml").read_text(encoding="utf-8")
        self.assertIn("scarp-by-example-alpha5-prerelease", workflow)
        self.assertIn("TAG: v0.1.0-alpha.5", workflow)
        self.assertIn("python scripts/check_alpha5_prerelease.py", workflow)
        self.assertIn("--notes-file docs/releases/v0.1.0-alpha.5.md", workflow)
        self.assertIn('if [[ "$main_sha" != "$SOURCE_SHA" ]]', workflow)
        self.assertIn('for workflow in "Verify Scarp examples" "Build and publish course catalog"', workflow)
        self.assertIn('.head_sha == $sha and .event == "push"', workflow)
        self.assertIn('conclusion == "success"', workflow)
        self.assertIn('--target "$SOURCE_SHA"', workflow)
        self.assertIn("--prerelease", workflow)
        self.assertNotIn("v0.1.0-alpha.4", workflow)

    def test_previous_published_alpha4_guard_remains_immutable(self):
        historical = (ROOT / "scripts/check_prerelease.py").read_text(encoding="utf-8")
        self.assertIn('TAG = "v0.1.0-alpha.4"', historical)
        self.assertIn("2eeed0aa52ccb59523307841ad8ffbd83f8911a8", historical)


if __name__ == "__main__":
    unittest.main()
