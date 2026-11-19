# Compiler compatibility policy

Scarp is a development-stage programming language. This learning repository selects an **immutable, publicly published compiler source commit**; a tag alone does not prove compatibility without real operating-system tests.

## Proposed active target: Scarp alpha.15

| Property | Target |
| --- | --- |
| Published release | [Scarp v0.0.6-alpha.15](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.15), 19 November 2026 (prerelease) |
| Exact annotated-tag source | [`a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281`](https://github.com/scarp-lang/scarp/commit/a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281) |
| Machine-readable target | [`docs/compiler-target.json`](compiler-target.json) |
| Main verification | [Linux, Windows and macOS source/output jobs](../.github/workflows/examples.yml), [Pages/catalog build](../.github/workflows/pages.yml), compiler-target tests and release-pinned workshop fidelity |
| Previous main target | [Scarp v0.0.6-alpha.14](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.14), `43627b74af5fccccc5e233e98207413983ebafc1` |

**Integration status:** This pull request proposes promoting the active course from published alpha.14 to alpha.15. Until its CI succeeds and it merges, the default branch and production Pages retain their prior target. All 52 numbered lessons and exact output fixtures are preserved.

## Source-language support and limits

- Scarp's original numbered course covers bindings, output, control flow, typed functions, numerical operations, imports, project commands, static inspection and AI-oriented numerical primitives.
- The alpha.9 [historical BigInt workshop](../tutorials/exact-bigint/README.md) remains frozen to its own published compiler.
- Exact decimal arithmetic arrived in alpha.11; the existing separately proposed Decimal feature workshop has its own release pin.
- Alpha.12 introduced bounded immutable typed lists and maps, concrete Option/Result variants, checked matching and restricted `?` propagation on immutable bind initializers in compatible named functions.
- Alpha.13 improved propagation/resource behavior and Rust embedding cache APIs. The eight-program [modern collections workshop](../tutorials/modern-collections/README.md) deliberately stays pinned to **published alpha.13**, including all 16 exact upstream source/output files.
- Alpha.14 improves pattern diagnostics and deterministic map projections. Its [structured-patterns workshop](../tutorials/structured-patterns/README.md) stays pinned to the separately published alpha.14 source; the nine-case lab retains its E0004 JSON diagnostics and exact outputs.
- Alpha.15 caps token and AST inspection source files at 1 MiB and meters equal-length string equality/inequality by UTF-8 bytes. The new [source-backed limits tutorial](../tutorials/alpha15-limits/README.md) ([हिन्दी](hi/alpha15-limits.md)) covers both. Semantic-cache revision validation and checked ELF64 shifts are Rust embedding APIs, not new Scarp syntax.

**Scope:** The active CLI runs programs with the local interpreter. Rust embedding interfaces for native C11/ELF64 object generation are experimental and restricted: no general `scarp compile` CLI, unrestricted native compilation, browser interpreter, networking, async runtime, GPU backend or automatic differentiation is implied.

## Build the exact active compiler

The `v0.0.6-alpha.15` annotated tag dereferences to **`a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281`**. Both main CI workflows pin this exact source commit at `.compiler`. Each additionally checks out alpha.13 as `.compiler-alpha13` solely for its historical workshop; those copies are not interchangeable.

~~~sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281
cargo build --locked --offline
./target/debug/scarp version
~~~

On Windows use `target\debug\scarp.exe`. In the learning repository, pass the absolute path to the built compiler:

~~~sh
python scripts/verify_examples.py --compiler /absolute/path/to/scarp
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
python scripts/verify_cli.py --compiler /absolute/path/to/scarp
python scripts/verify_alpha15_limits.py --compiler /absolute/path/to/scarp --compiler-source /path/to/alpha15/compiler/git/checkout
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
~~~

To verify the **historical** alpha.13 workshop, separately build the exact alpha.13 source (`e755fda37cdaeed29434e848cb5dd41f2f2e7eb2`) and run:

~~~sh
python scripts/verify_alpha13_compat.py --compiler /path/to/alpha13/scarp --compiler-source /path/to/alpha13/compiler/git/checkout
~~~

For the historical alpha.14 structured-pattern and diagnostic workshops, build source commit `43627b74af5fccccc5e233e98207413983ebafc1` in a separate checkout and run `scripts/verify_alpha14_patterns.py` and `scripts/verify_alpha14_diagnostics.py` using that binary and source directory. The active alpha.15 binary cannot replace these pinned provenance checks.

Historical programs and fixtures are compared to their original committed sources and executed against the corresponding release. CLI version, silent static verification and byte-exact UTF-8 stdout are checked. Python-only tests do not replace running the actual compiler.

## Upgrade policy

1. Resolve an already-published compiler tag to the full, immutable source commit and verify the published artifacts.
2. Update `compiler-target.json`, both active CI checkouts, human-readable release labels, and site-generated provenance together.
3. Keep all historical workshop compiler checkouts separate. Never silently repin them to the active compiler.
4. Run exact program output, guided labs, CLI/project smoke tests, bilingual HTML generation, link checks and regression tests on Linux, macOS and Windows.
5. Require successful checks and maintainer review before merging. Only a main-branch workflow may deploy the verified course website; a PR itself does not publish anything.

Scarp syntax remains unstable between prereleases. See the [compiler releases archive](https://github.com/scarp-lang/scarp/releases).
