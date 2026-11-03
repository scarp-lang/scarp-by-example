#!/usr/bin/env python3
"""Build a static learning portal from real Scarp source and exact stdout fixtures."""

from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from verify_examples import EXAMPLES, ROOT, discover_examples, read_expected_stdout

ASSETS = ROOT / "site"
REPOSITORY = "https://github.com/scarp-lang/scarp-by-example"
COMPILER = "https://github.com/scarp-lang/scarp"
PUBLIC_SITE = "https://scarp-lang.github.io/scarp-by-example/"


@dataclass(frozen=True)
class Lesson:
    source: Path
    stdout: Path
    section: str
    chapter: str
    title: str
    description: str

    @property
    def url(self) -> str:
        return f"lessons/{self.section}/{self.source.stem}/index.html"

    @property
    def source_path(self) -> str:
        return self.source.relative_to(ROOT).as_posix()


def escape(value: str) -> str:
    return html.escape(value, quote=True)


# Display-only highlighting: these spans never parse or execute Scarp code.
SCARP_TOKENS = re.compile(
    r'(?P<comment>//[^\n]*)'
    r'|(?P<string>"(?:\\.|[^"\\])*")'
    r'|(?P<keyword>\b(?:bind|var|pub|import|as|pure|funcra|return|'
    r'needs|ensures|if|elif|else|while|repeat|true|false|and|or|not)\b)'
    r'|(?P<number>\b\d+(?:\.\d+)?\b)'
)


def highlight_scarp(source: str) -> str:
    """Only decorate escaped code tokens; preserve every source character."""
    tokens: list[str] = []
    position = 0
    for match in SCARP_TOKENS.finditer(source):
        tokens.append(escape(source[position:match.start()]))
        tokens.append(
            f'<span class="syntax-{match.lastgroup}">{escape(match.group())}</span>'
        )
        position = match.end()
    tokens.append(escape(source[position:]))
    return "".join(tokens)


def section_heading(readme: Path) -> str:
    lines = readme.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"missing section heading in {readme}")
    return lines[0][2:].strip()


def plain_markdown(value: str) -> str:
    """Remove small inline Markdown markers from chapter and lesson summaries."""
    import re
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    return value.replace("**", "").replace(chr(96), "")


def section_intro(readme: Path) -> str:
    summary = next(
        (s.strip() for s in readme.read_text(encoding="utf-8").splitlines()[1:]
         if s.strip() and not s.startswith("#")),
        "Real examples tested with the Scarp compiler.",
    )
    return plain_markdown(summary)


def table_cells(line: str) -> list[str]:
    """Respect the pipe operators that appear inside Markdown code spans."""
    cells, part, code = [], [], False
    for char in line.strip().strip("|"):
        if char == chr(96):
            code = not code
        if char == "|" and not code:
            cells.append("".join(part).strip())
            part = []
        else:
            part.append(char)
    cells.append("".join(part).strip())
    return cells


def lesson_description(readme: Path, filename: str) -> str:
    for line in readme.read_text(encoding="utf-8").splitlines():
        if f"]({filename})" in line:
            cells = table_cells(line)
            if len(cells) >= 2:
                return plain_markdown(cells[1])
    raise ValueError(f"missing {filename} description in {readme}")


def chapter_url(section: str) -> str:
    return f"chapters/{section}/index.html"


def rel(page: str, target: str) -> str:
    base = PurePosixPath(page).parent.as_posix()
    return posixpath.relpath(target, start=base)


def read_course() -> tuple[list[Lesson], dict[str, list[Lesson]], dict]:
    all_lessons: list[Lesson] = []
    chapters: dict[str, list[Lesson]] = {}
    target = json.loads((ROOT / "docs/compiler-target.json").read_text(encoding="utf-8"))
    for source, output in discover_examples(EXAMPLES):
        section = source.parent.name
        guide = source.parent / "README.md"
        hindi = ROOT / "docs" / "hi" / f"{section}.md"
        if not hindi.is_file():
            raise ValueError(f"missing Hindi guide {hindi}")
        lesson = Lesson(
            source, output, section, section_heading(guide),
            source.stem.split("-", 1)[1].replace("-", " ").title(),
            lesson_description(guide, source.name),
        )
        all_lessons.append(lesson)
        chapters.setdefault(section, []).append(lesson)
    return all_lessons, chapters, target


def page_shell(page: str, title: str, description: str, main: str, layout: str = "") -> str:
    home = escape(rel(page, "index.html"))
    style = escape(rel(page, "styles.css"))
    script = escape(rel(page, "search.js"))
    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0b1120">
<meta name="description" content="{escape(description)}">
<title>{escape(title)} · Scarp by Example</title>
<link rel="stylesheet" href="{style}">
<link rel="canonical" href="{escape(PUBLIC_SITE + page.removesuffix("index.html"))}">
<script src="{script}" defer></script>
</head>
<body class="{escape(layout)}">
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header"><div class="container-wide header-inner">
<a class="brand" href="{home}" aria-label="Scarp by Example home">
  <span class="brand-icon" aria-hidden="true">S</span>
  <span>scarp<span class="brand-muted"> / by example</span></span></a>
<nav class="top-nav" aria-label="Primary navigation">
  <a href="{home}#chapters">Chapters</a>
  <a href="{home}#search-area">Search</a>
  <a href="{COMPILER}">Compiler</a>
  <a href="{REPOSITORY}">GitHub</a>
</nav>
<button id="theme-toggle" class="theme-button" type="button"
  aria-label="Switch to light theme">☀ <span>Light</span></button>
</div></header>
{main}
<footer class="site-footer"><div class="container-wide footer-inner">
<span>Scarp by Example · Learning from compiler-tested code</span>
<span><a href="{REPOSITORY}/blob/main/LICENSE">MIT editorial</a> ·
<a href="{REPOSITORY}/blob/main/THIRD_PARTY_NOTICES.md">Apache-2.0 upstream sources</a></span>
</div></footer>
</body></html>
"""


def lesson_card(lesson: Lesson, page: str) -> str:
    link = escape(rel(page, lesson.url))
    return f"""<a class="lesson-card" href="{link}">
<span class="lesson-number">{escape(lesson.source.stem[:2])}</span>
<span class="lesson-description"><strong>{escape(lesson.title)}</strong>
<span>{escape(lesson.description)}</span></span>
<span class="lesson-arrow" aria-hidden="true">↗</span></a>"""


def render_catalog() -> tuple[str, int]:
    lessons, chapters, target = read_course()
    first = lessons[0]
    tiles = []
    for section, chapter in chapters.items():
        chapter_title = chapter[0].chapter
        tiles.append(f"""<a class="chapter-tile" href="{escape(rel("index.html", chapter_url(section)))}">
<span class="eyebrow">CHAPTER {escape(section[:2])} · {len(chapter)} LESSONS</span>
<h3>{escape(chapter_title.split("·", 1)[-1].strip())}</h3>
<p>{escape(section_intro(EXAMPLES / section / "README.md"))}</p>
<span class="chapter-action">Explore chapter <span aria-hidden="true">↗</span></span></a>""")
    hello_source = escape(first.source.read_text(encoding="utf-8"))
    hello_output = escape(first.stdout.read_bytes().decode("utf-8").strip())
    main = f"""<main id="main-content">
<section class="hero container-wide">
<div class="hero-text">
<p class="eyebrow"><span class="status-dot" aria-hidden="true"></span> THE PRACTICAL SCARP HANDBOOK</p>
<h1>Learn Scarp.<br><span>One real program at a time.</span></h1>
<p class="lead">From your first line of code to numerical computing. Every lesson has its own page with original Scarp source and verified output.</p>
<div class="hero-buttons"><a class="primary-button" href="{escape(rel("index.html", first.url))}">Start learning <span aria-hidden="true">→</span></a>
<a class="secondary-button" href="#chapters">Explore chapters</a></div>
<div class="hero-stats"><span><strong>{len(lessons)}</strong> runnable lessons</span>
<span><strong>{len(chapters)}</strong> chapters</span><span><strong>EN + हिन्दी</strong> guides</span></div>
</div>
<div class="hero-terminal" aria-label="Example Scarp code">
<div class="terminal-heading"><span aria-hidden="true">● ● ●</span><span>{escape(first.source.name)}</span><span>Scarp</span></div>
<pre><code>{hello_source}</code></pre>
<div class="terminal-result"><span>Verified output</span><code>{hello_output}</code></div>
</div>
</section>
<section class="search-area container-wide" id="search-area" aria-labelledby="search-heading">
<div class="section-heading"><div><p class="eyebrow">FIND A TOPIC</p><h2 id="search-heading">Find your next example</h2></div><p>Search titles, syntax topics and chapters.</p></div>
<label class="sr-only" for="lesson-search">Search lessons</label>
<input id="lesson-search" type="search" data-index-url="search-index.json" data-lesson-count="{len(lessons)}" autocomplete="off"
 placeholder="Try functions, Unicode, modules, matrix..." aria-controls="search-results">
<p id="search-status" role="status" aria-live="polite">Browse the chapters below. Instant search is available with JavaScript.</p>
<ul id="search-results" class="search-results" aria-label="Search results"></ul>
</section>
<section class="chapters container-wide" id="chapters" aria-labelledby="chapters-heading">
<div class="section-heading"><div><p class="eyebrow">LEARNING PATH</p><h2 id="chapters-heading">Explore by chapter</h2></div>
<p>Six structured chapters. Choose a topic and read one example at a time.</p></div>
<div class="chapter-grid">{''.join(tiles)}</div>
</section>
<section class="compat-panel container-wide" aria-label="Compiler compatibility">
<div><p class="eyebrow">REPRODUCIBLE BY DESIGN</p><h2>Real code. Exact output.</h2>
<p>Every example is checked with the official compiler. This site displays examples but <strong>does not execute code inside your browser</strong>.</p>
<p>Target: <a href="{escape(target["release_url"])}">Scarp v{escape(target["version"])}</a> (prerelease) · pinned commit <code>{escape(target["source_commit"][:12])}</code></p></div>
<div class="compat-links"><a href="{REPOSITORY}/blob/main/docs/cli-quickstart.md">CLI quickstart ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/README.md">हिन्दी में सीखें ↗</a>
<a href="{REPOSITORY}/blob/main/docs/compatibility.md">Compatibility policy ↗</a></div>
</section>
</main>"""
    return page_shell("index.html", "Learn Scarp with real code", "A practical, verified Scarp learning resource with standalone examples.", main, "home-layout"), len(lessons)


def render_chapter(section: str, lessons: list[Lesson], target: dict) -> str:
    page = chapter_url(section)
    title = lessons[0].chapter
    summary = section_intro(EXAMPLES / section / "README.md")
    cards = "".join(lesson_card(item, page) for item in lessons)
    main = f"""<main id="main-content" class="container-wide chapter-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(page, "index.html"))}">All chapters</a><span>/</span><span aria-current="page">{escape(title)}</span></nav>
<header class="page-heading"><p class="eyebrow">CHAPTER {escape(section[:2])} · {len(lessons)} LESSONS</p>
<h1>{escape(title)}</h1><p class="lead">{escape(summary)}</p>
<div class="guide-links"><a href="{REPOSITORY}/blob/main/examples/{escape(section)}/README.md">English guide ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/{escape(section)}.md">हिन्दी अध्याय ↗</a></div></header>
<section class="chapter-list" aria-labelledby="chapter-list-title"><h2 id="chapter-list-title">Lessons in this chapter</h2>
<div class="lesson-list">{cards}</div></section>
<p class="fine-print">All examples are validated with Scarp v{escape(target["version"])}. Each lesson has its own code and expected-output page.</p>
</main>"""
    return page_shell(page, title, summary, main, "chapter-layout")


def render_lesson(source: Path, stdout: Path, description: str) -> str:
    """Preserve source characters and exact fixture bytes; display CR visibly."""
    raw = source.read_text(encoding="utf-8")
    output = read_expected_stdout(stdout).decode("utf-8")
    visible = output.replace("\r", r"\r")
    note = '<p class="output-note">A literal CR byte is shown as \\r for readability.</p>' if "\r" in output else ""
    src_url = REPOSITORY + "/blob/main/" + source.relative_to(ROOT).as_posix()
    out_url = REPOSITORY + "/blob/main/" + stdout.relative_to(ROOT).as_posix()
    return f"""<div class="code-grid">
<section class="code-panel" aria-labelledby="source-title"><div class="panel-heading">
<div><span class="eyebrow">ORIGINAL SOURCE</span><h2 id="source-title">{escape(source.name)}</h2></div>
<button type="button" class="copy-button" data-copy="scarp-code">Copy code</button></div>
<pre><code id="scarp-code">{highlight_scarp(raw)}</code></pre>
<div class="panel-footer"><a href="{escape(src_url)}">View .srp on GitHub ↗</a></div></section>
<section class="code-panel output-panel" aria-labelledby="output-title"><div class="panel-heading">
<div><span class="eyebrow">EXPECTED OUTPUT</span><h2 id="output-title">stdout</h2></div>
<span class="verified-tag">Verified</span></div>
<pre><code>{escape(visible)}</code></pre>{note}
<div class="panel-footer"><a href="{escape(out_url)}">View exact fixture ↗</a></div></section>
</div>"""


def render_lesson_page(lesson: Lesson, all_lessons: list[Lesson], chapter: list[Lesson], target: dict) -> str:
    page = lesson.url
    i = all_lessons.index(lesson)
    sidebar = "".join(
        f'<a href="{escape(rel(page, item.url))}"'
        + (' aria-current="page" class="active"' if item == lesson else '')
        + f'><span>{escape(item.source.stem[:2])}</span>{escape(item.title)}</a>'
        for item in chapter
    )

    def step(target_lesson: Lesson | None, label: str) -> str:
        if target_lesson is None:
            return f'<span class="step-disabled">{escape(label)} · End of course</span>'
        return (f'<a href="{escape(rel(page, target_lesson.url))}">'
                f'<span>{escape(label)}</span><strong>{escape(target_lesson.title)}</strong></a>')

    before = all_lessons[i - 1] if i > 0 else None
    after = all_lessons[i + 1] if i + 1 < len(all_lessons) else None
    code = render_lesson(lesson.source, lesson.stdout, lesson.description)
    main = f"""<main id="main-content" class="container-wide detail-layout">
<aside class="sidebar" aria-label="This chapter's lessons">
<div class="sidebar-heading"><span class="eyebrow">CHAPTER {escape(lesson.section[:2])}</span><strong>{escape(lesson.chapter)}</strong></div>
<nav aria-label="Chapter lesson navigation">{sidebar}</nav>
<a class="sidebar-return" href="{escape(rel(page, chapter_url(lesson.section)))}">Chapter overview ↗</a></aside>
<div class="lesson-main">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<a href="{escape(rel(page, chapter_url(lesson.section)))}">{escape(lesson.chapter)}</a>
<span>/</span><span aria-current="page">{escape(lesson.title)}</span></nav>
<header class="page-heading lesson-heading"><p class="eyebrow">LESSON {i + 1:02} OF {len(all_lessons)} · CHAPTER {escape(lesson.section[:2])}</p>
<h1>{escape(lesson.title)}</h1><p class="lead">{escape(lesson.description)}</p>
<div class="guide-links"><a href="{REPOSITORY}/blob/main/examples/{escape(lesson.section)}/README.md">Read the English notes ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/{escape(lesson.section)}.md">हिन्दी में पढ़ें ↗</a></div></header>
{code}
<section class="run-panel" aria-labelledby="run-title">
<div><p class="eyebrow">TRY IT LOCALLY</p><h2 id="run-title">Verify, then execute</h2>
<p>Use the pinned compiler from the course root. Keep any imported <code>_support</code> files next to the source.</p></div>
<div class="commands"><code>scarp verify {escape(lesson.source_path)}</code>
<code>scarp exec {escape(lesson.source_path)}</code></div>
<p>The website does not run code. <a href="{REPOSITORY}/blob/main/docs/cli-quickstart.md">Read the CLI guide ↗</a></p>
</section>
<nav class="step-nav" aria-label="Lesson navigation">
{step(before, "← Previous lesson")}{step(after, "Next lesson →")}</nav>
<p class="fine-print">Pinned compiler: <a href="{escape(target["release_url"])}">Scarp v{escape(target["version"])}</a>
· <code>{escape(target["source_commit"][:12])}</code>. No simulated output.</p>
</div></main>"""
    return page_shell(page, lesson.title, lesson.description, main, "lesson-layout")


def build(destination: Path) -> int:
    lessons, chapters, target = read_course()
    home, count = render_catalog()
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(home, encoding="utf-8", newline="\n")
    index = [{"title": l.title, "chapter": l.chapter, "description": l.description, "url": l.url}
             for l in lessons]
    (destination / "search-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for section, chapter in chapters.items():
        path = destination / chapter_url(section)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_chapter(section, chapter, target), encoding="utf-8", newline="\n")
    for lesson in lessons:
        path = destination / lesson.url
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_lesson_page(lesson, lessons, chapters[lesson.section], target),
                        encoding="utf-8", newline="\n")
    # Discoverable, stable directory URLs for search engines and learners.
    urls = ["index.html"]
    urls.extend(chapter_url(section) for section in chapters)
    urls.extend(lesson.url for lesson in lessons)
    sitemap = '<?xml version="1.0" encoding="utf-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(
        f'  <url><loc>{escape(PUBLIC_SITE + url.removesuffix("index.html"))}</loc></url>\n'
        for url in urls
    )
    sitemap += "</urlset>\n"
    (destination / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    for asset in ("styles.css", "search.js"):
        shutil.copyfile(ASSETS / asset, destination / asset)
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    count = build(args.output.resolve())
    print(f"Built {count} standalone lessons and chapter pages at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
