# Static Scarp learning portal

This project is built by `python scripts/build_site.py` using the real numbered `.srp` files, their byte-exact `.stdout` fixtures and the English/Hindi chapter guides. No external frontend dependencies, services, CDNs, frameworks or fake browser execution are needed.

## Generated routes

| Route | Content |
| --- | --- |
| `index.html` | Homepage, six chapter cards and a client-side lesson finder |
| `chapters/NN-topic/index.html` | Chapter overview with runnable lesson links and an expandable three-question bilingual review using fixture-validated answers |
| `lessons/NN-topic/NN-example/index.html` | Dedicated lesson: source, output, local run commands, in-page English/Hindi teaching notes and exercises, previous/next navigation |
| `projects/index.html` | Source-backed English/Hindi guide to `create`, project `verify` and `launch` (available since alpha.4) |
| `projects/module-inspection/index.html` | Bilingual source-backed project inspection with alpha.6 symbol/reference navigation links, real imports and verified runtime output |
| `projects/source-navigation/index.html` | Bilingual clickable reference explorer: annotated source links checked against real alpha.6 compiler metadata, with a static fallback and exact stdout fixture |
| `labs/index.html` | Overview of six standalone verified bilingual coding labs |
| `labs/NN-topic/index.html` | Chapter lab with starter, exact goal output, hints, runnable solution and local run commands |
| `search-index.json` | Static English/Hindi metadata and exact `.srp` lesson source for local search; never external tracking |

A course with 52 runnable examples and six guided labs produces **69 HTML documents** (home, six chapters, fifty-two lessons, three project tutorials, the lab index and six lab detail pages). The URL paths are designed to work under the GitHub Pages project prefix `/scarp-by-example/` and from nested subdirectories. All local links are checked by the Python unit tests.

**Connected chapter paths:** Each of the six existing chapter pages includes a read → self-check → code sequence assembled from the verified lesson, checkpoint and lab inventories. A native, expandable **Practice this chapter** review on each overview reuses the same three fixture-validated bilingual checkpoints already available on the lesson pages (18 unique questions, not 18 additional ones). The three independent forms work offline after loading, and each includes a direct link to the original lesson and recorded output. With JavaScript disabled, the answer/explanation disclosures remain accessible. Neither quiz scores nor attempts are stored, uploaded, or counted as lesson completion. Every chapter overview now links directly to the previous and next chapter in the authoritative course order; first and last chapters show readable boundaries instead of dead links. The last lesson in each chapter provides a distinct review/lab/next-chapter handoff, while intermediate lessons keep their original previous/next navigation. These are static links derived from the actual lesson inventory, not JavaScript or estimated completion. Each quiz links to the stable `#checkpoint` anchor in its corresponding lesson, and the lab and lesson pages return to `#chapter-path`. The optional local progress count shown in the path measures only lessons learners explicitly marked complete. Neither quiz correctness nor external code execution is tracked or inferred. The feature works without JavaScript; only the optional lesson count uses browser storage.

**Mobile accessibility:** The header keeps one shared set of navigation destinations for both the desktop bar and the native `<details>`/`<summary>` mobile menu. The menu is keyboard- and touch-operable even with JavaScript disabled; with JavaScript it supports Escape to close and restore summary focus, and closes after a destination is selected. Mobile links use touch-sized targets rather than requiring horizontal navigation scrolling. The static HTML structure is regression-tested across homepage, chapter, lesson, lab, and project routes. The Pages workflow also runs dependency-free browser interaction tests.

## Browser behavior

The theme toggle stores a preference locally when available; the initial dark design works without JavaScript. Optional **learning progress** saves only the stable IDs of lessons you explicitly mark complete in the browser's `localStorage`; it does not send data to a server, require an account, or use cookies. Homepage progress, chapter totals, next-incomplete links and sidebar completion checks are computed from the generated lesson index. Progress can be exported as a small local JSON backup and restored on another device by importing that file; restore **merges** the recognized completed lesson IDs and does not remove existing progress. Corrupt, oversized, unsupported-version and unsafe backup contents are rejected. Export/import use browser APIs only: no server upload, analytics or account. Progress can still be cleared from the homepage after confirmation; cross-tab changes are reflected with the storage event. No progress UI appears if storage or the lesson index is unavailable. Every lesson also offers an optional **Predict this output** activity: learners can hide the displayed verified stdout, type a prediction, check it against the displayed fixture text, and reveal the original for comparison. Wrong guesses show the first mismatching line, differences in line counts, or a whitespace/capitalization hint without exposing the actual output until the learner explicitly reveals it. Predictions are never stored, uploaded, or executed. The original output remains visible without JavaScript; browser comparison ignores one final newline and normalizes textarea line endings, so it is not a byte-for-byte compiler test. Eighteen optional bilingual multiple-choice checkpoints (three per chapter) are also progressive enhancements; chapter cards and lesson search label their availability. each correct answer is validated against an exact checked-in compiler output line during site generation. Checkpoint scores are not persisted, and the browser never executes Scarp. Without JavaScript, each checkpoint provides a readable answer-and-explanation disclosure. The language switch also updates its questions and answer choices. Search, copy-code and the English/हिन्दी explanation switch are progressive enhancements. With JavaScript disabled, both languages remain readable on each lesson page. Every lesson and chapter remains navigable without JavaScript, and the original GitHub source/fixture links are always present.

Displayed source is escaped as text, not evaluated. Control-character output such as a literal carriage return is rendered visibly as `\\r`, without rewriting the original fixture. No code is executed in the browser.

The project page reads an actual checked-in `Scarp.project`, `.srp` file and exact stdout fixture. It is not counted as a numbered lesson, and includes no simulated browser execution.

The website renders English descriptions and documented expected results directly from the chapter tables. Hindi notes and practice questions are extracted from the six authoritative Hindi Markdown chapter guides. The generator rejects missing, duplicated, misnumbered or wrongly linked notes, rather than publishing partial translations. Original chapter guides remain linked for context. Scarp is prerelease software; all examples are pinned to the exact compiler commit in `docs/compiler-target.json`.

Guided labs are generated from checked-in `labs/NN-topic/` sources and `docs/guided-labs.json` bilingual teaching text. Each starter and solution must pass the actual pinned Scarp compiler; the starter intentionally produces a different result from the exact reference fixture. The pages use native HTML hint/answer disclosures, do not execute Scarp in the browser, and do not save or upload attempts. See [the lab contributor guide](../docs/guided-labs.md).

## Build and test

```sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
node --check site/progress.js
node --check site/checkpoint.js
node --check site/output-practice.js
node --test site/test_output_practice.cjs
node --test site/test_progress.cjs site/test_progress_dom.cjs site/test_checkpoint.cjs
```

The GitHub Pages workflow first compiles and validates every real Scarp lesson and checks the CLI, then generates the static site. Pull requests build the site but do not deploy; merged `main` changes deploy using GitHub Actions. Git tracks source files under `site/` and `scripts/`, not generated `dist/`.

**Source-aware search:** Homepage search matches verified source as well as English/Hindi titles and descriptions, with an optional chapter filter. Every query word must occur in the lesson; title hits rank ahead of source-only hits and original lesson order breaks ties. The index is loaded from this site only when a learner searches or selects a chapter, and is neither uploaded nor stored. Source-only hits are labeled. Every result with source shows a compact, line-numbered snippet from the actual checked-in `.srp` program; the selected line favors query terms, falls back to the first nonblank line for metadata-only searches, and limits very long lines to 140 source characters plus ellipses. The browser inserts source as text rather than HTML, never executing it. All chapter and lesson links remain available without JavaScript.

**Shareable searches and keyboard access:** On the home page, press `/` outside an editable field to focus lesson search; press `Escape` inside the search field to clear both filters. When a search or chapter filter is active, **Share this search** is a normal link: right-click or long-press to copy its destination, or open it to test. Shared links take the form `index.html?q=funcra&chapter=03-functions#search-area`, restore only valid chapter options, and require no account. Ordinary typing does **not** change browser history or the address bar. The search text is visible in explicitly shared URLs and can be included in normal page-request logs when someone opens the link, so do not put secrets in shared searches. The browser never runs the Scarp source. Run `node --test site/test_search_core.cjs site/test_search_dom.cjs` for relevance ranking, filtering, deep-link restoration, keyboard shortcuts, browser DOM, stale-request and safe-link tests.
