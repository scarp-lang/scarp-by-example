# Scarp by Example

**Learn Scarp through practical, runnable code examples.**

**[Browse the learning catalog](https://scarp-lang.github.io/scarp-by-example/)** · [Scarp compiler](https://github.com/scarp-lang/scarp) · [Official documentation](https://github.com/scarp-lang/scarp-docs) · [Project website](https://scarp-lang.github.io/) · [Contribute](CONTRIBUTING.md)

Scarp by Example is the hands-on companion to the Scarp programming language. Lessons are arranged from first program to numeric and AI-oriented programming. Every runnable lesson includes a Scarp `.srp` source file, an exact `.stdout` fixture, and bilingual teaching notes shown directly on the lesson page from the existing source-linked chapter guides.

> **Development-stage language:** Scarp syntax can change between prereleases. This repository tests **Scarp v0.0.6-alpha.15 at exact source commit `a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281`** for CI. Do not assume that a lesson compatible with compiler `main` will run unchanged on an older download. See [compatibility](docs/compatibility.md).

## Online lessons

The [learning portal](https://scarp-lang.github.io/scarp-by-example/) now provides **a dedicated URL for every runnable lesson**, plus six chapter overview pages, source code, byte-exact expected output, previous/next lesson navigation, direct chapter-to-chapter journeys and last-lesson lab handoffs, English/Hindi explanations with exercises, bilingual source-aware lesson search with chapter filters and shareable links and compiler-source previews, optional **on-device lesson completion and resume**, and dark/light themes. It remains a static GitHub Pages site: Scarp code executes locally with the compiler, **not** in the browser. The [Pages workflow](.github/workflows/pages.yml) validates all lessons before publishing.

**Project inspection (introduced in alpha.5):** The new [English](docs/project-inspection.md) and [हिन्दी](docs/hi/project-inspection.md) tutorials demonstrate a real two-module project. The command `scarp inspect modules --json DIRECTORY` reports the statically checked module graph without executing runtime statements. The independent CLI tests compare project and entrypoint inventories. The optional [online tutorial](https://scarp-lang.github.io/scarp-by-example/projects/module-inspection/) makes the source and verified output visible. The experimental C11 emitter is **Rust embedding-only**, not a `scarp compile` CLI command.

**Scarp-first CLI quickstart:** [English guide](docs/cli-quickstart.md) · [हिन्दी गाइड](docs/hi/cli-quickstart.md). Static `verify` is different from the older `check`, which can evaluate runtime expressions.

**Local progress:** On a lesson page, choose **Mark lesson complete** to save that lesson's ID in this browser only. The homepage shows overall completion and lets you resume the next unfinished lesson, **export a JSON backup**, **import a backup to merge progress** across browsers or devices, or clear saved progress. Backups contain only completed lesson IDs and are processed locally without upload, account or tracking. Import rejects corrupt and oversized files and never deletes existing completions. On browsers without local storage, normal lesson navigation still works.

**Interactive checkpoints and chapter review:** Eighteen carefully reviewed lessons (three in each chapter) have optional English/Hindi multiple-choice questions with immediate feedback and source-backed explanations. Each chapter overview also has an expandable **Practice this chapter** section reusing those same three verified questions in independent forms, so learners can review without changing pages. Every review question links to its original `.srp` lesson and recorded output; the chapter review introduces no new or unverified questions. Chapter cards and lesson search identify available checkpoints. Questions are checked against the lessons' real `.stdout` fixtures at build time. They **do not execute Scarp in the browser**, store quiz results, or replace each lesson's independent practical exercise. If JavaScript is unavailable, the same answers remain readable through a disclosure control. See [question authoring rules](docs/practice-checkpoints.md).

**Connected learning path:** Each chapter now offers a three-step sequence: **read** its source-verified lessons, **check** understanding with three exact-output-backed English/Hindi questions, then **build** a real Scarp program in that chapter's local coding lab. Chapter, lesson, checkpoint and lab pages link back to each other. Previously saved lesson completions display in the path, but the site deliberately does not claim to grade quizzes or locally executed programs. [Start with the Basics learning path](https://scarp-lang.github.io/scarp-by-example/chapters/01-basics/#chapter-path).

**Guided coding labs:** Six **English/Hindi compiler-verified core challenges** (one per chapter) have runnable starter programs, exact target output, hints, and reference solutions. Control flow also offers an **optional, independently verified stretch challenge** for scanning integer readings and stopping at the first match. Every starter runs but differs from its solution; each solution matches an exact output fixture under the pinned compiler. **A second optional stretch challenge** in the AI foundations lab teaches alpha.3 `topk`, `softmax_temp` and `logsoftmax_temp`, with bilingual guidance and an upstream exact-output fixture. Practice locally; the website neither runs Scarp nor collects your attempts. [Open the coding lab index](https://scarp-lang.github.io/scarp-by-example/labs/) or [read the workflow](docs/guided-labs.md).

**Mobile and keyboard navigation:** On narrow screens, the site uses an accessible **Menu** disclosure rather than a horizontally scrolling header. It works without JavaScript, and keyboard users can close it with Escape and return focus to the menu trigger. Chapter, search, project, lab, compiler and GitHub destinations stay consistent across desktop and mobile. The skip-to-content link remains available on every page.

**Website navigation:** Open a chapter from the home page, then select an example. For a direct link, use a path like [01 · Hello](https://scarp-lang.github.io/scarp-by-example/lessons/01-basics/01-hello/). The same source and output fixtures remain in Git; [site development notes](site/README.md) document the generated routes.

## Start here

1. Install [Rust and Cargo](https://www.rust-lang.org/tools/install) to run the current compiler source, or select a supported binary from [Scarp prereleases](https://github.com/scarp-lang/scarp/releases).
2. Clone the [Scarp repository](https://github.com/scarp-lang/scarp), check out exact tested commit `a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281`, then build it with `cargo build --locked --offline`. Confirm the current executable version with `target/debug/scarp version` (Windows: `target\\debug\\scarp.exe version`).
3. Clone this repository. From your Scarp checkout, run the binary on a lesson, using the **absolute path** to its `.srp` file: `./target/debug/scarp exec /path/to/scarp-by-example/examples/01-basics/01-hello.srp`.
4. Compare output with the lesson's adjacent `.stdout` file. On Windows, use `target\\debug\\scarp.exe`.

For modules, the compiler resolves imports relative to the lesson file. Keep the companion `_support` directory with that lesson.

## Project workflow (available since alpha.4)

Learn to create, statically verify, and launch a real offline Scarp project. Follow the [English project tutorial](docs/project-workflow.md) or the [हिन्दी प्रोजेक्ट गाइड](docs/hi/project-workflow.md); the [checked-in sample project](tutorials/first-project/Scarp.project) runs with the official interpreter. Project commands are **not** native compilation or package publishing, and the sample is kept separate from the 52 numbered lessons.

**Source-navigation workshop (now with an interactive source explorer):** Trace two separately scoped bindings and named arguments through a real imported module. [Open the bilingual workshop](https://scarp-lang.github.io/scarp-by-example/projects/source-navigation/) or [inspect the original Scarp project](tutorials/source-navigation/README.md). Click a declaration or use to highlight all its compiler-verified links across both `.srp` files, with English/Hindi explanations and working no-JavaScript anchor links. The teaching map is checked against the pinned compiler on Linux, macOS and Windows; no browser execution or live LSP is implied.

**New in compiler alpha.6:** A [root mean square lesson](examples/04-collections/12-root-mean-square.srp) demonstrates numerically stable signal magnitude. The [English source navigation guide](docs/source-navigation.md) and [हिन्दी मार्गदर्शिका](docs/hi/source-navigation.md) explain read-only `inspect symbols` and `inspect references`; neither command executes the program.

**New in published compiler alpha.4:** Scarp adds bounded `sample_area`, `sample_cumulative_area`, `sample_slopes` and `cosine_similarity` vector built-ins, plus a limited Rust-host ELF64 relocatable object API. These historical numerical features remain available in the active alpha.15 compiler; examples must still pass exact-output verification before inclusion in the numbered course. The ELF API is **not** a `scarp compile` CLI or general native executable support. The historical alpha.13 source pin is independently checked in multi-platform CI.

**New in published compiler alpha.3:** [Practice deterministic Top-K and temperature-controlled probabilities](https://scarp-lang.github.io/scarp-by-example/labs/06-ai-foundations/#stretch-challenge) in the optional AI lab. This is score ranking, not random sampling, model training or a GPU runtime.

## Modern collections and checked results (published alpha.13)

[Explore the alpha.13 compatibility workshop on the learning website](https://scarp-lang.github.io/scarp-by-example/workshops/modern-collections/) ([source and bilingual notes](tutorials/modern-collections/README.md)) for eight executable **upstream source-and-output copies**: typed lists, persistent list updates, deterministic maps, persistent map updates, canonical key/value projections, checked Option/Result matches, explicit `?` propagation, and aggregate snapshot behavior. Its dedicated verifier checks **the published annotated-tag commit, executable version, unchanged upstream fixtures, static verification and byte-exact stdout** on Linux, Windows and macOS. The existing 52 numbered lessons remain separate and retain their historical fixtures.

The collections and `option<T>` / `result<T,E>` language features arrived in alpha.12. Alpha.13 primarily improves cache management, editor-host generation handling, propagation payload reuse and resource checks, rather than adding new collection syntax. Cache and editor features are **Rust embedding APIs**, not Scarp calls, native executables or browser execution. Previously opened alpha.10/alpha.11 feature pull requests are independent and are not silently merged by this compatibility change.

## Structured patterns and deterministic maps (published alpha.14)

[Read the alpha.14 English/Hindi workshop](tutorials/structured-patterns/README.md) to run two **exact upstream source-and-output pairs**: nested record/tuple destructuring and canonical map key/value projections across persistent updates. The independently pinned verifier checks published compiler Git objects and the executable version, then runs static verification and byte-exact output comparisons. A separate [Linux/Windows/macOS workflow](.github/workflows/alpha14-patterns.yml) also rechecks the original 52 numbered lessons, guided labs and CLI against alpha.14.

**New diagnostic repair lab:** [Nine syntax-error exercises](tutorials/structured-patterns/README.md#diagnose-and-fix-invalid-patterns) pair real alpha.14 parser errors with working corrected code, exact E0004 diagnostic spans and recorded stdout. The new dedicated page is part of the static website, not a browser interpreter.

**Compatibility status:** [PR #76](https://github.com/scarp-lang/scarp-by-example/pull/76) merged the active course's alpha.15 compiler pin after Linux/Windows/macOS verification. The alpha.13 and alpha.14 workshops retain independent immutable compiler pins. No numbered lesson output fixtures are rewritten and no stable or native-compiled release is implied.

## Alpha.15 compiler boundaries

[Read the source-backed alpha.15 limits tutorial](tutorials/alpha15-limits/README.md) ([हिन्दी](docs/hi/alpha15-limits.md)). The new independent verification gate tests the **1 MiB source-inspection boundary** and the **work-step budget for UTF-8 string equality** using the exact published compiler. It does not add an artificial browser interpreter or renumber the pre-existing core lessons. The additional while-foundations lessons are numbered within chapter 02.

## Course

| Section | Topics | Status |
| --- | --- | --- |
| [01 · Basics](examples/01-basics/README.md) | Output, bindings, scopes, Unicode construction, conversions, comments and bitwise operations | Runnable lessons |
| [02 · Control flow](examples/02-control-flow/README.md) | Conditions, while, counted repeat | Runnable lessons |
| [03 · Functions](examples/03-functions/README.md) | Typed functions, recursion, executable contracts and accumulator recursion | Runnable lessons |
| [04 · Numerical collections](examples/04-collections/README.md) | Numeric vectors, norms, refinement, windows and numeric kernels | Runnable lessons |
| [05 · Modules](examples/05-modules/README.md) | Imports, exported definitions, private helpers, numeric collections and inspectable signatures | Runnable lessons |
| [06 · AI foundations](examples/06-ai-foundations/README.md) | Matrix inference, composition, numerical probabilities and explicit gradients | Runnable lessons |
| [Future topics](docs/roadmap.md) | General exceptions, sets, async, networking and agents | Not taught as implemented |

**Status is not a promise of stable semantics.** Each section records its upstream example provenance and current CI target. Advanced examples represent numeric building blocks, **not** an integrated model-training framework.

## Verification

The [example verification workflow](.github/workflows/examples.yml) builds [Scarp v0.0.6-alpha.15](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.15) from its immutable source commit of the official compiler and performs static `scarp verify` then byte-exact `scarp exec` on every lesson on GitHub-hosted runners. An independent CLI smoke test checks legacy commands, real project creation/launch and **alpha.5 project-directory module inspection**, including file/project inventory equivalence, static-only behavior and invalid-manifest handling. Run the same checks locally:

```sh
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp/target/debug/scarp
```

No network calls or external Python packages are required by the verifier. A lesson without a matching expected-output fixture is rejected. See [compatibility policy](docs/compatibility.md).

## Translations and contributions

English remains the canonical source language. **[Read all 55 lessons in Hindi](docs/hi/README.md)** through companion guides for all six chapters. Each translated explanation links to the original `.srp` and exact `.stdout` fixture, and is displayed directly on its corresponding lesson page using a language toggle. Neither Scarp syntax nor verified outputs are translated. See [translation guidelines](docs/translations/README.md), [contributing](CONTRIBUTING.md), and the [lesson format](docs/lesson-format.md).

## Support Scarp learning resources

The lessons and runnable examples are free to use. To help maintain the Scarp ecosystem, [support development through GitHub Sponsors](https://github.com/sponsors/sanskarIN). Contributions are optional and do not affect access to lessons.

**License:** [MIT](LICENSE) for this learning repository. Some compiler-source examples originated in the separately licensed [Scarp compiler repository](https://github.com/scarp-lang/scarp); preserve upstream attribution and applicable licensing when reusing material. No stable Scarp by Example release is announced.
