"""Source-backed alpha.6 stdin/tuple workshop route for the static learning portal.

Separately pinned compiler and byte-exact input/output; no browser execution.
The matching release-pinned workflow runs the actual interpreter on every OS.
"""
from __future__ import annotations

import json
from pathlib import Path

VERSION = "0.0.6-alpha.6"
COMMIT = "cdf6a3924ec2a36c7beca5a9aec4f01a0bce515e"
RELEASE = "https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.6"
WORKSHOP = "tutorials/input-and-tuples"


def read_workshop(root: Path, read_stdout, read_stdin) -> dict:
    folder = root / WORKSHOP
    manifest = json.loads((folder / "compiler-target.json").read_text(encoding="utf-8"))
    required = {
        "version": VERSION,
        "source_commit": COMMIT,
        "release_tag": "v" + VERSION,
        "release_url": RELEASE,
        "status": "prerelease",
    }
    if not isinstance(manifest, dict) or any(
        manifest.get(key) != expected for key, expected in required.items()
    ):
        raise ValueError("alpha.6 input workshop release provenance changed")
    source = folder / "main.srp"
    stdin = folder / "main.stdin"
    stdout = folder / "main.stdout"
    if any(not file.is_file() or file.is_symlink() for file in (source, stdin, stdout)):
        raise ValueError("alpha.6 workshop has missing or unsafe source/fixture")
    text = source.read_text(encoding="utf-8")
    if len(text) > 16384 or text.count("read_line()") != 2 or (
        "tuple<string, integer>" not in text or "pure funcra profile(" not in text
    ):
        raise ValueError("alpha.6 workshop source differs from reviewed tutorial")
    if read_stdin(stdin) != "  संस्कार 🌍\n42\n".encode("utf-8"):
        raise ValueError("alpha.6 UTF-8 stdin fixture changed")
    if read_stdout(stdout) != 'Profile\n("संस्कार 🌍", 42)\nअंक: 42\n'.encode("utf-8"):
        raise ValueError("alpha.6 expected stdout differs from release verification")
    return manifest


def render_page(root: Path, page_shell, rel, escape, show_lesson, read_stdout, read_stdin) -> str:
    target = read_workshop(root, read_stdout, read_stdin)
    page = "workshops/input-and-tuples/index.html"
    folder = root / WORKSHOP
    project_rel = folder.relative_to(root).as_posix()
    code = show_lesson(folder / "main.srp", folder / "main.stdout",
                       "Two redirected UTF-8 input lines form an immutable Scarp tuple.")
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(page, "index.html"))}">Home</a><span>/</span>
<a href="{escape(rel(page, "workshops/index.html"))}">Workshops</a><span>/</span>
<span aria-current="page">Input and tuples</span></nav>
<header class="page-heading"><p class="eyebrow">PUBLISHED SCARP v{VERSION} · SEPARATE COMPILER PIN</p>
<h1>Read input and build an immutable tuple</h1>
<p class="lead">Practice real <code>read_line()</code>, Unicode text trimming,
integer parsing, tuple returns and indexing. The source and expected output
below are the checked-in programs verified by the published alpha.6 compiler.</p>
<div class="guide-links"><a href="https://github.com/scarp-lang/scarp-by-example/blob/main/{project_rel}/README.md">
Bilingual workshop guide ↗</a><a href="{RELEASE}">Published compiler ↗</a></div>
</header>
<p class="project-warning">This lesson needs <strong>v{VERSION}</strong>, built from
its own immutable compiler commit. The 52 numbered course lessons use alpha.4,
the conditional workshop uses alpha.7, and project testing uses alpha.8.
Do not assume these prerelease features are interchangeable.</p>
<section class="project-steps" aria-label="Local commands">
<div class="project-step"><span>01</span><h2>Verify source</h2>
<code>scarp verify {project_rel}/main.srp</code></div>
<div class="project-step"><span>02</span><h2>Run with exact input</h2>
<code>scarp exec {project_rel}/main.srp &lt; {project_rel}/main.stdin</code></div>
<div class="project-step"><span>03</span><h2>Compare output</h2>
<code>{project_rel}/main.stdout</code></div>
</section>
{code}
<section class="lesson-notes" id="lesson-notes" aria-labelledby="alpha6-notes-title">
<div class="notes-heading"><div><p class="eyebrow">ENGLISH + हिन्दी</p>
<h2 id="alpha6-notes-title">Understand the program</h2></div>
<div class="language-switch" role="group" aria-label="Explanation language">
<button class="note-lang-button" type="button" data-note-switch="en"
aria-controls="en-notes" aria-pressed="true">English</button>
<button class="note-lang-button" type="button" data-note-switch="hi"
aria-controls="hi-notes" aria-pressed="false" lang="hi">हिन्दी</button></div></div>
<div id="en-notes" class="note-content" lang="en">
<h3>Line input is not static verification</h3>
<p><code>verify</code> checks code without reading stdin.
The interpreter receives two UTF-8 lines from the checked-in <code>.stdin</code>
file: a padded name and a numeric score. <code>text_trim</code> removes
surrounding whitespace; <code>text_to_integer</code> explicitly parses the
score. The pure <code>profile</code> function returns a
<code>tuple&lt;string, integer&gt;</code> with zero-based index access.</p>
<h3>EOF and output atomicity</h3>
<p>Input must include both lines. Early EOF produces <code>E0055</code>
and prevents buffered <code>Profile</code> output from being emitted.
The site displays recorded output instead of executing the program.</p>
<div class="practice-challenge"><p><strong>Practice:</strong> Copy the
input file elsewhere, remove its second line and execute using that local
copy. Observe the missing-input diagnostic, then restore both lines.</p></div></div>
<div id="hi-notes" class="note-content" lang="hi">
<h3>दो पंक्तियों से tuple बनाएँ</h3>
<p><code>verify</code> इनपुट लिए बिना static जाँच करता है।
<code>read_line()</code> पहले नाम और फिर अंक की लाइन पढ़ता है।
<code>text_trim</code> अतिरिक्त खाली जगह हटाता है और
<code>text_to_integer</code> अंक को integer में बदलता है।
<code>profile</code> function एक immutable tuple लौटाता है।
<code>result[1]</code> उसका दूसरा सदस्य है।</p>
<h3>इनपुट खत्म होने पर</h3>
<p>दूसरी लाइन न मिले तो <code>E0055</code> त्रुटि आती है और
पहले लिखा <code>Profile</code> आउटपुट भी नहीं निकलता।
यह वेबसाइट कोड नहीं चलाती; केवल सत्यापित परिणाम दिखाती है।</p>
<div class="practice-challenge"><p><strong>अभ्यास:</strong> इनपुट
फ़ाइल की अलग कॉपी में दूसरी लाइन हटाकर चलाएँ।
फिर मूल दोनों लाइनें वापस रखें।</p></div></div>
<p class="notes-provenance">Both source and fixture are read directly from
Git-tracked files. A dedicated CI job builds exact compiler commit
<code>{COMMIT}</code> and checks the real runtime, bytes and EOF behavior.
This browser never runs Scarp.</p></section>
<p><a class="secondary-button" href="{escape(rel(page, "workshops/index.html"))}">
← Browse optional workshops</a></p>
<p class="fine-print">Independent release source:
<a href="{RELEASE}">v{target["version"]}</a> ·
<code>{target["source_commit"]}</code>. No simulated interpreter output.</p>
</main>"""
    return page_shell(page, "Input and tuples with published Scarp alpha.6",
                      "A source-backed bilingual Scarp alpha.6 stdin and tuple workshop.",
                      main, "lesson-layout")
