# Compiler compatibility policy

Scarp is experimental prerelease software. The learning course pins a published, immutable compiler source revision. The moving `main` branch and unimplemented language proposals are not compatibility contracts.

## Current compiler target

| Property | Recorded target |
| --- | --- |
| GitHub release | [Scarp v0.0.6-alpha.4](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.4), published 8 November 2026 as a prerelease |
| Annotated-tag source commit | [`f04be0758cbce405ddcdb229699b0ff83c09d207`](https://github.com/scarp-lang/scarp/commit/f04be0758cbce405ddcdb229699b0ff83c09d207) |
| Previous course compiler | [v0.0.6-alpha.4](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.4), commit `ceff07d9014f466974e0c9e02fc5d23573f55777` |
| Source of truth | [`compiler-target.json`](compiler-target.json) |
| Required gates | [Examples across three OSes](../.github/workflows/examples.yml) and [Pages build](../.github/workflows/pages.yml) |

The annotated `v0.0.6-alpha.4` Git tag dereferences to the exact commit above. The public prerelease provides Windows x64, Linux x64 and macOS Apple Silicon archives, checksum sidecars and a combined checksum manifest. The compiler's `docs/releases/v0.0.6-alpha.4.md` is a **historical prepublication candidate**, not its current release status; use the [published release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.4) and its verification record. The course must independently test all lessons, labs and source navigation at this SHA before merging its new pin.

## Changes in published alpha.4

- Bounded sampled calculus supports `sample_area(x, y)`, `sample_cumulative_area(x, y)`, and `sample_slopes(x, y)` for equal-length finite vectors with strictly increasing sample coordinates.
- `cosine_similarity(left, right)` handles nonzero finite vectors with scaling and compensated reductions.
- The experimental Rust embedding API can emit one restricted x86-64 ELF64 relocatable integer-kernel object; there is **no** general native executable compiler or `scarp compile` command.
- Alpha.4 preserves earlier language syntax and CLI contracts. All existing lessons, labs, and navigation fixtures must independently pass at the new exact compiler pin; historical exercises are not silently rewritten.

## Changes in published alpha.3

- `topk(scores, count)` returns **original zero-based indices** sorted by descending score, with earlier indices winning ties. `topk_values(scores, count)` returns their original finite values. Both are deterministic, pure and bounded.
- `softmax_temp(scores, temperature)` and `logsoftmax_temp(scores, temperature)` produce temperature-controlled (log-)probabilities using a strictly positive finite float temperature. These are not random sampling operations.
- The compiler adds private typed scalar IR and differential verification for its restricted experimental native pipeline. **No native object writer, user-facing `scarp compile` command, GPU engine, or integrated AI runtime is introduced.**
- The optional [AI coding lab stretch](../labs/06-ai-foundations/stretch-solution.srp) combines Top-K with temperature-aware probabilities. Its solution fixture follows the official compiler's alpha.3 sample and is verified again by the course's cross-platform interpreter checks.
- Alpha.2's opt-in Rust embedding caches and invalidation APIs remain available without new Scarp source syntax or CLI commands.

## Available in alpha.6

- Pure `rms(vector) -> float` computes root mean square on nonempty finite vectors and visible windows; it is stable for the tested large finite magnitudes. The empty input is an error. See the [numbered lesson](../examples/04-collections/12-root-mean-square.srp) and [Hindi notes](hi/04-collections.md).
- Read-only `scarp inspect symbols [--json] FILE|DIRECTORY` and `scarp inspect references [--json] FILE|DIRECTORY` provide typed, schema-v1 symbol/reference inventories without executing ordinary runtime statements. [English tutorial](source-navigation.md) · [हिन्दी गाइड](hi/source-navigation.md).
- Previous alpha.5 project-directory module inspection remains supported. The [source-navigation workshop](../tutorials/source-navigation/README.md) exercises alpha.6 shadowed bindings, imported definitions and named-argument references using the same compiler pin. All three inspection views are static metadata, **not program output**.

The existing limited scalar C11 emitter remains experimental and exposed only through Rust embedding APIs. There is no public `scarp compile` executable command, LSP server, stable symbol IDs across edits, rename engine, general arrays/tuples, maps/records, structured error values, async runtime, package registry, GPU execution or automatic differentiation.

## Build and verify the exact compiler

```sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout ceff07d9014f466974e0c9e02fc5d23573f55777
cargo build --locked --offline
./target/debug/scarp version
```

On Windows use `target\\debug\\scarp.exe`. From the course root:

```sh
python scripts/verify_examples.py --compiler /absolute/path/to/scarp
python scripts/verify_guided_labs.py --compiler /absolute/path/to/scarp
python scripts/verify_cli.py --compiler /absolute/path/to/scarp
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
```

Each lesson must pass static verification and byte-exact runtime stdout comparison. Guided lab starters/solutions, read-only metadata, project commands and website generation have independent tests. CI runs Linux, Windows and macOS compiler checks; GitHub Pages generation follows its own verification gate. The learning website does **not** execute Scarp in the browser.

## Upgrade checklist

1. Independently check the public prerelease, annotated tag and dereferenced source SHA.
2. Change `compiler-target.json` and **both** checkout pins in one pull request.
3. Keep runnable sources, stdout fixtures, English/Hindi explanations and test expectations synchronized. Never rewrite a fixture simply to conceal a regression.
4. Require passing required Actions checks on the pull request before merging. Do not publish an independent course prerelease from an unverified source revision.
5. After merge, independently verify GitHub Pages and any subsequent release record.
