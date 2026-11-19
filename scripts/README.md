# Automated lesson validation

Run these commands from the `scarp-by-example` repository root:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp
python3 scripts/verify_cli.py --compiler /absolute/path/to/scarp
```

The Python 3 verifier uses only the standard library. The project-smoke check also verifies the checked-in `tutorials/first-project` sample and the exact output bytes.

The Python 3 verifier uses only the standard library. It discovers all numbered `.srp` lessons (excluding `_support` source modules), rejects missing/orphaned `.stdout` files, invokes static `scarp verify` then `scarp exec`, and compares the raw output bytes. The independent CLI smoke test verifies legacy `run` equivalence, static-vs-runtime checks and real alpha.4 project creation, directory verification, launch, existing-directory rejection and path-traversal diagnostics.

The `test_lesson_notes.py` tests enforce 52 exact Hindi/source/fixture matches and HTML-safe rendering. The website generator embeds the notes and rejects missing explanations, so no page can silently show an unrelated translation.

CI builds and runs the exact Scarp source commit identified in `.github/workflows/examples.yml`, on Linux, Windows and macOS. A passing upstream compiler test is an **input** to this project, not a substitute for passing this repository's own checks.

To upgrade compiler compatibility, update `docs/compiler-target.json`, the primary `path: .compiler` checkout in **both** workflows and the build command in `docs/compatibility.md` together. The `scripts/test_compiler_target.py` guard validates the active checkout by path while allowing independently pinned historical compiler checkouts (for byte-exact lesson provenance). All compiler checkouts must use immutable 40-character commit SHAs. Run the full CI matrix and CLI smoke tests, and review every output change before merging. See the [CLI guide](../docs/cli-quickstart.md).

The source-navigation CLI smoke checks the two-module `tutorials/source-navigation` project (originally introduced in alpha.6) against the active alpha.13 compiler. It validates exact interpreter output, both shadowed `base` definitions and their reference targets, argument labels, imported visibility and UTF-8 byte spans on the supported CI platforms. Static inspection is never presented as program stdout.

**Current compiler workshop:** `scripts/verify_alpha13_compat.py` checks eight official alpha.13 list/map/Option/Result examples against the exact published compiler checkout, expected binary version, byte-identical upstream source and output, static verification and exact execution bytes. The main examples and Pages workflows run it alongside the existing course gates. The static course site generates a dedicated modern workshop page with source and exact expected output; browser execution is not provided.

## Published alpha.15 limits regression

The primary CI and Pages gates run `scripts/verify_alpha15_limits.py` against the
exact alpha.15 compiler checkout. It checks the full commit SHA, executable
version, source-backed string comparison output, the exact 1 MiB frontend
inspection boundary and the 129-byte string comparison work budget.

```sh
python scripts/verify_alpha15_limits.py --compiler .compiler/target/debug/scarp --compiler-source .compiler
```

The verifier creates only disposable files, uses standard-library Python and
runs independently of the historical alpha.13 and alpha.14 workshops.
