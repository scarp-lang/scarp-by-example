"""Bilingual, source-backed legacy-v1 -> declarative-v2 migration workshop."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from verify_project_migration import WORKSHOP, validate_fixtures


def render_page(
    root: Path,
    target: dict,
    page_shell: Callable,
    rel: Callable,
    escape: Callable,
    highlight_scarp: Callable,
) -> str:
    """Display checked-in manifests and byte-identical program/test fixtures."""
    if WORKSHOP != root / "tutorials" / "project-migration":
        raise ValueError("migration fixture path is outside course source root")
    exact_output = validate_fixtures(WORKSHOP)
    path = "projects/migration/index.html"
    old = escape((WORKSHOP / "legacy/Scarp.project").read_text(encoding="utf-8"))
    new = escape((WORKSHOP / "modern/scarp.project").read_text(encoding="utf-8"))
    source = highlight_scarp((WORKSHOP / "modern/src/main.srp").read_text(encoding="utf-8"))
    helper = highlight_scarp((WORKSHOP / "modern/src/lib/math.srp").read_text(encoding="utf-8"))
    test = highlight_scarp((WORKSHOP / "modern/tests/02-input.srp").read_text(encoding="utf-8"))
    stdin = escape((WORKSHOP / "modern/tests/02-input.stdin").read_text(encoding="utf-8"))
    output = escape(exact_output.decode("utf-8"))
    repo = "https://github.com/scarp-lang/scarp-by-example/blob/main/"
    tutorial = repo + "tutorials/project-migration/"
    en = repo + "docs/project-migration.md"
    hi = repo + "docs/hi/project-migration.md"

    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="{escape(rel(path, "index.html"))}">Home</a><span>/</span>
<a href="{escape(rel(path, "projects/declarative/index.html"))}">Projects</a><span>/</span>
<span aria-current="page">Migrate v1 to v2</span></nav>
<header class="page-heading">
<p class="eyebrow">SCARP v{escape(target["version"])} · TWO VERIFIED MANIFEST FORMATS</p>
<h1>From Scarp.project to scarp.project</h1>
<p class="lead">Compare the exact source and output of two real Scarp projects.
Only the manifest differs: legacy v1 becomes declarative v2, while the
program, its imports, its tests and its input fixtures stay identical.</p>
<div class="guide-links"><a href="{en}">Full English migration guide ↗</a>
<a href="{hi}" lang="hi">हिन्दी माइग्रेशन गाइड ↗</a></div>
</header>
<section class="project-steps" aria-label="Safe project migration">
<div class="project-step"><span>01</span><h2>Preserve source and tests</h2>
<code>src/ · tests/ · *.stdin</code></div>
<div class="project-step"><span>02</span><h2>Replace the manifest format</h2>
<code>Scarp.project → scarp.project</code></div>
<div class="project-step"><span>03</span><h2>Prove behavior stays equal</h2>
<code>scarp verify · run · test</code></div>
</section>
<p class="project-warning"><strong>Filename-only renaming is not v2 migration.</strong>
Replace the three-line body with the new declarative grammar and check
<code>scarp project info --json</code> reports <code>format: v2</code>.
Never ship both manifest filenames in the same directory.</p>
<div class="project-source-grid">
<section class="code-panel" aria-labelledby="legacy-migration-manifest">
<div class="panel-heading"><div><span class="eyebrow">BEFORE · LEGACY V1</span>
<h2 id="legacy-migration-manifest">Scarp.project</h2></div></div>
<pre><code>{old}</code></pre>
<div class="panel-footer"><a href="{tutorial}legacy/Scarp.project">View legacy manifest ↗</a></div>
</section>
<section class="code-panel" aria-labelledby="declarative-migration-manifest">
<div class="panel-heading"><div><span class="eyebrow">AFTER · DECLARATIVE V2</span>
<h2 id="declarative-migration-manifest">scarp.project</h2></div></div>
<pre><code>{new}</code></pre>
<div class="panel-footer"><a href="{tutorial}modern/scarp.project">View v2 manifest ↗</a></div>
</section>
<section class="code-panel" aria-labelledby="migration-main">
<div class="panel-heading"><div><span class="eyebrow">UNCHANGED ENTRYPOINT</span>
<h2 id="migration-main">src/main.srp</h2></div></div>
<pre><code>{source}</code></pre>
<div class="panel-footer"><a href="{tutorial}modern/src/main.srp">View Scarp code ↗</a></div>
</section>
<section class="code-panel" aria-labelledby="migration-helper">
<div class="panel-heading"><div><span class="eyebrow">UNCHANGED PURE IMPORT</span>
<h2 id="migration-helper">src/lib/math.srp</h2></div></div>
<pre><code>{helper}</code></pre>
<div class="panel-footer"><a href="{tutorial}modern/src/lib/math.srp">View module ↗</a></div>
</section>
<section class="code-panel" aria-labelledby="migration-input">
<div class="panel-heading"><div><span class="eyebrow">UNCHANGED INPUT TEST</span>
<h2 id="migration-input">tests/02-input.srp</h2></div></div>
<pre><code>{test}</code></pre>
<div class="panel-footer"><a href="{tutorial}modern/tests/02-input.srp">View test ↗</a></div>
</section>
<section class="code-panel" aria-labelledby="migration-stdin">
<div class="panel-heading"><div><span class="eyebrow">PER-TEST UTF-8 INPUT</span>
<h2 id="migration-stdin">tests/02-input.stdin</h2></div></div>
<pre><code>{stdin}</code></pre>
<div class="panel-footer"><a href="{tutorial}modern/tests/02-input.stdin">View test input ↗</a></div>
</section>
<section class="code-panel" aria-labelledby="migration-output">
<div class="panel-heading"><div><span class="eyebrow">EXACT OUTPUT IN BOTH FORMATS</span>
<h2 id="migration-output">expected.stdout</h2></div><span class="verified-tag">Byte-exact fixture</span></div>
<pre><code>{output}</code></pre>
<div class="panel-footer"><a href="{tutorial}modern/expected.stdout">View output ↗</a></div>
</section>
</div>
<section class="lesson-notes" id="migration-explanation" aria-labelledby="migration-why">
<h2 id="migration-why">Verify the contract · दोनों की जाँच</h2>
<div lang="en" class="note-content">
<h3>Why are the outputs equal?</h3>
<p>The only changed file is the manifest. Both projects still import
the same pure <code>math.add</code> function and print exactly
<code>Migrated: 42</code>. Each test suite contains two cases:
one checks arithmetic, and the other reads 19 and 23 from the
matching <code>.stdin</code> fixture. Both suites must pass two tests.</p>
<pre class="note-command"><code>scarp project info --json tutorials/project-migration/legacy
scarp project info --json tutorials/project-migration/modern
scarp test --require-tests --json tutorials/project-migration/legacy
scarp test --require-tests --json tutorials/project-migration/modern</code></pre>
<p>Legacy metadata includes <code>format: legacy-v1</code> and a null
version. Modern metadata includes <code>format: v2</code> and
<code>version: 0.1.0</code>. JSON schema-version 1 is not the same
thing as the project's manifest format.</p>
<div class="practice-challenge"><p><strong>Practice:</strong> Copy the
legacy sample into a new directory; replace its manifest with v2 syntax,
verify the metadata format and compare output. Never edit this reference
project while practicing.</p></div>
</div>
<div lang="hi" class="note-content">
<h3>नए प्रारूप में क्या बदलता है?</h3>
<p>सिर्फ़ मैनिफ़ेस्ट का नाम और लिखने का तरीका बदलता है।
<code>src/</code>, <code>tests/</code>, imports और input
fixture पहले जैसे रहते हैं। दोनों प्रोजेक्ट
<code>Migrated: 42</code> प्रिंट करते हैं, और दोनों
में दो-दो टेस्ट पास होते हैं।</p>
<p><code>project info --json</code> से सही फ़ॉर्मैट पहचानें:
पहले में <code>legacy-v1</code> और नए में <code>v2</code>।
नई फ़ाइल में <code>version: "0.1.0"</code> भी होता है।
यह TOML फ़ाइल या native compilation नहीं है।</p>
<div class="practice-challenge"><p><strong>अभ्यास:</strong>
पुराने प्रोजेक्ट की अलग कॉपी लें, नया मैनिफ़ेस्ट लिखें,
फिर <code>verify</code>, <code>run</code> और
<code>test --require-tests</code> के नतीजे मिलाएँ।</p></div>
</div>
<p class="notes-provenance">The source, manifests, input and output come from
checked-in fixtures. CI runs the actual pinned compiler on Linux,
Windows and macOS. This page does not execute Scarp in the browser.</p>
</section>
<section class="run-panel" aria-label="Migration limits">
<h2>Source-compatible project migration, not a package upgrade</h2>
<p>The empty <code>dependencies {{}}</code> block is syntax only.
This migration does not implement a registry, lockfile, native executable,
source workspace manager, automatic conversion or a browser interpreter.</p>
<a class="secondary-button" href="{escape(rel(path, "projects/declarative/index.html"))}">
← Modern project introduction</a>
</section>
<p class="fine-print">Published source pin:
<a href="{escape(target["release_url"])}">v{escape(target["version"])}</a> ·
<code>{escape(target["source_commit"][:12])}</code>.
<a href="{tutorial}README.md">Workshop source and reproducibility ↗</a></p>
</main>"""
    return page_shell(
        path, "Migrate Scarp projects: legacy v1 to declarative v2",
        "Verify identical source, output and tests across the Scarp v1/v2 manifest formats.",
        main, "project-layout",
    )
