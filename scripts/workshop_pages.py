"""Optional workshop pages sourced from immutable, release-pinned Scarp fixtures."""

from __future__ import annotations

import json
import re
from pathlib import Path


def read_workshops(root: Path, compiler_url: str, read_stdout) -> list[dict]:
    """Only explicitly opt-in workshops with complete checked-in fixtures are published."""
    workshops = []
    for manifest_path in sorted((root / "tutorials").glob("*/site-notes.json")):
        folder = manifest_path.parent
        slug = folder.name
        notes = json.loads(manifest_path.read_text(encoding="utf-8"))
        target = json.loads((folder / "compiler-target.json").read_text(encoding="utf-8"))
        if not re.fullmatch(r"[a-z][a-z0-9-]*", slug):
            raise ValueError(f"invalid workshop slug: {slug}")
        if not (notes.get("slug") == slug and notes.get("title") and notes.get("intro")
                and notes.get("intro_hi")):
            raise ValueError(f"{slug}: missing workshop metadata")
        version = target.get("version", "")
        sha = target.get("source_commit", "")
        if not (re.fullmatch(r"0[.][0-9]+[.][0-9]+-alpha[.][0-9]+", version)
                and re.fullmatch("[0-9a-f]{40}", sha)
                and target.get("release_tag") == "v" + version
                and target.get("release_url") == f"{compiler_url}/releases/tag/v{version}"
                and target.get("status") == "prerelease"):
            raise ValueError(f"{slug}: invalid release provenance")
        lessons = notes.get("lessons")
        if not isinstance(lessons, list) or not lessons:
            raise ValueError(f"{slug}: workshop has no lessons")
        required = ("source", "title", "summary", "summary_hi", "explanation",
                    "explanation_hi", "practice", "practice_hi")
        files = []
        for number, lesson in enumerate(lessons, start=1):
            if not isinstance(lesson, dict) or any(
                not isinstance(lesson.get(key), str) or not lesson[key].strip()
                for key in required
            ):
                raise ValueError(f"{slug}: incomplete bilingual lesson")
            name = lesson["source"]
            if not re.fullmatch(r"[0-9]{2}-[a-z0-9-]+[.]srp", name):
                raise ValueError(f"{slug}: invalid source file name")
            if not name.startswith(f"{number:02}-"):
                raise ValueError(f"{slug}: lessons out of order")
            source = folder / name
            stdout = source.with_suffix(".stdout")
            if not source.is_file() or not stdout.is_file():
                raise ValueError(f"{slug}: missing source/output file")
            read_stdout(stdout)
            files.append(name)
        expected = sorted(files)
        if expected != sorted(p.name for p in folder.glob("*.srp")):
            raise ValueError(f"{slug}: unlisted workshop source")
        if sorted(s.replace(".srp", ".stdout") for s in files) != sorted(
            p.name for p in folder.glob("*.stdout")
        ):
            raise ValueError(f"{slug}: orphaned workshop output")
        workshops.append(dict(notes, folder=folder, target=target))
    return workshops


def overview_url(workshop: dict) -> str:
    return f"workshops/{workshop['slug']}/index.html"


def lesson_url(workshop: dict, entry: dict) -> str:
    return f"workshops/{workshop['slug']}/{entry['source'][:-4]}/index.html"


def generate_workshop_pages(
    destination: Path, workshops: list[dict], root: Path, repo: str,
    page_shell, show_source, rel, escape,
) -> list[str]:
    """Write a workshop hub, overview and standalone source/output lesson pages."""
    def save(page: str, markup: str) -> None:
        path = destination / page
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markup, encoding="utf-8", newline="\n")

    routes = ["workshops/index.html"]
    hub = "workshops/index.html"
    cards = "".join(
        f'<a class="lesson-card" href="{escape(rel(hub, overview_url(w)))}">'
        f'<span class="lesson-description"><strong>{escape(w["title"])}</strong>'
        f'<span>{escape(w["intro"])} · Scarp v{escape(w["target"]["version"])}</span>'
        f'</span><span class="lesson-arrow" aria-hidden="true">↗</span></a>'
        for w in workshops
    )
    main = f"""<main id="main-content" class="container-wide chapter-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(hub,"index.html"))}">Home</a><span>/</span><span aria-current="page">Workshops</span></nav>
<header class="page-heading"><p class="eyebrow">SEPARATELY RELEASE-PINNED PRACTICE</p>
<h1>Optional workshops</h1><p class="lead">Learn from verified, real compiler examples. Each workshop uses its own published source pin. These pages do not run Scarp in the browser.</p></header>
<section class="lesson-list" aria-label="Available workshops">{cards}</section></main>"""
    save(hub, page_shell(hub, "Optional workshops", "Release-pinned additional Scarp workshops", main))

    for w in workshops:
        target = w["target"]
        page = overview_url(w)
        routes.append(page)
        cards = "".join(
            f'<a class="lesson-card" href="{escape(rel(page,lesson_url(w,e)))}">'
            f'<span class="lesson-number">{escape(e["source"][:2])}</span>'
            f'<span class="lesson-description"><strong>{escape(e["title"])}</strong>'
            f'<span>{escape(e["summary"])}</span></span>'
            f'<span class="lesson-arrow" aria-hidden="true">↗</span></a>'
            for e in w["lessons"]
        )
        main = f"""<main id="main-content" class="container-wide chapter-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page,"index.html"))}">Home</a><span>/</span>
<a href="{escape(rel(page,hub))}">Workshops</a><span>/</span>
<span aria-current="page">{escape(w["title"])}</span></nav>
<header class="page-heading"><p class="eyebrow">SCARP v{escape(target["version"])} · OPTIONAL</p>
<h1>{escape(w["title"])}</h1><p class="lead">{escape(w["intro"])}</p>
<p lang="hi">{escape(w["intro_hi"])}</p></header>
<section class="lesson-list" aria-label="Workshop lessons">{cards}</section>
<section class="run-panel"><h2>Reproducible interpreter lessons</h2>
<p>Compiler: <a href="{escape(target["release_url"])}">v{escape(target["version"])}</a>.
Pinned source commit: <code>{escape(target["source_commit"])}</code>.</p>
<p>The numbered course retains a different compiler target. Examples are displayed from original source and output fixtures; the browser does not execute them.</p>
<p><a href="{repo}/blob/main/tutorials/{escape(w["slug"])}/README.md">English/Hindi workshop guide ↗</a></p>
</section></main>"""
        save(page, page_shell(page, w["title"], w["intro"], main))
        for e in w["lessons"]:
            page = lesson_url(w, e)
            routes.append(page)
            source = w["folder"] / e["source"]
            stdout = source.with_suffix(".stdout")
            code = show_source(source, stdout, e["summary"])
            file_path = source.relative_to(root).as_posix()
            main = f"""<main id="main-content" class="container-wide chapter-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page,hub))}">Workshops</a><span>/</span>
<a href="{escape(rel(page,overview_url(w)))}">{escape(w["title"])}</a><span>/</span>
<span aria-current="page">{escape(e["title"])}</span></nav>
<header class="page-heading"><p class="eyebrow">VERIFIED SCARP v{escape(target["version"])}</p>
<h1>{escape(e["title"])}</h1><p class="lead">{escape(e["summary"])}</p></header>
{code}
<div class="lesson-notes">
<section id="en-notes" lang="en"><h2>Explanation and practice</h2>
<p>{escape(e["explanation"])}</p><div class="practice-challenge">
<p><strong>Practice:</strong> {escape(e["practice"])}</p></div></section>
<section id="hi-notes" lang="hi"><h2>हिन्दी में समझें और अभ्यास करें</h2>
<p>{escape(e["explanation_hi"])}</p><div class="practice-challenge">
<p><strong>अभ्यास:</strong> {escape(e["practice_hi"])}</p></div></section></div>
<section class="run-panel" aria-label="Local execution instructions">
<h2>Verify and run locally</h2><div class="commands">
<code>scarp verify {escape(file_path)}</code>
<code>scarp exec {escape(file_path)}</code></div>
<p>Requires published <a href="{escape(target["release_url"])}">Scarp v{escape(target["version"])}</a>
at immutable commit <code>{escape(target["source_commit"][:12])}</code>. This website never executes Scarp.</p>
<p><a href="{escape(rel(page,overview_url(w)))}">← Back to workshop</a></p></section>
</main>"""
            save(page, page_shell(page, e["title"], e["summary"], main, "lesson-layout"))
    return routes
