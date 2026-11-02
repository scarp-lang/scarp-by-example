#!/usr/bin/env python3
"""Generate a static, accessible catalog from the verified Scarp lesson sources."""

from __future__ import annotations

import argparse
import html
import re
import shutil
from pathlib import Path

from verify_examples import EXAMPLES, ROOT, discover_examples

ASSETS = ROOT / "site"
REPOSITORY = "https://github.com/scarp-lang/scarp-by-example"


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def section_heading(readme: Path) -> str:
    first = readme.read_text(encoding="utf-8").splitlines()[0]
    if not first.startswith("# "):
        raise ValueError(f"missing section heading in {readme}")
    return first.removeprefix("# ").strip()


def lesson_description(readme: Path, filename: str) -> str:
    """Extract the lesson's description from its human-written section table."""
    for line in readme.read_text(encoding="utf-8").splitlines():
        if f"]({filename})" not in line:
            continue
        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) >= 2:
            return columns[1].replace("`", "")
    raise ValueError(f"{readme}: no description for {filename}")


def render_lesson(source: Path, stdout: Path, description: str) -> str:
    rel = source.relative_to(ROOT).as_posix()
    title = source.stem.split("-", 1)[1].replace("-", " ").title()
    raw_source = source.read_text(encoding="utf-8")
    raw_output = stdout.read_text(encoding="utf-8")
    search_text = f"{title} {description} {source.parent.name}"
    return (
        f'<article class="lesson" data-search="{escape(search_text.lower())}">'
        f'<div class="lesson-info"><p class="eyebrow">{escape(source.stem[:2])}</p>'
        f'<h3>{escape(title)}</h3><p>{escape(description)}</p>'
        f'<a href="{escape(REPOSITORY + "/blob/main/" + rel)}">View Scarp source on GitHub</a></div>'
        f'<details><summary>Code and expected output</summary>'
        f'<p class="code-label">Scarp (.srp)</p>'
        f'<pre><code>{escape(raw_source)}</code></pre>'
        f'<p class="code-label">Expected stdout</p>'
        f'<pre><code>{escape(raw_output)}</code></pre>'
        f'</details></article>'
    )


def render_catalog() -> tuple[str, int]:
    lessons = discover_examples(EXAMPLES)
    by_section: dict[str, list[tuple[Path, Path]]] = {}
    for lesson, fixture in lessons:
        by_section.setdefault(lesson.parent.name, []).append((lesson, fixture))

    sections = []
    for section, pairs in sorted(by_section.items()):
        readme = EXAMPLES / section / "README.md"
        heading = section_heading(readme)
        cards = "".join(
            render_lesson(src, out, lesson_description(readme, src.name))
            for src, out in pairs
        )
        guide_url = REPOSITORY + "/blob/main/examples/" + section + "/README.md"
        sections.append(
            f'<section class="section" aria-label="{escape(heading)}">'
            f'<div class="section-heading"><h2>{escape(heading)}</h2>'
            f'<a href="{escape(guide_url)}">Read chapter guide</a></div>'
            f'<div class="lesson-grid">{cards}</div></section>'
        )
    content = "\n".join(sections)
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Learn the Scarp programming language with tested, practical .srp examples and expected outputs.">
<title>Scarp by Example — Learn with real Scarp code</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip-link" href="#course">Skip to lessons</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="./" aria-label="Scarp by Example home"><span class="mark">S</span><span>Scarp <strong>by Example</strong></span></a>
<nav aria-label="Project links"><a href="https://github.com/scarp-lang/scarp">Compiler</a><a href="https://github.com/scarp-lang/scarp-docs">Docs</a><a href="https://scarp-lang.github.io/">Website</a><a href="{REPOSITORY}">GitHub</a></nav>
</div></header>
<main id="course" class="container">
<section class="hero" aria-labelledby="hero-heading">
<p class="eyebrow">OPEN-SOURCE SCARP LEARNING</p>
<h1 id="hero-heading">Learn by reading <span>real code.</span></h1>
<p class="lead">A practical Scarp curriculum built from actual compiler examples. Each lesson includes the full source and its expected output. No invented syntax or unsupported features.</p>
<div class="hero-meta"><span>{len(lessons)} verified-source lessons</span><span>{len(by_section)} learning chapters</span><span>English first · Hindi planned</span></div>
<p class="caution"><strong>Language status:</strong> Scarp is prerelease software. These lessons target a pinned development compiler; runnable behavior is checked in CI, not in this browser. Async, networking, agents and general maps/sets are not advertised as implemented.</p>
</section>
<section class="discover" aria-label="Find lessons">
<label for="search">Find a lesson</label>
<input id="search" type="search" placeholder="Search topics, syntax or lesson titles" autocomplete="off">
<p id="search-status" aria-live="polite">Showing all {len(lessons)} lessons.</p>
</section>
{content}
<section class="next"><h2>Ready to run one?</h2><p>Get the current Scarp compiler, then use <code>scarp run PATH_TO_LESSON.srp</code>. Compare the result with the corresponding <code>.stdout</code> file.</p><a href="{REPOSITORY}#start-here">Installation and running instructions</a> · <a href="{REPOSITORY}/blob/main/docs/compatibility.md">Compatibility policy</a> · <a href="{REPOSITORY}/blob/main/CONTRIBUTING.md">Contribute a lesson</a></section>
</main>
<footer><div class="container"><p>Scarp by Example · Community learning resource · <a href="{REPOSITORY}/blob/main/LICENSE">MIT editorial material</a> · <a href="{REPOSITORY}/blob/main/THIRD_PARTY_NOTICES.md">Apache-licensed upstream examples</a></p></div></footer>
<script src="search.js" defer></script>
</body></html>
"""
    return document, len(lessons)


def build(destination: Path) -> int:
    page, count = render_catalog()
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(page, encoding="utf-8", newline="\n")
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    for asset in ("styles.css", "search.js"):
        shutil.copyfile(ASSETS / asset, destination / asset)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    count = build(args.output.resolve())
    print(f"Built catalog with {count} lessons at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
