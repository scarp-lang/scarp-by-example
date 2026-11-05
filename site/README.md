# Static Scarp learning portal

This project is built by `python scripts/build_site.py` using the real numbered `.srp` files, their byte-exact `.stdout` fixtures and the English/Hindi chapter guides. No external frontend dependencies, services, CDNs, frameworks or fake browser execution are needed.

## Generated routes

| Route | Content |
| --- | --- |
| `index.html` | Homepage, six chapter cards and a client-side lesson finder |
| `chapters/NN-topic/index.html` | Chapter overview with links to its runnable lessons |
| `lessons/NN-topic/NN-example/index.html` | Dedicated lesson: source, output, local run commands, in-page English/Hindi teaching notes and exercises, previous/next navigation |
| `projects/index.html` | Source-backed English/Hindi guide to `create`, project `verify` and `launch` (available since alpha.4) |
| `projects/module-inspection/index.html` | Bilingual source-backed project inspection with alpha.6 symbol/reference navigation links, real imports and verified runtime output |
| `projects/source-navigation/index.html` | Bilingual clickable reference explorer: annotated source links checked against real alpha.6 compiler metadata, with a static fallback and exact stdout fixture |
| `labs/index.html` | Overview of six standalone verified bilingual coding labs |
| `labs/NN-topic/index.html` | Chapter lab with starter, exact goal output, hints, runnable solution and local run commands |
| `search-index.json` | Static English/Hindi lesson metadata for local search; never external tracking |

A course with 51 runnable examples and six guided labs produces **68 HTML documents** (home, six chapters, fifty-one lessons, three project tutorials, the lab index and six lab detail pages). The URL paths are designed to work under the GitHub Pages project prefix `/scarp-by-example/` and from nested subdirectories. All local links are checked by the Python unit tests.

**Connected chapter paths:** Each of the six existing chapter pages includes a read → self-check → code sequence assembled from the verified lesson, checkpoint and lab inventories. Each quiz links to the stable `#checkpoint` anchor in its corresponding lesson, and the lab and lesson pages return to `#chapter-path`. The optional local progress count shown in the path measures only lessons learners explicitly marked complete. Neither quiz correctness nor external code execution is tracked or inferred. The feature works without JavaScript; only the optional lesson count uses browser storage.

**Mobile accessibility:** The header keeps one shared set of navigation destinations for both the desktop bar and the native `<details>`/`<summary>` mobile menu. The menu is keyboard- and touch-operable even with JavaScript disabled; with JavaScript it supports Escape to close and restore summary focus, and closes after a destination is selected. Mobile links use touch-sized targets rather than requiring horizontal navigation scrolling. The static HTML structure is regression-tested across homepage, chapter, lesson, lab, and project routes. The Pages workflow also runs dependency-free browser interaction tests.

## Browser behavior

The theme toggle stores a preference locally when available; the initial dark design works without JavaScript. Optional **learning progress** saves only the stable IDs of lessons you explicitly mark complete in the browser's `localStorage`; it does not send data to a server, require an account, or use cookies. Homepage progress, chapter totals, next-incomplete links and sidebar completion checks are computed from the generated lesson index. Progress can be exported as a small local JSON backup and restored on another device by importing that file; restore **merges** the recognized completed lesson IDs and does not remove existing progress. Corrupt, oversized, unsupported-version and unsafe backup contents are rejected. Export/import use browser APIs only: no server upload, analytics or account. Progress can still be cleared from the homepage after confirmation; cross-tab changes are reflected with the storage event. No progress UI appears if storage or the lesson index is unavailable. Eighteen optional bilingual multiple-choice checkpoints (three per chapter) are also progressive enhancements; chapter cards and lesson search label their availability. each correct answer is validated against an exact checked-in compiler output line during site generation. Checkpoint scores are not persisted, and the browser never executes Scarp. Without JavaScript, each checkpoint provides a readable answer-and-explanation disclosure. The language switch also updates its questions and answer choices. Search, copy-code and the English/हिन्दी explanation switch are progressive enhancements. With JavaScript disabled, both languages remain readable on each lesson page. Every lesson and chapter remains navigable without JavaScript, and the original GitHub source/fixture links are always present.

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
node --test site/test_progress.cjs site/test_progress_dom.cjs site/test_checkpoint.cjs
```

The GitHub Pages workflow first compiles and validates every real Scarp lesson and checks the CLI, then generates the static site. Pull requests build the site but do not deploy; merged `main` changes deploy using GitHub Actions. Git tracks source files under `site/` and `scripts/`, not generated `dist/`.
