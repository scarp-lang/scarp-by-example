# Compiler compatibility policy

Scarp is an experimental programming language; **syntax, commands and runtime behavior can change between prereleases**. Do not treat a matching version prefix or a development branch name as evidence of compatibility.

## Verified target for this learning course

| Property | Recorded target |
| --- | --- |
| Published Scarp prerelease | [v0.0.5-alpha.4](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.4) |
| Exact source commit | [`79141329176f5dce51457e90a6652902f6432135`](https://github.com/scarp-lang/scarp/commit/79141329176f5dce51457e90a6652902f6432135) |
| Status | **Prerelease**, not a stable or production-ready compiler |
| Previous tested target | Published [alpha.3](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.3) (source `7715c28df09c7703b39e14fddb963275b25df476`) |
| Source-of-truth metadata | [`compiler-target.json`](compiler-target.json) |
| Testing | [Three-platform compiler validation](../.github/workflows/examples.yml) and [pre-publish catalog checks](../.github/workflows/pages.yml) |

Both GitHub Actions workflows check out the **full immutable source SHA** rather than floating `main` or a release tag. The metadata contract is unit-tested against both workflow refs. The course statically validates every lesson with `scarp verify` and compares byte-exact output using `scarp exec`. An independent CLI smoke test checks legacy compatibility, real project scaffolding/launch, project static verification, and invalid manifest defenses. Historical `check` evaluates selected runtime statements silently; it **must not** be confused with non-executing `verify`.

The published alpha.4 source contains `exec`, static `verify`, and `inspect`, alongside legacy `run`/`check`. It adds **`create DIRECTORY`**, **`launch DIRECTORY`** and static **`verify DIRECTORY`** for bounded, explicit `Scarp.project` directories. See the [English project tutorial](project-workflow.md) and [हिन्दी गाइड](hi/project-workflow.md). New CLI names, AST inspection and text construction do **not** imply native code generation, an LSP, automatic differentiation, or general maps and sets. Scarp by Example teaches only source-backed features represented in its runnable lessons. Lesson `01-basics/16-text-construction.srp` uses text intrinsics first published in **alpha.3** and retained in alpha.4, including `text_concat`, `text_slice` and `text_repeat` implementation; it was not in the earlier pinned `e4db8e1` source. This is Unicode-scalar slicing, not a guarantee about grapheme clusters or Unicode normalization.

**Upstream published-release audit (2026-11-03):** GitHub's published release record and annotated tag identify v0.0.5-alpha.4 source SHA `7914132`. Some upstream reference text still describes alpha.4 as an unpublished candidate. The **public release record and annotated tag** confirm publication; stale prose is not used to select the pin. The published release record, immutable annotated tag and tagged `Cargo.toml` take precedence.

The project sample in [`tutorials/first-project/`](../tutorials/first-project/Scarp.project) is verified against the pinned compiler but is **not counted** as one of the 50 numbered source lessons. `launch` executes with the interpreter; this is not native source compilation or a package registry.

## Run exactly this tested source

```sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout 79141329176f5dce51457e90a6652902f6432135
cargo build --locked --offline
./target/debug/scarp --version
```

On Windows, use `target\\debug\\scarp.exe`. To run the full Scarp by Example suite, from the learning repository use:

```sh
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp/target/debug/scarp
```

The output fixtures follow the original compiler examples; a program may depend on that particular interpreter revision. An unrelated, older binary may reject newer syntax. `--version` identifies the package version, while `git rev-parse HEAD` identifies the precise checkout. For command usage, see the [English CLI guide](cli-quickstart.md) or [हिन्दी CLI गाइड](hi/cli-quickstart.md).

## Upgrading to another compiler release

1. Select a **published** release source revision and independently verify the tag resolves to a real immutable 40-character commit SHA.
2. In one PR, update `docs/compiler-target.json` and the compiler `ref` in **both** workflow files.
3. Run unit tests, all runnable examples with static `verify` and byte-exact `exec` on Linux, Windows and macOS; run the CLI/project smoke tests and Pages catalog build.
4. Investigate any changed output, failure, or error behavior. Modify a fixture only for an intentional, verified upstream change, preserving its provenance and both language guides.
5. Merge only after green checks. Confirm the new main-branch workflow and Pages deployment. Never describe an alpha as a stable release.

Unimplemented general-purpose collections, structured error values, async/await, networking, native compilation, general-purpose agent tooling and autograd must not be advertised as current features.
