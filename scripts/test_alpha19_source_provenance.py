"""Protect source-backed alpha.18/19 lessons against fixture drift.

IDs below are Git blob object hashes from published Scarp v0.0.6-alpha.19,
not cryptographic signatures. The CI compiler verifier also executes each lesson.
"""

import hashlib
import unittest

from verify_examples import ROOT

COMPILER_COMMIT = "e534e73a81c9500e3aef9f3d51cafa0bc7bbcf75"
UPSTREAM_GIT_BLOBS = {
    "examples/03-functions/05-callable-effect-boundaries.srp": "5ce51c2806c5804f0945fe4c756c9252bdda2c17",
    "examples/03-functions/05-callable-effect-boundaries.stdout": "ebdeb1a982646e24a77c63aecb5b83044fb50585",
    "examples/04-collections/15-persistent-array-updates.srp": "55cb1fc9b40d6f2cd45b293faad46a399357ca1b",
    "examples/04-collections/15-persistent-array-updates.stdout": "d336f29af65d87616a7ff84df989efd50756282e",
}


def git_blob_id(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


class Alpha19SourceProvenanceTests(unittest.TestCase):
    def test_source_and_output_match_published_git_objects(self):
        for path, expected_blob_id in UPSTREAM_GIT_BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(git_blob_id((ROOT / path).read_bytes()), expected_blob_id)


if __name__ == "__main__":
    unittest.main()
