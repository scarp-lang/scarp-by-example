"""Static, release-pinned alpha.3 lesson pages; no browser execution."""
from __future__ import annotations

from html import escape

from verify_alpha7_generics_text import PIN, VERSION, PROGRAMS, UPSTREAM, WORKSHOP, check_inventory

INDEX = "workshops/alpha7-generics-text/index.html"
RELEASE = "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION
REPO = "https://github.com/scarp-lang/scarp-by-example"
ORIGIN = "https://github.com/scarp-lang/scarp/blob/" + PIN + "/examples/"
LESSONS = {
    "generic_values": ("Generic functions and explicit arguments", "Infer types from values; pass explicit type arguments when needed.", "Predict the three output lines. Then call identity with another type.", "तीनों परिणामों का अनुमान लगाएँ। फिर identity को किसी अन्य प्रकार के साथ चलाएँ।"),
    "generic_constraints": ("Numeric and Comparable constraints", "Keep exact number types and compare compatible numeric tuples.", "Why does square(0.1d) yield 0.01? Compare two tuples with equal first members.", "square(0.1d) का परिणाम 0.01 क्यों है? समान पहले सदस्य वाले दो tuples की तुलना करें।"),
    "contextual_inference": ("Contextual inference and defaults", "Use a binding annotation or record field to infer a return-only type.", "Explain why empty() needs a context and try an annotated integer list.", "समझाएँ कि empty() को प्रकार का संदर्भ क्यों चाहिए। integer सूची बनाएँ।"),
    "generic_option": ("Generic Option and fallbacks", "Distinguish a present value from an absent value.", "Compare present zero with None. Which returns the fallback?", "उपस्थित शून्य की None से तुलना करें। किसमें fallback मिलेगा?"),
    "generic_result": ("Generic Result propagation", "Wrap success in a tuple while retaining the error type.", "Trace both branches of the match and change the error message.", "match की दोनों शाखाओं को समझें और त्रुटि संदेश बदलें।"),
    "string_operators": ("String operators and literals", "Concatenate, repeat, and preserve raw or multiline text.", "Find the trailing space in the repetition output. Compare a raw literal with a newline escape.", "दोहराए गए टेक्स्ट का अंतिम space देखें। raw string और newline escape की तुलना करें।"),
    "text_snapshots": ("String updates and snapshots", "Construct new UTF-8 text without modifying a saved value.", "Change the repetition count and predict which binding remains unchanged.", "दोहराने की संख्या बदलें और बताएँ कि कौन-सी binding नहीं बदलेगी।"),
}


def lesson_path(name: str) -> str:
    if name not in LESSONS:
        raise ValueError(f"unknown alpha.3 lesson: {name}")
    return f"workshops/alpha7-generics-text/{name.replace('_', '-')}/index.html"


def validate():
    check_inventory()
    if set(LESSONS) != set(PROGRAMS) or len(LESSONS) != len(PROGRAMS):
        raise ValueError("alpha.3 site inventory differs from verifier")


def render_index(page_shell, rel):
    validate()
    cards = "".join(
        f'<a class="lab-card" href="{escape(rel(INDEX, lesson_path(name)))}">'
        f'<span class="eyebrow">ALPHA.3</span><h2>{escape(LESSONS[name][0])}</h2>'
        f'<p>{escape(LESSONS[name][1])}</p><span class="lab-open">Open lesson →</span></a>'
        for name in PROGRAMS
    )
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(INDEX, 'index.html'))}">Home</a>
<span>/</span><span aria-current="page">Generics and text workshop</span></nav>
<header class="page-heading"><p class="eyebrow">PUBLISHED SCARP v{VERSION}</p>
<h1>Generic functions and string operations</h1>
<p class="lead">Seven runnable programs with exact expected outputs, independent of the numbered course.</p>
<p>Immutable compiler source: <code>{PIN}</code> · <a href="{RELEASE}">Published prerelease</a></p>
<div class="guide-links"><a href="{REPO}/blob/main/tutorials/alpha7-generics-text/README.md">English guide</a>
<a lang="hi" href="{REPO}/blob/main/tutorials/alpha7-generics-text/README.md#हिन्दी-मार्गदर्शिका">हिन्दी गाइड</a></div></header>
<section class="run-panel"><h2>Run locally</h2>
<p>The website does not execute code in your browser. Use the released compiler or build the exact pinned source.</p>
<code>python scripts/verify_alpha7_generics_text.py --compiler /path/to/scarp --compiler-source /path/to/pinned/scarp</code>
<p>Generic specializations and text construction are bounded. These lessons run through the interpreter, not native ELF64 objects.</p></section>
<section aria-label="Seven generic and text lessons"><div class="lab-grid">{cards}</div></section>
<section class="lesson-notes" lang="hi"><h2>हिन्दी में अभ्यास</h2>
<p>पहले परिणाम का अनुमान लगाएँ, फिर अपने कंप्यूटर पर Scarp से जाँचें। पुराने संस्करणों में generic functions और नए string operators को समर्थित न मानें।</p></section></main>"""
    return page_shell(INDEX, "Generics and text workshop", "Seven independently pinned Scarp generic and string examples.", main, "project-layout")


def render_example(name, page_shell, rel, highlight_scarp):
    page = lesson_path(name)
    validate()
    title, summary, exercise, hindi = LESSONS[name]
    source = (WORKSHOP / f"{name}.srp").read_bytes().decode("utf-8")
    output = (WORKSHOP / f"{name}.stdout").read_bytes().decode("utf-8")
    local = f"tutorials/alpha7-generics-text/{name}"
    course_url = REPO + "/blob/main/" + local
    upstream = f"{name}.srp" in UPSTREAM
    provenance = (
        f'<p>Unchanged upstream source: <a href="{ORIGIN}{name}.srp">original program</a> · '
        f'<a href="{ORIGIN}{name}.stdout">original output</a> (Apache-2.0).</p>'
        if upstream else '<p>Original Scarp by Example teaching program (MIT), with a pinned compiler verification workflow.</p>'
    )
    def adjacent(offset, label):
        index = PROGRAMS.index(name) + offset
        if not 0 <= index < len(PROGRAMS):
            return ""
        target = PROGRAMS[index]
        return f'<a href="{escape(rel(page, lesson_path(target)))}">{label}: {escape(LESSONS[target][0])}</a>'

    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(page, 'index.html'))}">Home</a>
<span>/</span><a href="{escape(rel(page, INDEX))}">Generics and text workshop</a><span>/</span>
<span aria-current="page">{escape(title)}</span></nav>
<header class="page-heading"><p class="eyebrow">SCARP v{VERSION}</p><h1>{escape(title)}</h1>
<p class="lead">{escape(summary)}</p><p>Compiler: <a href="{RELEASE}">published alpha.3</a> · <code>{PIN}</code></p>
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
