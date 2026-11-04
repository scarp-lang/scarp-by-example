"""Load curated English/Hindi checkpoints tied to exact checked-in Scarp output.

These are editorial multiple-choice questions, not browser execution.
A fixture-evidence line and the correct answer must agree before site publication.
"""

from __future__ import annotations

import json
from pathlib import Path

from verify_examples import ROOT, EXAMPLES, discover_examples, read_expected_stdout

QUESTION_FILE = ROOT / "docs" / "practice-questions.json"
LANGUAGES = {"en", "hi"}


def language_pair(value: object, label: str) -> None:
    if not isinstance(value, dict) or set(value) != LANGUAGES:
        raise ValueError(f"{label}: expected English and Hindi strings")
    if any(not isinstance(value[lang], str) or not value[lang].strip()
           or len(value[lang]) > 500 for lang in LANGUAGES):
        raise ValueError(f"{label}: missing or oversized translation")


def validate_question(question: object, fixtures: dict[str, bytes]) -> str:
    """Return source path only if source, fixture and translations all agree."""
    required = {"source", "evidence_line", "question", "options", "correct", "explanation"}
    if not isinstance(question, dict) or set(question) != required:
        raise ValueError("invalid practice question fields")
    source = question["source"]
    if not isinstance(source, str) or source not in fixtures:
        raise ValueError(f"practice question refers to an unknown lesson: {source}")
    evidence = question["evidence_line"]
    if not isinstance(evidence, str) or not evidence or len(evidence) > 250:
        raise ValueError(f"{source}: invalid evidence line")
    if evidence not in fixtures[source].decode("utf-8").splitlines():
        raise ValueError(f"{source}: evidence is absent from verified stdout")
    language_pair(question["question"], source + " question")
    language_pair(question["explanation"], source + " explanation")
    options = question["options"]
    if not isinstance(options, list) or len(options) != 3:
        raise ValueError(f"{source}: require exactly three answer options")
    for i, option in enumerate(options):
        language_pair(option, f"{source}: option {i}")
    for lang in LANGUAGES:
        if len({option[lang].strip().casefold() for option in options}) != 3:
            raise ValueError(f"{source}: duplicate {lang} answer options")
    correct = question["correct"]
    if type(correct) is not int or correct not in (0, 1, 2):
        raise ValueError(f"{source}: correct must be an option index")
    if options[correct]["en"] not in evidence:
        raise ValueError(f"{source}: correct answer does not appear in fixture evidence")
    return source


def read_practice_questions(root: Path = ROOT) -> dict[str, dict]:
    """Require exactly one curated, source-backed question per published chapter."""
    raw = json.loads((root / "docs/practice-questions.json").read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"schema", "questions"} or raw["schema"] != 1:
        raise ValueError("unsupported practice question schema")
    items = raw["questions"]
    if not isinstance(items, list):
        raise ValueError("practice questions must be a list")
    fixtures = {
        source.relative_to(root).as_posix(): read_expected_stdout(stdout)
        for source, stdout in discover_examples(root / "examples")
    }
    result: dict[str, dict] = {}
    for item in items:
        source = validate_question(item, fixtures)
        if source in result:
            raise ValueError(f"duplicate practice question: {source}")
        result[source] = item
    chapters = {Path(src).parent.name for src in fixtures}
    covered = {Path(src).parent.name for src in result}
    if covered != chapters:
        raise ValueError(f"chapter checkpoint coverage mismatch: {chapters - covered}")
    return result
