# Compiler compatibility policy

Scarp is an experimental programming language. Source syntax, CLI details and embedding APIs can change between prereleases; neither compiler `main` nor a proposal is a compatibility guarantee.

## Verified compiler pin for this learning course

| Property | Recorded target |
| --- | --- |
| Published release | [Scarp v0.0.5-alpha.5](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.5) |
| Immutable annotated-tag source commit | [`2eeed0aa52ccb59523307841ad8ffbd83f8911a8`](https://github.com/scarp-lang/scarp/commit/2eeed0aa52ccb59523307841ad8ffbd83f8911a8) |
| Status | **Prerelease**; not a stable or production-ready language |
| Previous course compiler | [v0.0.5-alpha.4](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.4) at `79141329176f5dce51457e90a6652902f6432135` |
| Source of truth | [`compiler-target.json`](compiler-target.json) |
| Validation | [All three OS platforms](../.github/workflows/examples.yml) and [Pages build](../.github/workflows/pages.yml) |

**Release audit (November 4, 2026):** GitHub's public release record has `prerelease=true` and seven native archive/checksum assets. Its annotated tag `v0.0.5-alpha.5` dereferences to **`2eeed0aa52ccb59523307841ad8ffbd83f8911a8`**, matching that tagged source's `Cargo.toml` package version. The later compiler `main` includes additional post-release maintenance commits and is **not** the tagged source. The [compiler's post-publication audit](https://github.com/scarp-lang/scarp/blob/main/docs/releases/v0.0.5-alpha.5-validation.md) independently documents the same source.

The pinned source and the **exact same full commit SHA** appear in both GitHub Actions workflows. The verifier runs static `scarp verify` followed by real `scarp exec` and compares all 50 lessons against byte-exact checked-in stdout. The six guided lab starters and reference solutions are also compiled, run and verified. The independent CLI test exercises project verification, launch and inspection. A green test is required before a new compiler target reaches `main`.

## What changed in published alpha.5

Alpha.4 introduced explicit `Scarp.project` directories with `scarp create DIRECTORY`, static `verify DIRECTORY` and interpreter-backed `launch DIRECTORY`. These continue to work in alpha.5.

**New in alpha.5:** `scarp inspect modules --json PROJECT_DIRECTORY` resolves the explicit manifest and returns schema-v1 read-only module metadata. The same graph can be inspected from the project's canonical entry `.srp` file. Neither invocation executes ordinary program statements. The legacy `scarp modules --json DIRECTORY` remains supported. See the [bilingual source-backed example](project-inspection.md) ([हिन्दी](hi/project-inspection.md)).

**Experimental embedding API only:** Alpha.5 adds scalar C11 source emission via `scarp::c_backend::emit_c` / `emit_program`. It is a deliberately restricted Rust library API. It does **not** create a `scarp compile` CLI command, general `.srp` executables or a stable ABI. Supported scalar control-flow forms do not imply that numerical vectors, functions/recursion, floating-point expressions, multi-argument output or GPU operations can be emitted by this backend. Runtime `exec` and `launch` remain interpreter-backed.

Source-only features such as text construction were first introduced before alpha.5 and are retained here. The original course lesson `01-basics/16-text-construction.srp` uses Unicode-scalar slicing, not Unicode grapheme-cluster segmentation.

## Reproduce the exact tested compiler

```sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout 2eeed0aa52ccb59523307841ad8ffbd83f8911a8
cargo build --locked --offline
./target/debug/scarp version
```

On Windows the binary is `target\\debug\\scarp.exe`. From the **scarp-by-example** root, use that exact executable to run:

```sh
python scripts/verify_examples.py --compiler /absolute/path/to/scarp
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
python scripts/verify_cli.py --compiler /absolute/path/to/scarp
```

The JSON metadata of module inspection is **not** ordinary Scarp program stdout and is not represented by a fake `.stdout` lesson fixture. The module-inspection tutorial has its own actual interpreter output fixture.

## Compiler upgrade gate

1. Verify the **published GitHub release**, annotated tag and full immutable source SHA; do not select floating `main`.
2. Update `compiler-target.json` and the pinned source checkout in **both** workflow files in the same PR.
3. Run the unit suite, all numbered lesson `verify` and byte-exact `exec` checks, six guided labs, project-level CLI/inspection tests and static site build on Linux, Windows and macOS.
4. Inspect diagnostics and output differences. Do not modify fixtures or source material merely to hide a mismatch; retain provenance and English/Hindi explanations.
5. Merge only when all required checks pass; independently confirm the GitHub Pages deployment and release records.

**Not implemented as general Scarp language features:** native `.srp` executable compilation from the CLI, a package registry, general-purpose records/maps/sets, structured error values, async/await, networking, a full GPU backend or automatic differentiation. Study [the current compiler feature matrix](https://github.com/scarp-lang/scarp/blob/main/docs/development/feature-matrix.md) for detailed status.
