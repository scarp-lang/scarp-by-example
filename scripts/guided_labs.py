"""Validate the bilingual guided-lab catalog and its source/fixture inventory.

Published labs are kept separate from the compiler-verified numbered lessons.
Each lab has a runnable starter, a runnable reference solution and a byte-exact
output fixture. The actual compiler runner verifies execution separately.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from verify_examples import ROOT, discover_examples, read_expected_stdout

CHAPTER = re.compile(r"^[0-9]{2}-[a-z0-9-]+$")
SUPPORT_FILE = re.compile(r"^[0-9]{2}-[a-z0-9-]+/_support/[a-z0-9_-]+[.]srp$")
FIELDS = {"id", "title", "task", "hint", "explanation"}
STRETCH_FIELDS = {"title", "task", "hint", "explanation"}
LANGUAGES = {"en", "hi"}


@dataclass(frozen=True)
class StretchChallenge:
    title: dict[str, str]
    task: dict[str, str]
    hint: dict[str, str]
    explanation: dict[str, str]
    starter: Path
    solution: Path
    expected: Path


@dataclass(frozen=True)
class GuidedLab:
    identifier: str
    title: dict[str, str]
    task: dict[str, str]
    hint: dict[str, str]
    explanation: dict[str, str]
    starter: Path
    solution: Path
    expected: Path
    stretch: StretchChallenge | None = None

    @property
    def url(self) -> str:
        return f"labs/{self.identifier}/index.html"


def validate_bilingual(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != LANGUAGES:
        raise ValueError(f"{label}: expected English and Hindi text")
    if any(not isinstance(value[lang], str) or not value[lang].strip()
           or len(value[lang]) > 600 for lang in ("en", "hi")):
        raise ValueError(f"{label}: missing or oversized translation")
    return value


def read_labs(root: Path = ROOT) -> list[GuidedLab]:
    """Reject unpublished dirs, missing files, incorrect chapters, or bad metadata."""
    metadata = json.loads((root / "docs/guided-labs.json").read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or set(metadata) != {"schema", "labs"} or metadata["schema"] != 1:
        raise ValueError("unsupported guided-lab schema")
    items = metadata["labs"]
    if not isinstance(items, list):
        raise ValueError("guided labs must be a list")
    chapters = {src.parent.name for src, _ in discover_examples(root / "examples")}
    labs: list[GuidedLab] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or set(item) not in (FIELDS, FIELDS | {"stretch"}):
            raise ValueError("guided-lab entry has missing or unexpected fields")
        identifier = item["id"]
        if not isinstance(identifier, str) or not CHAPTER.fullmatch(identifier) or identifier not in chapters:
            raise ValueError(f"unknown guided-lab chapter: {identifier!r}")
        if identifier in seen:
            raise ValueError(f"duplicate guided-lab chapter: {identifier}")
        seen.add(identifier)
        location = root / "labs" / identifier
        starter = location / "starter.srp"
        solution = location / "solution.srp"
        expected = location / "solution.stdout"
        for path in (starter, solution, expected):
            if not path.is_file():
                raise ValueError(f"missing guided-lab file: {path}")
        for path in (starter, solution):
            contents = path.read_bytes()
            if not contents or b"\r\n" in contents:
                raise ValueError(f"{path}: empty program or CRLF line endings")
            contents.decode("utf-8")
        if starter.read_bytes() == solution.read_bytes():
            raise ValueError(f"{identifier}: starter must differ from reference solution")
        if not read_expected_stdout(expected):
            raise ValueError(f"{identifier}: expected output must not be empty")
        stretch = None
        if "stretch" in item:
            extra = item["stretch"]
            if not isinstance(extra, dict) or set(extra) != STRETCH_FIELDS:
                raise ValueError(f"{identifier}: stretch challenge needs four bilingual fields")
            stretch_starter = location / "stretch-starter.srp"
            stretch_solution = location / "stretch-solution.srp"
            stretch_expected = location / "stretch-solution.stdout"
            for path in (stretch_starter, stretch_solution, stretch_expected):
                if not path.is_file():
                    raise ValueError(f"missing stretch challenge file: {path}")
            for path in (stretch_starter, stretch_solution):
                contents = path.read_bytes()
                if not contents or b"\r\n" in contents:
                    raise ValueError(f"{path}: empty program or CRLF line endings")
                contents.decode("utf-8")
            if stretch_starter.read_bytes() == stretch_solution.read_bytes():
                raise ValueError(f"{identifier}: stretch starter must differ from its solution")
            if not read_expected_stdout(stretch_expected):
                raise ValueError(f"{identifier}: stretch expected output must not be empty")
            stretch = StretchChallenge(
                title=validate_bilingual(extra["title"], identifier + " stretch title"),
                task=validate_bilingual(extra["task"], identifier + " stretch task"),
                hint=validate_bilingual(extra["hint"], identifier + " stretch hint"),
                explanation=validate_bilingual(extra["explanation"], identifier + " stretch explanation"),
                starter=stretch_starter,
                solution=stretch_solution,
                expected=stretch_expected,
            )
        labs.append(GuidedLab(
            identifier=identifier,
            title=validate_bilingual(item["title"], identifier + " title"),
            task=validate_bilingual(item["task"], identifier + " task"),
            hint=validate_bilingual(item["hint"], identifier + " hint"),
            explanation=validate_bilingual(item["explanation"], identifier + " explanation"),
            starter=starter,
            solution=solution,
            expected=expected,
            stretch=stretch,
        ))
    if seen != chapters:
        raise ValueError(f"guided-lab coverage mismatch: {sorted(chapters - seen)}")
    disk_folders = {
        folder.name for folder in (root / "labs").iterdir() if folder.is_dir()
    }
    if disk_folders != chapters:
        raise ValueError("unexpected or missing guided-lab directories")
    listed = {
        f"{lab.identifier}/{name}" for lab in labs
        for name in ("starter.srp", "solution.srp", "solution.stdout")
    }
    listed.update(
        f"{lab.identifier}/{name}" for lab in labs if lab.stretch is not None
        for name in ("stretch-starter.srp", "stretch-solution.srp", "stretch-solution.stdout")
    )
    on_disk = {
        path.relative_to(root / "labs").as_posix()
        for path in (root / "labs").rglob("*") if path.is_file()
    }
    unexpected = {p for p in on_disk - listed if not SUPPORT_FILE.fullmatch(p)}
    if unexpected:
        raise ValueError(f"unlisted guided-lab files: {sorted(unexpected)}")
    return sorted(labs, key=lambda lab: lab.identifier)
