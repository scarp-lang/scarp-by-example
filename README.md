# Scarp by Example

**Learn Scarp through practical, runnable code examples.**

**[Browse the learning catalog](https://scarp-lang.github.io/scarp-by-example/)** · [Scarp compiler](https://github.com/scarp-lang/scarp) · [Official documentation](https://github.com/scarp-lang/scarp-docs) · [Project website](https://scarp-lang.github.io/) · [Contribute](CONTRIBUTING.md)

Scarp by Example is the hands-on companion to the Scarp programming language. Lessons are arranged from first program to numeric and AI-oriented programming. Every runnable lesson includes a Scarp `.srp` source file, an exact `.stdout` fixture, and bilingual teaching notes shown directly on the lesson page from the existing source-linked chapter guides.

> **Development-stage language:** Scarp syntax can change between prereleases. This repository tests **Scarp v0.0.5-alpha.4 at exact source commit `7914132`** for CI. Do not assume that a lesson compatible with compiler `main` will run unchanged on an older download. See [compatibility](docs/compatibility.md).

## Online lessons

The [learning portal](https://scarp-lang.github.io/scarp-by-example/) now provides **a dedicated URL for every runnable lesson**, plus six chapter overview pages, source code, byte-exact expected output, previous/next navigation, English/Hindi explanations with exercises, bilingual lesson search, optional **on-device lesson completion and resume**, and dark/light themes. It remains a static GitHub Pages site: Scarp code executes locally with the compiler, **not** in the browser. The [Pages workflow](.github/workflows/pages.yml) validates all lessons before publishing.

**Scarp-first CLI quickstart:** [English guide](docs/cli-quickstart.md) · [हिन्दी गाइड](docs/hi/cli-quickstart.md). Static `verify` is different from the older `check`, which can evaluate runtime expressions.

**Local progress:** On a lesson page, choose **Mark lesson complete** to save that lesson's ID in this browser only. The homepage shows overall completion and lets you resume the next unfinished lesson or clear your saved progress. Nothing is sent to the server, and no account is needed. On browsers without local storage, normal lesson navigation still works.

**Website navigation:** Open a chapter from the home page, then select an example. For a direct link, use a path like [01 · Hello](https://scarp-lang.github.io/scarp-by-example/lessons/01-basics/01-hello/). The same source and output fixtures remain in Git; [site development notes](site/README.md) document the generated routes.

## Start here

1. Install [Rust and Cargo](https://www.rust-lang.org/tools/install) to run the current compiler source, or select a supported binary from [Scarp prereleases](https://github.com/scarp-lang/scarp/releases).
2. Clone the [Scarp repository](https://github.com/scarp-lang/scarp), check out exact tested commit `79141329176f5dce51457e90a6652902f6432135`, then build it with `cargo build --locked --offline`. Confirm `target/debug/scarp --version` reports `scarp 0.0.5-alpha.4`.
3. Clone this repository. From your Scarp checkout, run the binary on a lesson, using the **absolute path** to its `.srp` file: `./target/debug/scarp exec /path/to/scarp-by-example/examples/01-basics/01-hello.srp`.
4. Compare output with the lesson's adjacent `.stdout` file. On Windows, use `target\\debug\\scarp.exe`.

For modules, the compiler resolves imports relative to the lesson file. Keep the companion `_support` directory with that lesson.

## Project workflow (published alpha.4)

Learn to create, statically verify, and launch a real offline Scarp project. Follow the [English project tutorial](docs/project-workflow.md) or the [हिन्दी प्रोजेक्ट गाइड](docs/hi/project-workflow.md); the [checked-in sample project](tutorials/first-project/Scarp.project) runs with the official interpreter. Project commands are **not** native compilation or package publishing, and the sample is kept separate from the 50 numbered lessons.

## Course

| Section | Topics | Status |
| --- | --- | --- |
| [01 · Basics](examples/01-basics/README.md) | Output, bindings, scopes, Unicode construction, conversions, comments and bitwise operations | Runnable lessons |
| [02 · Control flow](examples/02-control-flow/README.md) | Conditions, while, counted repeat | Runnable lessons |
| [03 · Functions](examples/03-functions/README.md) | Typed functions, recursion, executable contracts and accumulator recursion | Runnable lessons |
| [04 · Numerical collections](examples/04-collections/README.md) | Numeric vectors, norms, refinement, windows and numeric kernels | Runnable lessons |
| [05 · Modules](examples/05-modules/README.md) | Imports, exported definitions, private helpers, numeric collections and inspectable signatures | Runnable lessons |
| [06 · AI foundations](examples/06-ai-foundations/README.md) | Matrix inference, composition, numerical probabilities and explicit gradients | Runnable lessons |
| [Future topics](docs/roadmap.md) | Structured errors, general collections, async, networking, agents | Not taught as implemented |

**Status is not a promise of stable semantics.** Each section records its upstream example provenance and current CI target. Advanced examples represent numeric building blocks, **not** an integrated model-training framework.

## Verification

The [example verification workflow](.github/workflows/examples.yml) builds [Scarp v0.0.5-alpha.4](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.4) from its immutable source commit of the official compiler and performs static `scarp verify` then byte-exact `scarp exec` on every lesson on GitHub-hosted runners. An independent CLI smoke test checks command inspection, legacy migration and real alpha.4 project creation, static verification, launching and invalid-manifest handling. Run the same checks locally:

```sh
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp/target/debug/scarp
```

No network calls or external Python packages are required by the verifier. A lesson without a matching expected-output fixture is rejected. See [compatibility policy](docs/compatibility.md).

## Translations and contributions

English remains the canonical source language. **[Read all 50 lessons in Hindi](docs/hi/README.md)** through companion guides for all six chapters. Each translated explanation links to the original `.srp` and exact `.stdout` fixture, and is displayed directly on its corresponding lesson page using a language toggle. Neither Scarp syntax nor verified outputs are translated. See [translation guidelines](docs/translations/README.md), [contributing](CONTRIBUTING.md), and the [lesson format](docs/lesson-format.md).

**License:** [MIT](LICENSE) for this learning repository. Some compiler-source examples originated in the separately licensed [Scarp compiler repository](https://github.com/scarp-lang/scarp); preserve upstream attribution and applicable licensing when reusing material. No stable Scarp by Example release is announced.
