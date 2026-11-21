"""Guard the historical alpha.14 course snapshot against accidental upgrades."""

from __future__ import annotations

import json
import unittest

from verify_alpha14_course import (
    MANIFEST, COMPILER_PIN, COURSE_BASELINE, git_blob_sha, validate_manifest,
)
from verify_examples import EXAMPLES, VerificationError, discover_examples


class FrozenCourseTests(unittest.TestCase):
    def setUp(self):
        self.metadata = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_immutable_release_and_55_lesson_baseline(self):
        self.assertEqual(COMPILER_PIN, "43627b74af5fccccc5e233e98207413983ebafc1")
        self.assertEqual(COURSE_BASELINE, "03e0c93807e509e0a3a88da37e7ea4b3f6ef98d8")
        pairs = validate_manifest(self.metadata)
        self.assertEqual(len(pairs), 55)
        discovered = {src for src, _ in discover_examples(EXAMPLES)}
        self.assertTrue({src for src, _ in pairs} <= discovered)
        self.assertEqual(len(discovered), 58)

    def test_does_not_smuggle_newer_alpha17_features_into_alpha14(self):
        frozen = {p["source"] for p in self.metadata["lessons"]}
        for newer in (
            "examples/01-basics/17-boolean-input.srp",
            "examples/04-collections/13-fixed-array-traversal.srp",
            "examples/04-collections/14-order-statistics.srp",
        ):
            self.assertNotIn(newer, frozen)

    def test_rejects_missing_manifest_entry(self):
        self.metadata["lessons"].pop()
        with self.assertRaisesRegex(VerificationError, "manifest identity or count"):
            validate_manifest(self.metadata)

    def test_rejects_duplicate_or_wrong_checksum(self):
        item = self.metadata["lessons"][0]
        self.metadata["lessons"][1]["source"] = item["source"]
        with self.assertRaisesRegex(VerificationError, "duplicate"):
            validate_manifest(self.metadata)
        self.metadata = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.metadata["lessons"][0]["source_blob"] = "0" * 40
        with self.assertRaisesRegex(VerificationError, "differs from baseline"):
            validate_manifest(self.metadata)

    def test_git_blob_hash_is_sensitive_to_bytes(self):
        self.assertNotEqual(git_blob_sha(b"alpha14\\n"), git_blob_sha(b"alpha17\\n"))

    def test_workflow_checks_only_historical_subset_with_old_compiler(self):
        from verify_examples import ROOT
        workflow = (ROOT / ".github/workflows/alpha14-patterns.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/verify_alpha14_course.py --compiler", workflow)
        self.assertNotIn("scripts/verify_examples.py --compiler", workflow)


if __name__ == "__main__":
    unittest.main()
