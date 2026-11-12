"""Render the separately published alpha.8 project workshop from original files.

No browser execution, network requests, fabricated test output, or main-course
compiler pin changes. Actual compiler behavior is checked by the separate CI.
"""
from __future__ import annotations

import json
from html import escape as html_escape
from pathlib import Path
from typing import Callable

REPO = "https://github.com/scarp-lang/scarp-by-example"
SOURCE_SHA = "37253e7805c0ca594560700dd1deb3928458e60d"
VERSION = "0.0.6-alpha.8"
RELEASE_URL = "https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.8"
FILES = (
    "scarp.project",
    "src/main.srp",
    "src/offset.srp",
    "tests/addition.srp",
    "tests/input.srp",
    "tests/input.stdin",
    "expected.stdout",
)


def read_workshop(root: Path) -> tuple[dict, dict[str, bytes]]:
    """Reject missing, oversized, unsafe or wrongly pinned teaching fixtures."""
    target = json.loads((root / "docs/compiler-target-alpha8.json").read_text(encoding="utf-8"))
    expected_metadata = {
        "version": VERSION,
        "source_commit": SOURCE_SHA,
        "release_url": RELEASE_URL,
        "scope": "tutorials/alpha8-project-testing",
    }
    if not isinstance(target, dict) or any(
        target.get(field) != expected for field, expected in expected_metadata.items()
    ):
        raise ValueError("alpha.8 workshop release provenance has changed")
    folder = root / "tutorials/alpha8-project-testing"
    contents: dict[str, bytes] = {}
    for name in FILES:
        candidate = folder / name
        if candidate.is_symlink() or not candidate.is_file():
            raise ValueError("missing or unsafe alpha.8 workshop file: " + name)
        contents[name] = candidate.read_bytes()
        if len(contents[name]) > 65536:
            raise ValueError("oversized alpha.8 workshop file: " + name)
        contents[name].decode("utf-8")  # Site sources must be valid UTF-8.
    if contents["tests/input.stdin"] != b"17\n25\n":
        raise ValueError("alpha.8 input fixture changed without verification")
    if contents["expected.stdout"] != b"42\n":
        raise ValueError("alpha.8 stdout fixture changed without verification")
    if not contents["scarp.project"].startswith(b'project "alpha8-test-workshop" {\n'):
        raise ValueError("alpha.8 manifest is not the reviewed v2 project")
    if (b"assert(" not in contents["tests/addition.srp"]
            or b"read_line()" not in contents["tests/input.srp"]):
        raise ValueError("alpha.8 test sources differ from the reviewed workshop")
    return target, contents


def render_page(
    root: Path,
    page_shell: Callable,
    rel: Callable,
    highlight: Callable,
    visible_stdin: Callable,
) -> str:
    target, data = read_workshop(root)
    page = "projects/project-testing/index.html"
    esc = lambda value: html_escape(str(value), quote=True)
    origin = REPO + "/blob/main/tutorials/alpha8-project-testing/"

    def panel(name: str, heading: str) -> str:
        ident = "alpha8-" + name.replace("/", "-").replace(".", "-")
        if name.endswith(".srp"):
            content = highlight(data[name].decode("utf-8"))
        elif name.endswith(".stdin"):
            content = esc(visible_stdin(data[name]))
        else:
            content = esc(data[name].decode("utf-8"))
        return (f'<section class="code-panel" aria-labelledby="{ident}">'
                f'<div class="panel-heading"><div><span class="eyebrow">{esc(heading)}</span>'
                f'<h2 id="{ident}">{esc(name)}</h2></div></div>'
                f'<pre><code>{content}</code></pre>'
                f'<div class="panel-footer"><a href="{esc(origin + name)}">'
                'Original file ↗</a></div></section>')

    panels = "".join((
        panel("scarp.project", "V2 MANIFEST"),
        panel("src/main.srp", "REAL ENTRYPOINT"),
        panel("src/offset.srp", "EXPORTED PURE FUNCTION"),
        panel("expected.stdout", "EXACT INTERPRETER STDOUT"),
        panel("tests/addition.srp", "BOOLEAN ASSERTION TEST"),
        panel("tests/input.srp", "INPUT-DRIVEN TEST"),
        panel("tests/input.stdin", "EXACT TEST INPUT"),
    ))
    home = esc(rel(page, "index.html"))
    projects = esc(rel(page, "projects/index.html"))
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{home}">Home</a><span>/</span>
<a href="{projects}">Projects</a><span>/</span>
<span aria-current="page">Published alpha.8 testing</span></nav>
<header class="page-heading">
<p class="eyebrow">PUBLISHED SCARP v{VERSION} · INDEPENDENT SOURCE PIN</p>
<h1>Test a real Scarp project</h1>
<p class="lead">Follow original, runnable Scarp source, two assertion-based tests,
a byte-exact input fixture and recorded application output. This static site
does not execute code in your browser.</p>
<div class="guide-links"><a href="{REPO}/blob/main/docs/alpha8-project-testing.md">
English guide ↗</a>
<a href="{REPO}/blob/main/docs/hi/alpha8-project-testing.md" lang="hi">
हिन्दी गाइड ↗</a>
<a href="{RELEASE_URL}">Get alpha.8 ↗</a></div></header>
<p class="project-warning">Compiler compatibility matters:
this project requires <strong>v{VERSION}</strong>.
The existing numbered course still targets alpha.4. Do not run alpha.8
test commands with the older course compiler executable.</p>
<section class="project-steps" aria-label="Project testing commands">
<div class="project-step"><span>01</span><h2>Verify</h2>
<code>scarp verify tutorials/alpha8-project-testing</code></div>
<div class="project-step"><span>02</span><h2>Run</h2>
<code>scarp run tutorials/alpha8-project-testing</code></div>
<div class="project-step"><span>03</span><h2>Test</h2>
<code>scarp test --require-tests tutorials/alpha8-project-testing</code></div>
</section>
<div class="project-source-grid">{panels}</div>
<section class="lesson-notes" aria-labelledby="alpha8-notes-heading">
<div class="notes-heading"><div><p class="eyebrow">ENGLISH + हिन्दी</p>
<h2 id="alpha8-notes-heading">Why each file matters</h2></div>
<div class="language-switch" role="group" aria-label="Explanation language">
<button class="note-lang-button" type="button" data-note-switch="en"
aria-controls="en-notes" aria-pressed="true">English</button>
<button class="note-lang-button" type="button" data-note-switch="hi"
aria-controls="hi-notes" aria-pressed="false" lang="hi">हिन्दी</button></div></div>
<div class="note-content" id="en-notes" lang="en">
<h3>Manifest, source and tests</h3>
<p>The <code>scarp.project</code> manifest names <code>src/main.srp</code>.
Static <code>verify</code> checks it without executing runtime statements.
Interpreter-backed <code>run</code> prints <code>42</code> followed by LF.
The two test programs import the same pure function. A false
<code>assert</code> produces diagnostic <code>E0065</code>.</p>
<h3>List or filter tests</h3>
<pre class="note-command"><code>scarp test --list tutorials/alpha8-project-testing
scarp test --json --filter input tutorials/alpha8-project-testing</code></pre>
<p><code>--list</code> discovers tests without running them or reading input fixtures.
<code>--json</code> returns schema-v1 test results, not program output.
<code>--filter input</code> selects filenames by case-sensitive substring.
Each test receives only its matching <code>.stdin</code> fixture.</p>
<div class="practice-challenge"><p><strong>Practice:</strong> In a separate local
copy, change 25 to 24 in the input file and rerun the filtered test.
The false assertion should report <code>E0065</code>.</p></div></div>
<div class="note-content" id="hi-notes" lang="hi">
<h3>प्रोजेक्ट और टेस्ट का अर्थ</h3>
<p><code>scarp.project</code> में मुख्य फ़ाइल दी जाती है।
<code>verify</code> बिना कोड चलाए static जाँच करता है;
<code>run</code> असली interpreter से <code>42</code> प्रिंट करता है।
दोनों टेस्ट एक ही pure function import करते हैं।
गलत <code>assert</code> पर <code>E0065</code> मिलता है।</p>
<h3>इनपुट फ़ाइल और फ़िल्टर</h3>
<p><code>tests/input.stdin</code> के 17 और 25 उसी नाम के टेस्ट को मिलते हैं।
<code>--list</code> टेस्ट नहीं चलाता और input fixture नहीं पढ़ता।
<code>--json</code> schema-1 परिणाम देता है।
<code>--filter input</code> नाम में input वाला टेस्ट चुनता है।</p>
<div class="practice-challenge"><p><strong>अभ्यास:</strong> अपनी अलग local copy
में 25 को 24 करें और फ़िल्टर वाला टेस्ट चलाएँ। अब <code>E0065</code>
मिलना चाहिए। मूल fixture न बदलें।</p></div></div>
<p class="notes-provenance">All source and output above come from original
checked-in files. Independent CI runs this project with the exact published
compiler on Linux, Windows and macOS. This page displays no fabricated
test report and does not execute Scarp.</p></section>
<section class="run-panel"><p class="eyebrow">BOUNDARIES</p>
<h2>Real interpreter tests, not a package registry</h2>
<p>The empty <code>dependencies {{}}</code> manifest block does not install
packages. Native executable compilation, arbitrary dependencies, and browser
execution are not provided by this tutorial.</p></section>
<p><a class="secondary-button" href="{projects}">← Earlier project workflows</a>
<a class="secondary-button" href="{REPO}/blob/main/tutorials/alpha8-project-testing/README.md">
Read full workshop ↗</a></p>
<p class="fine-print">Compiler pin: <a href="{RELEASE_URL}">v{VERSION}</a> ·
<code>{SOURCE_SHA}</code>. The 52 numbered lessons remain separately pinned.</p>
</main>"""
    return page_shell(
        page,
        "Scarp alpha.8 project testing",
        "Explore the published alpha.8 Scarp project and its source-backed tests.",
        main,
        "project-layout",
    )
