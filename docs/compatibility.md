# Compiler compatibility policy

Scarp is experimental prerelease software. The learning course pins a published, immutable compiler source revision. The moving `main` branch and unimplemented language proposals are not compatibility contracts.

## Current compiler target

| Property | Recorded target |
| --- | --- |
| GitHub release | [Scarp v0.0.6-alpha.1](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.1), published 5 November 2026 as a prerelease |
| Annotated-tag source commit | [`aa329a22cf2bf92d2c9814a26ff9c8b67a72e6e8`](https://github.com/scarp-lang/scarp/commit/aa329a22cf2bf92d2c9814a26ff9c8b67a72e6e8) |
| Previous course compiler | [v0.0.5-alpha.5](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.5), commit `2eeed0aa52ccb59523307841ad8ffbd83f8911a8` |
| Source of truth | [`compiler-target.json`](compiler-target.json) |
| Required gates | [Examples across three OSes](../.github/workflows/examples.yml) and [Pages build](../.github/workflows/pages.yml) |

The annotated `v0.0.6-alpha.1` Git tag dereferences to the exact commit above. The public GitHub release lists seven archive/checksum assets. Some upstream release prose still says *unpublished candidate*, which describes its original preparation, not its subsequent publication. CI must validate **the course itself** against the pinned commit before merging this upgrade.

## Available in alpha.6

- Pure `rms(vector) -> float` computes root mean square on nonempty finite vectors and visible windows; it is stable for the tested large finite magnitudes. The empty input is an error. See the [numbered lesson](../examples/04-collections/12-root-mean-square.srp) and [Hindi notes](hi/04-collections.md).
- Read-only `scarp inspect symbols [--json] FILE|DIRECTORY` and `scarp inspect references [--json] FILE|DIRECTORY` provide typed, schema-v1 symbol/reference inventories without executing ordinary runtime statements. [English tutorial](source-navigation.md) · [हिन्दी गाइड](hi/source-navigation.md).
- Previous alpha.5 project-directory module inspection remains supported. All three inspection views are static metadata, **not program output**.

The existing limited scalar C11 emitter remains experimental and exposed only through Rust embedding APIs. There is no public `scarp compile` executable command, LSP server, stable symbol IDs across edits, rename engine, general arrays/tuples, maps/records, structured error values, async runtime, package registry, GPU execution or automatic differentiation.

## Build and verify the exact compiler

```sh
git clone https://github.com/scarp-lang/scarp.git
cd scarp
git checkout aa329a22cf2bf92d2c9814a26ff9c8b67a72e6e8
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
