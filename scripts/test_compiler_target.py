"""Ensure the website and both workflows agree on an immutable released compiler SHA."""

from __future__ import annotations

import json
import re
import unittest

from verify_examples import ROOT

TARGET = ROOT / "docs" / "compiler-target.json"
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "examples.yml",
    ROOT / ".github" / "workflows" / "pages.yml",
)


class CompilerTargetTests(unittest.TestCase):
    def test_target_is_full_immutable_sha_and_explicit_prerelease(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertRegex(target["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(target["version"], target["release_tag"].removeprefix("v"))
        self.assertEqual(target["status"], "prerelease")
        self.assertEqual(
            target["release_url"],
            "https://github.com/scarp-lang/scarp/releases/tag/" + target["release_tag"],
        )

    def test_both_workflows_pin_same_exact_commit(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                contents = workflow.read_text(encoding="utf-8")
                refs = re.findall(r"(?m)^\s+ref:\s+([0-9a-f]{40})\s*$", contents)
                self.assertEqual(refs, [target["source_commit"]])
                self.assertIn("repository: scarp-lang/scarp", contents)


if __name__ == "__main__":
    unittest.main()
