"""Test the prerelease-only tag policy, without freezing later course lesson counts."""

import unittest

from check_prerelease import valid_prerelease_tag, check_prerelease


class TagPolicyTests(unittest.TestCase):
    def test_alpha4_release_snapshot_is_complete(self):
        self.assertIn("v0.1.0-alpha.4", check_prerelease())
        self.assertIn("18 checkpoints", check_prerelease())
        self.assertIn("6 guided labs", check_prerelease())

    def test_accepts_prerelease_tags(self):
        for tag in ("v0.1.0-alpha.1", "v0.1.0-beta.2", "v0.1.0-rc.1"):
            with self.subTest(tag=tag):
                self.assertTrue(valid_prerelease_tag(tag))

    def test_rejects_stable_and_malformed_tags(self):
        for tag in ("v1.0.0", "v0.1.0", "v0.1.0-alpha", "0.1.0-alpha.1", "v0.1.0-alpha.1\nbad"):
            with self.subTest(tag=tag):
                self.assertFalse(valid_prerelease_tag(tag))


if __name__ == "__main__":
    unittest.main()
