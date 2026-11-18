# Compiler compatibility policy

Scarp is a development-stage language. The learning repository tests a **published, immutable compiler source commit**, not a moving `main` branch or an unimplemented proposal. A release tag alone does not prove example compatibility; passing CI is required.

## Current target in this integration branch

| Property | Selected target |
| --- | --- |
| Release | [Scarp v0.0.6-alpha.13](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.13), published 17 November 2026 as a prerelease |
| Annotated tag | `v0.0.6-alpha.13` resolves to [`e755fda37cdaeed29434e848cb5dd41f2f2e7eb2`](https://github.com/scarp-lang/scarp/commit/e755fda37cdaeed29434e848cb5dd41f2f2e7eb2) |
| Source of truth | [`compiler-target.json`](compiler-target.json) |
| Required gates | [Examples on three operating systems](../.github/workflows/examples.yml), [Pages build](../.github/workflows/pages.yml), release-pinned workshop fidelity, compiler-target and course unit tests |
| Previous course target | [Scarp v0.0.6-alpha.4](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.4), commit `f04be0758cbce405ddcdb229699b0ff83c09d207` |

**Status:** This pull request proposes alpha.13 as the active compiler target. Do **not** describe the upgrade as fully validated until the relevant GitHub Actions checks have completed successfully and the pull request has been reviewed.

## Features supported by the selected compiler

- Existing 52 numbered lessons: output, bindings, function contracts, control flow, numeric vectors, imports, project workflows and static source inspection. Their code and expected outputs remain unchanged during this upgrade.
- Alpha.9: bounded exact `bigint` (see the independently pinned [BigInt workshop](../tutorials/exact-bigint/README.md)).
- Alpha.10 / alpha.11: bounded decimal core and exact `decimal` source-language operations from alpha.11. This type is not a silently converted binary float.
- Alpha.12: immutable typed `list<T>` and `map<K,V>`, concrete `option<T>` and `result<T,E>`, checked exhaustive matching, and `?` propagation on immutable bind initializers in compatible named functions.
- Alpha.13: better immutable-error propagation handling, resource-budget regression coverage, revision-aware semantic caches and editor-host workspace generations. Cache and editor improvements are **Rust hosting APIs**, not new Scarp-language intrinsics.

See the [source-pinned modern collections and checked-results workshop](../tutorials/modern-collections/README.md) for eight canonical executable examples of the alpha.12 language features on the **published alpha.13** compiler.

**Boundaries:** This is an interpreter-backed language. Native C11 and ELF64 scalar backends remain experimental and restricted. Do not infer a production native compiler, async runtime, networking, GPU backend, package registry, general heap mutation or automatic differentiation from these examples. Lists/maps are immutable snapshots with explicit resource limits.

## Published alpha.14 compatibility preview (separate from the active target)

[Scarp v0.0.6-alpha.14](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.14) was published 18 November 2026 at exact source commit `43627b74af5fccccc5e233e98207413983ebafc1`. It improves diagnostics for nested record/tuple/array destructuring patterns, checks deterministic map projections and adds **Rust-host-only** editor-cache and checked ELF64 integer kernel behavior. These changes do not provide a general native-code Scarp command or new pattern guards.

The [alpha.14 workshop](../tutorials/structured-patterns/README.md) imports two source-and-output pairs from that immutable compiler commit. The separate [alpha.14 compatibility workflow](../.github/workflows/alpha14-patterns.yml) checks their committed Git-object provenance, compiler version, static verification and exact output **and additionally runs the existing numbered course, labs and CLI** on Linux, Windows and macOS.

**Promotion gate:** The main `docs/compiler-target.json` and both active compiler workflows continue to select alpha.13. Alpha.14 is a **candidate compatibility target**, not yet the proven default for this repository. Move the shared pin and update all human labels only after the independent matrix passes and a separate reviewed change confirms Pages, lessons, CLI, labs and historical workshop behavior. Do not rewrite expected outputs just to silence a regression.

## Build and verify exact source

The annotated `v0.0.6-alpha.13` tag dereferences to **`e755fda37cdaeed29434e848cb5dd41f2f2e7eb2`**. Both active CI compiler checkouts must use that full immutable SHA, recorded in `compiler-target.json`. Historic workshops retain their own immutable compiler pins.

~~~sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout e755fda37cdaeed29434e848cb5dd41f2f2e7eb2
cargo build --locked --offline
./target/debug/scarp version
~~~

On Windows use `target\debug\scarp.exe`. From the course checkout, run:

~~~sh
python scripts/verify_examples.py --compiler /absolute/path/to/scarp
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
python scripts/verify_cli.py --compiler /absolute/path/to/scarp
python scripts/verify_alpha13_compat.py --compiler /absolute/path/to/scarp --compiler-source /path/to/compiler/git/checkout
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
~~~

The workshop verifier checks upstream source and fixture copies **byte-for-byte** against the exact compiler checkout, confirms the binary version, invokes static `verify` and compares interpreter stdout bytes. Python-only unit tests cannot replace a real compiler run. The static Pages site does **not** execute Scarp in a browser.

## Upgrade rules

1. Resolve a published annotated compiler release to its exact source commit.
2. Update `compiler-target.json`, the compiler checkout in **both** active workflows, and human compatibility labels as one change.
3. Preserve historic expected output. Do not rewrite fixtures to hide semantic regressions.
4. Run old lessons, bilingual guide checks, labs, CLI/project smoke tests, workshop fidelity and site generation across supported CI platforms.
5. Merge only after required checks pass. A proposed source pin is not a published Scarp by Example prerelease or proof of compatibility.

Historical compiler detail remains in [the official release archive](https://github.com/scarp-lang/scarp/releases) and repository history.
