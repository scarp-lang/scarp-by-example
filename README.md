# Scarp by Example

**Learn Scarp through practical, runnable code examples.**

**[Browse the learning catalog](https://scarp-lang.github.io/scarp-by-example/)** · [Scarp compiler](https://github.com/scarp-lang/scarp) · [Official documentation](https://github.com/scarp-lang/scarp-docs) · [Project website](https://scarp-lang.github.io/) · [Contribute](CONTRIBUTING.md)

Scarp by Example is the hands-on companion to the Scarp programming language. Lessons are arranged from first program to numeric and AI-oriented programming. Every runnable lesson includes a Scarp `.srp` source file, an exact `.stdout` output fixture and a focused explanation in its section's guide.

> **Development-stage language:** Scarp syntax can change between prereleases. This repository follows a **source-pinned compiler checkout** for CI. Do not assume that a lesson compatible with compiler `main` will run unchanged on an older download. See [compatibility](docs/compatibility.md).

## Online lessons

The [searchable lesson catalog](https://scarp-lang.github.io/scarp-by-example/) presents the same source-backed examples and expected output fixtures in a readable website. Scarp code executes locally with the compiler, **not** in the browser. The [Pages workflow](.github/workflows/pages.yml) validates the full lesson suite before publishing.

## Start here

1. Install [Rust and Cargo](https://www.rust-lang.org/tools/install) to run the current compiler source, or select a supported binary from [Scarp prereleases](https://github.com/scarp-lang/scarp/releases).
2. Clone the [Scarp repository](https://github.com/scarp-lang/scarp) and build it with `cargo build --locked`. Confirm `target/debug/scarp --version`.
3. Clone this repository. From your Scarp checkout, run the binary on a lesson, using the **absolute path** to its `.srp` file: `./target/debug/scarp run /path/to/scarp-by-example/examples/01-basics/01-hello.srp`.
4. Compare output with the lesson's adjacent `.stdout` file. On Windows, use `target\\debug\\scarp.exe`.

For modules, the compiler resolves imports relative to the lesson file. Keep the companion `_support` directory with that lesson.

## Course

| Section | Topics | Status |
| --- | --- | --- |
| [01 · Basics](examples/01-basics/README.md) | Output, bindings, scopes, Unicode and conversions | Runnable lessons |
| [02 · Control flow](examples/02-control-flow/README.md) | Conditions, while, counted repeat | Runnable lessons |
| [03 · Functions](examples/03-functions/README.md) | Typed functions, recursion, executable contracts | Runnable lessons |
| [04 · Numerical collections](examples/04-collections/README.md) | Numeric vectors, windows, typed declarations | Runnable lessons |
| [05 · Modules](examples/05-modules/README.md) | Imports and exported definitions, constants | Runnable lessons |
| [06 · AI foundations](examples/06-ai-foundations/README.md) | Matrix inference, explicit loss gradients | Runnable lessons |
| [Future topics](docs/roadmap.md) | Structured errors, general collections, async, networking, agents | Not taught as implemented |

**Status is not a promise of stable semantics.** Each section records its upstream example provenance and current CI target. Advanced examples represent numeric building blocks, **not** an integrated model-training framework.

## Verification

The [example verification workflow](.github/workflows/examples.yml) builds a specific commit of the official compiler and checks each lesson's compilation and exact stdout on GitHub-hosted runners. Run the same checks locally:

```sh
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp/target/debug/scarp
```

No network calls or external Python packages are required by the verifier. A lesson without a matching expected-output fixture is rejected. See [compatibility policy](docs/compatibility.md).

## Translations and contributions

English remains the canonical source language. **[Read all 28 lessons in Hindi](docs/hi/README.md)** through companion guides for all six chapters. Each translated explanation links to the original `.srp` and exact `.stdout` fixture; neither the Scarp language syntax nor the verified outputs are translated. See [translation guidelines](docs/translations/README.md), [contributing](CONTRIBUTING.md), and the [lesson format](docs/lesson-format.md).

**License:** [MIT](LICENSE) for this learning repository. Some compiler-source examples originated in the separately licensed [Scarp compiler repository](https://github.com/scarp-lang/scarp); preserve upstream attribution and applicable licensing when reusing material. No stable Scarp by Example release is announced.
