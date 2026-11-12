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

from verify_examples import EXAMPLES, ROOT, discover_examples, read_expected_stdout, read_optional_stdin
from lesson_notes import HindiNote, read_hindi_notes, render_hindi_note
from practice_questions import read_practice_questions
from guided_labs import GuidedLab, read_labs
from source_explorer import render_reference_explorer
from alpha8_project_page import render_page as render_alpha8_project_page

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


def lesson_result(readme: Path, filename: str) -> str:
    """Retrieve the actual documented result from a chapter table, not a guess."""
    for line in readme.read_text(encoding="utf-8").splitlines():
        if f"]({filename})" not in line:
            continue
        columns = table_cells(line)
        if len(columns) < 3:
            raise ValueError(f"{readme}: missing expected result for {filename}")
        return plain_markdown(columns[2])
    raise ValueError(f"{readme}: no documented expected result for {filename}")


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
    search_core = escape(rel(page, "search-core.js"))
    checkpoint_script = (f'<script src="{escape(rel(page, "checkpoint.js"))}" defer></script>'
                         if layout in ("lesson-layout", "chapter-layout") else "")
    practice_script = (f'<script src="{escape(rel(page, "output-practice.js"))}" defer></script>'
                       if layout == "lesson-layout" else "")
    reference_script = (f'<script src="{escape(rel(page, "reference-explorer.js"))}" defer></script>'
                        if "reference-explorer-layout" in layout else "")
    # Keep both navigation views in sync, with native disclosure on small screens.
    # This works without JavaScript and avoids forcing horizontal page scrolling.
    nav_links = f"""<a href="{home}#chapters">Chapters</a>
<a href="{home}#search-area">Search</a>
<a href="{escape(rel(page, "projects/index.html"))}">Projects</a>
<a href="{escape(rel(page, "labs/index.html"))}">Coding labs</a>
<a href="{COMPILER}">Compiler</a>
<a href="{REPOSITORY}">GitHub</a>"""
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
<script src="{search_core}" defer></script>
<script src="{script}" defer></script>
<script src="{escape(rel(page, "progress.js"))}" defer></script>
{checkpoint_script}
{practice_script}
{reference_script}
</head>
<body class="{escape(layout)}">
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header"><div class="container-wide header-inner">
<a class="brand" href="{home}" aria-label="Scarp by Example home">
  <span class="brand-icon" aria-hidden="true">S</span>
  <span>scarp<span class="brand-muted"> / by example</span></span></a>
<nav class="top-nav" aria-label="Primary navigation">{nav_links}</nav>
<details class="mobile-nav" data-mobile-nav>
<summary>Menu</summary>
<nav class="mobile-menu-links" aria-label="Mobile navigation">{nav_links}</nav>
</details>
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


def lesson_card(lesson: Lesson, page: str, question_paths: set[str] | None = None) -> str:
    link = escape(rel(page, lesson.url))
    checkpoint = ('<small class="lesson-check-tag">Quick check · प्रश्न</small>'
                  if lesson.source_path in (question_paths or set()) else "")
    return f"""<a class="lesson-card" href="{link}">
<span class="lesson-number">{escape(lesson.source.stem[:2])}</span>
<span class="lesson-description"><strong>{escape(lesson.title)}</strong>
<span>{escape(lesson.description)}</span>{checkpoint}</span>
<span class="lesson-arrow" aria-hidden="true">↗</span></a>"""


def render_catalog(questions: dict[str, dict] | None = None) -> tuple[str, int]:
    lessons, chapters, target = read_course()
    questions = read_practice_questions(ROOT) if questions is None else questions
    first = lessons[0]
    tiles = []
    chapter_options = "".join(
        f'<option value="{escape(section)}">{escape(chapter[0].chapter)}</option>'
        for section, chapter in chapters.items()
    )
    for section, chapter in chapters.items():
        chapter_title = chapter[0].chapter
        checkpoint_count = sum(item.source_path in questions for item in chapter)
        tiles.append(f"""<a class="chapter-tile" href="{escape(rel("index.html", chapter_url(section)))}">
<span class="eyebrow">CHAPTER {escape(section[:2])} · {len(chapter)} LESSONS</span>
<h3>{escape(chapter_title.split("·", 1)[-1].strip())}</h3>
<p>{escape(section_intro(EXAMPLES / section / "README.md"))}</p>
<span class="chapter-check-count">{checkpoint_count} self-checks · प्रश्न</span>
<span class="chapter-progress" data-progress-chapter="{escape(section)}" aria-live="polite"></span>
<span class="chapter-action">Explore chapter <span aria-hidden="true">↗</span></span></a>""")
    hello_source = escape(first.source.read_text(encoding="utf-8"))
    hello_output = escape(first.stdout.read_bytes().decode("utf-8").strip())
    main = f"""<main id="main-content">
<section class="hero container-wide">
<div class="hero-text">
<p class="eyebrow"><span class="status-dot" aria-hidden="true"></span> THE PRACTICAL SCARP HANDBOOK</p>
<h1>Learn Scarp.<br><span>One real program at a time.</span></h1>
<p class="lead">From your first line of code to numerical computing. Every lesson has its own page with real Scarp source, verified output, English and Hindi explanations, and a practice question.</p>
<div class="hero-buttons"><a class="primary-button" href="{escape(rel("index.html", first.url))}">Start learning <span aria-hidden="true">→</span></a>
<a class="secondary-button" href="#chapters">Explore chapters</a>
<a class="secondary-button" href="labs/index.html">Solve guided labs ↗</a></div>
<div class="hero-stats"><span><strong>{len(lessons)}</strong> runnable lessons</span>
<span><strong>{len(chapters)}</strong> chapters</span><span><strong>English + हिन्दी</strong> explanations</span></div>
</div>
<div class="hero-terminal" aria-label="Example Scarp code">
<div class="terminal-heading"><span aria-hidden="true">● ● ●</span><span>{escape(first.source.name)}</span><span>Scarp</span></div>
<pre><code>{hello_source}</code></pre>
<div class="terminal-result"><span>Verified output</span><code>{hello_output}</code></div>
</div>
</section>
<section class="progress-dashboard container-wide" data-progress-index="search-index.json"
 data-progress-root="index.html" hidden aria-labelledby="dashboard-heading">
<div><p class="eyebrow">YOUR LEARNING JOURNEY</p><h2 id="dashboard-heading">Pick up where you left off</h2>
<p class="progress-disclaimer" data-progress-status>Saved only in this browser. No account or tracking.</p>
<progress data-progress-bar max="{len(lessons)}" value="0" aria-label="Completed lessons"></progress>
<p class="progress-count"><strong data-progress-count="all">0 of {len(lessons)} completed</strong></p></div>
<div class="progress-actions"><a class="primary-button" data-progress-resume
 href="{escape(rel("index.html", first.url))}">Start learning →</a>
<button class="progress-reset" type="button" data-progress-export>Export progress</button>
<button class="progress-reset" type="button" data-progress-import>Import progress</button>
<input type="file" accept=".json,application/json" data-progress-file hidden
 aria-label="Select a Scarp progress backup JSON file">
<button class="progress-reset" type="button" data-progress-clear>Clear saved progress</button>
<p class="progress-feedback" role="status" aria-live="polite" data-progress-message></p></div>
</section>
<section class="search-area container-wide" id="search-area" aria-labelledby="search-heading">
<div class="section-heading"><div><p class="eyebrow">FIND A TOPIC</p><h2 id="search-heading">Find your next example</h2></div><p>Search English/Hindi lessons and real Scarp source. Filter by chapter.</p></div>
<div class="search-controls"><div>
<label class="sr-only" for="lesson-search">Search lessons or Scarp source</label>
<input id="lesson-search" type="search" data-index-url="search-index.json" data-lesson-count="{len(lessons)}" autocomplete="off" maxlength="160"
 placeholder="Try funcra, Unicode, modules, matrix..." aria-controls="search-results" aria-describedby="search-help" aria-keyshortcuts="/">
</div><div class="search-chapter-control">
<label for="lesson-chapter">Chapter</label>
<select id="lesson-chapter" aria-controls="search-results">
<option value="">All chapters</option>{chapter_options}
</select></div></div>
<p id="search-help" class="search-help">Press <kbd>/</kbd> to focus search. Press <kbd>Esc</kbd> in the search box to clear both filters.</p>
<a id="share-search-link" class="search-share" href="index.html#search-area" hidden>Share this search ↗</a>
<p id="search-status" role="status" aria-live="polite">Browse the chapters below. Instant search is available with JavaScript.</p>
<ul id="search-results" class="search-results" aria-label="Search results"></ul>
</section>
<section class="chapters container-wide" id="chapters" aria-labelledby="chapters-heading">
<div class="section-heading"><div><p class="eyebrow">LEARNING PATH</p><h2 id="chapters-heading">Explore by chapter</h2></div>
<p>Six structured chapters: read real code, answer bilingual checkpoints, then solve a coding lab.</p></div>
<div class="chapter-grid">{''.join(tiles)}</div>
</section>
<section class="project-feature container-wide" aria-labelledby="projects-heading">
<div><p class="eyebrow">NOW SUPPORTED IN ALPHA.4</p>
<h2 id="projects-heading">Go beyond a single file.</h2>
<p>Learn how the real Scarp compiler creates a project, validates its manifest without running code and launches its declared entrypoint.</p>
<a class="primary-button" href="{escape(rel("index.html", "projects/index.html"))}">Build your first project →</a></div>
<div class="project-feature-command"><span>Terminal · Scarp v{escape(target["version"])}</span>
<pre><code>scarp create hello-world
scarp verify hello-world
scarp launch hello-world</code></pre></div>
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


def render_chapter_path(section: str, lessons: list[Lesson],
                        question_paths: set[str], lab: GuidedLab) -> str:
    """Show a genuine read → self-check → code sequence from existing artifacts.

    Self-check and lab success are deliberately not inferred from lesson progress:
    the website does not record quiz answers or execute the learner's code.
    """
    if lab.identifier != section:
        raise ValueError(f"guided lab does not match chapter {section}")
    checks = [lesson for lesson in lessons if lesson.source_path in question_paths]
    if not checks:
        raise ValueError(f"no source-backed checkpoints for chapter {section}")
    if len(checks) != len({lesson.source_path for lesson in checks}):
        raise ValueError(f"duplicate checkpoint for chapter {section}")
    page = chapter_url(section)
    checkpoint_links = "".join(
        f'<li><a href="{escape(rel(page, lesson.url))}#checkpoint">'
        f'{escape(lesson.title)} · <span lang="hi">अभ्यास</span></a></li>'
        for lesson in checks
    )
    return f"""<section class="chapter-path" id="chapter-path" aria-labelledby="chapter-path-heading">
<div class="section-heading">
<div><p class="eyebrow">YOUR CHAPTER LEARNING PATH · सीखने का क्रम</p>
<h2 id="chapter-path-heading">Read. Check. Build.</h2></div>
<p>Three linked steps using real Scarp source and verified output.</p></div>
<ol class="path-steps">
<li class="path-step">
<span class="path-step-number" aria-hidden="true">01</span>
<h3>Read the lessons <span lang="hi">· पाठ पढ़ें</span></h3>
<p>Work through all {len(lessons)} verified examples. Save optional local lesson
progress as you learn; this does not certify code execution.</p>
<a class="path-step-link" href="{escape(rel(page, lessons[0].url))}">Start with {escape(lessons[0].title)} ↗</a>
<p class="path-step-status" data-path-lesson-status="{escape(section)}">
Lesson tracking is optional and only available when browser storage works.</p>
</li>
<li class="path-step">
<span class="path-step-number" aria-hidden="true">02</span>
<h3>Check understanding <span lang="hi">· समझ जाँचें</span></h3>
<p>Try {len(checks)} bilingual questions linked directly to their original
source and expected output. No quiz score is stored.</p>
<ul class="path-check-links">{checkpoint_links}</ul>
<a class="path-step-link" href="#chapter-review">Review all three questions here · यहाँ अभ्यास करें ↓</a>
</li>
<li class="path-step">
<span class="path-step-number" aria-hidden="true">03</span>
<h3>Write Scarp <span lang="hi">· कोड लिखें</span></h3>
<p>Edit the real starter locally, compare output with the compiler-verified goal,
and use the hint or tested solution when needed.</p>
<a class="path-step-link" href="{escape(rel(page, lab.url))}">Open {escape(lab.title["en"])} lab ↗</a>
</li>
</ol>
<p class="path-disclaimer">Lesson completion is voluntary local tracking.
Passing a quiz or lab is not automatically recorded or claimed by this website.
The Scarp compiler runs locally, not in your browser.</p>
</section>"""



def render_chapter_journey(section: str, chapters: dict[str, list[Lesson]]) -> str:
    """Link adjacent chapters from the real, ordered verified course inventory."""
    sections = list(chapters)
    if section not in chapters or not chapters[section]:
        raise ValueError(f"unknown or empty chapter {section}")
    i = sections.index(section)
    page = chapter_url(section)

    def card(target: str | None, label: str) -> str:
        if target is None:
            boundary = ("Course start / पाठ्यक्रम की शुरुआत"
                        if label.startswith("←") else "Course end / पाठ्यक्रम का अंत")
            return ('<span class="chapter-journey-end" aria-disabled="true">'
                    + escape(label) + ' · ' + boundary + '</span>')
        lesson_list = chapters[target]
        title = lesson_list[0].chapter
        return (f'<a class="chapter-journey-card" href="{escape(rel(page, chapter_url(target)))}">'
                f'<span>{escape(label)} · अध्याय</span>'
                f'<strong>{escape(title)}</strong>'
                f'<small>{len(lesson_list)} verified lessons</small></a>')

    previous = sections[i - 1] if i > 0 else None
    following = sections[i + 1] if i + 1 < len(sections) else None
    return f"""<nav class="chapter-journey" aria-label="Previous and next chapters">
<h2>Keep exploring · आगे सीखें</h2>
<p>Chapter {i + 1} of {len(sections)}. Move through the verified Scarp course in order.</p>
<div class="chapter-journey-links">
{card(previous, "← Previous chapter")}{card(following, "Next chapter →")}
</div></nav>"""


def render_lesson_chapter_handoff(
    lesson: Lesson, chapter: list[Lesson], all_lessons: list[Lesson]
) -> str:
    """Offer the real chapter lab and onward route at chapter boundaries only."""
    if not chapter or lesson != chapter[-1]:
        return ""
    page = lesson.url
    i = all_lessons.index(lesson)
    following = all_lessons[i + 1] if i + 1 < len(all_lessons) else None
    if following and following.section == lesson.section:
        raise ValueError("chapter boundary is inconsistent with lesson order")
    next_step = (
        f'<a class="chapter-handoff-next" href="{escape(rel(page, chapter_url(following.section)))}">'
        f'Explore next chapter: {escape(following.chapter)} →</a>'
        if following else
        f'<a class="chapter-handoff-next" href="{escape(rel(page, "index.html"))}#chapters">'
        'Review all chapters · सभी अध्याय देखें →</a>'
    )
    return f"""<section class="chapter-handoff" aria-labelledby="chapter-handoff-title">
<p class="eyebrow">CHAPTER {escape(lesson.section[:2])} · LAST LESSON</p>
<h2 id="chapter-handoff-title">Ready for your next step? · आगे क्या सीखें?</h2>
<p>This is the final example in this chapter. Try its verified coding lab before moving on.
Your lesson progress changes only when you mark a lesson complete.</p>
<div class="chapter-handoff-links">
<a href="{escape(rel(page, "labs/" + lesson.section + "/index.html"))}">Try this chapter's lab ↗</a>
<a href="{escape(rel(page, chapter_url(lesson.section)))}#chapter-path">Review chapter path ↗</a>
{next_step}
</div></section>"""


def render_chapter(section: str, lessons: list[Lesson], target: dict,
                   question_paths: set[str] | None = None, lab: GuidedLab | None = None,
                   chapters: dict[str, list[Lesson]] | None = None,
                   questions: dict[str, dict] | None = None) -> str:
    page = chapter_url(section)
    title = lessons[0].chapter
    summary = section_intro(EXAMPLES / section / "README.md")
    cards = "".join(lesson_card(item, page, question_paths) for item in lessons)
    if lab is None:
        matching = [item for item in read_labs(ROOT) if item.identifier == section]
        if len(matching) != 1:
            raise ValueError(f"missing guided lab for chapter {section}")
        lab = matching[0]
    path_steps = render_chapter_path(section, lessons, question_paths or set(), lab)
    chapter_review = render_chapter_review(section, lessons,
                                          read_practice_questions(ROOT) if questions is None else questions)
    chapter_journey = render_chapter_journey(section, chapters if chapters is not None else read_course()[1])
    main = f"""<main id="main-content" class="container-wide chapter-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(page, "index.html"))}">All chapters</a><span>/</span><span aria-current="page">{escape(title)}</span></nav>
<header class="page-heading"><p class="eyebrow">CHAPTER {escape(section[:2])} · {len(lessons)} LESSONS</p>
<h1>{escape(title)}</h1><p class="lead">{escape(summary)}</p>
<div class="guide-links"><a href="{REPOSITORY}/blob/main/examples/{escape(section)}/README.md">English guide ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/{escape(section)}.md">हिन्दी अध्याय ↗</a>
<a href="{escape(rel(page, "labs/" + section + "/index.html"))}">Coding lab for this chapter ↗</a></div></header>
<section class="chapter-progress-panel" data-progress-index="{escape(rel(page, "search-index.json"))}"
 data-progress-root="{escape(rel(page, "index.html"))}" data-progress-scope="{escape(section)}"
 hidden aria-label="Progress in this chapter">
<div><p class="eyebrow">YOUR CHAPTER PROGRESS</p>
<strong data-progress-count="{escape(section)}">0 of {len(lessons)} completed</strong>
<progress data-progress-bar max="{len(lessons)}" value="0" aria-label="Completed chapter lessons"></progress>
<p data-progress-status>Saved only in this browser. No account or tracking.</p></div>
<a data-progress-resume href="{escape(rel(page, lessons[0].url))}" class="secondary-button">Continue chapter →</a>
</section>
{path_steps}
<section class="chapter-list" aria-labelledby="chapter-list-title"><h2 id="chapter-list-title">Lessons in this chapter</h2>
<div class="lesson-list">{cards}</div></section>
{chapter_review}
{chapter_journey}
<p class="fine-print">All examples are validated with Scarp v{escape(target["version"])}. Each lesson has its own code and expected-output page.</p>
</main>"""
    return page_shell(page, title, summary, main, "chapter-layout")





def render_labs_index(labs: list[GuidedLab], target: dict) -> str:
    """Discovery page for six independently compiler-verified guided exercises."""
    page = "labs/index.html"
    cards = "".join(
        f'<a class="lab-card" href="{escape(rel(page, lab.url))}">'
        + f'<span class="eyebrow">LAB {escape(lab.identifier[:2])}</span>'
        + f'<h2>{escape(lab.title["en"])}</h2>'
        + f'<p lang="hi">{escape(lab.title["hi"])}</p>'
        + (f'<span class="lab-stretch-indicator">+ Optional stretch challenge</span>' if lab.stretch else '')
        + f'<span class="lab-open">Open guided exercise ↗</span></a>'
        for lab in labs
    )
    main = f"""<main id="main-content" class="container-wide lab-index">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<span aria-current="page">Coding labs</span></nav>
<header class="page-heading"><p class="eyebrow">LEARN BY EDITING REAL SCARP</p>
<h1>Guided coding labs</h1>
<p class="lead">Six practical challenges, one per chapter. Start with working Scarp,
change it to match an exact expected output, and check your code using the published compiler.
Tasks and hints are available in English and हिन्दी. Some labs include a second,
independently verified stretch challenge for extra practice.</p></header>
<section class="lab-grid" aria-label="Coding labs">{cards}</section>
<section class="run-panel"><h2>No simulated results</h2>
<p>Every starter and reference solution is verified with the pinned Scarp compiler,
and each solution must match its checked-in output fixture byte for byte.
You edit and run Scarp on your own computer. There is no browser compiler or score tracking.</p>
<p>Compiler target: <a href="{escape(target["release_url"])}">v{escape(target["version"])}</a>.
<a href="{REPOSITORY}/blob/main/docs/guided-labs.md">Read lab instructions ↗</a></p>
</section></main>"""
    return page_shell(page, "Guided coding labs",
                      "Six bilingual compiler-verified Scarp exercises", main, "lab-layout")


def render_lab_stretch(lab: GuidedLab) -> str:
    """Optional second practical challenge, with checked compiler output and no JS gate."""
    if lab.stretch is None:
        return ""
    task = lab.stretch
    folder = "labs/" + lab.identifier
    source = highlight_scarp(task.starter.read_text(encoding="utf-8"))
    solution = highlight_scarp(task.solution.read_text(encoding="utf-8"))
    expected = read_expected_stdout(task.expected).decode("utf-8").replace("\r", r"\r")
    starter_url = REPOSITORY + "/blob/main/" + folder + "/stretch-starter.srp"
    solution_url = REPOSITORY + "/blob/main/" + folder + "/stretch-solution.srp"
    output_url = REPOSITORY + "/blob/main/" + folder + "/stretch-solution.stdout"
    return f"""<section class="lab-stretch" id="stretch-challenge" aria-labelledby="stretch-title">
<header><p class="eyebrow">OPTIONAL · COMPILER-VERIFIED STRETCH</p>
<h2 id="stretch-title">{escape(task.title["en"])}</h2>
<p lang="hi">{escape(task.title["hi"])}</p></header>
<div class="lab-translations">
<p lang="en">{escape(task.task["en"])}</p>
<p lang="hi">{escape(task.task["hi"])}</p></div>
<div class="code-grid">
<section class="code-panel" aria-labelledby="stretch-source-title">
<div class="panel-heading"><div><span class="eyebrow">EDIT A SECOND STARTER</span>
<h3 id="stretch-source-title">stretch-starter.srp</h3></div>
<button type="button" class="copy-button" data-copy="stretch-source">Copy code</button></div>
<pre><code id="stretch-source">{source}</code></pre>
<div class="panel-footer"><a href="{escape(starter_url)}">View stretch starter ↗</a></div>
</section>
<section class="code-panel output-panel" aria-labelledby="stretch-output-title">
<div class="panel-heading"><div><span class="eyebrow">MATCH EXACT COMPILER OUTPUT</span>
<h3 id="stretch-output-title">stretch-solution.stdout</h3></div>
<span class="verified-tag">Compiler fixture</span></div>
<pre><code>{escape(expected)}</code></pre>
<div class="panel-footer"><a href="{escape(output_url)}">View stretch fixture ↗</a></div>
</section></div>
<div class="run-panel"><h3>Try it locally · स्वयं चलाएँ</h3>
<p>Copy <code>stretch-starter.srp</code> to <code>stretch-attempt.srp</code> in the same lab folder.
Edit only your copy; the original starter and fixture remain unchanged.</p>
<div class="commands"><code>scarp verify {escape(folder)}/stretch-attempt.srp</code>
<code>scarp exec {escape(folder)}/stretch-attempt.srp</code></div>
<p>Compare the exact stdout above. The website does not run Scarp, save attempts or award a score.</p>
</div>
<div class="lab-reveals" aria-label="Stretch hints and tested solution">
<details><summary>Show stretch hint · संकेत देखें</summary>
<p lang="en">{escape(task.hint["en"])}</p>
<p lang="hi">{escape(task.hint["hi"])}</p></details>
<details><summary>Reveal tested stretch solution · सत्यापित हल देखें</summary>
<pre><code>{solution}</code></pre>
<p lang="en">{escape(task.explanation["en"])}</p>
<p lang="hi">{escape(task.explanation["hi"])}</p>
<a href="{escape(solution_url)}">View tested stretch solution ↗</a>
</details></div></section>"""


def render_lab_page(lab: GuidedLab, target: dict) -> str:
    """Display an authentic starter, native hint and solution reveals, and real stdout."""
    page = lab.url
    folder = "labs/" + lab.identifier
    source = lab.starter.read_text(encoding="utf-8")
    solution = lab.solution.read_text(encoding="utf-8")
    expected = read_expected_stdout(lab.expected).decode("utf-8")
    visible_output = expected.replace("\r", r"\r")
    source_url = REPOSITORY + "/blob/main/" + folder + "/starter.srp"
    solution_url = REPOSITORY + "/blob/main/" + folder + "/solution.srp"
    fixture_url = REPOSITORY + "/blob/main/" + folder + "/solution.stdout"
    previous = escape(rel(page, "labs/index.html"))
    stretch_markup = render_lab_stretch(lab)
    main = f"""<main id="main-content" class="container-wide lab-detail">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<a href="{previous}">Coding labs</a><span>/</span>
<span aria-current="page">{escape(lab.title["en"])}</span></nav>
<header class="page-heading">
<p class="eyebrow">GUIDED LAB {escape(lab.identifier[:2])} OF 06 · VERIFIED SCARP</p>
<h1>{escape(lab.title["en"])}</h1>
<p lang="hi" class="lead">{escape(lab.title["hi"])}</p>
</header>
<nav class="lesson-path-nav" aria-label="Chapter learning path">
<a href="{escape(rel(page, chapter_url(lab.identifier)))}#chapter-path">← Return to this chapter learning path</a>
</nav>
<section class="lab-task" aria-label="Your task">
<h2>The challenge · अभ्यास</h2>
<div class="lab-translations">
<p lang="en">{escape(lab.task["en"])}</p>
<p lang="hi">{escape(lab.task["hi"])}</p></div>
</section>
<div class="code-grid">
<section class="code-panel" aria-labelledby="lab-starter-title">
<div class="panel-heading"><div><span class="eyebrow">EDIT THIS STARTER</span>
<h2 id="lab-starter-title">starter.srp</h2></div>
<button type="button" class="copy-button" data-copy="scarp-code">Copy code</button></div>
<pre><code id="scarp-code">{highlight_scarp(source)}</code></pre>
<div class="panel-footer"><a href="{escape(source_url)}">View starter source ↗</a></div>
</section>
<section class="code-panel output-panel" aria-labelledby="lab-goal-title">
<div class="panel-heading"><div><span class="eyebrow">MATCH THIS VERIFIED OUTPUT</span>
<h2 id="lab-goal-title">solution.stdout</h2></div>
<span class="verified-tag">Compiler fixture</span></div>
<pre><code>{escape(visible_output)}</code></pre>
<div class="panel-footer"><a href="{escape(fixture_url)}">View exact fixture ↗</a></div></section>
</div>
<section class="run-panel" aria-labelledby="lab-run-title">
<h2 id="lab-run-title">Run and check your attempt locally</h2>
<p>Copy <code>starter.srp</code> to <code>attempt.srp</code> in the <strong>same lab folder</strong>,
edit it, and use the pinned Scarp compiler from the repository root.
Keeping the same folder is important for imports and the bundled <code>_support</code> helper.</p>
<div class="commands"><code>scarp verify {escape(folder)}/attempt.srp</code>
<code>scarp exec {escape(folder)}/attempt.srp</code></div>
<p>Compare the printed output with the fixture shown above. No website execution,
uploads or stored answers are involved.</p></section>
<section class="lab-reveals" aria-label="Hints and reference solution">
<details><summary>Show hint · संकेत देखें</summary>
<p lang="en">{escape(lab.hint["en"])}</p>
<p lang="hi">{escape(lab.hint["hi"])}</p></details>
<details><summary>Reveal tested solution · सत्यापित हल देखें</summary>
<pre><code>{highlight_scarp(solution)}</code></pre>
<p lang="en">{escape(lab.explanation["en"])}</p>
<p lang="hi">{escape(lab.explanation["hi"])}</p>
<a href="{escape(solution_url)}">Reference .srp on GitHub ↗</a>
</details></section>
{stretch_markup}
<p class="fine-print">The starter compiles but intentionally does not produce the goal.
The reference solution and its output are verified on Linux, macOS and Windows
against <a href="{escape(target["release_url"])}">Scarp v{escape(target["version"])}</a>.
<a href="{previous}">Browse all labs ↗</a></p>
</main>"""
    return page_shell(page, lab.title["en"], lab.task["en"], main, "lab-layout")

def render_project_page(target: dict) -> str:
    """Publish the compiler-backed, bilingual tutorial from real project files."""
    page = "projects/index.html"
    folder = ROOT / "tutorials/first-project"
    manifest_path = folder / "Scarp.project"
    entry_path = folder / "src/main.srp"
    expected_path = folder / "expected.stdout"
    manifest_bytes = manifest_path.read_bytes()
    source_bytes = entry_path.read_bytes()
    expected_bytes = expected_path.read_bytes()
    if manifest_bytes != b"scarp-project: 1\nname: first-project\nentry: src/main.srp\n":
        raise ValueError("the verified project manifest has changed; review the tutorial")
    if source_bytes != b'print("Hello from Scarp!");\n':
        raise ValueError("the sample project source differs from the verified scaffold")
    reference = (EXAMPLES / "01-basics/01-hello.stdout").read_bytes()
    if expected_bytes != reference:
        raise ValueError("the project stdout no longer matches compiler-verified hello")
    manifest = escape(manifest_bytes.decode("utf-8"))
    source = highlight_scarp(source_bytes.decode("utf-8"))
    output = escape(expected_bytes.decode("utf-8"))
    en = REPOSITORY + "/blob/main/docs/project-workflow.md"
    hi = REPOSITORY + "/blob/main/docs/hi/project-workflow.md"
    src = REPOSITORY + "/blob/main/tutorials/first-project/src/main.srp"
    title = "Your first Scarp project"
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<span aria-current="page">Projects</span></nav>
<header class="page-heading"><p class="eyebrow">REAL COMPILER WORKFLOW · {escape(target["version"])}</p>
<h1>{title}</h1>
<p class="lead">Create a project, verify it without running runtime statements, and execute the declared entrypoint using the published Scarp interpreter.</p>
<div class="guide-links"><a href="{en}">Full English guide ↗</a>
<a href="{hi}" lang="hi">पूरी हिन्दी गाइड ↗</a></div></header>
<section class="project-steps" aria-label="Project commands">
<div class="project-step"><span>01</span><h2>Create</h2><code>scarp create hello-world</code></div>
<div class="project-step"><span>02</span><h2>Verify</h2><code>scarp verify hello-world</code></div>
<div class="project-step"><span>03</span><h2>Launch</h2><code>scarp launch hello-world</code></div></section>
<p class="project-warning">Run <code>create</code> only with a new, nonexistent directory. To try this course's checked-in sample, use <code>tutorials/first-project</code> without creating it again.</p>
<div class="project-source-grid">
<section class="code-panel" aria-labelledby="project-manifest-title">
<div class="panel-heading"><div><span class="eyebrow">PROJECT MANIFEST</span>
<h2 id="project-manifest-title">Scarp.project</h2></div></div>
<pre><code>{manifest}</code></pre></section>
<section class="code-panel" aria-labelledby="project-code-title">
<div class="panel-heading"><div><span class="eyebrow">REAL ENTRYPOINT</span>
<h2 id="project-code-title">src/main.srp</h2></div>
<button type="button" class="copy-button" data-copy="scarp-code">Copy code</button></div>
<pre><code id="scarp-code">{source}</code></pre>
<div class="panel-footer"><a href="{src}">View the original source ↗</a></div></section>
<section class="code-panel" aria-labelledby="project-output-title">
<div class="panel-heading"><div><span class="eyebrow">VERIFIED STDOUT</span>
<h2 id="project-output-title">Expected output</h2></div><span class="verified-tag">Real fixture</span></div>
<pre><code>{output}</code></pre></section></div>
<section class="lesson-notes" id="lesson-notes" aria-labelledby="project-explain-title">
<div class="notes-heading"><div><p class="eyebrow">UNDERSTAND PROJECTS</p>
<h2 id="project-explain-title">Explanation &amp; practice</h2></div>
<div class="language-switch" role="group" aria-label="Explanation language">
<button type="button" class="note-lang-button" data-note-switch="en"
 aria-controls="en-notes" aria-pressed="true">English</button>
<button type="button" class="note-lang-button" data-note-switch="hi"
 aria-controls="hi-notes" aria-pressed="false" lang="hi">हिन्दी</button></div></div>
<div class="note-content" id="en-notes" lang="en">
<h3>What do these commands actually do?</h3>
<p><strong>create</strong> makes a new directory with a three-line, version-1 manifest and one starter source file. It refuses existing destinations. <strong>verify DIRECTORY</strong> validates the manifest and program statically. <strong>launch DIRECTORY</strong> runs the selected source using the interpreter, not a native compiler.</p>
<h3>Run the checked-in sample</h3>
<pre class="note-command"><code>scarp verify tutorials/first-project
scarp launch tutorials/first-project</code></pre>
<div class="practice-challenge"><p><strong>Practice:</strong> Create a fresh project with a different name. In that new project's <code>src/main.srp</code>, write <code>print(6 * 7);</code>. Predict the output, verify it and launch it.</p></div></div>
<div class="note-content" id="hi-notes" lang="hi">
<h3>ये कमांड क्या करते हैं?</h3>
<p><strong>create</strong> नया प्रोजेक्ट फ़ोल्डर और उसमें <code>Scarp.project</code> तथा <code>src/main.srp</code> बनाता है। पहले से मौजूद फ़ोल्डर पर यह काम नहीं करता। <strong>verify DIRECTORY</strong> बिना प्रोग्राम चलाए static जाँच करता है। <strong>launch DIRECTORY</strong> असली interpreter से प्रोग्राम चलाता है।</p>
<h3>तैयार प्रोजेक्ट चलाएँ</h3>
<pre class="note-command"><code>scarp verify tutorials/first-project
scarp launch tutorials/first-project</code></pre>
<div class="practice-challenge"><p><strong>अभ्यास:</strong> अलग नाम से अपना नया प्रोजेक्ट बनाएँ। उसके <code>src/main.srp</code> में <code>print(6 * 7);</code> लिखकर पहले आउटपुट सोचें, फिर verify और launch करें।</p></div></div>
<p class="notes-provenance">Scarp source, manifest and output come from the checked-in sample; the exact interpreter behavior is tested against the pinned compiler. <a href="{en}">Read detailed constraints ↗</a></p></section>
<section class="run-panel"><p class="eyebrow">IMPORTANT LIMITS</p>
<h2>Interpreter projects, not native builds</h2>
<p>The development manifest is limited to 4,096 bytes and three ordered fields. Project entrypoints cannot escape the project root. These commands do not provide native executable generation, package downloads, lockfiles, a registry or a stable workspace format.</p></section>
<p><a class="secondary-button" href="{escape(rel(page, "projects/module-inspection/index.html"))}">Inspect a project\u0027s modules →</a>
<a class="secondary-button" href="{escape(rel(page, "projects/source-navigation/index.html"))}">Trace symbols and references →</a>
<a class="secondary-button" href="{escape(rel(page, "projects/project-testing/index.html"))}">Test a published alpha.8 project →</a></p>
<p class="fine-print">Pinned published compiler: <a href="{escape(target["release_url"])}">Scarp v{escape(target["version"])}</a> · source <code>{escape(target["source_commit"][:12])}</code>. No browser execution or fabricated output.</p>
</main>"""
    return page_shell(page, title, "Learn the real Scarp project CLI workflow in English and Hindi, with verified source and output.", main, "project-layout")



def render_project_inspection_page(target: dict) -> str:
    """Present a checked-in multi-module project and the read-only alpha.5 CLI."""
    page = "projects/module-inspection/index.html"
    folder = ROOT / "tutorials/module-inspection"
    manifest = (folder / "Scarp.project").read_bytes()
    entry = (folder / "src/main.srp").read_bytes()
    helper = (folder / "src/lib/math.srp").read_bytes()
    expected = read_expected_stdout(folder / "expected.stdout")
    if manifest != b"scarp-project: 1\nname: module-inspection\nentry: src/main.srp\n":
        raise ValueError("module inspection manifest differs from the tested example")
    if entry != b'import "lib/math.srp" as math;\nprint(math.answer);\n':
        raise ValueError("module inspection entry differs from the tested example")
    if not helper.endswith(b"pub bind answer = 21 * 2;\n") or expected != b"42\n":
        raise ValueError("module inspection module or output differs from the tested example")
    root_link = REPOSITORY + "/blob/main/tutorials/module-inspection/"
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<a href="{escape(rel(page, "projects/index.html"))}">Projects</a><span>/</span>
<span aria-current="page">Inspect project modules</span></nav>
<header class="page-heading">
<p class="eyebrow">PUBLISHED SCARP v{escape(target["version"])} · SOURCE-VERIFIED</p>
<h1>Inspect a Scarp project's modules</h1>
<p class="lead">Use the published Scarp-first CLI to inspect a full project module graph
without executing its program. This project includes a real import, public constant and
byte-exact interpreter output.</p>
<div class="guide-links">
<a href="{REPOSITORY}/blob/main/docs/project-inspection.md">English tutorial ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/project-inspection.md">हिन्दी ट्यूटोरियल ↗</a>
<a href="{REPOSITORY}/blob/main/docs/source-navigation.md">Symbol/reference navigation ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/source-navigation.md">नाम और संदर्भ गाइड ↗</a>
</div></header>
<section class="project-steps" aria-label="Project inspection commands">
<div class="project-step"><span>01</span><h2>Verify</h2>
<code>scarp verify tutorials/module-inspection</code></div>
<div class="project-step"><span>02</span><h2>Inspect</h2>
<code>scarp inspect modules --json tutorials/module-inspection</code></div>
<div class="project-step"><span>03</span><h2>Launch</h2>
<code>scarp launch tutorials/module-inspection</code></div></section>
<p class="project-warning">Inspection does not execute the program. It is <strong>static</strong> and emits
schema-v1 metadata, not program output. The JSON includes project-relative
file/module metadata and should not be confused with a compiler execution result.
<code>launch</code> uses the interpreter. There is no <code>scarp compile</code> command.</p>
<p class="project-warning">Compiler alpha.6 also supports <code>scarp inspect symbols --json tutorials/module-inspection</code> and <code>scarp inspect references --json tutorials/module-inspection</code>. These show definitions and use sites without executing code. IDs are local to one inspection, not permanent editor identities.</p>
<div class="project-source-grid">
<section class="code-panel" aria-labelledby="inspect-manifest">
<div class="panel-heading"><div><span class="eyebrow">REAL PROJECT MANIFEST</span>
<h2 id="inspect-manifest">Scarp.project</h2></div></div>
<pre><code>{escape(manifest.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{root_link}Scarp.project">View manifest ↗</a></div></section>
<section class="code-panel" aria-labelledby="inspect-main">
<div class="panel-heading"><div><span class="eyebrow">IMPORTED ENTRYPOINT</span>
<h2 id="inspect-main">src/main.srp</h2></div>
<button type="button" class="copy-button" data-copy="scarp-code">Copy code</button></div>
<pre><code id="scarp-code">{highlight_scarp(entry.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{root_link}src/main.srp">View entrypoint ↗</a></div></section>
<section class="code-panel" aria-labelledby="inspect-helper">
<div class="panel-heading"><div><span class="eyebrow">REAL SUPPORT MODULE</span>
<h2 id="inspect-helper">src/lib/math.srp</h2></div></div>
<pre><code>{highlight_scarp(helper.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{root_link}src/lib/math.srp">View helper ↗</a></div></section>
<section class="code-panel output-panel" aria-labelledby="inspect-output">
<div class="panel-heading"><div><span class="eyebrow">LAUNCH STDOUT FIXTURE</span>
<h2 id="inspect-output">expected.stdout</h2></div><span class="verified-tag">Real compiler</span></div>
<pre><code>{escape(expected.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{root_link}expected.stdout">View fixture ↗</a></div></section>
</div>
<section class="lesson-notes" aria-labelledby="inspection-explain">
<div class="notes-heading"><div><p class="eyebrow">WHAT IS INSPECTED?</p>
<h2 id="inspection-explain">Read the project without running it</h2></div>
<div class="language-switch" role="group" aria-label="Explanation language">
<button class="note-lang-button" type="button" data-note-switch="en"
aria-controls="en-notes" aria-pressed="true">English</button>
<button class="note-lang-button" type="button" data-note-switch="hi"
aria-controls="hi-notes" aria-pressed="false" lang="hi">हिन्दी</button>
</div></div>
<div class="note-content" id="en-notes" lang="en">
<p>The manifest selects <code>src/main.srp</code> as the entrypoint.
It imports <code>lib/math.srp</code>, which exposes a public compile-time scalar
constant. <strong>inspect modules --json DIRECTORY</strong> checks the actual graph and
returns metadata without evaluating <code>print</code>.
<strong>launch DIRECTORY</strong> executes the entrypoint and prints the verified
result <code>42</code>.</p>
<div class="practice-challenge"><p><strong>Try it:</strong> Run inspection against
the project directory, then against <code>tutorials/module-inspection/src/main.srp</code>.
Compare imports, dependencies and symbols. Schema-v1 module display labels may differ across platforms; the checked-in CLI tests compare the underlying graph.</p></div>
</div>
<div class="note-content" id="hi-notes" lang="hi">
<p><code>Scarp.project</code> में <code>src/main.srp</code> को entrypoint चुना गया है।
यह <code>lib/math.srp</code> मॉड्यूल import करता है।
<strong>inspect modules --json DIRECTORY</strong> बिना <code>print</code> चलाए
मॉड्यूल और dependencies की सूची देता है।
<strong>launch DIRECTORY</strong> interpreter से प्रोग्राम चलाकर सत्यापित आउटपुट
<code>42</code> प्रिंट करता है।</p>
<div class="practice-challenge"><p><strong>अभ्यास:</strong> पहले project फ़ोल्डर
की inspection करें, फिर उसके <code>src/main.srp</code> को inspect करें।
दोनों JSON inventories में imports, dependencies और symbols की तुलना करें। Display path अलग हो सकता है।</p></div></div>
<p class="notes-provenance">Pinned compiler
<a href="{escape(target["release_url"])}">v{escape(target["version"])}</a>,
source <code>{escape(target["source_commit"][:12])}</code>.
No browser Scarp execution or simulated JSON results.</p></section>
<p><a class="secondary-button" href="{escape(rel(page, "projects/source-navigation/index.html"))}">Next: trace declarations and uses →</a></p>
<p class="fine-print"><a href="{escape(rel(page, "projects/index.html"))}">← Your first Scarp project</a>
· <a href="{REPOSITORY}/blob/main/docs/compatibility.md">Published compiler compatibility</a></p>
</main>"""
    return page_shell(page, "Project module inspection",
                      "Read a real Scarp project's module graph using published compiler metadata.",
                      main, "project-layout")


def render_source_navigation_page(target: dict) -> str:
    """Publish a source-backed alpha.6 workshop; do not simulate a compiler index."""
    page = "projects/source-navigation/index.html"
    folder = ROOT / "tutorials/source-navigation"
    manifest = (folder / "Scarp.project").read_bytes()
    entry = (folder / "src/main.srp").read_bytes()
    helper = (folder / "src/lib/navigation_values.srp").read_bytes()
    expected = read_expected_stdout(folder / "expected.stdout")
    if manifest != b"scarp-project: 1\nname: source-navigation\nentry: src/main.srp\n":
        raise ValueError("navigation workshop manifest differs from the reviewed source")
    if (not entry.startswith(b'import "lib/navigation_values.srp" as library;\n')
            or entry.count(b"bind base =") != 2
            or b"twice(value: library.adjust(n: base + step))" not in entry
            or b"print(total);\n" not in entry):
        raise ValueError("navigation workshop entrypoint must be reviewed before publishing")
    if (b"bind private_seed = 2;" not in helper
            or b"pub bind offset = private_seed;" not in helper
            or b"pub pure funcra adjust(n: integer)" not in helper
            or expected != b"30\n"):
        raise ValueError("navigation workshop helper or output differs from the verified upstream fixture")

    origin = REPOSITORY + "/blob/main/tutorials/source-navigation/"
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<a href="{escape(rel(page, "projects/index.html"))}">Projects</a><span>/</span>
<span aria-current="page">Trace symbols and references</span></nav>
<header class="page-heading">
<p class="eyebrow">SCARP v{escape(target["version"])} · COMPILER-VALIDATED WORKSHOP</p>
<h1>Trace symbols across Scarp modules</h1>
<p class="lead">Follow two different <code>base</code> bindings, imported public definitions,
named arguments and a counted loop. Learn how <code>inspect symbols</code> differs
from <code>inspect references</code> without executing ordinary statements.</p>
<div class="guide-links">
<a href="{REPOSITORY}/blob/main/docs/source-navigation.md">English walkthrough ↗</a>
<a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/source-navigation.md">हिन्दी गाइड ↗</a>
<a href="{origin}README.md">Original project instructions ↗</a>
</div></header>
<section class="project-steps" aria-label="Run the real compiler">
<div class="project-step"><span>01</span><h2>Verify</h2>
<code>scarp verify tutorials/source-navigation</code></div>
<div class="project-step"><span>02</span><h2>Inspect</h2>
<code>scarp inspect references --json tutorials/source-navigation</code></div>
<div class="project-step"><span>03</span><h2>Launch</h2>
<code>scarp launch tutorials/source-navigation</code></div></section>
<p class="project-warning">Before launching, also try
<code>scarp inspect symbols --json tutorials/source-navigation</code>.
Both inspection commands type-check the source graph and emit metadata;
they do <strong>not</strong> execute the interpreter or produce the checked-in output.
Symbol IDs are local to a single inspection and file display paths vary.</p>
{render_reference_explorer(ROOT)}
<details class="ref-plain-sources"><summary>View unannotated files and copy code · मूल कोड देखें</summary>
<div class="project-source-grid">
<section class="code-panel" aria-labelledby="navigation-entry-title">
<div class="panel-heading"><div><span class="eyebrow">PROJECT ENTRYPOINT</span>
<h2 id="navigation-entry-title">src/main.srp</h2></div>
<button type="button" class="copy-button" data-copy="scarp-code">Copy code</button></div>
<pre><code id="scarp-code">{highlight_scarp(entry.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{origin}src/main.srp">View source ↗</a></div></section>
<section class="code-panel" aria-labelledby="navigation-helper-title">
<div class="panel-heading"><div><span class="eyebrow">IMPORTED SOURCE</span>
<h2 id="navigation-helper-title">src/lib/navigation_values.srp</h2></div></div>
<pre><code>{highlight_scarp(helper.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{origin}src/lib/navigation_values.srp">View helper ↗</a></div></section>
</div></details>
<div class="project-source-grid">
<section class="code-panel output-panel" aria-labelledby="navigation-stdout-title">
<div class="panel-heading"><div><span class="eyebrow">EXACT INTERPRETER OUTPUT</span>
<h2 id="navigation-stdout-title">expected.stdout</h2></div><span class="verified-tag">Real fixture</span></div>
<pre><code>{escape(expected.decode("utf-8"))}</code></pre>
<div class="panel-footer"><a href="{origin}expected.stdout">View exact bytes ↗</a></div></section>
</div>
<section class="lesson-notes" id="lesson-notes" aria-labelledby="navigation-explain">
<div class="notes-heading"><div><p class="eyebrow">EXPLORE THE SOURCE</p>
<h2 id="navigation-explain">Definitions are not the same as uses</h2></div>
<div class="language-switch" role="group" aria-label="Explanation language">
<button class="note-lang-button" type="button" data-note-switch="en"
aria-controls="en-notes" aria-pressed="true">English</button>
<button class="note-lang-button" type="button" data-note-switch="hi"
aria-controls="hi-notes" aria-pressed="false" lang="hi">हिन्दी</button></div></div>
<div class="note-content" id="en-notes" lang="en">
<p><strong>Definitions:</strong> the imported module declares public
<code>offset</code> and <code>adjust</code>, plus private
<code>private_seed</code>. The entrypoint declares an import alias,
a function named <code>twice</code>, and two separately scoped
<code>base</code> bindings.</p>
<p><strong>References:</strong> the inner <code>base</code> initializer reads
the outer <code>base</code>, while <code>total += base</code> reads
the inner one. Named argument labels <code>value:</code> and
<code>n:</code> refer to function parameters. The counted
<code>step</code> variable belongs to the <code>repeat</code> loop.</p>
<div class="practice-challenge"><p><strong>Try it:</strong> inspect the project
and the entrypoint file separately. Find both <code>base</code> definitions and
their reference targets. Then launch and compare the program's only output
line with the fixture. Do not compare symbol ID numbers between invocations.</p></div></div>
<div class="note-content" id="hi-notes" lang="hi">
<p><strong>घोषणाएँ:</strong> दूसरे मॉड्यूल में सार्वजनिक <code>offset</code> और
<code>adjust</code> तथा निजी <code>private_seed</code> हैं।
मुख्य फ़ाइल में <code>library</code> इम्पोर्ट नाम, <code>twice</code>
फ़ंक्शन और अलग स्कोप के दो <code>base</code> बाइंडिंग हैं।</p>
<p><strong>उपयोग:</strong> अंदर वाले <code>base</code> का प्रारम्भिक मान
बाहर वाले <code>base</code> से बनता है। <code>total += base</code>
अंदर वाले मान का उपयोग करता है। <code>value:</code> और <code>n:</code>
फ़ंक्शन पैरामीटर के नाम हैं; <code>step</code> लूप की गिनती है।</p>
<div class="practice-challenge"><p><strong>अभ्यास:</strong> प्रोजेक्ट और
<code>src/main.srp</code> दोनों पर निरीक्षण चलाएँ। <code>base</code> की
दो घोषणाएँ और उनके उपयोग खोजें। फिर <code>launch</code> का वास्तविक परिणाम
<code>expected.stdout</code> से मिलाएँ। अलग-अलग जाँच की symbol IDs की
तुलना न करें।</p></div></div>
<p class="notes-provenance">Pinned published
<a href="{escape(target["release_url"])}">v{escape(target["version"])}</a>
· source <code>{escape(target["source_commit"][:12])}</code>.
Read-only metadata is not program output. The browser does not execute Scarp.</p></section>
<section class="lab-reveals" aria-label="Self-check questions">
<details><summary>Which <code>base</code> is read inside <code>twice(value: library.adjust(n: base + step))</code>?</summary>
<p>The outer <code>base</code>. The inner binding is not visible until its initializer is resolved.</p>
<p lang="hi">बाहर वाला <code>base</code>। अंदर वाले बाइंडिंग का नाम उसके initializer के बाद उपलब्ध होता है।</p></details>
<details><summary>Why can the source inventory be inspected without printing <code>30</code>?</summary>
<p>Inspection performs static name/type checking. Only <code>launch</code> executes the program and produces the exact stdout fixture.</p>
<p lang="hi">निरीक्षण केवल नाम और प्रकार की स्थिर जाँच करता है; <code>launch</code> प्रोग्राम चलाकर <code>30</code> प्रिंट करता है।</p></details>
</section>
<p class="fine-print"><a href="{escape(rel(page, "projects/module-inspection/index.html"))}">← First inspect project modules</a>
· <a href="{escape(rel(page, "projects/index.html"))}">Project basics</a>
· <a href="{REPOSITORY}/blob/main/THIRD_PARTY_NOTICES.md">Source provenance and license</a></p>
</main>"""
    return page_shell(page, "Source navigation workshop",
                      "Compiler-tested bilingual guide to definitions and references in Scarp.",
                      main, "project-layout reference-explorer-layout")


def visible_stdin(data: bytes) -> str:
    """Make control bytes legible without treating displayed text as the raw file."""
    source = data.decode("utf-8")
    controls = {"\\": r"\\", "\r": r"\r", "\t": r"\t", "\x00": r"\0"}
    return "".join(
        controls.get(char, f"\\u{{{ord(char):x}}}" if ord(char) < 32 and char != "\n" else char)
        for char in source
    )


def lesson_exec_command(source: Path) -> str:
    """Include deterministic stdin redirection only when a fixture exists."""
    command = "scarp exec " + source.relative_to(ROOT).as_posix()
    stdin = source.with_suffix(".stdin")
    if stdin.is_file():
        read_optional_stdin(stdin)  # Same UTF-8 and size gate as the lesson verifier.
        command += " < " + stdin.relative_to(ROOT).as_posix()
    return command


def render_lesson(source: Path, stdout: Path, description: str) -> str:
    """Preserve source characters and exact fixture bytes; display CR visibly."""
    raw = source.read_text(encoding="utf-8")
    output = read_expected_stdout(stdout).decode("utf-8")
    visible = output.replace("\r", r"\r")
    note = '<p class="output-note">A literal CR byte is shown as \\r for readability.</p>' if "\r" in output else ""
    src_url = REPOSITORY + "/blob/main/" + source.relative_to(ROOT).as_posix()
    out_url = REPOSITORY + "/blob/main/" + stdout.relative_to(ROOT).as_posix()
    input_panel = ""
    stdin_path = source.with_suffix(".stdin")
    if stdin_path.is_file():
        supplied = read_optional_stdin(stdin_path)
        stdin_url = REPOSITORY + "/blob/main/" + stdin_path.relative_to(ROOT).as_posix()
        displayed = visible_stdin(supplied)
        if not supplied:
            displayed = "(empty input: immediate EOF)"
        input_panel = f"""<section class="code-panel stdin-fixture-panel" aria-labelledby="stdin-title">
<div class="panel-heading">
<div><span class="eyebrow">SUPPLIED PROGRAM INPUT · प्रोग्राम इनपुट</span>
<h2 id="stdin-title">{escape(stdin_path.name)}</h2></div></div>
<pre><code id="scarp-stdin">{escape(displayed)}</code></pre>
<p class="output-note">Displayed UTF-8 input is for reading only. Backslashes and control
bytes are shown visibly; the linked <code>.stdin</code> fixture is the source of exact
input bytes. Static <code>scarp verify</code> does not read input. The website
does not execute Scarp.</p>
<div class="panel-footer"><a href="{escape(stdin_url)}">View original .stdin fixture ↗</a></div>
</section>"""
    return f"""<div class="code-grid">
<section class="code-panel" aria-labelledby="source-title"><div class="panel-heading">
<div><span class="eyebrow">ORIGINAL SOURCE</span><h2 id="source-title">{escape(source.name)}</h2></div>
<button type="button" class="copy-button" data-copy="scarp-code">Copy code</button></div>
<pre><code id="scarp-code">{highlight_scarp(raw)}</code></pre>
<div class="panel-footer"><a href="{escape(src_url)}">View .srp on GitHub ↗</a></div></section>
<section class="code-panel output-panel" aria-labelledby="output-title"><div class="panel-heading">
<div><span class="eyebrow">EXPECTED OUTPUT</span><h2 id="output-title">stdout</h2></div>
<span class="verified-tag">Verified</span></div>
<div id="verified-output" data-verified-output><pre><code>{escape(visible)}</code></pre>{note}</div>
<div class="output-practice" data-output-practice hidden>
<button class="progress-toggle" type="button" data-output-start>Predict this output · आउटपुट का अनुमान लगाएँ</button>
<div data-output-workspace hidden>
<p id="output-practice-instructions">Write what you expect this program to print. Check prediction for a line-level hint without revealing the answer, or reveal the verified output when ready. This checks displayed text only; it does not run Scarp or save your input.</p>
<label for="output-prediction">Your predicted output · आपका अनुमान</label>
<textarea id="output-prediction" data-output-prediction rows="4" spellcheck="false"
 aria-describedby="output-practice-instructions" placeholder="What will this program print?"></textarea>
<div class="output-practice-actions">
<button class="progress-toggle" type="button" data-output-check>Check prediction · जाँचें</button>
<button class="progress-reset" type="button" data-output-toggle aria-controls="verified-output" aria-expanded="false">Reveal verified output</button>
<button class="progress-reset" type="button" data-output-reset>Start over</button></div>
<p data-output-feedback role="status" aria-live="polite"></p>
</div></div>
<div class="panel-footer"><a href="{escape(out_url)}">View exact fixture ↗</a></div></section>
</div>
{input_panel}"""


def render_notes(lesson: Lesson, hindi: HindiNote) -> str:
    """Show existing educational prose in both languages on every lesson page."""
    if lesson.source_path != hindi.source_path:
        raise ValueError(f"wrong Hindi notes for {lesson.source_path}")
    outcome = lesson_result(lesson.source.parent / "README.md", lesson.source.name)
    return f"""<section class="lesson-notes" id="lesson-notes" aria-labelledby="notes-heading">
<div class="notes-heading">
<div><p class="eyebrow">UNDERSTAND THE CODE</p>
<h2 id="notes-heading">Explanation &amp; practice</h2></div>
<div class="language-switch" role="group" aria-label="Explanation language">
<button type="button" class="note-lang-button" data-note-switch="en"
 aria-controls="en-notes" aria-pressed="true">English</button>
<button type="button" class="note-lang-button" data-note-switch="hi"
 aria-controls="hi-notes" aria-pressed="false" lang="hi">हिन्दी</button>
</div></div>
<div class="note-content" id="en-notes" data-note-language="en" lang="en">
<h3>What this example teaches</h3>
<p>{escape(lesson.description)}</p>
<h3>Expected behavior</h3>
<p>{escape(outcome)}</p>
<div class="practice-challenge"><p><strong>Practice:</strong>
Read the source before looking at the output. Predict the values and their order,
then use the pinned compiler to execute this lesson and compare the exact fixture.
Identify which operation produces the result.</p></div>
</div>
<div class="note-content" id="hi-notes" data-note-language="hi" lang="hi">
<h3>{escape(hindi.title)}</h3>
{render_hindi_note(hindi)}
</div>
<p class="notes-provenance">Explanations are sourced from the project's
<a href="{REPOSITORY}/blob/main/examples/{escape(lesson.section)}/README.md">English chapter guide</a>
and <a lang="hi" href="{REPOSITORY}/blob/main/docs/hi/{escape(lesson.section)}.md">हिन्दी अध्याय</a>.
The Scarp program and output are unchanged.</p>
</section>"""



def checkpoint_translation(values: dict[str, str]) -> str:
    """Two localizable spans; without JavaScript both remain readable."""
    return (
        '<span data-checkpoint-lang="en" lang="en">' + escape(values["en"]) + '</span>'
        '<span data-checkpoint-lang="hi" lang="hi">' + escape(values["hi"]) + '</span>'
    )


def render_checkpoint(lesson: Lesson, questions: dict[str, dict],
                      identifier: str = "checkpoint") -> str:
    """Progressively enhanced multiple-choice checkpoint, never fake code execution."""
    question = questions.get(lesson.source_path)
    if question is None:
        return ""
    options = "".join(
        '<label class="checkpoint-option"><input type="radio" name="checkpoint-choice"'
        + f' value="{index}" required><span>{checkpoint_translation(option)}</span></label>'
        for index, option in enumerate(question["options"])
    )
    correct = question["options"][question["correct"]]
    explanation = question["explanation"]
    revealed = {
        language: correct[language] + " — " + explanation[language]
        for language in ("en", "hi")
    }
    return f"""<section class="checkpoint-card" id="{escape(identifier)}" data-checkpoint
 data-checkpoint-answer="{question["correct"]}" aria-labelledby="{escape(identifier)}-title">
<p class="eyebrow">SOURCE-BACKED SELF-CHECK · स्रोत-आधारित अभ्यास</p>
<h2 id="{escape(identifier)}-title">Quick checkpoint / त्वरित अभ्यास</h2>
<p class="checkpoint-question">{checkpoint_translation(question["question"])}</p>
<div data-checkpoint-interactive hidden>
<form data-checkpoint-form>
<fieldset><legend>Choose one answer / एक उत्तर चुनें</legend>
<div class="checkpoint-options">{options}</div></fieldset>
<div class="checkpoint-buttons"><button type="submit" class="progress-toggle">Check answer / उत्तर जाँचें</button>
<button type="reset" class="progress-reset">Try again / दोबारा प्रयास</button></div>
<p class="checkpoint-feedback" data-checkpoint-feedback role="status" aria-live="polite"></p>
<div class="checkpoint-explanation" data-checkpoint-explanation hidden>
<p>{checkpoint_translation(revealed)}</p></div>
</form></div>
<details class="checkpoint-fallback" data-checkpoint-fallback>
<summary>Reveal the source-backed answer / सही उत्तर देखें</summary>
<p>{checkpoint_translation(revealed)}</p>
</details>
<p class="checkpoint-footnote">This question checks understanding of a recorded
 compiler output. It does not run Scarp in the browser.
 यह प्रश्न सत्यापित आउटपुट पर आधारित है; ब्राउज़र में Scarp नहीं चलता।</p>
</section>"""




def render_chapter_review(section: str, lessons: list[Lesson],
                          questions: dict[str, dict]) -> str:
    """Reuse fixture-validated checkpoints for a bilingual chapter review.

    Each card owns its own form and unique ids. The existing checkpoint script
    enhances each card independently; without JS the answer disclosure works.
    """
    if any(lesson.section != section for lesson in lessons):
        raise ValueError(f"chapter review includes lessons outside {section}")
    checks = [lesson for lesson in lessons if lesson.source_path in questions]
    if len(checks) != 3 or len({lesson.source_path for lesson in checks}) != 3:
        raise ValueError(f"chapter review requires three distinct verified questions: {section}")
    page = chapter_url(section)
    cards = "".join(
        f'<div class="chapter-review-entry">'
        f'<p class="chapter-review-context">'
        f'<strong>Question {index} of {len(checks)}</strong> · '
        f'<a href="{escape(rel(page, lesson.url))}#verified-output">'
        f'{escape(lesson.title)} · View source and recorded output ↗</a></p>'
        + render_checkpoint(lesson, questions, f"chapter-check-{index:02}")
        + '</div>'
        for index, lesson in enumerate(checks, 1)
    )
    return f"""<details class="chapter-review" id="chapter-review">
<summary><span>Practice this chapter · इस अध्याय का अभ्यास करें</span>
<small>{len(checks)} bilingual, compiler-evidenced questions</small></summary>
<div class="chapter-review-content">
<p>Answer all three questions using the checked-in lessons.
Feedback runs only in your browser; there is no stored score, automatic
lesson completion or Scarp execution. Answers remain readable without JavaScript.</p>
{cards}
</div></details>"""


def render_lesson_page(lesson: Lesson, all_lessons: list[Lesson], chapter: list[Lesson], target: dict, hindi: HindiNote, questions: dict[str, dict] | None = None) -> str:
    page = lesson.url
    i = all_lessons.index(lesson)
    sidebar = "".join(
        f'<a href="{escape(rel(page, item.url))}"'
        + (' aria-current="page" class="active"' if item == lesson else '')
        + f'><span>{escape(item.source.stem[:2])}</span>{escape(item.title)}<span class="completed-mark" data-progress-complete="{escape(item.section + "/" + item.source.stem)}" hidden aria-hidden="true">✓</span></a>'
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
    execution_command = lesson_exec_command(lesson.source)
    uses_stdin = lesson.source.with_suffix(".stdin").is_file()
    input_hint = ""
    if uses_stdin:
        input_hint = (
            "<p>In Bash or Windows Command Prompt, redirect the exact supplied input file "
            "with <code>&lt;</code>. For PowerShell, use a shell that supports "
            "byte-preserving stdin redirection instead of pasting displayed text.</p>"
        )
    notes = render_notes(lesson, hindi)
    checkpoint = render_checkpoint(lesson, questions or {})
    handoff = render_lesson_chapter_handoff(lesson, chapter, all_lessons)
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
<a lang="hi" href="#hi-notes">हिन्दी में समझें ↓</a></div></header>
<nav class="lesson-path-nav" aria-label="Chapter learning path">
<a href="{escape(rel(page, chapter_url(lesson.section)))}#chapter-path">← Chapter learning path</a>
{f'<a href="#checkpoint">Practice checkpoint ↓</a>' if checkpoint else ''}
<a href="{escape(rel(page, "labs/" + lesson.section + "/index.html"))}">Try chapter coding lab ↗</a>
</nav>
{code}
{notes}
{checkpoint}
<section class="lesson-progress-panel" data-progress-index="{escape(rel(page, "search-index.json"))}"
 data-progress-root="{escape(rel(page, "index.html"))}"
 data-progress-current="{escape(lesson.section + "/" + lesson.source.stem)}" hidden
 aria-label="Local lesson progress">
<div><p class="eyebrow">LEARNING PROGRESS</p>
<h2>Keep your place</h2><p data-progress-status role="status">Mark this lesson complete when you are ready.</p>
<p class="progress-disclaimer">Only saved in this browser. No account or tracking.</p></div>
<div class="progress-actions">
<button type="button" class="progress-toggle" data-progress-toggle aria-pressed="false">Mark lesson complete</button>
<a data-progress-resume href="{escape(rel(page, lesson.url))}" class="secondary-button">Continue learning →</a>
<p role="status" data-progress-message class="progress-feedback"></p></div>
</section>
<section class="run-panel" aria-labelledby="run-title">
<div><p class="eyebrow">TRY IT LOCALLY</p><h2 id="run-title">Verify, then execute</h2>
<p>Use the pinned compiler from the course root. Keep any imported <code>_support</code> files next to the source.</p></div>
<div class="commands"><code>scarp verify {escape(lesson.source_path)}</code>
<code>{escape(execution_command)}</code></div>
{input_hint}
<p>The website does not run code. <a href="{REPOSITORY}/blob/main/docs/cli-quickstart.md">Read the CLI guide ↗</a></p>
</section>
<nav class="step-nav" aria-label="Lesson navigation">
{step(before, "← Previous lesson")}{step(after, "Next lesson →")}</nav>
{handoff}
<p class="fine-print">Pinned compiler: <a href="{escape(target["release_url"])}">Scarp v{escape(target["version"])}</a>
· <code>{escape(target["source_commit"][:12])}</code>. No simulated output.</p>
</div></main>"""
    return page_shell(page, lesson.title, lesson.description, main, "lesson-layout")


def build(destination: Path) -> int:
    lessons, chapters, target = read_course()
    hindi_notes = read_hindi_notes(ROOT)
    questions = read_practice_questions(ROOT)
    labs = read_labs(ROOT)
    home, count = render_catalog(questions)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(home, encoding="utf-8", newline="\n")
    lab_index = destination / "labs/index.html"
    lab_index.parent.mkdir(parents=True, exist_ok=True)
    lab_index.write_text(render_labs_index(labs, target), encoding="utf-8", newline="\n")
    for lab in labs:
        lab_path = destination / lab.url
        lab_path.parent.mkdir(parents=True, exist_ok=True)
        lab_path.write_text(render_lab_page(lab, target), encoding="utf-8", newline="\n")
    index = [{"id": l.section + "/" + l.source.stem,
              "title": l.title, "chapter": l.chapter, "description": l.description,
              "hindi_title": hindi_notes[l.source_path].title,
              "hindi_summary": hindi_notes[l.source_path].summary,
              "has_checkpoint": l.source_path in questions,
              "url": l.url, "source": l.source.read_text(encoding="utf-8")} for l in lessons]
    (destination / "search-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    project_path = destination / "projects/index.html"
    project_path.parent.mkdir(parents=True, exist_ok=True)
    project_path.write_text(render_project_page(target), encoding="utf-8", newline="\n")
    inspect_path = destination / "projects/module-inspection/index.html"
    inspect_path.parent.mkdir(parents=True, exist_ok=True)
    inspect_path.write_text(render_project_inspection_page(target), encoding="utf-8", newline="\n")
    navigation_path = destination / "projects/source-navigation/index.html"
    navigation_path.parent.mkdir(parents=True, exist_ok=True)
    navigation_path.write_text(render_source_navigation_page(target), encoding="utf-8", newline="\n")
    alpha8_path = destination / "projects/project-testing/index.html"
    alpha8_path.parent.mkdir(parents=True, exist_ok=True)
    alpha8_path.write_text(
        render_alpha8_project_page(ROOT, page_shell, rel, highlight_scarp, visible_stdin),
        encoding="utf-8", newline="\n",
    )
    for section, chapter in chapters.items():
        path = destination / chapter_url(section)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_chapter(section, chapter, target, set(questions),
                                      next(lab for lab in labs if lab.identifier == section), chapters, questions),
                        encoding="utf-8", newline="\n")
    for lesson in lessons:
        path = destination / lesson.url
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_lesson_page(lesson, lessons, chapters[lesson.section],
                                           target, hindi_notes[lesson.source_path], questions),
                        encoding="utf-8", newline="\n")
    # Discoverable, stable directory URLs for search engines and learners.
    urls = ["index.html", "projects/index.html",
            "projects/module-inspection/index.html",
            "projects/source-navigation/index.html",
            "projects/project-testing/index.html", "labs/index.html"]
    urls.extend(lab.url for lab in labs)
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
    for asset in ("styles.css", "search-core.js", "search.js", "progress.js", "checkpoint.js",
                  "output-practice.js", "reference-explorer.js"):
        shutil.copyfile(ASSETS / asset, destination / asset)
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    count = build(args.output.resolve())
    print(f"Built {count} standalone lessons, 6 chapters, and four project tutorials at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
