"""Guard the active Scarp compiler pin while allowing separate historical checkouts."""

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
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")


def checkout_inputs(workflow_text: str) -> list[dict[str, str]]:
    """Read checkout `with:` maps without interpreting arbitrary GitHub expressions.

    CI uses ordinary two-space-indented scalar YAML fields. Historical compiler
    checkouts must be distinguished by their `path`, not the order of `ref`s.
    This intentionally small parser is for auditing our checked-in workflows,
    not a general YAML implementation.
    """
    lines = workflow_text.splitlines()
    result: list[dict[str, str]] = []
    for i, line in enumerate(lines):
        match = re.fullmatch(r"( *)with:\s*(?:#.*)?", line)
        if not match:
            continue
        base_indent = len(match.group(1))
        values: dict[str, str] = {}
        for child in lines[i + 1 :]:
            if not child.strip() or child.lstrip().startswith("#"):
                continue
            indent = len(child) - len(child.lstrip(" "))
            if indent <= base_indent:
                break
            if indent != base_indent + 2:
                continue
            field = re.fullmatch(r" *([a-z][a-z0-9_-]*):\s*(.*?)\s*", child)
            if not field:
                continue
            key, raw_value = field.groups()
            if key in values:
                raise ValueError(f"duplicate checkout `with:` field: {key}")
            value = re.split(r"\s+#", raw_value, maxsplit=1)[0].strip()
            values[key] = value.strip('"\'')
        result.append(values)
    return result


def validate_compiler_checkouts(workflow_text: str, expected_sha: str) -> None:
    """Require exactly one pinned active compiler and immutable history refs."""
    if not SHA_PATTERN.fullmatch(expected_sha):
        raise ValueError("compiler target is not a full lowercase commit SHA")
    entries = [
        entry for entry in checkout_inputs(workflow_text)
        if entry.get("path", "").startswith(".compiler")
        or entry.get("repository") == "scarp-lang/scarp"
    ]
    active = [entry for entry in entries if entry.get("path") == ".compiler"]
    if len(active) != 1:
        raise ValueError(f"expected exactly one active .compiler checkout; found {len(active)}")
    for entry in entries:
        if entry.get("repository") != "scarp-lang/scarp":
            raise ValueError("compiler checkout must use the official scarp-lang/scarp repository")
        if not entry.get("path", "").startswith(".compiler"):
            raise ValueError("compiler checkout must declare a distinct .compiler path")
        if not SHA_PATTERN.fullmatch(entry.get("ref", "")):
            raise ValueError("compiler checkout must use a full immutable commit SHA")
    if active[0]["ref"] != expected_sha:
        raise ValueError("active compiler checkout differs from docs/compiler-target.json")


class CompilerTargetTests(unittest.TestCase):
    def test_active_release_is_the_reviewed_published_commit(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertEqual((target["version"], target["source_commit"]), (
            "0.0.7-alpha.1", "996bd5b83c8cb26e98637563729f67bdacc61cd4",
        ))

    def test_target_is_full_immutable_sha_and_explicit_prerelease(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertRegex(target["source_commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(target["release_tag"], r"^v\d+\.\d+\.\d+-(alpha|beta|rc)\.\d+$")
        self.assertEqual(target["version"], target["release_tag"].removeprefix("v"))
        self.assertEqual(target["status"], "prerelease")
        self.assertEqual(
            target["release_url"],
            "https://github.com/scarp-lang/scarp/releases/tag/" + target["release_tag"],
        )

    def test_human_release_labels_match_immutable_compiler_pin(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        compatibility = (ROOT / "docs" / "compatibility.md").read_text(encoding="utf-8")
        self.assertIn(
            f"Scarp {target['release_tag']} at exact source commit "
            f"`{target['source_commit']}`",
            readme,
        )
        self.assertIn(
            f"[Scarp {target['release_tag']}]({target['release_url']})",
            compatibility,
        )
        self.assertIn(f"git checkout {target['source_commit']}", compatibility)

    def test_both_workflows_pin_same_active_compiler(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                validate_compiler_checkouts(
                    workflow.read_text(encoding="utf-8"), target["source_commit"]
                )


    def test_historical_alpha13_source_remains_independently_pinned(self):
        historical = "e755fda37cdaeed29434e848cb5dd41f2f2e7eb2"
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                entries = checkout_inputs(workflow.read_text(encoding="utf-8"))
                previous = [entry for entry in entries if entry.get("path") == ".compiler-alpha13"]
                self.assertEqual(len(previous), 1)
                self.assertEqual(previous[0]["repository"], "scarp-lang/scarp")
                self.assertEqual(previous[0]["ref"], historical)
                self.assertIn(".compiler-alpha13/Cargo.toml", workflow.read_text(encoding="utf-8"))
                self.assertIn("--compiler-source .compiler-alpha13", workflow.read_text(encoding="utf-8"))

    def test_historical_exact_values_and_numerical_workshop_pins(self):
        pages = WORKFLOWS[1].read_text(encoding="utf-8")
        for directory, workflow_name, checkout, verifier in (
            ("alpha20-exact-values", "alpha20-exact-values.yml", ".compiler-alpha20", "verify_alpha20_exact_values.py"),
            ("alpha7-numerical", "alpha7-numerical.yml", ".compiler-alpha7", "verify_alpha7_numerical.py"),
        ):
            with self.subTest(workshop=directory):
                target = json.loads((ROOT / "tutorials" / directory / "compiler-target.json").read_text(encoding="utf-8"))
                workflow = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
                for source in (pages, workflow):
                    entries = [e for e in checkout_inputs(source) if e.get("path") == checkout]
                    self.assertEqual(len(entries), 1)
                    self.assertEqual(entries[0]["repository"], "scarp-lang/scarp")
                    self.assertEqual(entries[0]["ref"], target["source_commit"])
                    self.assertIn(checkout + "/Cargo.toml", source)
                    self.assertIn("scripts/" + verifier, source)
                    self.assertIn("--compiler-source " + checkout, source)

    def test_pages_publication_is_main_only(self):
        pages = WORKFLOWS[1].read_text(encoding="utf-8")
        gate = "if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'"
        # Configure, upload, and deploy must all be guarded, including manual runs.
        self.assertEqual(pages.count(gate), 3)
        deploy = pages.split("\n  deploy:\n", 1)[1]
        self.assertIn(gate, deploy)
        self.assertIn("needs: build", deploy)

    def test_historical_alpha15_boundary_compiler_is_independently_pinned(self):
        historical = "a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281"
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                contents = workflow.read_text(encoding="utf-8")
                entries = checkout_inputs(contents)
                previous = [item for item in entries if item.get("path") == ".compiler-alpha15"]
                self.assertEqual(len(previous), 1)
                self.assertEqual(previous[0]["repository"], "scarp-lang/scarp")
                self.assertEqual(previous[0]["ref"], historical)
                self.assertIn(".compiler-alpha15/Cargo.toml", contents)
                self.assertIn("--compiler-source .compiler-alpha15", contents)
                self.assertIn(
                    "scripts/verify_alpha15_limits.py --compiler .compiler-alpha15/",
                    contents,
                )

class CompilerCheckoutParserTests(unittest.TestCase):
    SHA = "a" * 40
    HISTORICAL = "b" * 40

    def sample(self, ref: str | None = None, repository: str = "scarp-lang/scarp") -> str:
        ref = self.SHA if ref is None else ref
        return (
            "steps:\n"
            "  - name: Check out active compiler\n"
            "    uses: actions/checkout@full-sha\n"
            "    with:\n"
            f"      repository: {repository}\n"
            f"      ref: {ref}\n"
            "      path: .compiler\n"
            "      persist-credentials: false\n"
        )

    def test_active_checkout(self):
        validate_compiler_checkouts(self.sample(), self.SHA)

    def test_historical_checkout_may_have_different_immutable_sha(self):
        contents = self.sample() + (
            "  - name: Check original release provenance\n"
            "    uses: actions/checkout@full-sha\n"
            "    with:\n"
            "      repository: 'scarp-lang/scarp'\n"
            f"      ref: '{self.HISTORICAL}' # immutable origin\n"
            "      path: .compiler-alpha4\n"
        )
        validate_compiler_checkouts(contents, self.SHA)

    def test_rejects_wrong_active_sha(self):
        with self.assertRaisesRegex(ValueError, "differs"):
            validate_compiler_checkouts(self.sample(self.HISTORICAL), self.SHA)

    def test_rejects_symbolic_ref_even_in_historical_checkout(self):
        contents = self.sample() + self.sample("main").replace("path: .compiler", "path: .compiler-alpha4")
        with self.assertRaisesRegex(ValueError, "immutable"):
            validate_compiler_checkouts(contents, self.SHA)

    def test_rejects_wrong_repository(self):
        with self.assertRaisesRegex(ValueError, "official"):
            validate_compiler_checkouts(self.sample(repository="example/fork"), self.SHA)

    def test_rejects_missing_or_duplicate_active_checkout(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_compiler_checkouts("steps:\n  - name: no compiler\n", self.SHA)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_compiler_checkouts(self.sample() + self.sample(), self.SHA)

    def test_rejects_hidden_ref_override(self):
        contents = self.sample().replace("      path: .compiler", "      ref: " + self.HISTORICAL + "\n      path: .compiler")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_compiler_checkouts(contents, self.SHA)


if __name__ == "__main__":
    unittest.main()
