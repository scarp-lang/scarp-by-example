"""Lock Scarp alpha.17 source/fixture provenance and interactive inputs.

These three lessons copy files from Scarp release commit
7831a37939965f557ce746e1d86bf82d3d629f74.
Their exact upstream Git blob identities are checked independently of the
cross-platform compiler execution suite.
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from verify_examples import EXAMPLES, discover_examples, read_expected_stdout, read_optional_stdin

# Values are Git blob hashes from the tagged upstream Scarp compiler release.
BLOBS = {
    "01-basics/17-boolean-input.srp": "5379f5ba6e2b2410e0066f80311705b7edf91dbb",
    "01-basics/17-boolean-input.stdin": "da29283aaa47cd5d0ac424a424fe51351b767933",
    "01-basics/17-boolean-input.stdout": "daebc3e130858e0d3439ca3b3c4248ef59a597db",
    "04-collections/13-fixed-array-traversal.srp": "b88e2e700f9e8d4a5ca5f12a315a10621e3854fe",
    "04-collections/13-fixed-array-traversal.stdout": "ffd8738f199c0ae4da530c1ac41a1679bf921a58",
    "04-collections/14-order-statistics.srp": "51a417bddf5172ef775be5eb8db2600cfaea2519",
    "04-collections/14-order-statistics.stdout": "1beeaa675292c5a39226bd01c8e835b99060baac",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class Alpha17LessonSourceTests(unittest.TestCase):
    def test_exact_upstream_blobs(self):
        for name, upstream_sha in BLOBS.items():
            with self.subTest(path=name):
                content = (EXAMPLES / name).read_bytes()
                self.assertEqual(git_blob_sha(content), upstream_sha)

    def test_three_new_lessons_are_discoverable(self):
        lesson_names = {
            "01-basics/17-boolean-input.srp",
            "04-collections/13-fixed-array-traversal.srp",
            "04-collections/14-order-statistics.srp",
        }
        discovered = {
            source.relative_to(EXAMPLES).as_posix()
            for source, _ in discover_examples(EXAMPLES)
        }
        self.assertTrue(lesson_names <= discovered)

    def test_boolean_input_and_output_are_byte_exact(self):
        path = EXAMPLES / "01-basics" / "17-boolean-input.srp"
        self.assertEqual(read_optional_stdin(path.with_suffix(".stdin")), b"true\nfalse\n")
        self.assertEqual(
            read_expected_stdout(path.with_suffix(".stdout")),
            b"Continue (true/false)? Continue (true/false)? Continuing\nStopped\n",
        )


if __name__ == "__main__":
    unittest.main()
