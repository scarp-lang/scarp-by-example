"""Test the prerelease-only tag policy, without freezing later course lesson counts."""

import unittest

from check_prerelease import valid_prerelease_tag, check_prerelease


class TagPolicyTests(unittest.TestCase):
    def test_published_alpha4_gate_rejects_later_course_snapshot(self):
        # The historical alpha.4 gate is deliberately fixed to its published
        # contents; a new compiler target must not qualify as that release.
        with self.assertRaisesRegex(ValueError, "compiler pin no longer matches"):
            check_prerelease()

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
