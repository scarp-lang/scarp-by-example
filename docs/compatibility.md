# Compiler compatibility policy

Scarp is a development-stage programming language. This learning repository selects an **immutable, publicly published compiler source commit**; a tag alone does not prove compatibility without real operating-system tests.

## Proposed active target: Scarp alpha.14

| Property | Target |
| --- | --- |
| Published release | [Scarp v0.0.6-alpha.14](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.14), 18 November 2026 (prerelease) |
| Exact annotated-tag source | [`43627b74af5fccccc5e233e98207413983ebafc1`](https://github.com/scarp-lang/scarp/commit/43627b74af5fccccc5e233e98207413983ebafc1) |
| Machine-readable target | [`docs/compiler-target.json`](compiler-target.json) |
| Main verification | [Linux, Windows and macOS source/output jobs](../.github/workflows/examples.yml), [Pages/catalog build](../.github/workflows/pages.yml), compiler-target tests and release-pinned workshop fidelity |
| Previous main target | [Scarp v0.0.6-alpha.13](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.13), `e755fda37cdaeed29434e848cb5dd41f2f2e7eb2` |

**Integration status:** This stacked pull request proposes promoting alpha.14. It is **not** a claim that the default branch already uses alpha.14, that production Pages was redeployed, or that a new Scarp by Example release was published. The existing 52 numbered lessons and their exact output fixtures are preserved.

## Source-language support and limits

- Scarp's original numbered course covers bindings, output, control flow, typed functions, numerical operations, imports, project commands, static inspection and AI-oriented numerical primitives.
- The alpha.9 [historical BigInt workshop](../tutorials/exact-bigint/README.md) remains frozen to its own published compiler.
- Exact decimal arithmetic arrived in alpha.11; the existing separately proposed Decimal feature workshop has its own release pin.
- Alpha.12 introduced bounded immutable typed lists and maps, concrete Option/Result variants, checked matching and restricted `?` propagation on immutable bind initializers in compatible named functions.
- Alpha.13 improved propagation/resource behavior and Rust embedding cache APIs. The eight-program [modern collections workshop](../tutorials/modern-collections/README.md) deliberately stays pinned to **published alpha.13**, including all 16 exact upstream source/output files.
- Alpha.14 improves parsing diagnostics for nested tuple/array/record binding patterns, tests deterministic map projections, and extends Rust-host-only editor caches and checked ELF64 integer object emission. The [alpha.14 structured-patterns workshop](../tutorials/structured-patterns/README.md) shows two original source-and-output pairs on separate bilingual website pages. An additional nine-case diagnostic repair lab checks the published parser's E0004 JSON messages and UTF-8 byte spans, then verifies each repaired program and exact output.

**Scope:** The active CLI runs programs with the local interpreter. Rust embedding interfaces for native C11/ELF64 object generation are experimental and restricted: no general `scarp compile` CLI, unrestricted native compilation, browser interpreter, networking, async runtime, GPU backend or automatic differentiation is implied.

## Build the exact active compiler

The `v0.0.6-alpha.14` annotated tag dereferences to **`43627b74af5fccccc5e233e98207413983ebafc1`**. Both main CI workflows pin this exact source commit at `.compiler`. Each additionally checks out alpha.13 as `.compiler-alpha13` solely for its historical workshop; those copies are not interchangeable.

~~~sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout 43627b74af5fccccc5e233e98207413983ebafc1
cargo build --locked --offline
./target/debug/scarp version
~~~

On Windows use `target\debug\scarp.exe`. In the learning repository, pass the absolute path to the built compiler:

~~~sh
python scripts/verify_examples.py --compiler /absolute/path/to/scarp
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
python scripts/verify_cli.py --compiler /absolute/path/to/scarp
python scripts/verify_alpha14_patterns.py --compiler /absolute/path/to/scarp --compiler-source /path/to/alpha14/compiler/git/checkout
python scripts/verify_alpha14_diagnostics.py --compiler /absolute/path/to/scarp --compiler-source /path/to/alpha14/compiler/git/checkout
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
~~~

To verify the **historical** alpha.13 workshop, separately build the exact alpha.13 source (`e755fda37cdaeed29434e848cb5dd41f2f2e7eb2`) and run:

~~~sh
python scripts/verify_alpha13_compat.py --compiler /path/to/alpha13/scarp --compiler-source /path/to/alpha13/compiler/git/checkout
~~~

Historical programs and fixtures are compared to their original committed sources and executed against the corresponding release. CLI version, silent static verification and byte-exact UTF-8 stdout are checked. Python-only tests do not replace running the actual compiler.

## Upgrade policy

1. Resolve an already-published compiler tag to the full, immutable source commit and verify the published artifacts.
2. Update `compiler-target.json`, both active CI checkouts, human-readable release labels, and site-generated provenance together.
3. Keep all historical workshop compiler checkouts separate. Never silently repin them to the active compiler.
4. Run exact program output, guided labs, CLI/project smoke tests, bilingual HTML generation, link checks and regression tests on Linux, macOS and Windows.
5. Require successful checks and maintainer review before merging. Only a main-branch workflow may deploy the verified course website; a PR itself does not publish anything.

Scarp syntax remains unstable between prereleases. See the [compiler releases archive](https://github.com/scarp-lang/scarp/releases).
