"""Regression tests for source/output provenance, pinning and path safety."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from verify_migration_provenance import ProvenanceError, verify_provenance

COMMIT = "f04be0758cbce405ddcdb229699b0ff83c09d207"


class MigrationProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.compiler = self.root / "compiler"
        self.course = self.root / "course"
        self.target = {"release_tag": "v0.0.6-alpha.4", "source_commit": COMMIT}
        self.entry = {
            "compiler_source": "examples/case.srp",
            "compiler_stdout": "examples/case.stdout",
            "course_source": "examples/01-basics/01-case.srp",
            "course_stdout": "examples/01-basics/01-case.stdout",
        }
        self.manifest = {
            "schema_version": 1,
            "compiler_release": self.target["release_tag"],
            "compiler_source_commit": COMMIT,
            "migrations": [copy.deepcopy(self.entry)],
        }
        for prefix, source, output in [
            (self.compiler, "examples/case.srp", "examples/case.stdout"),
            (self.course, "examples/01-basics/01-case.srp", "examples/01-basics/01-case.stdout"),
        ]:
            a, b = prefix / source, prefix / output
            a.parent.mkdir(parents=True, exist_ok=True)
            a.write_bytes(b'print("ok");\n')
            b.write_bytes(b"ok\n")

    def check(self) -> int:
        return verify_provenance(self.manifest, self.target, self.compiler, self.course)

    def test_exact_tagged_program_and_stdout_are_preserved(self):
        self.assertEqual(self.check(), 1)

    def test_copied_program_drift_is_rejected(self):
        (self.course / self.entry["course_source"]).write_bytes(b'print("changed");\n')
        with self.assertRaisesRegex(ProvenanceError, "source diverged"):
            self.check()

    def test_copied_stdout_drift_is_rejected(self):
        (self.course / self.entry["course_stdout"]).write_bytes(b"changed\n")
        with self.assertRaisesRegex(ProvenanceError, "stdout diverged"):
            self.check()

    def test_pin_mismatch_is_rejected(self):
        self.manifest["compiler_release"] = "v0.0.6-alpha.5"
        with self.assertRaisesRegex(ProvenanceError, "pinned published compiler"):
            self.check()

    def test_commit_mismatch_is_rejected(self):
        self.manifest["compiler_source_commit"] = "0" * 40
        with self.assertRaisesRegex(ProvenanceError, "pinned published compiler"):
            self.check()

    def test_path_traversal_is_rejected(self):
        self.manifest["migrations"][0]["course_source"] = "../outside.srp"
        with self.assertRaisesRegex(ProvenanceError, "invalid example path"):
            self.check()

    def test_missing_source_file_is_rejected(self):
        (self.compiler / self.entry["compiler_source"]).unlink()
        with self.assertRaisesRegex(ProvenanceError, "missing example fixture"):
            self.check()

    def test_orphaned_stdout_mapping_is_rejected(self):
        self.manifest["migrations"][0]["compiler_stdout"] = "examples/different.stdout"
        with self.assertRaisesRegex(ProvenanceError, "source and stdout names"):
            self.check()

    def test_duplicate_entry_is_rejected(self):
        self.manifest["migrations"].append(copy.deepcopy(self.entry))
        with self.assertRaisesRegex(ProvenanceError, "duplicate compiler source"):
            self.check()

    def test_empty_manifest_is_rejected(self):
        self.manifest["migrations"] = []
        with self.assertRaisesRegex(ProvenanceError, "at least one"):
            self.check()

    def test_incomplete_manifest_is_rejected(self):
        del self.manifest["migrations"][0]["course_stdout"]
        with self.assertRaisesRegex(ProvenanceError, "incomplete"):
            self.check()


if __name__ == "__main__":
    unittest.main()
