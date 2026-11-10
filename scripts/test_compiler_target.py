"""Guard the active Scarp compiler pin while allowing separate historical checkouts."""

from __future__ import annotations

import json
import re
import unittest

from verify_examples import ROOT

TARGET = ROOT / "docs" / "compiler-target.json"
HISTORICAL_TARGET = ROOT / "docs" / "compiler-target-alpha4.json"
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

    def test_historical_provenance_uses_its_own_immutable_release_pin(self):
        historical = json.loads(HISTORICAL_TARGET.read_text(encoding="utf-8"))
        self.assertRegex(historical["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(historical["status"], "prerelease")
        self.assertEqual(historical["version"], historical["release_tag"].removeprefix("v"))
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                contents = workflow.read_text(encoding="utf-8")
                entries = [
                    entry for entry in checkout_inputs(contents)
                    if entry.get("path") == ".compiler-alpha4"
                ]
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["repository"], "scarp-lang/scarp")
                self.assertEqual(entries[0]["ref"], historical["source_commit"])
                self.assertIn("docs/compiler-target-alpha4.json", contents)
                self.assertIn("docs/migration-provenance-alpha5.json", contents)

    def test_both_workflows_pin_same_active_compiler(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                validate_compiler_checkouts(
                    workflow.read_text(encoding="utf-8"), target["source_commit"]
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
