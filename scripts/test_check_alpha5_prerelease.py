"""Retain the exact historical alpha.5 course release guard.

The published alpha.5 tag and compiler source are immutable. Newer course
main branches deliberately do not satisfy the old publication gate.
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from check_alpha5_prerelease import check_alpha5, COMPILER_SHA, COMPILER_TAG, TAG
from verify_examples import ROOT


class Alpha5MilestoneTests(unittest.TestCase):
    def test_historical_release_metadata_remains_unchanged(self):
        self.assertEqual(TAG, "v0.1.0-alpha.5")
        self.assertEqual(COMPILER_TAG, "v0.0.6-alpha.2")
        self.assertEqual(COMPILER_SHA, "398b8ff705154a02423fe458ce3a427401e81e31")
        notes = (ROOT / "docs/releases/v0.1.0-alpha.5.md").read_text(encoding="utf-8")
        for value in (TAG, COMPILER_SHA, "52 lessons", "69 HTML pages"):
            self.assertIn(value, notes)

    def test_old_gate_rejects_current_compiler_upgrade(self):
        target = json.loads((ROOT / "docs/compiler-target.json").read_text(encoding="utf-8"))
        self.assertNotEqual(target["source_commit"], COMPILER_SHA)
        with self.assertRaisesRegex(ValueError, "compiler pin"):
            check_alpha5()

    def test_old_gate_rejects_stable_release_tag(self):
        with patch("check_alpha5_prerelease.TAG", "v0.1.0"):
            with self.assertRaisesRegex(ValueError, "stable or malformed"):
                check_alpha5()

    def test_historical_alpha4_gate_remains_present(self):
        old = (ROOT / "scripts/check_prerelease.py").read_text(encoding="utf-8")
        self.assertIn('TAG = "v0.1.0-alpha.4"', old)
        self.assertIn("2eeed0aa52ccb59523307841ad8ffbd83f8911a8", old)

    def test_publication_workflow_retains_immutable_release_gates(self):
        workflow = (ROOT / ".github/workflows/course-prerelease.yml").read_text(encoding="utf-8")
        for fragment in (
            "scarp-by-example-alpha5-prerelease",
            "TAG: v0.1.0-alpha.5",
            "python scripts/check_alpha5_prerelease.py",
            "--notes-file docs/releases/v0.1.0-alpha.5.md",
            'if [[ "$main_sha" != "$SOURCE_SHA" ]]',
            'for workflow in "Verify Scarp examples" "Build and publish course catalog"',
            '.head_sha == $sha and .event == "push"',
            'conclusion == "success"',
            '--target "$SOURCE_SHA"',
            "--prerelease",
            'gh release view "$TAG"',
        ):
            self.assertIn(fragment, workflow)


if __name__ == "__main__":
    unittest.main()
