"""Offline verifier and static route regressions for v0.0.7-alpha.1."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import alpha7_numerical_page as page
import verify_alpha7_numerical as verifier
from build_site import build, page_shell, rel, highlight_scarp
from test_alpha14_workshop_site import CodeText


class NumericalVerifierTests(unittest.TestCase):
    def test_canonical_inventory(self):
        verifier.check_inventory()

    def test_rejects_missing_extra_and_crlf_fixtures(self):
        for mode in ("missing", "extra", "crlf", "wrong_pin"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp) / "workshop"
                shutil.copytree(verifier.WORKSHOP, folder)
                fixture = folder / "array_concat.stdout"
                if mode == "missing":
                    fixture.unlink()
                elif mode == "extra":
                    (folder / "orphan.stdin").write_bytes(b"1\n")
                elif mode == "crlf":
                    fixture.write_bytes(b"4\r\n")
                else:
                    metadata = json.loads((folder / "compiler-target.json").read_text())
                    metadata["source_commit"] = "0" * 40
                    (folder / "compiler-target.json").write_text(json.dumps(metadata))
                with self.assertRaises(ValueError):
                    verifier.check_inventory(folder)

    def test_success_requires_exact_output_and_empty_stderr(self):
        verifier.require_success(subprocess.CompletedProcess([], 0, b"6\n", b""), b"6\n", "valid")
        for rc, stdout, stderr in ((1, b"6\n", b""), (0, b"7\n", b""), (0, b"6\n", b"warning")):
            with self.subTest(rc=rc, stdout=stdout, stderr=stderr), self.assertRaises(ValueError):
                verifier.require_success(subprocess.CompletedProcess([], rc, stdout, stderr), b"6\n", "invalid")

    def test_rejection_requires_structured_error_and_no_stdout(self):
        good = b'{"schema_version":1,"code":"E0015"}'
        verifier.require_rejection(subprocess.CompletedProcess([], 1, b"", good), "valid")
        for rc, stdout, stderr in ((0, b"", good), (1, b"unexpected", good), (1, b"", b""),
                                   (1, b"", b'{"schema_version":2,"code":"E0015"}')):
            with self.subTest(rc=rc, stdout=stdout, stderr=stderr), self.assertRaises(ValueError):
                verifier.require_rejection(subprocess.CompletedProcess([], rc, stdout, stderr), "invalid")

    def test_wrong_checkout_stops_before_compiler_execution(self):
        with patch.object(verifier.subprocess, "check_output", return_value=b"wrong\n"), \
                patch.object(verifier, "call") as call:
            with self.assertRaisesRegex(ValueError, "compiler source mismatch"):
                verifier.verify(Path("compiler"), Path("source"))
            call.assert_not_called()


class NumericalSiteTests(unittest.TestCase):
    def test_source_output_provenance_and_bilingual_notes(self):
        for name in verifier.PROGRAMS:
            with self.subTest(name=name):
                html = page.render_example(name, page_shell, rel, highlight_scarp)
                for code_id, suffix in (("scarp-code", ".srp"), ("scarp-output", ".stdout")):
                    parser = CodeText(code_id)
                    parser.feed(html)
                    self.assertEqual(parser.result(), (verifier.WORKSHOP / (name + suffix)).read_bytes().decode("utf-8"))
                self.assertIn(verifier.PIN, html)
                self.assertIn('lang="hi"', html)
                self.assertIn('lang="en"', html)
                self.assertIn("does not execute code in your browser", html)
                self.assertIn("Original MIT-licensed course program", html)

    def test_unknown_route_and_missing_fixture_fail_closed(self):
        with self.assertRaises(ValueError):
            page.lesson_path("../not-a-lesson")
        with patch.object(page, "check_inventory", side_effect=ValueError("fixture drift")):
            with self.assertRaisesRegex(ValueError, "fixture drift"):
                page.render_index(page_shell, rel)

    def test_routes_and_sitemap_do_not_change_numbered_course(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(build(folder), 60)
            routes = [page.INDEX, *(page.lesson_path(name) for name in verifier.PROGRAMS)]
            self.assertEqual(len(set(routes)), 4)
            home = (folder / "index.html").read_text(encoding="utf-8")
            sitemap = (folder / "sitemap.xml").read_text(encoding="utf-8")
            self.assertIn(f'href="{page.INDEX}"', home)
            for route in routes:
                self.assertTrue((folder / route).is_file())
                self.assertIn("https://scarp-lang.github.io/scarp-by-example/" + route.removesuffix("index.html"), sitemap)
            numbered = json.loads((folder / "search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(numbered), 60)
            self.assertNotIn("alpha7-numerical", json.dumps(numbered))


if __name__ == "__main__":
    unittest.main()
