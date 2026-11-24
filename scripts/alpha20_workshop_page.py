"""Static, release-pinned alpha.20 lesson pages; no browser execution."""
from __future__ import annotations

from html import escape

from verify_alpha20_exact_values import PIN, VERSION, PROGRAMS, UPSTREAM, WORKSHOP, check_inventory

INDEX = "workshops/alpha20-exact-values/index.html"
RELEASE = "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION
REPO = "https://github.com/scarp-lang/scarp-by-example"
ORIGIN = "https://github.com/scarp-lang/scarp/blob/" + PIN + "/examples/"
LESSONS = {
    "decimal_exact": ("Exact decimal arithmetic", "Explicit constructors, typed arrays and rounded division.",
        "Predict the result of rounding one-third to two decimal places.",
        "एक तिहाई को दो दशमलव स्थानों तक round करने पर क्या मिलेगा?"),
    "decimal_literals": ("Decimal literals versus float", "The d suffix selects exact base-ten arithmetic.",
        "Why does adding 0.1d three times produce exactly 0.3?",
        "0.1d को तीन बार जोड़ने पर ठीक 0.3 क्यों मिलता है?"),
    "tuple_index_updates": ("Mutable tuple member replacement", "A constant index replaces a member of a var binding.",
        "Which saved tuple retains the original coordinates?",
        "कौन-सा सुरक्षित tuple पुराने coordinates रखता है?"),
    "tuple_ordering": ("Numeric tuple ordering", "Compare compatible numeric tuples lexicographically.",
        "Which first unequal member determines the ordering?",
        "पहला असमान सदस्य क्रम का निर्णय कैसे करता है?"),
    "tuple_snapshots": ("Tuple snapshot independence", "Keep the old tuple while replacing a member in a mutable binding.",
        "Why is (1, 90) less than (2, 0), regardless of the second member?",
        "(1, 90) और (2, 0) में दूसरे सदस्य से पहले पहला सदस्य क्यों देखा जाता है?"),
}


def lesson_path(name: str) -> str:
    if name not in LESSONS:
        raise ValueError(f"unknown alpha.20 lesson: {name}")
    return f"workshops/alpha20-exact-values/{name.replace('_', '-')}/index.html"


def validate():
    check_inventory()
    if set(LESSONS) != set(PROGRAMS) or len(LESSONS) != len(PROGRAMS):
        raise ValueError("alpha.20 site inventory differs from verifier")


def render_index(page_shell, rel):
    validate()
    cards = "".join(
        f'<a class="lab-card" href="{escape(rel(INDEX, lesson_path(name)))}">'
        f'<span class="eyebrow">ALPHA.20</span><h2>{escape(LESSONS[name][0])}</h2>'
        f'<p>{escape(LESSONS[name][1])}</p><span class="lab-open">Open lesson →</span></a>'
        for name in PROGRAMS
    )
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(INDEX, 'index.html'))}">Home</a>
<span>/</span><span aria-current="page">Exact values workshop</span></nav>
<header class="page-heading"><p class="eyebrow">PUBLISHED SCARP v{VERSION}</p>
<h1>Exact decimals and tuple snapshots</h1>
<p class="lead">Five runnable programs with exact expected outputs, independent of the 60 numbered lessons.</p>
<p>Immutable compiler source: <code>{PIN}</code> · <a href="{RELEASE}">Published prerelease</a></p>
<div class="guide-links"><a href="{REPO}/blob/main/tutorials/alpha20-exact-values/README.md">English guide</a>
<a lang="hi" href="{REPO}/blob/main/docs/hi/alpha20-exact-values.md">हिन्दी गाइड</a></div></header>
<section class="run-panel"><h2>Run locally</h2>
<p>The website does not execute code in your browser. Use the released compiler or build the exact pinned source.</p>
<code>python scripts/verify_alpha20_exact_values.py --compiler /path/to/scarp --compiler-source /path/to/pinned/scarp</code>
<p>Decimal precision is bounded. Tuple replacement is not in-place array assignment. The native ELF64 API is Rust-host only.</p></section>
<section aria-label="Five exact-value lessons"><div class="lab-grid">{cards}</div></section>
<section class="lesson-notes" lang="hi"><h2>हिन्दी में अभ्यास</h2>
<p>पहले परिणाम का अनुमान लगाएँ, फिर अपने कंप्यूटर पर Scarp से जाँचें। पुराने संस्करणों में इन नए literals और tuple assignments को समर्थित न मानें।</p></section></main>"""
    return page_shell(INDEX, "Exact values workshop", "Five pinned Scarp alpha.20 decimal and tuple examples.", main, "project-layout")


def render_example(name, page_shell, rel, highlight_scarp):
    page = lesson_path(name)
    validate()
    title, summary, exercise, hindi = LESSONS[name]
    source = (WORKSHOP / f"{name}.srp").read_bytes().decode("utf-8")
    output = (WORKSHOP / f"{name}.stdout").read_bytes().decode("utf-8")
    local = f"tutorials/alpha20-exact-values/{name}"
    course_url = REPO + "/blob/main/" + local
    upstream = f"{name}.srp" in UPSTREAM
    provenance = (
        f'<p>Unchanged upstream source: <a href="{ORIGIN}{name}.srp">original program</a> · '
        f'<a href="{ORIGIN}{name}.stdout">original output</a> (Apache-2.0).</p>'
        if upstream else '<p>Original Scarp by Example teaching program (MIT), executed by the pinned compiler.</p>'
    )
    def adjacent(offset, label):
        index = PROGRAMS.index(name) + offset
        if not 0 <= index < len(PROGRAMS):
            return ""
        target = PROGRAMS[index]
        return f'<a href="{escape(rel(page, lesson_path(target)))}">{label}: {escape(LESSONS[target][0])}</a>'

    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(page, 'index.html'))}">Home</a>
<span>/</span><a href="{escape(rel(page, INDEX))}">Exact values workshop</a><span>/</span>
<span aria-current="page">{escape(title)}</span></nav>
<header class="page-heading"><p class="eyebrow">SCARP v{VERSION}</p><h1>{escape(title)}</h1>
<p class="lead">{escape(summary)}</p><p>Compiler: <a href="{RELEASE}">published alpha.20</a> · <code>{PIN}</code></p>
{provenance}</header>
<section class="lesson-notes" lang="en"><h2>Predict before running</h2><p>{escape(exercise)}</p></section>
<div class="code-grid">
<section class="code-panel" aria-label="Scarp source"><div class="panel-heading"><h2>{name}.srp</h2></div>
<pre><code id="scarp-code">{highlight_scarp(source)}</code></pre>
<div class="panel-footer"><a href="{course_url}.srp">Source file</a></div></section>
<section class="code-panel output-panel" aria-label="Expected output"><div class="panel-heading"><h2>{name}.stdout</h2></div>
<pre><code id="scarp-output">{escape(output)}</code></pre>
<div class="panel-footer"><a href="{course_url}.stdout">Exact output file</a></div></section></div>
<section class="run-panel"><h2>Run on your computer</h2>
<pre><code>scarp verify {local}.srp
scarp exec {local}.srp</code></pre>
<p>The website does not execute code in your browser. Compare local output against the fixture.</p></section>
<section class="lesson-notes" lang="hi"><h2>हिन्दी में अभ्यास</h2><p>{escape(hindi)}</p></section>
<nav class="step-nav" aria-label="Workshop lesson navigation">{adjacent(-1, "Previous")}
<a href="{escape(rel(page, INDEX))}">Workshop overview</a>{adjacent(1, "Next")}</nav></main>"""
    return page_shell(page, title, summary, main, "project-layout")
