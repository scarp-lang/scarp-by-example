"""Static bilingual pages for the separately pinned numerical workshop."""
from html import escape

from verify_alpha7_numerical import PIN, VERSION, RELEASE, PROGRAMS, WORKSHOP, check_inventory

INDEX = "workshops/alpha7-numerical/index.html"
REPO = "https://github.com/scarp-lang/scarp-by-example"
COMPILER_EXAMPLES = "https://github.com/scarp-lang/scarp/tree/" + PIN + "/examples"
LESSONS = {
    "array_concat": (
        "Join fixed-size arrays",
        "Combine two typed arrays into a new array whose length is the sum of the input lengths.",
        "Predict the merged length, then check that neither original array changes.",
        "दो-दो मानों वाले ऐरे से चार मानों का नया ऐरे बनता है। मूल ऐरे नहीं बदलते।",
        "पहले ऐरे में नए मान रखकर पाँचों आउटपुट पंक्तियों का अनुमान लगाएँ।",
    ),
    "integer_reductions": (
        "GCD, HCF and LCM",
        "Reduce several integers to a common divisor or common multiple. GCD and HCF are aliases.",
        "Find the common divisor of 18, 30 and 42 and the shared period of 3, 5 and 8.",
        "18, 30 और 42 का महत्तम समापवर्तक 6 है। 3, 5 और 8 का लघुत्तम समापवर्त्य 120 है।",
        "6, 10 और 15 का GCD तथा LCM निकालें।",
    ),
    "stable_softplus": (
        "Stable vector softplus",
        "Apply a numerically stable floating-point activation to finite scores; compare the value at zero with a tolerance.",
        "Predict the two extreme activations, and explain why the central value is between 0.69 and 0.70.",
        "softplus हर स्कोर पर अलग लागू होता है। शून्य पर मान log(2) के करीब है।",
        "किस स्कोर का परिणाम अधिक होगा? दोनों असमानताएँ सत्य क्यों हैं?",
    ),
}


def lesson_path(name):
    if name not in LESSONS:
        raise ValueError(f"unknown numerical workshop lesson: {name}")
    return f"workshops/alpha7-numerical/{name.replace('_', '-')}/index.html"


def validate():
    check_inventory()
    if tuple(LESSONS) != PROGRAMS:
        raise ValueError("numerical workshop site inventory differs from verifier")


def render_index(page_shell, rel):
    validate()
    cards = "".join(
        f'<a class="lab-card" href="{escape(rel(INDEX, lesson_path(name)))}">'
        f'<span class="eyebrow">v{VERSION}</span><h2>{escape(LESSONS[name][0])}</h2>'
        f'<p>{escape(LESSONS[name][1])}</p><span class="lab-open">Open lesson →</span></a>'
        for name in PROGRAMS
    )
    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(INDEX, 'index.html'))}">Home</a>
<span>/</span><span aria-current="page">Numerical programming</span></nav>
<header class="page-heading"><p class="eyebrow">PUBLISHED SCARP v{VERSION}</p>
<h1>Numerical programming in Scarp</h1>
<p class="lead">Three original programs with exact output fixtures, separately pinned from the numbered course.</p>
<p><a href="{RELEASE}">Published compiler prerelease</a> · <code>{PIN}</code></p>
<div class="guide-links"><a href="{REPO}/blob/main/tutorials/alpha7-numerical/README.md">English guide</a>
<a lang="hi" href="{REPO}/blob/main/docs/hi/alpha7-numerical.md">हिन्दी गाइड</a></div></header>
<section class="run-panel"><h2>Run locally</h2>
<p>Use the published compiler or build its exact source. This website does not execute code in your browser.</p>
<pre><code>python scripts/verify_alpha7_numerical.py --compiler /path/to/scarp --compiler-source /path/to/pinned/scarp</code></pre>
<p>The native backend and token-cache controls are experimental Rust-host APIs, not Scarp source-language or CLI compilation features.</p></section>
<section aria-label="Numerical programming lessons"><div class="lab-grid">{cards}</div></section>
<section class="lesson-notes" lang="hi"><h2>हिन्दी में अभ्यास</h2>
<p>पहले परिणाम का अनुमान लगाएँ और फिर सही संस्करण वाले Scarp कम्पाइलर से अपने कंप्यूटर पर जाँचें।</p></section>
</main>"""
    return page_shell(INDEX, "Numerical programming workshop", "Three release-pinned numerical Scarp programs.", main, "project-layout")


def render_example(name, page_shell, rel, highlight_scarp):
    page = lesson_path(name)
    validate()
    title, summary, exercise, hindi, hindi_exercise = LESSONS[name]
    source = (WORKSHOP / (name + ".srp")).read_bytes().decode("utf-8")
    output = (WORKSHOP / (name + ".stdout")).read_bytes().decode("utf-8")
    local = "tutorials/alpha7-numerical/" + name
    course_url = REPO + "/blob/main/" + local

    def adjacent(offset, label):
        index = PROGRAMS.index(name) + offset
        if not 0 <= index < len(PROGRAMS):
            return ""
        target = PROGRAMS[index]
        return f'<a href="{escape(rel(page, lesson_path(target)))}">{label}: {escape(LESSONS[target][0])}</a>'

    main = f"""<main id="main-content" class="container-wide chapter-page project-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{escape(rel(page, 'index.html'))}">Home</a>
<span>/</span><a href="{escape(rel(page, INDEX))}">Numerical programming</a><span>/</span>
<span aria-current="page">{escape(title)}</span></nav>
<header class="page-heading"><p class="eyebrow">SCARP v{VERSION}</p><h1>{escape(title)}</h1>
<p class="lead">{escape(summary)}</p><p><a href="{RELEASE}">Published compiler</a> · <code>{PIN}</code></p>
<p>Original MIT-licensed course program; see the <a href="{COMPILER_EXAMPLES}">pinned compiler examples</a> for upstream context.</p></header>
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
<p>This website does not execute code in your browser. Compare local output against the fixture.</p></section>
<section class="lesson-notes" lang="hi"><h2>हिन्दी में समझें</h2><p>{escape(hindi)}</p>
<h3>अभ्यास</h3><p>{escape(hindi_exercise)}</p></section>
<nav class="step-nav" aria-label="Workshop lesson navigation">{adjacent(-1, "Previous")}
<a href="{escape(rel(page, INDEX))}">Workshop overview</a>{adjacent(1, "Next")}</nav></main>"""
    return page_shell(page, title, summary, main, "project-layout")
