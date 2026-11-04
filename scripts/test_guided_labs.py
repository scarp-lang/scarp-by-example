"""Source-backed guided coding lab catalog and runner regression tests."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

from guided_labs import read_labs, validate_bilingual
from verify_examples import ROOT, VerificationError, read_expected_stdout
from verify_guided_labs import verify_lab
from build_site import build


class GuidedLabCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labs = read_labs()

    def test_one_authentic_starter_and_solution_per_course_chapter(self):
        self.assertEqual(len(self.labs), 6)
        self.assertEqual({lab.identifier for lab in self.labs}, {
            "01-basics", "02-control-flow", "03-functions",
            "04-collections", "05-modules", "06-ai-foundations",
        })
        for lab in self.labs:
            self.assertNotEqual(lab.starter.read_bytes(), lab.solution.read_bytes())
            self.assertTrue(read_expected_stdout(lab.expected))
            self.assertEqual(set(lab.title), {"en", "hi"})
            self.assertEqual(set(lab.task), {"en", "hi"})
            self.assertEqual(set(lab.hint), {"en", "hi"})
            self.assertEqual(set(lab.explanation), {"en", "hi"})

    def test_bad_translation_rejected(self):
        with self.assertRaisesRegex(ValueError, "English and Hindi"):
            validate_bilingual({"en": "hello"}, "test")
        with self.assertRaisesRegex(ValueError, "translation"):
            validate_bilingual({"en": " ", "hi": "नमस्ते"}, "test")

    def test_static_verify_and_real_exec_are_required_for_starter(self):
        lab = self.labs[0]
        quiet = subprocess.CompletedProcess(["scarp"], 0, b"", b"")
        wrong = subprocess.CompletedProcess(["scarp"], 0, b"13\n", b"")
        with patch("verify_guided_labs.run_checked", side_effect=[quiet, wrong]) as runner, \
             patch("verify_guided_labs.verify_one") as solution_verifier:
            verify_lab(Path("scarp"), lab)
        self.assertEqual([call.args[1] for call in runner.call_args_list], ["verify", "exec"])
        solution_verifier.assert_called_once()

    def test_starter_must_not_already_match_reference_output(self):
        lab = self.labs[0]
        quiet = subprocess.CompletedProcess(["scarp"], 0, b"", b"")
        solved = subprocess.CompletedProcess(["scarp"], 0, b"42\n", b"")
        with patch("verify_guided_labs.run_checked", side_effect=[quiet, solved]), \
             patch("verify_guided_labs.verify_one") as solution_verifier:
            with self.assertRaisesRegex(VerificationError, "already matches"):
                verify_lab(Path("scarp"), lab)
        solution_verifier.assert_not_called()

    def test_starter_verify_must_be_silent(self):
        lab = self.labs[0]
        noisy = subprocess.CompletedProcess(["scarp"], 0, b"wrong\n", b"")
        with patch("verify_guided_labs.run_checked", return_value=noisy):
            with self.assertRaisesRegex(VerificationError, "must be silent"):
                verify_lab(Path("scarp"), lab)

    def test_generated_labs_are_linked_and_have_exact_github_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            self.assertEqual(build(out), 50)
            homepage = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="labs/index.html"', homepage)
            overview = (out / "labs/index.html").read_text(encoding="utf-8")
            self.assertEqual(overview.count('class="lab-card"'), 6)
            for lab in self.labs:
                page = out / lab.url
                self.assertTrue(page.is_file())
                markup = page.read_text(encoding="utf-8")
                self.assertIn("starter.srp", markup)
                self.assertIn("solution.srp", markup)
                self.assertIn("solution.stdout", markup)
                self.assertIn("attempt.srp", markup)
                self.assertIn("<details>", markup)
                self.assertIn("lang=\"hi\"", markup)
                self.assertIn("does not produce the goal", markup)
                self.assertIn("scarp verify labs/" + lab.identifier + "/attempt.srp", markup)
                self.assertIn("scarp exec labs/" + lab.identifier + "/attempt.srp", markup)
                self.assertIn("github.com/scarp-lang/scarp-by-example/blob/main/", markup)
                expected = read_expected_stdout(lab.expected).decode("utf-8").strip()
                self.assertIn(expected, markup)
            sitemap = ET.parse(out / "sitemap.xml")
            locations = [node.text for node in sitemap.findall(
                ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )]
            self.assertEqual(len(locations), 65)
            self.assertIn(
                "https://scarp-lang.github.io/scarp-by-example/labs/01-basics/",
                locations
            )
            self.assertEqual(len(list(out.rglob("index.html"))), 65)


if __name__ == "__main__":
    unittest.main()
