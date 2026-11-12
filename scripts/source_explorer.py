"""Compiler-checked editorial annotations for the offline source-navigation viewer.

The JSON map gives stable *course* keys, never compiler symbol IDs. Each
position is one-based Unicode-scalar (line, column); compiler source spans are
validated as half-open UTF-8 byte ranges when the pinned CLI is available.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = Path("tutorials/source-navigation")
INDEX = PROJECT / "reference-map.json"
ALLOWED_KINDS = {"namespace", "read", "read_write", "call", "argument_label"}


def byte_span(source: bytes, line: int, column: int, token: str) -> tuple[int, int]:
    """Convert a Scarp one-based Unicode-scalar position to a UTF-8 byte span."""
    if type(line) is not int or type(column) is not int or line < 1 or column < 1:
        raise ValueError("source location must use positive integer line and column")
    lines = source.decode("utf-8").splitlines(keepends=True)
    if line > len(lines):
        raise ValueError("source line outside source file")
    text = lines[line - 1].removesuffix("\n").removesuffix("\r")
    if column > len(text) + 1:
        raise ValueError("source column outside source line")
    prefix = "".join(lines[:line - 1]).encode("utf-8")
    offset = len(prefix) + len(text[:column - 1].encode("utf-8"))
    stop = offset + len(token.encode("utf-8"))
    if source[offset:stop] != token.encode("utf-8"):
        raise ValueError(f"source location does not contain {token!r} at {line}:{column}")
    return offset, stop


def load_reference_map(root: Path = ROOT) -> dict:
    """Reject stale, unsafe or overlapping annotations before site generation."""
    data = json.loads((root / INDEX).read_text(encoding="utf-8"))
    historical = json.loads((root / "docs/compiler-target-alpha4.json").read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("schema_version") != 1
            or data.get("compiler_commit") != historical.get("source_commit")):
        raise ValueError("reference map compiler pin or schema mismatch")
    files = data.get("files")
    expected_files = ["src/main.srp", "src/lib/navigation_values.srp"]
    if files != expected_files:
        raise ValueError("reference map must include exactly the workshop source files")
    sources = {file: (root / PROJECT / file).read_bytes() for file in files}
    symbols = data.get("symbols")
    if not isinstance(symbols, list) or not symbols:
        raise ValueError("reference map is empty")
    keys: set[str] = set()
    seen: set[tuple[str, int, int]] = set()
    for symbol in symbols:
        if not isinstance(symbol, dict):
            raise ValueError("reference map contains malformed symbol")
        key = symbol.get("id")
        name = symbol.get("name")
        source_file = symbol.get("file")
        explanation = symbol.get("explanation")
        if (not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", key)
                or key in keys or not isinstance(name, str) or not name.isidentifier()
                or not isinstance(symbol.get("kind"), str) or
                type(symbol.get("public")) is not bool or source_file not in sources
                or not isinstance(explanation, dict)
                or not all(isinstance(explanation.get(lang), str)
                           and explanation[lang].strip() for lang in ("en", "hi"))):
            raise ValueError("reference map symbol fields are invalid or duplicated")
        keys.add(key)
        definition = symbol.get("definition")
        if not isinstance(definition, list) or len(definition) != 2:
            raise ValueError(f"missing definition location for {key}")
        start, end = byte_span(sources[source_file], definition[0], definition[1], name)
        if (source_file, start, end) in seen:
            raise ValueError("reference map contains overlapping or repeated locations")
        seen.add((source_file, start, end))
        references = symbol.get("references")
        if not isinstance(references, list) or not references:
            raise ValueError(f"missing reference locations for {key}")
        for ref in references:
            if (not isinstance(ref, list) or len(ref) != 4
                    or ref[0] not in sources or ref[3] not in ALLOWED_KINDS):
                raise ValueError(f"malformed reference for {key}")
            rs, re_ = byte_span(sources[ref[0]], ref[1], ref[2], name)
            if (ref[0], rs, re_) in seen:
                raise ValueError("reference map contains overlapping or repeated locations")
            seen.add((ref[0], rs, re_))
    if {s["id"] for s in symbols if s["name"] == "base"} != {
            "base-outer", "base-inner"}:
        raise ValueError("both shadowed base declarations must remain annotated")
    return data


def verify_reference_map(inventory: dict, root: Path = ROOT) -> None:
    """Check every authored link against one *real* compiler reference snapshot."""
    mapping = load_reference_map(root)
    if inventory.get("kind") != "scarp.references":
        raise ValueError("source explorer requires compiler reference metadata")
    sources = {f: (root / PROJECT / f).read_bytes() for f in mapping["files"]}
    files = inventory.get("files", [])
    file_ids: dict[str, int] = {}
    for path in mapping["files"]:
        matches = [f["id"] for f in files if
                   f["path"].replace(chr(92), "/").endswith(path)]
        # File-mode inspection on Windows may label a module by filename only.
        if not matches:
            matches = [f["id"] for f in files if
                       f["path"].replace(chr(92), "/").split("/")[-1] == path.split("/")[-1]]
        if len(matches) != 1:
            raise ValueError(f"compiler index is missing source file {path}")
        file_ids[path] = matches[0]
    symbols = inventory.get("symbols", [])
    references = inventory.get("references", [])
    for authored in mapping["symbols"]:
        file_path = authored["file"]
        span = list(byte_span(sources[file_path], *authored["definition"], authored["name"]))
        matched = [
            s for s in symbols
            if (s.get("name") == authored["name"]
                and s.get("kind") == authored["kind"]
                and s.get("public") is authored["public"]
                and isinstance(s.get("location"), dict)
                and s["location"].get("source") == file_ids[file_path]
                and s["location"].get("span") == span)
        ]
        if len(matched) != 1:
            raise ValueError(f"compiler declaration missing for {authored['id']}")
        symbol_id = matched[0]["id"]  # Local to this one result; never exported.
        for ref in authored["references"]:
            source, line, column, kind = ref
            ref_span = list(byte_span(sources[source], line, column, authored["name"]))
            uses = [r for r in references if
                    r.get("target") == symbol_id and r.get("kind") == kind
                    and r.get("location", {}).get("source") == file_ids[source]
                    and r["location"].get("span") == ref_span]
            if len(uses) != 1:
                raise ValueError(
                    f"compiler reference missing: {authored['id']} at {source}:{line}:{column}"
                )


def render_reference_explorer(root: Path = ROOT) -> str:
    """Return source-backed progressive HTML; links work without JavaScript."""
    data = load_reference_map(root)
    sources = {f: (root / PROJECT / f).read_text(encoding="utf-8")
               for f in data["files"]}
    points: dict[str, dict[int, list[tuple[int, str, str, str]]]] = {
        f: {} for f in data["files"]
    }
    for symbol in data["symbols"]:
        file = symbol["file"]
        line, col = symbol["definition"]
        points[file].setdefault(line, []).append((col, symbol["name"], symbol["id"], "definition"))
        for ref_file, line, col, kind in symbol["references"]:
            points[ref_file].setdefault(line, []).append((col, symbol["name"], symbol["id"], kind))
    panels = []
    for file, source in sources.items():
        code_lines = []
        for number, line in enumerate(source.splitlines(), 1):
            cursor = 0
            fragments = []
            for column, name, key, kind in sorted(points[file].get(number, [])):
                start = column - 1
                end = start + len(name)
                if start < cursor or line[start:end] != name:
                    raise ValueError(f"source link overlap or wrong token in {file}:{number}")
                fragments.append(html.escape(line[cursor:start], quote=True))
                fragments.append(
                    f'<a class="ref-token" href="#ref-card-{html.escape(key)}"'
                    f' data-ref-symbol="{html.escape(key)}"'
                    f' data-ref-kind="{html.escape(kind)}"'
                    f' title="{html.escape(kind.replace("_", " "))}">'
                    f'{html.escape(name)}</a>'
                )
                cursor = end
            fragments.append(html.escape(line[cursor:], quote=True))
            code_lines.append(
                f'<span class="ref-code-line" data-line="{number}">'
                f'{"".join(fragments)}\n</span>'
            )
        panels.append(
            f'<section class="ref-source-panel" aria-label="{html.escape(file)}">'
            f'<h3><code>{html.escape(file)}</code></h3>'
            f'<pre><code>{"".join(code_lines)}</code></pre></section>'
        )
    cards = []
    for symbol in data["symbols"]:
        key = html.escape(symbol["id"])
        name = html.escape(symbol["name"])
        definition = f'{symbol["file"]}:{symbol["definition"][0]}'
        count = len(symbol["references"])
        desc = symbol["explanation"]
        summary = f'{symbol["name"]}: {definition}; {count} reference(s). {desc["en"]}'
        cards.append(
            f'<li class="ref-card" id="ref-card-{key}"'
            f' data-ref-card="{key}" data-ref-summary="{html.escape(summary)}">'
            f'<a href="#ref-card-{key}" data-ref-symbol="{key}">'
            f'<strong>{name}</strong> <small>{html.escape(symbol["kind"])}</small></a>'
            f'<p class="ref-card-meta"><code>{html.escape(definition)}</code>'
            f' · {count} use(s)</p>'
            f'<p lang="en">{html.escape(desc["en"])}</p>'
            f'<p lang="hi">{html.escape(desc["hi"])}</p></li>'
        )
    return (
        '<section class="reference-explorer" data-reference-explorer'
        ' aria-labelledby="reference-explorer-title">'
        '<div class="ref-intro"><p class="eyebrow">EXPLORE STATIC LINKS · बिना कोड चलाए</p>'
        '<h2 id="reference-explorer-title">Click a name to trace its uses</h2>'
        '<p>Choose a highlighted declaration or use in either file. The matching'
        ' source positions and explanation are linked below. This is an'
        ' <strong>editorial teaching map checked against the pinned compiler</strong>,'
        ' not a live language server or browser-based Scarp execution.</p>'
        '<p class="ref-live" data-ref-status role="status" aria-live="polite">'
        'Select a highlighted name to trace it, or follow the links to a'
        ' description without JavaScript.</p></div>'
        f'<div class="ref-source-grid">{"".join(panels)}</div>'
        '<h3 class="ref-list-title">Definitions and their use sites · घोषणाएँ और प्रयोग</h3>'
        f'<ol class="ref-card-list">{"".join(cards)}</ol></section>'
    )
