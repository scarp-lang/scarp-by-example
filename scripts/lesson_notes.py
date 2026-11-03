"""Extract verified per-lesson Hindi teaching notes from existing chapter guides.

One authoritative Hindi chapter file per subject remains the source of truth.
All entry paths are checked against discover_examples; no guessed lesson content
or copied source is introduced by the static website.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from verify_examples import ROOT, discover_examples

HEADER = re.compile(r"^### ([0-9]{2}) · (.+)$", re.MULTILINE)
NEXT_HEADING = re.compile(r"^#{2,3} ", re.MULTILINE)
SOURCE_REF = re.compile(
    r"\[Scarp स्रोत\]\(\.\./\.\./(examples/[a-z0-9/_-]+\.srp)\)"
)
OUTPUT_REF = re.compile(
    r"\[सटीक अपेक्षित आउटपुट\]\(\.\./\.\./(examples/[a-z0-9/_-]+\.stdout)\)"
)
MARKUP = re.compile(
    r"(\*\*[^*\n]+\*\*|`[^`\n]+`|\[[^\]]+\]\([^)]+\))"
)
SOURCE_LINE = re.compile(r"^\[Scarp स्रोत\].*$", re.MULTILINE)


@dataclass(frozen=True)
class HindiNote:
    title: str
    source_path: str
    stdout_path: str
    blocks: tuple[str, ...]

    @property
    def summary(self) -> str:
        return next(
            (block.replace("`", "").replace("**", "")
             for block in self.blocks
             if not block.startswith(("**", "```"))),
            self.title,
        )


def parse_hindi_guide(guide: Path, expected_outputs: dict[str, str]) -> dict[str, HindiNote]:
    """Validate every heading/link in one guide, preserving its original prose."""
    text = guide.read_text(encoding="utf-8")
    parsed: dict[str, HindiNote] = {}
    headings = list(HEADER.finditer(text))
    if not headings:
        raise ValueError(f"{guide}: no numbered Hindi lesson headings")
    for heading in headings:
        start = heading.end()
        following = NEXT_HEADING.search(text, start)
        end = following.start() if following else len(text)
        content = text[start:end].strip()
        source = SOURCE_REF.findall(content)
        output = OUTPUT_REF.findall(content)
        if len(source) != 1 or len(output) != 1:
            raise ValueError(
                f"{guide}: lesson {heading.group(1)} must link one source and stdout"
            )
        src, out = source[0], output[0]
        if (src not in expected_outputs or expected_outputs[src] != out
                or Path(src).parent.name != guide.stem
                or Path(src).stem[:2] != heading.group(1)):
            raise ValueError(f"{guide}: unmatched or misnumbered lesson {src}")
        if src in parsed:
            raise ValueError(f"{guide}: duplicate lesson {src}")
        prose = SOURCE_LINE.sub("", content).strip()
        blocks = tuple(p.strip() for p in re.split(r"\n\s*\n", prose) if p.strip())
        if not blocks or not any(b.startswith("**अभ्यास:**") for b in blocks):
            raise ValueError(f"{guide}: missing teaching explanation or exercise for {src}")
        parsed[src] = HindiNote(
            title=heading.group(2).strip(),
            source_path=src,
            stdout_path=out,
            blocks=blocks,
        )
    return parsed


def read_hindi_notes(root: Path = ROOT) -> dict[str, HindiNote]:
    """Require exactly one Hindi note for every runnable Scarp lesson."""
    pairs = discover_examples(root / "examples")
    expected = {
        source.relative_to(root).as_posix(): stdout.relative_to(root).as_posix()
        for source, stdout in pairs
    }
    notes: dict[str, HindiNote] = {}
    for section in sorted({src.parent.name for src, _ in pairs}):
        guide = root / "docs" / "hi" / f"{section}.md"
        if not guide.is_file():
            raise ValueError(f"missing Hindi guide: {guide}")
        chapter_notes = parse_hindi_guide(guide, expected)
        for path, note in chapter_notes.items():
            if path in notes:
                raise ValueError(f"duplicate cross-chapter Hindi note: {path}")
            notes[path] = note
    if notes.keys() != expected.keys():
        missing = sorted(expected.keys() - notes.keys())
        raise ValueError(f"Hindi lesson coverage mismatch: {missing}")
    return notes


def inline_html(markdown: str) -> str:
    """Escape arbitrary HTML; render only simple inline code, bold and a safe link."""
    chunks: list[str] = []
    cursor = 0
    for match in MARKUP.finditer(markdown):
        chunks.append(html.escape(markdown[cursor:match.start()], quote=True))
        token = match.group()
        if token.startswith("**"):
            chunks.append(f"<strong>{html.escape(token[2:-2], quote=True)}</strong>")
        elif token.startswith("`"):
            chunks.append(f"<code>{html.escape(token[1:-1], quote=True)}</code>")
        else:
            link = re.fullmatch(r"\[([^]]+)\]\(([^)]+)\)", token)
            if link and link.group(2) == "cli-quickstart.md":
                chunks.append(
                    '<a href="https://github.com/scarp-lang/scarp-by-example/'
                    'blob/main/docs/hi/cli-quickstart.md">'
                    + html.escape(link.group(1), quote=True) + "</a>"
                )
            else:
                chunks.append(html.escape(token, quote=True))
        cursor = match.end()
    chunks.append(html.escape(markdown[cursor:], quote=True))
    return "".join(chunks)


def render_hindi_note(note: HindiNote) -> str:
    """Render the original explanation, expected-output hints and practice safely."""
    rendered: list[str] = []
    for block in note.blocks:
        if block.startswith("```") and block.endswith("```"):
            lines = block.splitlines()
            if len(lines) < 3:
                raise ValueError(f"{note.source_path}: invalid fenced command block")
            rendered.append(
                '<pre class="note-command"><code>'
                + html.escape("\n".join(lines[1:-1]), quote=True)
                + "</code></pre>"
            )
        elif block.startswith("**अभ्यास:**"):
            rendered.append(
                '<div class="practice-challenge"><p>'
                + inline_html(" ".join(block.splitlines()))
                + "</p></div>"
            )
        else:
            rendered.append(f'<p>{inline_html(" ".join(block.splitlines()))}</p>')
    return "\n".join(rendered)
