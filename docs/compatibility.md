# Compiler compatibility policy

Scarp is a development-stage programming language. This learning repository selects an **immutable, publicly published compiler source commit**; a tag alone does not prove compatibility without real operating-system tests.

## Proposed active course target: Scarp v0.0.7-alpha.1

| Property | Target |
| --- | --- |
| Published release | [Scarp v0.0.7-alpha.1](https://github.com/scarp-lang/scarp/releases/tag/v0.0.7-alpha.1), 25 November 2026 (prerelease) |
| Exact release-tag source | [`996bd5b83c8cb26e98637563729f67bdacc61cd4`](https://github.com/scarp-lang/scarp/commit/996bd5b83c8cb26e98637563729f67bdacc61cd4) |
| Machine-readable target | [`docs/compiler-target.json`](compiler-target.json) |
| Main verification | [Linux, Windows and macOS source/output jobs](../.github/workflows/examples.yml), [Pages/catalog build](../.github/workflows/pages.yml), compiler-target tests and historical source fidelity |
| Previous active target | [Scarp v0.0.6-alpha.20](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.20), `b1a9347f93540fdf95b0ddecba4adc55a3b4bb98` |

**Integration status:** The published `v0.0.7-alpha.1` tag directly identifies the exact compiler source commit above. This PR proposes that published source as the active target while preserving all **60 numbered lessons**, including their original alpha.18/19 source provenance. Existing fixtures remain intact. Historical alpha.13, alpha.14, alpha.15 and alpha.20 checks continue to use their independent release source commits. Linux/Windows/macOS and Pages validations plus maintainer review are required before merging; PR creation does not deploy the website.

## Source-language support and limits

- Scarp's original numbered course covers bindings, output, control flow, typed functions, numerical operations, imports, project commands, static inspection and AI-oriented numerical primitives.
- Published alpha.6 supports redirected `read_line()` and immutable tuple values; the [bilingual input and tuples workshop](../tutorials/input-and-tuples/README.md) remains separately pinned to `cdf6a3924ec2a36c7beca5a9aec4f01a0bce515e`. Its dedicated workflow exercises raw UTF-8 redirected stdin and E0055 on premature EOF. **Alpha.6 does not support `--interactive` or `--input-file`**; those are newer CLI features.
- The alpha.9 [historical BigInt workshop](../tutorials/exact-bigint/README.md) remains frozen to its own published compiler.
- Exact decimal arithmetic arrived in alpha.11; the [historical Decimal workshop](../tutorials/exact-decimal/README.md) has its own alpha.11 release pin.
- Alpha.12 introduced bounded immutable typed lists and maps, concrete Option/Result variants, checked matching and restricted `?` propagation on immutable bind initializers in compatible named functions.
- Alpha.13 improved propagation/resource behavior and Rust embedding cache APIs. The eight-program [modern collections workshop](../tutorials/modern-collections/README.md) deliberately stays pinned to **published alpha.13**, including all 16 exact upstream source/output files.
- Alpha.14 improves pattern diagnostics and deterministic map projections. Its [structured-patterns workshop](../tutorials/structured-patterns/README.md) stays pinned to the separately published alpha.14 source; the nine-case lab retains its E0004 JSON diagnostics and exact outputs.
- Historical alpha.15 caps token and AST inspection source files at 1 MiB and meters equal-length string equality/inequality by UTF-8 bytes. The new [source-backed limits tutorial](../tutorials/alpha15-limits/README.md) ([हिन्दी](hi/alpha15-limits.md)) covers both. Semantic-cache revision validation and checked ELF64 shifts are Rust embedding APIs, not new Scarp syntax.

**Scope:** The active CLI runs programs with the local interpreter. Rust embedding interfaces for native C11/ELF64 object generation are experimental and restricted: no general `scarp compile` CLI, unrestricted native compilation, browser interpreter, networking, async runtime, GPU backend or automatic differentiation is implied.

- Alpha.16 introduces bounded finite-vector median/quantile and Unicode text and integer helpers.
- Alpha.17 introduces fixed-array `array_len` and `array_get_or` and an explicitly interactive `input_boolean` path.
- Alpha.8 added the declarative lower-case `scarp.project` v2 format, `scarp init`, `scarp test` and `scarp project info` while preserving legacy `Scarp.project` v1.
- The [published-manifest migration workshop](../tutorials/project-migration/README.md) checks that legacy `Scarp.project` v1 and declarative `scarp.project` v2 use byte-identical source, tests, stdin and stdout; it rejects incorrectly declaring a rename-only legacy header to be v2.
- Alpha.18 adds pure fixed-array `array_set` (a new immutable snapshot), empty-window memory-retention improvements, and default project resolution for `scarp exec`.
- Alpha.19 adds Rust-host named callable handles, signature/effect compatibility, usage receipts and cumulative execution ledgers. It **does not** add first-class Scarp function values, closures or an unrestricted native compiler CLI. Tuple indexed assignment was not published until alpha.20.
- Alpha.20 introduces exact decimal literals, constant-index persistent mutable tuple replacement, numeric tuple ordering and canonical lowercase v2 scaffolding for both `create` and `init`. The CLI still uses the interpreter; native ELF64 generation remains a restricted Rust API.

- Scarp v0.0.7-alpha.1 adds fixed-array concatenation, variadic integer reductions and stable softplus. Its experimental Rust-host ELF64 API supports additional integer arguments and restricted loop/control-flow forms; the source CLI still executes through the interpreter. Interpreter frame reuse is an implementation improvement, not a source-level lifetime annotation or a general native backend.

## Build the exact active compiler

The `v0.0.7-alpha.1` release tag resolves to **`996bd5b83c8cb26e98637563729f67bdacc61cd4`**. Both CI workflows pin this source commit at `.compiler`. They separately check out alpha.13 as `.compiler-alpha13` and alpha.15 as `.compiler-alpha15` for their historic workshop/boundary regressions; those copies are not interchangeable.

~~~sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout 996bd5b83c8cb26e98637563729f67bdacc61cd4
cargo build --locked --offline
./target/debug/scarp version
~~~

On Windows use `target\debug\scarp.exe`. In the learning repository, pass the absolute path to the built compiler:

~~~sh
python scripts/verify_examples.py --compiler /absolute/path/to/scarp
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
python scripts/verify_cli.py --compiler /absolute/path/to/scarp
python scripts/verify_alpha15_limits.py --compiler /absolute/path/to/alpha15/scarp --compiler-source /path/to/alpha15/compiler/git/checkout
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
~~~

To verify the **historical** alpha.13 workshop, separately build the exact alpha.13 source (`e755fda37cdaeed29434e848cb5dd41f2f2e7eb2`) and run:

~~~sh
python scripts/verify_alpha13_compat.py --compiler /path/to/alpha13/scarp --compiler-source /path/to/alpha13/compiler/git/checkout
~~~

For the historical alpha.14 structured-pattern, diagnostic and frozen 55-lesson workshops, build source commit `43627b74af5fccccc5e233e98207413983ebafc1` in a separate checkout and run `scripts/verify_alpha14_patterns.py`, `scripts/verify_alpha14_diagnostics.py` and `scripts/verify_alpha14_course.py` using that binary and source directory (the frozen lesson verifier only needs the compiler executable). The active v0.0.7-alpha.1 binary cannot replace these pinned provenance checks.

Historical programs and fixtures are compared to their original committed sources and executed against the corresponding release. CLI version, silent static verification and byte-exact UTF-8 stdout are checked. Python-only tests do not replace running the actual compiler.

## Upgrade policy

1. Resolve an already-published compiler tag to the full, immutable source commit and verify the published artifacts.
2. Update `compiler-target.json`, both active CI checkouts, human-readable release labels, and site-generated provenance together.
3. Keep all historical workshop compiler checkouts separate. Never silently repin them to the active compiler.
4. Run exact program output, guided labs, CLI/project smoke tests, bilingual HTML generation, link checks and regression tests on Linux, macOS and Windows.
5. Require successful checks and maintainer review before merging. Only a main-branch workflow may deploy the verified course website; a PR itself does not publish anything.

Scarp syntax remains unstable between prereleases. See the [compiler releases archive](https://github.com/scarp-lang/scarp/releases).

## Independent published alpha.20 workshop

The [exact-values workshop](../tutorials/alpha20-exact-values/README.md) ([हिन्दी](hi/alpha20-exact-values.md)) retains its own published alpha.20 pin, even after the active numbered course migrates to v0.0.7-alpha.1. Its five programs and six negative cases run on all three supported hosts. Decimal literal and tuple indexed assignment support must not be inferred for older releases.

## Independent published v0.0.7-alpha.1 workshop

The [numerical programming workshop](../tutorials/alpha7-numerical/README.md) ([हिन्दी](hi/alpha7-numerical.md)) pins the published compiler commit `996bd5b83c8cb26e98637563729f67bdacc61cd4`. It teaches array concatenation, multi-argument integer reductions and stable vector softplus with original programs and exact output fixtures. The proposed numbered course target now matches this workshop, which retains a separate three-platform verifier and Pages publication gate. Historical compiler pins remain unchanged. Native object emission in this release is still an experimental Rust API, not a general CLI compilation mode.

### Historical alpha.10 and alpha.11 workshops

The [alpha.10 foundations workshop](../tutorials/alpha10-foundations/README.md) uses immutable source `44fcd0f77ccb92648cdb1fc7632495c506c87cb3`. Its redirected stdin and interactive capability requirements describe that release, not the newer default interactive behavior of `exec`.

The [alpha.11 Decimal workshop](../tutorials/exact-decimal/README.md) uses immutable source `79b57395957f47e1270ee542a856c844b82386de`. Its constructors, rounding and interactive gate predate alpha.20 decimal literal syntax. Each workshop has a separate real-compiler verifier and three-platform CI. No current course fixtures are replaced.
