# Compiler compatibility policy

Scarp is an experimental programming language; **syntax, commands and runtime behavior can change between prereleases**. Do not treat a matching version prefix or a development branch name as evidence of compatibility.

## Verified target for this learning course

| Property | Recorded target |
| --- | --- |
| Published Scarp prerelease | [v0.0.5-alpha.3](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.3) |
| Exact source commit | [`7715c28df09c7703b39e14fddb963275b25df476`](https://github.com/scarp-lang/scarp/commit/7715c28df09c7703b39e14fddb963275b25df476) |
| Status | **Prerelease**, not a stable or production-ready compiler |
| Previous tested target | `e4db8e191cd7ea623123cae7348450ca6c95b170`, an earlier development commit |
| Source-of-truth metadata | [`compiler-target.json`](compiler-target.json) |
| Testing | [Three-platform compiler validation](../.github/workflows/examples.yml) and [pre-publish catalog checks](../.github/workflows/pages.yml) |

Both GitHub Actions workflows check out the **full immutable source SHA** rather than floating `main` or a release tag. The metadata contract is unit-tested against both workflow refs. Source and expected output are byte-for-byte compared using `scarp run`, and `scarp check` must succeed. Those two commands are still supported by this release, but the historical `check` path evaluates selected runtime statements silently—it **must not** be confused with the newer non-executing `verify` command.

The alpha.3 source contains newer Scarp-first CLI entries such as `exec`, `verify` and `inspect`, alongside legacy `run` and `check`. New CLI names, AST inspection and text construction do **not** imply native code generation, an LSP, automatic differentiation, or general maps and sets. Scarp by Example currently teaches only the source-backed features represented in its runnable lessons.

**Upstream documentation audit (2026-11-02):** GitHub's published release record and annotated tag identify v0.0.5-alpha.3 source SHA `7715c28`. Several older upstream README/changelog/reference paragraphs still describe 0.0.5-alpha.1 or alpha.2 as the latest; those passages are stale and are not used to choose this pinned revision. The immutable release tag and source `Cargo.toml` take precedence.

## Run exactly this tested source

```sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout 7715c28df09c7703b39e14fddb963275b25df476
cargo build --locked --offline
./target/debug/scarp --version
```

On Windows, use `target\\debug\\scarp.exe`. To run the full Scarp by Example suite, from the learning repository use:

```sh
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp/target/debug/scarp
```

The output fixtures follow the original compiler examples; a program may depend on that particular interpreter revision. An unrelated, older binary may reject newer syntax. `--version` identifies the package version, while `git rev-parse HEAD` identifies the precise checkout.

## Upgrading to another compiler release

1. Select a **published** release source revision and independently verify the tag resolves to a real immutable 40-character commit SHA.
2. In one PR, update `docs/compiler-target.json` and the compiler `ref` in **both** workflow files.
3. Run unit tests, all runnable examples with `check` and byte-exact `run` on Linux, Windows and macOS; run the Pages catalog build.
4. Investigate any changed output, failure, or error behavior. Modify a fixture only for an intentional, verified upstream change, preserving its provenance and both language guides.
5. Merge only after green checks. Confirm the new main-branch workflow and Pages deployment. Never describe an alpha as a stable release.

Unimplemented general-purpose collections, structured error values, async/await, networking, native compilation, general-purpose agent tooling and autograd must not be advertised as current features.
